from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yakhteh Auth Service", 
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

    # Routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "service": "auth", "environment": settings.environment}

    return app
