"""
FastAPI application entry point for the AI Text Assistant Backend.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config.settings import settings
from app.config.database_init import database_lifespan
from app.config.validation import validate_configuration, log_configuration_summary
from app.middlewares.logging import LoggingMiddleware, RequestTimingMiddleware
from app.middlewares.error_handler import (
    ErrorHandlerMiddleware,
    AIServiceError,
    TextProcessingError,
    ConfigurationError,
    handle_ai_service_error,
    handle_text_processing_error,
    handle_configuration_error
)
from app.middlewares.cors import create_cors_middleware
from app.routes.api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(message)s"
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Text Assistant Backend")
    
    # Validate configuration
    is_valid, errors = validate_configuration()
    if not is_valid:
        logger.critical("Configuration validation failed")
        for error in errors:
            logger.critical(f"  - {error}")
        raise ConfigurationError("Invalid configuration")
    
    # Log configuration summary
    log_configuration_summary()
    
    # Database initialization is handled by database_lifespan
    async with database_lifespan(app):
        logger.info("Application startup completed")
        yield
    
    # Shutdown
    logger.info("Shutting down AI Text Assistant Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered text modification service with Windows background service capabilities",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
cors_middleware = create_cors_middleware()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_middleware.allow_origins,
    allow_credentials=cors_middleware.allow_credentials,
    allow_methods=cors_middleware.allow_methods,
    allow_headers=cors_middleware.allow_headers,
    expose_headers=cors_middleware.expose_headers
)

# Add custom middlewares
app.add_middleware(ErrorHandlerMiddleware, include_debug_info=settings.debug)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(LoggingMiddleware, log_requests=True, log_responses=True)

# Add exception handlers for custom exceptions
app.add_exception_handler(AIServiceError, handle_ai_service_error)
app.add_exception_handler(TextProcessingError, handle_text_processing_error)
app.add_exception_handler(ConfigurationError, handle_configuration_error)

# Include API routes
app.include_router(api_router)


@app.get("/", summary="Root endpoint", description="Application root endpoint")
async def root(request: Request) -> dict:
    """
    Root endpoint.
    
    Returns basic application information.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/docs",
        "api": "/api/v1"
    }


@app.get("/ping", summary="Ping endpoint", description="Simple ping endpoint for basic health check")
async def ping(request: Request) -> dict:
    """
    Simple ping endpoint.
    
    Returns a simple pong response for basic connectivity testing.
    """
    return {"message": "pong"}


# Global exception handler for any unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for any unhandled exceptions.
    This is a fallback in case the middleware doesn't catch something.
    """
    logger.error(
        "Unhandled exception in global handler",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )