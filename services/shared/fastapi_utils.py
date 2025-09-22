"""Common FastAPI utilities."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .base_config import BaseServiceSettings


def setup_cors(app: FastAPI, settings: BaseServiceSettings) -> None:
    """Setup CORS middleware for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_logging(settings: BaseServiceSettings) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


@asynccontextmanager
async def lifespan_with_db_init(app: FastAPI, engine, base) -> AsyncGenerator[None, None]:
    """Lifespan context manager that initializes database tables."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    yield
    # Shutdown - nothing to do for now