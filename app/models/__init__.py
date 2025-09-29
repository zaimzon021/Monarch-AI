"""
Models package for the AI Text Assistant Backend.
Contains all data models, validation schemas, and utilities.
"""

from .requests import (
    TextOperation,
    TextModificationRequest,
    BackgroundTextRequest,
    HealthCheckRequest
)

from .responses import (
    TextModificationResponse,
    BackgroundTextResponse,
    ModificationHistoryResponse,
    HealthCheckResponse,
    ErrorResponse,
    APIStatusResponse
)

from .database import (
    PyObjectId,
    ModificationRecord,
    UserSession,
    SystemMetrics
)

from .validation import (
    ValidationUtils,
    validate_text_modification_request,
    validate_background_text_request,
    sanitize_text_input
)

__all__ = [
    # Enums
    "TextOperation",
    
    # Request models
    "TextModificationRequest",
    "BackgroundTextRequest", 
    "HealthCheckRequest",
    
    # Response models
    "TextModificationResponse",
    "BackgroundTextResponse",
    "ModificationHistoryResponse",
    "HealthCheckResponse",
    "ErrorResponse",
    "APIStatusResponse",
    
    # Database models
    "PyObjectId",
    "ModificationRecord",
    "UserSession",
    "SystemMetrics",
    
    # Validation utilities
    "ValidationUtils",
    "validate_text_modification_request",
    "validate_background_text_request",
    "sanitize_text_input"
]