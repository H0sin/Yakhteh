from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints.clinics import router as clinics_router


def create_app() -> FastAPI:
    app = FastAPI(title="Yakhteh Clinic Service", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(clinics_router, prefix="/api/v1/clinics", tags=["clinics"])

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "service": "clinic", "environment": settings.environment}

    return app
