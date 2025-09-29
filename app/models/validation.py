"""
Request validation utilities and functions.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from .requests import TextOperation
from ..utils.validation_utils import (
    validate_text_length,
    is_valid_language_code,
    normalize_whitespace,
    clean_html_tags
)


def validate_text_modification_request(request_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate text modification request data.
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['text', 'operation']
    for field in required_fields:
        if field not in request_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate text
    if 'text' in request_data:
        text = request_data['text']
        if not isinstance(text, str):
            errors.append("Text must be a string")
        else:
            is_valid, error = validate_text_length(text, min_length=1, max_length=10000)
            if not is_valid:
                errors.append(error)
    
    # Validate operation
    if 'operation' in request_data:
        operation = request_data['operation']
        if not isinstance(operation, str):
            errors.append("Operation must be a string")
        else:
            try:
                TextOperation(operation.lower())
            except ValueError:
                valid_operations = [op.value for op in TextOperation]
                errors.append(f"Invalid operation. Valid operations: {', '.join(valid_operations)}")
    
    # Validate optional fields
    if 'user_id' in request_data:
        user_id = request_data['user_id']
        if user_id is not None:
            if not isinstance(user_id, str):
                errors.append("User ID must be a string")
            elif len(user_id) > 100:
                errors.append("User ID cannot exceed 100 characters")
            elif not user_id.strip():
                errors.append("User ID cannot be empty")
    
    # Validate target_language
    if 'target_language' in request_data:
        target_language = request_data['target_language']
        if target_language is not None:
            if not isinstance(target_language, str):
                errors.append("Target language must be a string")
            elif not is_valid_language_code(target_language):
                errors.append("Invalid target language code")
    
    # Validate translation requirements
    if ('operation' in request_data and 
        request_data['operation'] == TextOperation.TRANSLATE.value and
        'target_language' not in request_data):
        errors.append("Target language is required for translation operations")
    
    # Validate options
    if 'options' in request_data:
        options = request_data['options']
        if options is not None:
            if not isinstance(options, dict):
                errors.append("Options must be a dictionary")
            elif len(str(options)) > 1000:
                errors.append("Options dictionary is too large")
    
    # Validate preserve_formatting
    if 'preserve_formatting' in request_data:
        preserve_formatting = request_data['preserve_formatting']
        if not isinstance(preserve_formatting, bool):
            errors.append("Preserve formatting must be a boolean")
    
    return len(errors) == 0, errors


def validate_background_text_request(request_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate background text request data.
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['text', 'operation']
    for field in required_fields:
        if field not in request_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate text
    if 'text' in request_data:
        text = request_data['text']
        if not isinstance(text, str):
            errors.append("Text must be a string")
        else:
            is_valid, error = validate_text_length(text, min_length=1, max_length=10000)
            if not is_valid:
                errors.append(error)
    
    # Validate operation
    if 'operation' in request_data:
        operation = request_data['operation']
        if not isinstance(operation, str):
            errors.append("Operation must be a string")
        else:
            try:
                TextOperation(operation.lower())
            except ValueError:
                valid_operations = [op.value for op in TextOperation]
                errors.append(f"Invalid operation. Valid operations: {', '.join(valid_operations)}")
    
    # Validate optional fields
    optional_string_fields = {
        'source_application': 100,
        'window_title': 200,
        'user_id': 100
    }
    
    for field, max_length in optional_string_fields.items():
        if field in request_data:
            value = request_data[field]
            if value is not None:
                if not isinstance(value, str):
                    errors.append(f"{field} must be a string")
                elif len(value) > max_length:
                    errors.append(f"{field} cannot exceed {max_length} characters")
    
    # Validate options
    if 'options' in request_data:
        options = request_data['options']
        if options is not None:
            if not isinstance(options, dict):
                errors.append("Options must be a dictionary")
    
    return len(errors) == 0, errors


def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input by cleaning and normalizing.
    
    Args:
        text: Raw text input
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Clean HTML tags
    text = clean_html_tags(text)
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def validate_pagination_request(page: int, page_size: int) -> Tuple[bool, List[str]]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        page_size: Items per page
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if page < 1:
        errors.append("Page number must be >= 1")
    
    if page_size < 1:
        errors.append("Page size must be >= 1")
    
    if page_size > 100:
        errors.append("Page size cannot exceed 100")
    
    return len(errors) == 0, errors


def validate_user_id(user_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate user ID format.
    
    Args:
        user_id: User identifier
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if user_id is None:
        return True, None
    
    if not isinstance(user_id, str):
        return False, "User ID must be a string"
    
    if not user_id.strip():
        return False, "User ID cannot be empty"
    
    if len(user_id) > 100:
        return False, "User ID cannot exceed 100 characters"
    
    # Check for invalid characters
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', user_id):
        return False, "User ID contains invalid characters"
    
    return True, None


def validate_operation_filter(operation: Optional[str]) -> Tuple[bool, Optional[str], Optional[TextOperation]]:
    """
    Validate operation filter parameter.
    
    Args:
        operation: Operation string to validate
        
    Returns:
        Tuple[bool, Optional[str], Optional[TextOperation]]: (is_valid, error_message, parsed_operation)
    """
    if operation is None:
        return True, None, None
    
    if not isinstance(operation, str):
        return False, "Operation must be a string", None
    
    try:
        parsed_operation = TextOperation(operation.lower())
        return True, None, parsed_operation
    except ValueError:
        valid_operations = [op.value for op in TextOperation]
        return False, f"Invalid operation. Valid operations: {', '.join(valid_operations)}", None


def validate_analysis_request(text: str, user_id: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate text analysis request.
    
    Args:
        text: Text to analyze
        user_id: Optional user identifier
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate text
    if not isinstance(text, str):
        errors.append("Text must be a string")
    else:
        is_valid, error = validate_text_length(text, min_length=1, max_length=10000)
        if not is_valid:
            errors.append(error)
    
    # Validate user_id
    if user_id is not None:
        is_valid, error = validate_user_id(user_id)
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors


def validate_health_check_request(
    include_database: bool = True,
    include_ai_service: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate health check request parameters.
    
    Args:
        include_database: Whether to include database health
        include_ai_service: Whether to include AI service health
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(include_database, bool):
        errors.append("include_database must be a boolean")
    
    if not isinstance(include_ai_service, bool):
        errors.append("include_ai_service must be a boolean")
    
    return len(errors) == 0, errors


def extract_and_validate_request_metadata(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate request metadata.
    
    Args:
        request_data: Raw request data
        
    Returns:
        Dict containing validated metadata
    """
    metadata = {}
    
    # Extract timestamp
    metadata['received_at'] = datetime.utcnow()
    
    # Extract and validate text length
    if 'text' in request_data and isinstance(request_data['text'], str):
        metadata['text_length'] = len(request_data['text'])
        metadata['word_count'] = len(request_data['text'].split())
    
    # Extract operation
    if 'operation' in request_data:
        metadata['operation'] = request_data['operation']
    
    # Extract user information
    if 'user_id' in request_data and request_data['user_id']:
        metadata['user_id'] = request_data['user_id']
    
    # Extract source information for background requests
    if 'source_application' in request_data and request_data['source_application']:
        metadata['source_application'] = request_data['source_application']
    
    if 'window_title' in request_data and request_data['window_title']:
        metadata['window_title'] = request_data['window_title']
    
    return metadata