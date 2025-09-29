"""
CORS middleware for handling cross-origin requests.
"""

from typing import List
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


def create_cors_middleware() -> CORSMiddleware:
    """
    Create and configure CORS middleware based on application settings.
    
    Returns:
        CORSMiddleware: Configured CORS middleware
    """
    
    return CORSMiddleware(
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key",
            "X-Correlation-ID",
            "User-Agent"
        ],
        expose_headers=[
            "X-Correlation-ID",
            "X-Process-Time",
            "X-Process-Time-Seconds",
            "X-Process-Time-MS"
        ]
    )


def get_cors_origins() -> List[str]:
    """
    Get CORS origins from settings with validation.
    
    Returns:
        List[str]: List of allowed origins
    """
    origins = settings.cors_origins
    
    # Validate origins
    validated_origins = []
    for origin in origins:
        if origin == "*":
            validated_origins.append(origin)
        elif origin.startswith(("http://", "https://")):
            validated_origins.append(origin)
        else:
            # Add protocol if missing
            validated_origins.append(f"https://{origin}")
    
    return validated_origins