import os
from typing import AsyncGenerator, Callable
from urllib.parse import urlsplit, urlunsplit

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.session import Base, get_session
from app.main import create_app


@pytest.fixture()
def anyio_backend() -> str:
    """Force pytest-anyio to use asyncio backend only."""
    return "asyncio"


def _build_test_database_url() -> str:
    """Create a test database URL, allowing override via TEST_DATABASE_URL env var."""
    override = os.getenv("TEST_DATABASE_URL")
    if override:
        return override

    raw = settings.database_url
    parts = urlsplit(raw)
    # parts.path includes leading '/'
    db_name = parts.path.rsplit('/', 1)[-1]
    if not db_name:
        raise RuntimeError("DATABASE_URL must include a database name")
    test_db_name = f"{db_name}_test"
    new_path = parts.path.rsplit('/', 1)[0] + f"/{test_db_name}"
    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))


async def _ensure_database_exists(db_url: str) -> None:
    """
    Ensure the target database exists by connecting to the admin 'postgres' database
    and creating it if missing. Works for Postgres with asyncpg. No-op for other DBs.
    """
    parts = urlsplit(db_url)
    if not parts.scheme.startswith("postgresql"):
        return  # Non-Postgres (e.g., SQLite) doesn't need explicit DB creation

    target_db = parts.path.rsplit('/', 1)[-1]
    admin_path = parts.path.rsplit('/', 1)[0] + "/postgres"
    admin_url = urlunsplit((parts.scheme, parts.netloc, admin_path, parts.query, parts.fragment))

    admin_engine = create_async_engine(admin_url, pool_pre_ping=True)
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": target_db})
            if not exists:
                # CREATE DATABASE cannot run inside a transaction
                await conn.exec_driver_sql("COMMIT")
                await conn.exec_driver_sql(f'CREATE DATABASE "{target_db}"')
    finally:
        await admin_engine.dispose()


@pytest.fixture()
async def test_engine_and_sessionmaker() -> AsyncGenerator[tuple[AsyncEngine, async_sessionmaker[AsyncSession]], None]:
    """
    Create an async engine/sessionmaker bound to an isolated test database.
    It creates all tables before the test and drops them afterwards.
    """
    test_db_url = _build_test_database_url()

    # Ensure DB exists before binding engine
    await _ensure_database_exists(test_db_url)

    engine = create_async_engine(test_db_url, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine, SessionLocal
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture()
async def app_with_overrides(test_engine_and_sessionmaker) -> FastAPI:
    """FastAPI app with DB dependency overridden to use the test session."""
    _, SessionLocal = test_engine_and_sessionmaker
    app = create_app()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:  # type: ignore[override]
        async with SessionLocal() as session:  # type: ignore
            yield session

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture()
async def client(app_with_overrides: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app_with_overrides), base_url="http://test") as ac:
        yield ac
