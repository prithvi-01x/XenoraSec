# app/routes/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, UTC

from app.schemas.scan import HealthResponse
from app.db.database import get_db
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint with database connectivity test.
    
    Returns 200 if healthy, 503 if database is unreachable.
    """
    
    # Test database connection
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        status_code = 200
        overall_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        status_code = 503
        overall_status = "unhealthy"
    
    response_data = {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
        "database": db_status
    }
    
    if status_code == 503:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content=response_data
        )
    
    return HealthResponse(**response_data)


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    """
    return {"alive": True}