"""
Additional validation utilities and data transformation functions.
"""

import re
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from urllib.parse import urlparse

from .constants import RegexPatterns, SUPPORTED_LANGUAGES


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email or len(email) > 254:
        return False
    
    return bool(re.match(RegexPatterns.EMAIL, email))


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(RegexPatterns.UUID, uuid_string.lower()))


def is_valid_ipv4(ip: str) -> bool:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(RegexPatterns.IPV4, ip))


def is_valid_language_code(code: str) -> bool:
    """
    Validate language code.
    
    Args:
        code: Language code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return code.lower() in SUPPORTED_LANGUAGES


def validate_text_length(text: str, min_length: int = 1, max_length: int = 10000) -> Tuple[bool, Optional[str]]:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not text:
        return False, "Text cannot be empty"
    
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"Text must be at least {min_length} characters long"
    
    if text_length > max_length:
        return False, f"Text cannot exceed {max_length} characters"
    
    return True, None


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        page_size: Items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if page < 1:
        return False, "Page number must be >= 1"
    
    if page_size < 1:
        return False, "Page size must be >= 1"
    
    if page_size > max_page_size:
        return False, f"Page size cannot exceed {max_page_size}"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Trim whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def validate_json_structure(data: Any, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate JSON structure has required fields.
    
    Args:
        data: Data to validate
        required_fields: List of required field names
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, missing_fields)
    """
    if not isinstance(data, dict):
        return False, ["Data must be a JSON object"]
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        str: Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List[float]: List of numbers found
    """
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(float(int(match)))
        except ValueError:
            continue
    
    return numbers


def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, Optional[str]]:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    # Check if dates are reasonable (not too far in past/future)
    now = datetime.utcnow()
    max_past = datetime(1900, 1, 1)
    max_future = datetime(2100, 1, 1)
    
    if start_date < max_past or end_date < max_past:
        return False, "Dates cannot be before year 1900"
    
    if start_date > max_future or end_date > max_future:
        return False, "Dates cannot be after year 2100"
    
    return True, None


def clean_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text with potential HTML tags
        
    Returns:
        str: Text with HTML tags removed
    """
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    return clean_text


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in weak_passwords:
        issues.append("Password is too common")
    
    return len(issues) == 0, issues


def truncate_with_ellipsis(text: str, max_length: int, ellipsis: str = "...") -> str:
    """
    Truncate text with ellipsis if too long.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including ellipsis
        ellipsis: Ellipsis string to append
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(ellipsis)] + ellipsis


def validate_sort_params(sort_by: str, sort_order: str, allowed_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate sorting parameters.
    
    Args:
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        allowed_fields: List of allowed sort fields
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if sort_by not in allowed_fields:
        return False, f"Invalid sort field. Allowed fields: {', '.join(allowed_fields)}"
    
    if sort_order.lower() not in ['asc', 'desc']:
        return False, "Sort order must be 'asc' or 'desc'"
    
    return True, None