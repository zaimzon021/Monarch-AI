"""
Request models for the AI Text Assistant API.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class TextOperation(str, Enum):
    """Supported text modification operations."""
    SUMMARIZE = "summarize"
    IMPROVE = "improve"
    TRANSLATE = "translate"
    CORRECT = "correct"
    EXPAND = "expand"
    SIMPLIFY = "simplify"
    ANALYZE = "analyze"


class TextModificationRequest(BaseModel):
    """Request model for text modification operations."""
    
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=10000,
        description="The text to be modified"
    )
    
    operation: TextOperation = Field(
        ...,
        description="The type of modification to perform"
    )
    
    user_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional user identifier"
    )
    
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional options for the operation"
    )
    
    target_language: Optional[str] = Field(
        None,
        max_length=10,
        description="Target language for translation operations (e.g., 'es', 'fr', 'de')"
    )
    
    preserve_formatting: bool = Field(
        default=True,
        description="Whether to preserve original text formatting"
    )
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text content."""
        if not v or not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()
    
    @validator('target_language')
    def validate_target_language(cls, v, values):
        """Validate target language for translation operations."""
        if values.get('operation') == TextOperation.TRANSLATE and not v:
            raise ValueError('target_language is required for translation operations')
        return v
    
    @validator('options')
    def validate_options(cls, v):
        """Validate options dictionary."""
        if v is not None:
            # Ensure options don't exceed reasonable size
            if len(str(v)) > 1000:
                raise ValueError('Options dictionary is too large')
        return v


class BackgroundTextRequest(BaseModel):
    """Request model for background text processing."""
    
    text: str = Field(..., min_length=1, max_length=10000)
    operation: TextOperation
    source_application: Optional[str] = Field(None, max_length=100)
    window_title: Optional[str] = Field(None, max_length=200)
    user_id: Optional[str] = Field(None, max_length=100)
    options: Optional[Dict[str, Any]] = None
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text content."""
        if not v or not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class HealthCheckRequest(BaseModel):
    """Request model for health check operations."""
    
    include_database: bool = Field(default=True, description="Include database health in check")
    include_ai_service: bool = Field(default=True, description="Include AI service health in check")