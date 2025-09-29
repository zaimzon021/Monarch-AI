"""
Main API router that includes all route modules.
"""

from fastapi import APIRouter, Request
from datetime import datetime

from app.config.settings import settings
from app.config.database_init import check_database_health
from app.services.ai_service import get_ai_service
from app.models.responses import HealthCheckResponse, APIStatusResponse
from .text_routes import router as text_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(text_router)


@api_router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check the health status of the application and its dependencies"
)
async def health_check(
    request: Request,
    include_database: bool = True,
    include_ai_service: bool = True
) -> HealthCheckResponse:
    """
    Perform comprehensive health check.
    
    - **include_database**: Include database health in check (default: true)
    - **include_ai_service**: Include AI service health in check (default: true)
    """
    # Calculate uptime (simplified - would need actual start time in production)
    uptime = 0.0  # Placeholder
    
    health_response = HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        uptime=uptime
    )
    
    # Check database health
    if include_database:
        try:
            db_health = await check_database_health()
            health_response.database = db_health
            
            if db_health.get("status") != "healthy":
                health_response.status = "degraded"
        except Exception as e:
            health_response.database = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_response.status = "degraded"
    
    # Check AI service health
    if include_ai_service:
        try:
            ai_service = await get_ai_service()
            ai_health = await ai_service.health_check()
            health_response.ai_service = ai_health
            
            if ai_health.get("status") != "healthy":
                health_response.status = "degraded"
        except Exception as e:
            health_response.ai_service = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_response.status = "degraded"
    
    return health_response


@api_router.get(
    "/status",
    response_model=APIStatusResponse,
    summary="API status",
    description="Get current API status and feature availability"
)
async def get_api_status(request: Request) -> APIStatusResponse:
    """
    Get API status information.
    
    Returns current service status, version, and feature availability.
    """
    return APIStatusResponse(
        service_name=settings.app_name,
        version=settings.app_version,
        status="operational",
        timestamp=datetime.utcnow(),
        features={
            "text_modification": True,
            "text_analysis": True,
            "user_history": True,
            "user_statistics": True,
            "background_service": settings.background_service_enabled
        },
        maintenance_mode=False
    )


@api_router.get(
    "/",
    summary="API root",
    description="API root endpoint with basic information"
)
async def api_root(request: Request) -> dict:
    """
    API root endpoint.
    
    Returns basic API information and available endpoints.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "timestamp": datetime.utcnow(),
        "endpoints": {
            "health": "/api/v1/health",
            "status": "/api/v1/status",
            "text_modification": "/api/v1/text/modify",
            "text_analysis": "/api/v1/text/analyze",
            "user_history": "/api/v1/text/history/{user_id}",
            "user_statistics": "/api/v1/text/statistics/{user_id}",
            "supported_operations": "/api/v1/text/operations",
            "documentation": "/docs",
            "openapi_schema": "/openapi.json"
        }
    }