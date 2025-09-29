"""
Configuration settings for the AI Text Assistant Backend.
Uses Pydantic BaseSettings for environment variable management.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="AI Text Assistant Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database settings
    mongodb_url: str = Field(..., description="MongoDB connection URL")
    mongodb_database: str = Field(default="ai_text_assistant", description="MongoDB database name")
    
    # AI Service settings
    ai_api_key: str = Field(..., description="AI service API key")
    ai_api_endpoint: str = Field(..., description="AI service API endpoint")
    ai_api_timeout: int = Field(default=30, description="AI API request timeout in seconds")
    ai_model: str = Field(default="gpt-3.5-turbo", description="AI model to use")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Background service settings
    background_service_port: int = Field(default=8001, description="Background service port")
    background_service_enabled: bool = Field(default=True, description="Enable background service")
    
    # Security settings
    secret_key: Optional[str] = Field(default=None, description="Secret key for security")
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Performance settings
    max_request_size: int = Field(default=1024 * 1024, description="Maximum request size in bytes")
    request_timeout: int = Field(default=60, description="Request timeout in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()