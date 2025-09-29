"""
Constants and enums for the AI Text Assistant Backend.
"""

from enum import Enum


# Application constants
APP_NAME = "AI Text Assistant Backend"
APP_VERSION = "1.0.0"
API_VERSION = "v1"

# Text processing limits
MAX_TEXT_LENGTH = 10000
MAX_BATCH_SIZE = 100
MAX_HISTORY_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

# Timeout constants (in seconds)
DEFAULT_REQUEST_TIMEOUT = 60
AI_SERVICE_TIMEOUT = 30
DATABASE_TIMEOUT = 10
BACKGROUND_SERVICE_TIMEOUT = 5

# Cache constants
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE = 1000

# Rate limiting
DEFAULT_RATE_LIMIT = 100  # requests per minute
BURST_RATE_LIMIT = 200

# File size limits
MAX_LOG_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_BACKUP_COUNT = 5

# Database constants
DEFAULT_CONNECTION_POOL_SIZE = 10
MAX_CONNECTION_POOL_SIZE = 50
CONNECTION_TIMEOUT_MS = 5000

# Background service constants
BACKGROUND_SERVICE_HOST = "127.0.0.1"
BACKGROUND_SERVICE_PORT = 8001
MAX_CONCURRENT_REQUESTS = 10

# Security constants
MIN_PASSWORD_LENGTH = 8
TOKEN_EXPIRY_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5

# Monitoring constants
HEALTH_CHECK_INTERVAL = 30  # seconds
METRICS_COLLECTION_INTERVAL = 60  # seconds


class ServiceStatus(str, Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorType(str, Enum):
    """Error type enumeration."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVICE_ERROR = "service_error"
    DATABASE_ERROR = "database_error"
    AI_SERVICE_ERROR = "ai_service_error"
    TEXT_PROCESSING_ERROR = "text_processing_error"
    CONFIGURATION_ERROR = "configuration_error"
    INTERNAL_ERROR = "internal_error"


class CacheKey(str, Enum):
    """Cache key prefixes."""
    USER_STATS = "user_stats"
    TEXT_ANALYSIS = "text_analysis"
    AI_RESPONSE = "ai_response"
    HEALTH_CHECK = "health_check"


class MetricType(str, Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AuditEventType(str, Enum):
    """Audit event type enumeration."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    TEXT_MODIFICATION = "text_modification"
    TEXT_ANALYSIS = "text_analysis"
    CONFIGURATION_CHANGE = "configuration_change"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    ERROR_OCCURRED = "error_occurred"


# HTTP status codes
class HTTPStatus:
    """HTTP status code constants."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# Content types
class ContentType:
    """Content type constants."""
    JSON = "application/json"
    TEXT = "text/plain"
    HTML = "text/html"
    XML = "application/xml"
    FORM_DATA = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"


# Headers
class Headers:
    """HTTP header constants."""
    CONTENT_TYPE = "Content-Type"
    AUTHORIZATION = "Authorization"
    USER_AGENT = "User-Agent"
    CORRELATION_ID = "X-Correlation-ID"
    REQUEST_ID = "X-Request-ID"
    PROCESS_TIME = "X-Process-Time"
    RATE_LIMIT_REMAINING = "X-RateLimit-Remaining"
    RATE_LIMIT_RESET = "X-RateLimit-Reset"


# Regular expressions
class RegexPatterns:
    """Common regex patterns."""
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    UUID = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    IPV4 = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    PHONE = r'^\+?1?-?\.?\s?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})$'


# Language codes (ISO 639-1)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'pl': 'Polish',
    'tr': 'Turkish',
    'he': 'Hebrew'
}

# Default configuration values
DEFAULT_CONFIG = {
    'host': '127.0.0.1',
    'port': 8000,
    'debug': False,
    'log_level': 'INFO',
    'log_format': 'json',
    'cors_origins': ['*'],
    'max_request_size': 1024 * 1024,  # 1MB
    'request_timeout': 60,
    'ai_api_timeout': 30,
    'background_service_enabled': True,
    'background_service_port': 8001
}