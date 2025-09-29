"""
Middlewares package for the AI Text Assistant Backend.
Contains all middleware components for logging, error handling, and request processing.
"""

from .logging import (
    LoggingMiddleware,
    RequestTimingMiddleware,
    get_correlation_id,
    log_with_correlation
)

from .error_handler import (
    ErrorHandlerMiddleware,
    AIServiceError,
    TextProcessingError,
    ConfigurationError,
    handle_ai_service_error,
    handle_text_processing_error,
    handle_configuration_error
)

from .cors import (
    create_cors_middleware,
    get_cors_origins
)

__all__ = [
    # Logging middleware
    "LoggingMiddleware",
    "RequestTimingMiddleware",
    "get_correlation_id",
    "log_with_correlation",
    
    # Error handling middleware
    "ErrorHandlerMiddleware",
    "AIServiceError",
    "TextProcessingError", 
    "ConfigurationError",
    "handle_ai_service_error",
    "handle_text_processing_error",
    "handle_configuration_error",
    
    # CORS middleware
    "create_cors_middleware",
    "get_cors_origins"
]