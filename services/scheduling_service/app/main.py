from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints.appointments import router as appointments_router
from app.api.v1.endpoints.availability import router as availability_router
from app.db.session import engine, Base


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yakhteh Scheduling Service", 
        version="0.1.0",
        docs_url="/docs",  # Default docs URL
        redoc_url="/redoc"  # Default ReDoc URL
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

    app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["appointments"])
    app.include_router(availability_router, prefix="/api/v1/availability", tags=["availability"])

    @app.on_event("startup")
    async def on_startup():
        # Ensure tables exist (dev convenience). In prod, rely on Alembic migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "service": "scheduling", "environment": settings.environment}

    return app
