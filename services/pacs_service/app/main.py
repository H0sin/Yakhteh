from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, Base


def create_app() -> FastAPI:
    app = FastAPI(title="Yakhteh PACS Service", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup():
        # Ensure tables exist (dev convenience). In prod, rely on Alembic migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "service": "pacs", "environment": settings.environment}

    return app

