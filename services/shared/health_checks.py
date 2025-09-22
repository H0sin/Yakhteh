"""Health check utilities for services."""

import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def check_database_health(db: AsyncSession) -> Dict[str, Any]:
    """Check database connectivity and basic functionality."""
    try:
        # Simple query to test connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {"status": "healthy", "latency_ms": None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis_health(redis_url: str) -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        import redis.asyncio as redis
        
        r = redis.from_url(redis_url, decode_responses=True)
        await r.ping()
        await r.aclose()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def create_health_response(
    service_name: str,
    version: str,
    environment: str,
    checks: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Create standardized health check response."""
    response = {
        "service": service_name,
        "version": version,
        "environment": environment,
        "status": "healthy",
        "timestamp": None  # Will be set by calling service
    }
    
    if checks:
        response["checks"] = checks
        # Overall status is unhealthy if any check fails
        if any(check.get("status") == "unhealthy" for check in checks.values()):
            response["status"] = "unhealthy"
    
    return response