from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1.endpoints.studies import router as studies_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown - nothing to do for now


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yakhteh PACS Service", 
        version="0.1.0",
        docs_url="/docs",  # Default docs URL
        redoc_url="/redoc",  # Default ReDoc URL
        lifespan=lifespan
    )

    # CORS (restrict to specific origins for security)
    allowed_origins = [
        "http://localhost:3000",  # Local development
    ]
    if settings.my_domain != "localhost":
        allowed_origins.append(f"https://frontend.{settings.my_domain}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(studies_router, prefix="/api/v1/studies", tags=["studies"])

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "service": "pacs", "environment": settings.environment}

    return app
