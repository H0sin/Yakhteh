from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.api.v1.endpoints.auth import router as auth_router

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation errors consistently."""
    logger.error(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": str(exc)}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yakhteh Auth Service", 
        version="0.1.0",
        docs_url="/docs",  # Default docs URL
        redoc_url="/redoc"  # Default ReDoc URL
    )

    # Add exception handlers
    app.add_exception_handler(422, validation_exception_handler)
    app.add_exception_handler(500, general_exception_handler)

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
        return {
            "status": "ok", 
            "service": "auth", 
            "environment": settings.environment,
            "version": "0.1.0"
        }

    return app
