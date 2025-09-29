"""
Logging utilities and configuration helpers.
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger

from app.config.settings import settings


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add service information
        log_record['service'] = settings.app_name
        log_record['version'] = settings.app_version
        
        # Add level name
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name


def setup_logging():
    """Setup application logging configuration."""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.log_format.lower() == 'json':
        # JSON formatter
        formatter = CustomJSONFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Text formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format.lower() == 'json' 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        structlog.BoundLogger: Configured logger
    """
    return structlog.get_logger(name)


def log_performance(operation: str, duration: float, **kwargs):
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional context
    """
    logger = get_logger("performance")
    
    logger.info(
        "Performance metric",
        operation=operation,
        duration_seconds=duration,
        duration_ms=duration * 1000,
        **kwargs
    )


def log_error_with_context(
    logger: structlog.BoundLogger,
    error: Exception,
    operation: str,
    **context
):
    """
    Log error with full context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        operation: Operation being performed
        **context: Additional context
    """
    logger.error(
        f"Error in {operation}",
        error=str(error),
        error_type=type(error).__name__,
        operation=operation,
        **context
    )


def log_request_response(
    logger: structlog.BoundLogger,
    method: str,
    url: str,
    status_code: int,
    duration: float,
    **context
):
    """
    Log HTTP request/response information.
    
    Args:
        logger: Logger instance
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration
        **context: Additional context
    """
    logger.info(
        "HTTP request completed",
        method=method,
        url=url,
        status_code=status_code,
        duration_seconds=duration,
        **context
    )


class LoggingContext:
    """Context manager for adding logging context."""
    
    def __init__(self, logger: structlog.BoundLogger, **context):
        self.logger = logger
        self.context = context
        self.bound_logger = None
    
    def __enter__(self):
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.bound_logger.error(
                "Exception in logging context",
                error=str(exc_val),
                error_type=exc_type.__name__
            )


def create_audit_logger() -> structlog.BoundLogger:
    """
    Create logger specifically for audit events.
    
    Returns:
        structlog.BoundLogger: Audit logger
    """
    return get_logger("audit")


def log_audit_event(
    event_type: str,
    user_id: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    **details
):
    """
    Log audit event.
    
    Args:
        event_type: Type of audit event
        user_id: User identifier
        resource: Resource being accessed
        action: Action being performed
        **details: Additional event details
    """
    audit_logger = create_audit_logger()
    
    audit_logger.info(
        "Audit event",
        event_type=event_type,
        user_id=user_id,
        resource=resource,
        action=action,
        timestamp=datetime.utcnow().isoformat(),
        **details
    )


def configure_third_party_loggers():
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    third_party_loggers = [
        'httpx',
        'httpcore',
        'urllib3',
        'asyncio',
        'motor',
        'pymongo'
    ]
    
    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    # Special handling for uvicorn
    if not settings.debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def setup_file_logging(log_file_path: str):
    """
    Setup file logging in addition to console logging.
    
    Args:
        log_file_path: Path to log file
    """
    root_logger = logging.getLogger()
    
    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Use JSON formatter for file logs
    formatter = CustomJSONFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)


# Initialize logging on module import
setup_logging()
configure_third_party_loggers()