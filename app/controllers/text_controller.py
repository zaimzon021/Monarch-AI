"""
Text controller for handling API requests related to text modification.
"""

from typing import Optional
from fastapi import Request, HTTPException, Depends
import structlog

from app.models.requests import TextModificationRequest, TextOperation
from app.models.responses import (
    TextModificationResponse, 
    ModificationHistoryResponse,
    APIStatusResponse
)
from app.services.text_service import get_text_service, TextService
from app.middlewares.logging import get_correlation_id, log_with_correlation
from app.middlewares.error_handler import TextProcessingError
from app.models.validation import validate_text_modification_request

logger = structlog.get_logger(__name__)


class TextController:
    """Controller for text modification and analysis operations."""
    
    def __init__(self):
        pass
    
    async def process_text_modification(
        self, 
        request: Request,
        modification_request: TextModificationRequest,
        text_service: TextService = Depends(get_text_service)
    ) -> TextModificationResponse:
        """
        Process text modification request.
        
        Args:
            request: FastAPI request object
            modification_request: Text modification request data
            text_service: Text service dependency
            
        Returns:
            TextModificationResponse: Processing results
            
        Raises:
            HTTPException: If processing fails
        """
        correlation_id = get_correlation_id(request)
        
        try:
            # Log incoming request
            log_with_correlation(
                request, 
                "info", 
                "Processing text modification request",
                operation=modification_request.operation.value,
                text_length=len(modification_request.text),
                user_id=modification_request.user_id
            )
            
            # Validate request data
            request_dict = modification_request.dict()
            is_valid, errors = validate_text_modification_request(request_dict)
            
            if not is_valid:
                log_with_correlation(
                    request,
                    "warning",
                    "Text modification request validation failed",
                    errors=errors
                )
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Validation failed",
                        "details": errors,
                        "correlation_id": correlation_id
                    }
                )
            
            # Process the request
            response = await text_service.process_text_modification(modification_request)
            
            # Log successful processing
            log_with_correlation(
                request,
                "info",
                "Text modification completed successfully",
                operation=modification_request.operation.value,
                processing_time=response.processing_time,
                user_id=modification_request.user_id,
                word_count_change=response.word_count_modified - response.word_count_original
            )
            
            return response
            
        except TextProcessingError as e:
            log_with_correlation(
                request,
                "error",
                "Text processing error",
                error=str(e),
                operation=e.operation,
                is_retryable=e.is_retryable
            )
            
            status_code = 500 if e.is_retryable else 400
            raise HTTPException(
                status_code=status_code,
                detail={
                    "error": "Text processing failed",
                    "message": str(e),
                    "operation": e.operation,
                    "is_retryable": e.is_retryable,
                    "correlation_id": correlation_id
                }
            )
            
        except Exception as e:
            log_with_correlation(
                request,
                "error",
                "Unexpected error in text modification",
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_modification_history(
        self,
        request: Request,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        operation: Optional[str] = None,
        text_service: TextService = Depends(get_text_service)
    ) -> ModificationHistoryResponse:
        """
        Get modification history for a user.
        
        Args:
            request: FastAPI request object
            user_id: User identifier
            page: Page number (1-based)
            page_size: Number of items per page
            operation: Optional operation filter
            text_service: Text service dependency
            
        Returns:
            ModificationHistoryResponse: User's modification history
        """
        correlation_id = get_correlation_id(request)
        
        try:
            # Validate parameters
            if page < 1:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid page number",
                        "message": "Page number must be >= 1",
                        "correlation_id": correlation_id
                    }
                )
            
            if page_size < 1 or page_size > 100:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid page size",
                        "message": "Page size must be between 1 and 100",
                        "correlation_id": correlation_id
                    }
                )
            
            # Parse operation filter
            operation_filter = None
            if operation:
                try:
                    operation_filter = TextOperation(operation.lower())
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid operation",
                            "message": f"Operation '{operation}' is not supported",
                            "supported_operations": [op.value for op in TextOperation],
                            "correlation_id": correlation_id
                        }
                    )
            
            log_with_correlation(
                request,
                "info",
                "Retrieving modification history",
                user_id=user_id,
                page=page,
                page_size=page_size,
                operation_filter=operation
            )
            
            # Get history from service
            history = await text_service.get_modification_history(
                user_id=user_id,
                page=page,
                page_size=page_size,
                operation_filter=operation_filter
            )
            
            log_with_correlation(
                request,
                "info",
                "Modification history retrieved successfully",
                user_id=user_id,
                total_modifications=history.total_modifications,
                returned_items=len(history.modifications)
            )
            
            return history
            
        except HTTPException:
            raise
            
        except Exception as e:
            log_with_correlation(
                request,
                "error",
                "Failed to retrieve modification history",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve history",
                    "message": "An error occurred while retrieving modification history",
                    "correlation_id": correlation_id
                }
            )
    
    async def analyze_text(
        self,
        request: Request,
        text: str,
        user_id: Optional[str] = None,
        text_service: TextService = Depends(get_text_service)
    ) -> dict:
        """
        Analyze text using AI service.
        
        Args:
            request: FastAPI request object
            text: Text to analyze
            user_id: Optional user identifier
            text_service: Text service dependency
            
        Returns:
            dict: Analysis results
        """
        correlation_id = get_correlation_id(request)
        
        try:
            # Validate text input
            if not text or not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid text",
                        "message": "Text cannot be empty",
                        "correlation_id": correlation_id
                    }
                )
            
            if len(text) > 10000:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Text too long",
                        "message": "Text cannot exceed 10,000 characters",
                        "correlation_id": correlation_id
                    }
                )
            
            log_with_correlation(
                request,
                "info",
                "Analyzing text",
                text_length=len(text),
                user_id=user_id
            )
            
            # Analyze text
            analysis = await text_service.analyze_text(text, user_id)
            
            log_with_correlation(
                request,
                "info",
                "Text analysis completed",
                user_id=user_id,
                word_count=analysis.get("word_count", 0)
            )
            
            return analysis
            
        except HTTPException:
            raise
            
        except Exception as e:
            log_with_correlation(
                request,
                "error",
                "Text analysis failed",
                error=str(e),
                error_type=type(e).__name__,
                user_id=user_id
            )
            
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Analysis failed",
                    "message": "An error occurred during text analysis",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_user_statistics(
        self,
        request: Request,
        user_id: str,
        text_service: TextService = Depends(get_text_service)
    ) -> dict:
        """
        Get statistics for a user's text modifications.
        
        Args:
            request: FastAPI request object
            user_id: User identifier
            text_service: Text service dependency
            
        Returns:
            dict: User statistics
        """
        correlation_id = get_correlation_id(request)
        
        try:
            log_with_correlation(
                request,
                "info",
                "Retrieving user statistics",
                user_id=user_id
            )
            
            # Get statistics from service
            stats = await text_service.get_user_statistics(user_id)
            
            log_with_correlation(
                request,
                "info",
                "User statistics retrieved successfully",
                user_id=user_id,
                total_modifications=stats.get("total_modifications", 0)
            )
            
            return stats
            
        except Exception as e:
            log_with_correlation(
                request,
                "error",
                "Failed to retrieve user statistics",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to retrieve statistics",
                    "message": "An error occurred while retrieving user statistics",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_supported_operations(self, request: Request) -> dict:
        """
        Get list of supported text operations.
        
        Args:
            request: FastAPI request object
            
        Returns:
            dict: Supported operations and their descriptions
        """
        log_with_correlation(
            request,
            "info",
            "Retrieving supported operations"
        )
        
        operations = {
            "operations": [
                {
                    "name": TextOperation.SUMMARIZE.value,
                    "description": "Create a concise summary of the text"
                },
                {
                    "name": TextOperation.IMPROVE.value,
                    "description": "Improve text clarity, grammar, and readability"
                },
                {
                    "name": TextOperation.TRANSLATE.value,
                    "description": "Translate text to another language"
                },
                {
                    "name": TextOperation.CORRECT.value,
                    "description": "Correct grammar, spelling, and punctuation errors"
                },
                {
                    "name": TextOperation.EXPAND.value,
                    "description": "Expand and elaborate on the text with more details"
                },
                {
                    "name": TextOperation.SIMPLIFY.value,
                    "description": "Simplify text to make it easier to understand"
                },
                {
                    "name": TextOperation.ANALYZE.value,
                    "description": "Analyze text and provide insights"
                }
            ]
        }
        
        return operations


# Global controller instance
text_controller = TextController()


def get_text_controller() -> TextController:
    """Dependency function to get text controller instance."""
    return text_controller