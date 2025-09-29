"""
Global error handling middleware for consistent error responses.
"""

import traceback
from datetime import datetime
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
from pymongo.errors import PyMongoError
import structlog

from app.models.responses import ErrorResponse
from .logging import get_correlation_id

logger = structlog.get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling all application errors consistently."""
    
    def __init__(self, app, include_debug_info: bool = False):
        super().__init__(app)
        self.include_debug_info = include_debug_info
    
    async def dispatch(self, request: Request, call_next):
        """Handle request processing with comprehensive error handling."""
        
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            return await self._handle_http_exception(request, e)
            
        except ValidationError as e:
            return await self._handle_validation_error(request, e)
            
        except PyMongoError as e:
            return await self._handle_database_error(request, e)
            
        except Exception as e:
            return await self._handle_generic_error(request, e)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        
        correlation_id = get_correlation_id(request)
        
        error_response = ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            timestamp=datetime.utcnow(),
            request_id=correlation_id,
            error_type="http_error",
            is_retryable=exc.status_code >= 500
        )
        
        # Log the error
        logger.warning(
            "HTTP exception occurred",
            correlation_id=correlation_id,
            status_code=exc.status_code,
            detail=exc.detail,
            method=request.method,
            url=str(request.url)
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(),
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        
        correlation_id = get_correlation_id(request)
        
        # Format validation errors
        validation_details = []
        for error in exc.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            validation_details.append({
                "field": field,
                "message": error['msg'],
                "type": error['type']
            })
        
        error_response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"validation_errors": validation_details},
            timestamp=datetime.utcnow(),
            request_id=correlation_id,
            error_type="validation_error",
            is_retryable=False
        )
        
        # Log the error
        logger.warning(
            "Validation error occurred",
            correlation_id=correlation_id,
            validation_errors=validation_details,
            method=request.method,
            url=str(request.url)
        )
        
        return JSONResponse(
            status_code=422,
            content=error_response.dict(),
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_database_error(self, request: Request, exc: PyMongoError) -> JSONResponse:
        """Handle MongoDB database errors."""
        
        correlation_id = get_correlation_id(request)
        
        error_response = ErrorResponse(
            error_code="DATABASE_ERROR",
            message="Database operation failed",
            details={"database_error": str(exc)} if self.include_debug_info else None,
            timestamp=datetime.utcnow(),
            request_id=correlation_id,
            error_type="database_error",
            is_retryable=True
        )
        
        # Log the error
        logger.error(
            "Database error occurred",
            correlation_id=correlation_id,
            error=str(exc),
            error_type=type(exc).__name__,
            method=request.method,
            url=str(request.url)
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.dict(),
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_generic_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle all other unexpected errors."""
        
        correlation_id = get_correlation_id(request)
        
        # Prepare debug information
        debug_info = None
        if self.include_debug_info:
            debug_info = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc()
            }
        
        error_response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details=debug_info,
            timestamp=datetime.utcnow(),
            request_id=correlation_id,
            error_type="internal_error",
            is_retryable=True,
            support_reference=correlation_id
        )
        
        # Log the error with full traceback
        logger.error(
            "Unexpected error occurred",
            correlation_id=correlation_id,
            error=str(exc),
            error_type=type(exc).__name__,
            method=request.method,
            url=str(request.url),
            traceback=traceback.format_exc()
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.dict(),
            headers={"X-Correlation-ID": correlation_id}
        )


# Custom exception classes for specific error scenarios
class AIServiceError(Exception):
    """Exception raised when AI service operations fail."""
    
    def __init__(self, message: str, status_code: int = 502, is_retryable: bool = True):
        self.message = message
        self.status_code = status_code
        self.is_retryable = is_retryable
        super().__init__(self.message)


class TextProcessingError(Exception):
    """Exception raised when text processing operations fail."""
    
    def __init__(self, message: str, operation: str = None, is_retryable: bool = False):
        self.message = message
        self.operation = operation
        self.is_retryable = is_retryable
        super().__init__(self.message)


class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None):
        self.message = message
        self.config_key = config_key
        super().__init__(self.message)


# Exception handlers for custom exceptions
async def handle_ai_service_error(request: Request, exc: AIServiceError) -> JSONResponse:
    """Handle AI service specific errors."""
    
    correlation_id = get_correlation_id(request)
    
    error_response = ErrorResponse(
        error_code="AI_SERVICE_ERROR",
        message=exc.message,
        timestamp=datetime.utcnow(),
        request_id=correlation_id,
        error_type="ai_service_error",
        is_retryable=exc.is_retryable
    )
    
    logger.error(
        "AI service error",
        correlation_id=correlation_id,
        error=exc.message,
        is_retryable=exc.is_retryable,
        method=request.method,
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers={"X-Correlation-ID": correlation_id}
    )


async def handle_text_processing_error(request: Request, exc: TextProcessingError) -> JSONResponse:
    """Handle text processing specific errors."""
    
    correlation_id = get_correlation_id(request)
    
    error_response = ErrorResponse(
        error_code="TEXT_PROCESSING_ERROR",
        message=exc.message,
        details={"operation": exc.operation} if exc.operation else None,
        timestamp=datetime.utcnow(),
        request_id=correlation_id,
        error_type="text_processing_error",
        is_retryable=exc.is_retryable
    )
    
    logger.error(
        "Text processing error",
        correlation_id=correlation_id,
        error=exc.message,
        operation=exc.operation,
        is_retryable=exc.is_retryable,
        method=request.method,
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=400,
        content=error_response.dict(),
        headers={"X-Correlation-ID": correlation_id}
    )


async def handle_configuration_error(request: Request, exc: ConfigurationError) -> JSONResponse:
    """Handle configuration specific errors."""
    
    correlation_id = get_correlation_id(request)
    
    error_response = ErrorResponse(
        error_code="CONFIGURATION_ERROR",
        message="Service configuration error",
        details={"config_key": exc.config_key} if exc.config_key else None,
        timestamp=datetime.utcnow(),
        request_id=correlation_id,
        error_type="configuration_error",
        is_retryable=False
    )
    
    logger.critical(
        "Configuration error",
        correlation_id=correlation_id,
        error=exc.message,
        config_key=exc.config_key,
        method=request.method,
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict(),
        headers={"X-Correlation-ID": correlation_id}
    )