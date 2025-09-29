"""
Text modification API routes.
"""

from typing import Optional
from fastapi import APIRouter, Request, Query, Body, Depends
from fastapi.responses import JSONResponse

from app.controllers.text_controller import get_text_controller, TextController
from app.models.requests import TextModificationRequest
from app.models.responses import (
    TextModificationResponse,
    ModificationHistoryResponse
)

# Create router for text operations
router = APIRouter(
    prefix="/text",
    tags=["text"],
    responses={
        400: {"description": "Bad Request"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "/modify",
    response_model=TextModificationResponse,
    summary="Modify text using AI",
    description="Process text modification using AI service with the specified operation"
)
async def modify_text(
    request: Request,
    modification_request: TextModificationRequest,
    controller: TextController = Depends(get_text_controller)
) -> TextModificationResponse:
    """
    Modify text using AI service.
    
    - **text**: The text to be modified (required, max 10,000 characters)
    - **operation**: Type of modification (summarize, improve, translate, correct, expand, simplify, analyze)
    - **user_id**: Optional user identifier for tracking
    - **target_language**: Required for translation operations (e.g., 'es', 'fr', 'de')
    - **preserve_formatting**: Whether to preserve original formatting (default: true)
    - **options**: Additional options for the operation
    """
    return await controller.process_text_modification(request, modification_request)


@router.get(
    "/history/{user_id}",
    response_model=ModificationHistoryResponse,
    summary="Get user modification history",
    description="Retrieve modification history for a specific user with pagination"
)
async def get_modification_history(
    request: Request,
    user_id: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    operation: Optional[str] = Query(None, description="Filter by operation type"),
    controller: TextController = Depends(get_text_controller)
) -> ModificationHistoryResponse:
    """
    Get modification history for a user.
    
    - **user_id**: User identifier
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **operation**: Optional filter by operation type
    """
    return await controller.get_modification_history(
        request, user_id, page, page_size, operation
    )


@router.post(
    "/analyze",
    summary="Analyze text",
    description="Analyze text and provide insights about content, structure, and metrics"
)
async def analyze_text(
    request: Request,
    text: str = Body(..., description="Text to analyze", max_length=10000),
    user_id: Optional[str] = Body(None, description="Optional user identifier"),
    controller: TextController = Depends(get_text_controller)
) -> dict:
    """
    Analyze text using AI service.
    
    - **text**: The text to analyze (required, max 10,000 characters)
    - **user_id**: Optional user identifier for tracking
    
    Returns analysis including word count, sentiment, topics, reading level, etc.
    """
    return await controller.analyze_text(request, text, user_id)


@router.get(
    "/statistics/{user_id}",
    summary="Get user statistics",
    description="Get comprehensive statistics for a user's text modifications"
)
async def get_user_statistics(
    request: Request,
    user_id: str,
    controller: TextController = Depends(get_text_controller)
) -> dict:
    """
    Get statistics for a user's text modifications.
    
    - **user_id**: User identifier
    
    Returns statistics including total modifications, processing times, operation breakdown, etc.
    """
    return await controller.get_user_statistics(request, user_id)


@router.get(
    "/operations",
    summary="Get supported operations",
    description="Get list of all supported text modification operations"
)
async def get_supported_operations(
    request: Request,
    controller: TextController = Depends(get_text_controller)
) -> dict:
    """
    Get list of supported text operations.
    
    Returns a list of all available operations with descriptions.
    """
    return await controller.get_supported_operations(request)