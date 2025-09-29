"""
Configuration validation utilities.
"""

import os
from typing import List, Tuple, Dict, Any
import structlog

from .settings import settings

logger = structlog.get_logger(__name__)


def validate_configuration() -> Tuple[bool, List[str]]:
    """
    Validate application configuration.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate required environment variables
    required_vars = [
        'MONGODB_URL',
        'AI_API_KEY',
        'AI_API_ENDPOINT'
    ]
    
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            errors.append(f"Missing required environment variable: {var}")
    
    # Validate MongoDB URL format
    if settings.mongodb_url:
        if not settings.mongodb_url.startswith(('mongodb://', 'mongodb+srv://')):
            errors.append("MONGODB_URL must start with 'mongodb://' or 'mongodb+srv://'")
    
    # Validate AI API endpoint
    if settings.ai_api_endpoint:
        if not settings.ai_api_endpoint.startswith(('http://', 'https://')):
            errors.append("AI_API_ENDPOINT must be a valid HTTP/HTTPS URL")
    
    # Validate port numbers
    if not (1 <= settings.port <= 65535):
        errors.append(f"Invalid port number: {settings.port}")
    
    if not (1 <= settings.background_service_port <= 65535):
        errors.append(f"Invalid background service port: {settings.background_service_port}")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if settings.log_level.upper() not in valid_log_levels:
        errors.append(f"Invalid log level: {settings.log_level}")
    
    # Validate log format
    valid_log_formats = ['json', 'text']
    if settings.log_format.lower() not in valid_log_formats:
        errors.append(f"Invalid log format: {settings.log_format}")
    
    # Validate timeout values
    if settings.ai_api_timeout <= 0:
        errors.append("AI_API_TIMEOUT must be positive")
    
    if settings.request_timeout <= 0:
        errors.append("REQUEST_TIMEOUT must be positive")
    
    # Validate max request size
    if settings.max_request_size <= 0:
        errors.append("MAX_REQUEST_SIZE must be positive")
    
    # Check for potential security issues
    if settings.debug and not _is_development_environment():
        errors.append("DEBUG mode should not be enabled in production")
    
    if settings.cors_origins == ["*"] and not _is_development_environment():
        errors.append("CORS origins should be restricted in production")
    
    return len(errors) == 0, errors


def validate_ai_service_config() -> Tuple[bool, List[str]]:
    """
    Validate AI service specific configuration.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check AI API key format (basic validation)
    if settings.ai_api_key:
        if len(settings.ai_api_key) < 10:
            errors.append("AI_API_KEY appears to be too short")
        
        if settings.ai_api_key.startswith('sk-') and len(settings.ai_api_key) < 40:
            errors.append("OpenAI API key format appears invalid")
    
    # Validate AI model name
    if settings.ai_model:
        valid_models = [
            'gpt-3.5-turbo',
            'gpt-4',
            'gpt-4-turbo',
            'claude-3-sonnet',
            'claude-3-opus'
        ]
        if settings.ai_model not in valid_models:
            logger.warning(f"AI model '{settings.ai_model}' is not in the list of known models")
    
    return len(errors) == 0, errors


def validate_database_config() -> Tuple[bool, List[str]]:
    """
    Validate database configuration.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate database name
    if not settings.mongodb_database:
        errors.append("MONGODB_DATABASE cannot be empty")
    elif len(settings.mongodb_database) > 64:
        errors.append("MONGODB_DATABASE name is too long (max 64 characters)")
    
    # Check for invalid characters in database name
    invalid_chars = ['/', '\\', '.', '"', '*', '<', '>', ':', '|', '?']
    for char in invalid_chars:
        if char in settings.mongodb_database:
            errors.append(f"MONGODB_DATABASE contains invalid character: {char}")
            break
    
    return len(errors) == 0, errors


def validate_security_config() -> Tuple[bool, List[str]]:
    """
    Validate security configuration.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check secret key
    if settings.secret_key:
        if len(settings.secret_key) < 32:
            errors.append("SECRET_KEY should be at least 32 characters long")
    elif not _is_development_environment():
        errors.append("SECRET_KEY should be set in production")
    
    # Validate CORS origins
    for origin in settings.cors_origins:
        if origin != "*" and not origin.startswith(('http://', 'https://')):
            errors.append(f"Invalid CORS origin format: {origin}")
    
    return len(errors) == 0, errors


def _is_development_environment() -> bool:
    """Check if running in development environment."""
    return (
        settings.debug or
        os.getenv('ENVIRONMENT', '').lower() in ['dev', 'development', 'local'] or
        settings.host in ['127.0.0.1', 'localhost']
    )


def log_configuration_summary():
    """Log a summary of the current configuration."""
    logger.info(
        "Configuration summary",
        app_name=settings.app_name,
        app_version=settings.app_version,
        debug=settings.debug,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        log_format=settings.log_format,
        mongodb_database=settings.mongodb_database,
        ai_model=settings.ai_model,
        background_service_enabled=settings.background_service_enabled,
        background_service_port=settings.background_service_port,
        cors_origins_count=len(settings.cors_origins),
        environment=os.getenv('ENVIRONMENT', 'unknown')
    )


def get_configuration_dict() -> Dict[str, Any]:
    """
    Get configuration as dictionary (excluding sensitive values).
    
    Returns:
        Dict containing non-sensitive configuration values
    """
    return {
        'app_name': settings.app_name,
        'app_version': settings.app_version,
        'debug': settings.debug,
        'host': settings.host,
        'port': settings.port,
        'log_level': settings.log_level,
        'log_format': settings.log_format,
        'mongodb_database': settings.mongodb_database,
        'ai_model': settings.ai_model,
        'ai_api_timeout': settings.ai_api_timeout,
        'background_service_enabled': settings.background_service_enabled,
        'background_service_port': settings.background_service_port,
        'max_request_size': settings.max_request_size,
        'request_timeout': settings.request_timeout,
        'cors_origins_count': len(settings.cors_origins),
        'environment': os.getenv('ENVIRONMENT', 'unknown')
    }