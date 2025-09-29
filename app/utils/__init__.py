"""
Utils package for the AI Text Assistant Backend.
Contains helper functions, utilities, constants, and validation tools.
"""

from .helpers import (
    generate_secure_token,
    hash_text,
    truncate_text,
    clean_text,
    extract_urls,
    is_valid_url,
    calculate_reading_time,
    get_text_statistics,
    format_duration,
    format_file_size,
    utc_now,
    format_timestamp,
    parse_timestamp,
    mask_sensitive_data,
    deep_merge_dicts,
    flatten_dict,
    chunk_list,
    retry_with_backoff
)

from .logging_utils import (
    setup_logging,
    get_logger,
    log_performance,
    log_error_with_context,
    log_request_response,
    LoggingContext,
    create_audit_logger,
    log_audit_event,
    configure_third_party_loggers,
    setup_file_logging
)

from .constants import (
    APP_NAME,
    APP_VERSION,
    API_VERSION,
    MAX_TEXT_LENGTH,
    MAX_BATCH_SIZE,
    MAX_HISTORY_PAGE_SIZE,
    DEFAULT_PAGE_SIZE,
    ServiceStatus,
    LogLevel,
    ErrorType,
    CacheKey,
    MetricType,
    AuditEventType,
    HTTPStatus,
    ContentType,
    Headers,
    RegexPatterns,
    SUPPORTED_LANGUAGES,
    DEFAULT_CONFIG
)

from .validation_utils import (
    is_valid_email,
    is_valid_uuid,
    is_valid_ipv4,
    is_valid_language_code,
    validate_text_length,
    validate_pagination_params,
    sanitize_filename,
    validate_json_structure,
    normalize_whitespace,
    extract_numbers,
    validate_date_range,
    clean_html_tags,
    validate_password_strength,
    truncate_with_ellipsis,
    validate_sort_params
)

__all__ = [
    # Helper functions
    "generate_secure_token",
    "hash_text",
    "truncate_text", 
    "clean_text",
    "extract_urls",
    "is_valid_url",
    "calculate_reading_time",
    "get_text_statistics",
    "format_duration",
    "format_file_size",
    "utc_now",
    "format_timestamp",
    "parse_timestamp",
    "mask_sensitive_data",
    "deep_merge_dicts",
    "flatten_dict",
    "chunk_list",
    "retry_with_backoff",
    
    # Logging utilities
    "setup_logging",
    "get_logger",
    "log_performance",
    "log_error_with_context",
    "log_request_response",
    "LoggingContext",
    "create_audit_logger",
    "log_audit_event",
    "configure_third_party_loggers",
    "setup_file_logging",
    
    # Constants
    "APP_NAME",
    "APP_VERSION",
    "API_VERSION",
    "MAX_TEXT_LENGTH",
    "MAX_BATCH_SIZE",
    "MAX_HISTORY_PAGE_SIZE",
    "DEFAULT_PAGE_SIZE",
    "ServiceStatus",
    "LogLevel",
    "ErrorType",
    "CacheKey",
    "MetricType",
    "AuditEventType",
    "HTTPStatus",
    "ContentType",
    "Headers",
    "RegexPatterns",
    "SUPPORTED_LANGUAGES",
    "DEFAULT_CONFIG",
    
    # Validation utilities
    "is_valid_email",
    "is_valid_uuid",
    "is_valid_ipv4",
    "is_valid_language_code",
    "validate_text_length",
    "validate_pagination_params",
    "sanitize_filename",
    "validate_json_structure",
    "normalize_whitespace",
    "extract_numbers",
    "validate_date_range",
    "clean_html_tags",
    "validate_password_strength",
    "truncate_with_ellipsis",
    "validate_sort_params"
]