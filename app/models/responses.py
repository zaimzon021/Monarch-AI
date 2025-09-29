"""
Response models for the AI Text Assistant API.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from .requests import TextOperation


class TextModificationResponse(BaseModel):
    """Response model for text modification operations."""
    
    original_text: str = Field(..., description="The original input text")
    modified_text: str = Field(..., description="The modified text result")
    operation: TextOperation = Field(..., description="The operation that was performed")
    timestamp: datetime = Field(..., description="When the operation was completed")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    # Optional metadata
    user_id: Optional[str] = Field(None, description="User identifier if provided")
    ai_model_used: Optional[str] = Field(None, description="AI model used for processing")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the result")
    word_count_original: int = Field(..., description="Word count of original text")
    word_count_modified: int = Field(..., description="Word count of modified text")
    
    # Additional operation-specific data
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional operation-specific metadata")


class BackgroundTextResponse(BaseModel):
    """Response model for background text processing."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    modified_text: Optional[str] = Field(None, description="The modified text if successful")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(..., description="When the operation was completed")


class ModificationHistoryResponse(BaseModel):
    """Response model for modification history queries."""
    
    user_id: str = Field(..., description="User identifier")
    total_modifications: int = Field(..., description="Total number of modifications")
    modifications: List[Dict[str, Any]] = Field(..., description="List of modification records")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=10, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class HealthCheckResponse(BaseModel):
    """Response model for health check operations."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Application uptime in seconds")
    
    # Component health
    database: Optional[Dict[str, Any]] = Field(None, description="Database health status")
    ai_service: Optional[Dict[str, Any]] = Field(None, description="AI service health status")
    
    # System metrics
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage statistics")
    active_connections: Optional[int] = Field(None, description="Number of active connections")


class ErrorResponse(BaseModel):
    """Response model for error conditions."""
    
    error_code: str = Field(..., description="Specific error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="When the error occurred")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    
    # Error categorization
    error_type: str = Field(..., description="Type of error (validation, service, database, etc.)")
    is_retryable: bool = Field(default=False, description="Whether the operation can be retried")
    
    # Support information
    support_reference: Optional[str] = Field(None, description="Support reference for tracking")


class APIStatusResponse(BaseModel):
    """Response model for API status information."""
    
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Status check timestamp")
    
    # Feature availability
    features: Dict[str, bool] = Field(..., description="Available features and their status")
    
    # Performance metrics
    average_response_time: Optional[float] = Field(None, description="Average response time in seconds")
    requests_per_minute: Optional[int] = Field(None, description="Current requests per minute")
    
    # Maintenance information
    maintenance_mode: bool = Field(default=False, description="Whether service is in maintenance mode")
    maintenance_message: Optional[str] = Field(None, description="Maintenance message if applicable")