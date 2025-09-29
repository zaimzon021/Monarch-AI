"""
Database models for MongoDB storage.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from .requests import TextOperation


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class ModificationRecord(BaseModel):
    """Database model for storing text modification records."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Core modification data
    user_id: Optional[str] = Field(None, max_length=100)
    original_text: str = Field(..., max_length=10000)
    modified_text: str = Field(..., max_length=15000)  # Allow for expansion
    operation: TextOperation = Field(...)
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float = Field(..., ge=0.0)
    ai_model_used: str = Field(..., max_length=100)
    
    # Optional fields
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    word_count_original: int = Field(..., ge=0)
    word_count_modified: int = Field(..., ge=0)
    
    # Request context
    source_application: Optional[str] = Field(None, max_length=100)
    window_title: Optional[str] = Field(None, max_length=200)
    target_language: Optional[str] = Field(None, max_length=10)
    preserve_formatting: bool = Field(default=True)
    
    # Additional metadata
    options: Optional[Dict[str, Any]] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "user123",
                "original_text": "This is the original text that needs improvement.",
                "modified_text": "This is the enhanced text that has been improved for clarity and readability.",
                "operation": "improve",
                "processing_time": 1.23,
                "ai_model_used": "gpt-3.5-turbo",
                "confidence_score": 0.95,
                "word_count_original": 10,
                "word_count_modified": 12,
                "source_application": "notepad.exe",
                "target_language": None,
                "preserve_formatting": True
            }
        }


class UserSession(BaseModel):
    """Database model for user session tracking."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    user_id: str = Field(..., max_length=100)
    session_start: datetime = Field(default_factory=datetime.utcnow)
    session_end: Optional[datetime] = Field(None)
    
    # Session statistics
    total_modifications: int = Field(default=0, ge=0)
    total_processing_time: float = Field(default=0.0, ge=0.0)
    operations_count: Dict[str, int] = Field(default_factory=dict)
    
    # Session metadata
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)  # IPv6 compatible
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SystemMetrics(BaseModel):
    """Database model for system performance metrics."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Performance metrics
    total_requests: int = Field(..., ge=0)
    successful_requests: int = Field(..., ge=0)
    failed_requests: int = Field(..., ge=0)
    average_response_time: float = Field(..., ge=0.0)
    
    # Resource usage
    memory_usage_mb: Optional[float] = Field(None, ge=0.0)
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # AI service metrics
    ai_service_calls: int = Field(default=0, ge=0)
    ai_service_failures: int = Field(default=0, ge=0)
    ai_service_avg_time: Optional[float] = Field(None, ge=0.0)
    
    # Database metrics
    db_connections_active: Optional[int] = Field(None, ge=0)
    db_query_avg_time: Optional[float] = Field(None, ge=0.0)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}