"""
Logging middleware for request/response tracking with correlation IDs.
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog

# Configure structured logging
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
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses with correlation IDs."""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with logging."""
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        if self.log_requests:
            await self._log_request(request, correlation_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            # Log response
            if self.log_responses:
                await self._log_response(request, response, correlation_id, process_time)
            
            return response
            
        except Exception as e:
            # Calculate processing time for error case
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                "Request processing failed",
                correlation_id=correlation_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                process_time=process_time
            )
            
            # Re-raise the exception to be handled by error middleware
            raise
    
    async def _log_request(self, request: Request, correlation_id: str):
        """Log incoming request details."""
        
        # Get client information
        client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        client_port = getattr(request.client, 'port', 'unknown') if request.client else 'unknown'
        
        # Get headers (excluding sensitive ones)
        headers = dict(request.headers)
        sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        filtered_headers = {
            k: '***' if k.lower() in sensitive_headers else v 
            for k, v in headers.items()
        }
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        logger.info(
            "Incoming request",
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=query_params,
            client_host=client_host,
            client_port=client_port,
            user_agent=headers.get('user-agent', 'unknown'),
            content_type=headers.get('content-type'),
            content_length=headers.get('content-length'),
            headers=filtered_headers
        )
    
    async def _log_response(self, request: Request, response: Response, correlation_id: str, process_time: float):
        """Log outgoing response details."""
        
        logger.info(
            "Outgoing response",
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
            response_size=response.headers.get('content-length'),
            content_type=response.headers.get('content-type')
        )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request timing and performance monitoring."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add detailed timing information to requests."""
        
        # Record start time
        start_time = time.perf_counter()
        request.state.start_time = start_time
        
        # Process request
        response = await call_next(request)
        
        # Calculate timing
        end_time = time.perf_counter()
        process_time = end_time - start_time
        
        # Add timing headers
        response.headers["X-Process-Time-Seconds"] = str(round(process_time, 6))
        response.headers["X-Process-Time-MS"] = str(round(process_time * 1000, 2))
        
        # Log slow requests
        if process_time > 5.0:  # Log requests taking more than 5 seconds
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')
            logger.warning(
                "Slow request detected",
                correlation_id=correlation_id,
                method=request.method,
                url=str(request.url),
                process_time=process_time,
                status_code=response.status_code
            )
        
        return response


def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Correlation ID
    """
    return getattr(request.state, 'correlation_id', 'unknown')


def log_with_correlation(request: Request, level: str, message: str, **kwargs):
    """
    Log message with correlation ID from request.
    
    Args:
        request: FastAPI request object
        level: Log level (info, warning, error, etc.)
        message: Log message
        **kwargs: Additional log data
    """
    correlation_id = get_correlation_id(request)
    log_func = getattr(logger, level.lower(), logger.info)
    
    log_func(message, correlation_id=correlation_id, **kwargs)