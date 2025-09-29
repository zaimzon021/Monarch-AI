"""
Tests for utility functions and helpers.
"""

import pytest
from datetime import datetime, timezone

from app.utils.helpers import (
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
    chunk_list
)

from app.utils.validation_utils import (
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
    clean_html_tags,
    validate_password_strength,
    truncate_with_ellipsis,
    validate_sort_params
)


class TestHelpers:
    """Test cases for helper functions."""
    
    def test_generate_secure_token(self):
        """Test secure token generation."""
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        
        assert len(token1) == 32
        assert len(token2) == 32
        assert token1 != token2  # Should be different
        assert token1.isalnum()  # Should contain only alphanumeric characters
    
    def test_hash_text(self):
        """Test text hashing."""
        text = "This is a test text"
        hash1 = hash_text(text)
        hash2 = hash_text(text)
        hash3 = hash_text("Different text")
        
        assert hash1 == hash2  # Same text should produce same hash
        assert hash1 != hash3  # Different text should produce different hash
        assert len(hash1) == 64  # SHA256 produces 64 character hex string
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated"
        
        # Test normal truncation
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")
        
        # Test text shorter than max length
        short_text = "Short"
        result = truncate_text(short_text, 20)
        assert result == short_text
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  This   has    extra   spaces  \n\n  and  \t tabs  "
        clean = clean_text(dirty_text)
        
        assert clean == "This has extra spaces and tabs"
        assert "  " not in clean  # No double spaces
    
    def test_extract_urls(self):
        """Test URL extraction from text."""
        text = "Visit https://example.com and http://test.org for more info"
        urls = extract_urls(text)
        
        assert len(urls) == 2
        assert "https://example.com" in urls
        assert "http://test.org" in urls
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://test.org")
        assert not is_valid_url("not-a-url")
        assert not is_valid_url("ftp://example.com")  # Only http/https allowed
    
    def test_calculate_reading_time(self):
        """Test reading time calculation."""
        text = " ".join(["word"] * 200)  # 200 words
        reading_time = calculate_reading_time(text, 200)  # 200 WPM
        
        assert reading_time == 1  # Should be 1 minute
        
        # Test with shorter text
        short_text = "Just a few words"
        reading_time = calculate_reading_time(short_text, 200)
        assert reading_time == 1  # Minimum 1 minute
    
    def test_get_text_statistics(self):
        """Test text statistics calculation."""
        text = "This is a test. It has multiple sentences! And paragraphs.\n\nSecond paragraph here."
        stats = get_text_statistics(text)
        
        assert stats["word_count"] > 0
        assert stats["sentence_count"] >= 3
        assert stats["paragraph_count"] == 2
        assert stats["character_count"] > 0
        assert "reading_time_minutes" in stats
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(0.5) == "500ms"
        assert format_duration(1.5) == "1.5s"
        assert format_duration(65) == "1m 5s"
        assert format_duration(3665) == "1h 1m"
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(512) == "512.0 B"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(1048576) == "1.0 MB"
    
    def test_utc_now(self):
        """Test UTC timestamp generation."""
        now = utc_now()
        assert now.tzinfo == timezone.utc
        assert isinstance(now, datetime)
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        formatted = format_timestamp(dt)
        
        assert "2023-01-01" in formatted
        assert "12:00:00" in formatted
        assert "UTC" in formatted
    
    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        timestamp_str = "2023-01-01T12:00:00Z"
        dt = parse_timestamp(timestamp_str)
        
        assert dt is not None
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        data = "secret123456"
        masked = mask_sensitive_data(data, visible_chars=4)
        
        assert masked.endswith("3456")
        assert masked.startswith("*")
        assert len(masked) == len(data)
    
    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
        dict2 = {"b": {"d": 4, "e": 5}, "f": 6}
        
        result = deep_merge_dicts(dict1, dict2)
        
        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 4  # dict2 takes precedence
        assert result["b"]["e"] == 5
        assert result["f"] == 6
    
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_dict(nested)
        
        assert flattened["a"] == 1
        assert flattened["b.c"] == 2
        assert flattened["b.d.e"] == 3
    
    def test_chunk_list(self):
        """Test list chunking."""
        lst = list(range(10))
        chunks = chunk_list(lst, 3)
        
        assert len(chunks) == 4  # [0,1,2], [3,4,5], [6,7,8], [9]
        assert chunks[0] == [0, 1, 2]
        assert chunks[-1] == [9]


class TestValidationUtils:
    """Test cases for validation utilities."""
    
    def test_is_valid_email(self):
        """Test email validation."""
        assert is_valid_email("test@example.com")
        assert is_valid_email("user.name+tag@domain.co.uk")
        assert not is_valid_email("invalid-email")
        assert not is_valid_email("@domain.com")
        assert not is_valid_email("user@")
    
    def test_is_valid_uuid(self):
        """Test UUID validation."""
        assert is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
        assert not is_valid_uuid("not-a-uuid")
        assert not is_valid_uuid("123e4567-e89b-12d3-a456")  # Too short
    
    def test_is_valid_ipv4(self):
        """Test IPv4 validation."""
        assert is_valid_ipv4("192.168.1.1")
        assert is_valid_ipv4("127.0.0.1")
        assert not is_valid_ipv4("256.1.1.1")  # Invalid octet
        assert not is_valid_ipv4("192.168.1")  # Incomplete
    
    def test_is_valid_language_code(self):
        """Test language code validation."""
        assert is_valid_language_code("en")
        assert is_valid_language_code("ES")  # Case insensitive
        assert not is_valid_language_code("invalid")
    
    def test_validate_text_length(self):
        """Test text length validation."""
        is_valid, error = validate_text_length("Valid text", 1, 100)
        assert is_valid
        assert error is None
        
        is_valid, error = validate_text_length("", 1, 100)
        assert not is_valid
        assert "empty" in error
        
        is_valid, error = validate_text_length("x" * 101, 1, 100)
        assert not is_valid
        assert "exceed" in error
    
    def test_validate_pagination_params(self):
        """Test pagination parameter validation."""
        is_valid, error = validate_pagination_params(1, 10, 100)
        assert is_valid
        assert error is None
        
        is_valid, error = validate_pagination_params(0, 10, 100)
        assert not is_valid
        assert "Page number" in error
        
        is_valid, error = validate_pagination_params(1, 101, 100)
        assert not is_valid
        assert "exceed" in error
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("valid_file.txt") == "valid_file.txt"
        assert sanitize_filename("file<>with|bad*chars") == "filewithbadchars"
        assert sanitize_filename("   ") == "untitled"
    
    def test_validate_json_structure(self):
        """Test JSON structure validation."""
        data = {"name": "test", "value": 123}
        is_valid, missing = validate_json_structure(data, ["name", "value"])
        assert is_valid
        assert len(missing) == 0
        
        is_valid, missing = validate_json_structure(data, ["name", "missing"])
        assert not is_valid
        assert "missing" in missing
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "  Multiple   spaces   and\n\ntabs\t  "
        normalized = normalize_whitespace(text)
        assert normalized == "Multiple spaces and tabs"
    
    def test_extract_numbers(self):
        """Test number extraction."""
        text = "I have 5 apples and 3.14 oranges, but -2 bananas"
        numbers = extract_numbers(text)
        
        assert 5.0 in numbers
        assert 3.14 in numbers
        assert -2.0 in numbers
    
    def test_clean_html_tags(self):
        """Test HTML tag cleaning."""
        html = "<p>This is <strong>bold</strong> text with <a href='#'>link</a></p>"
        clean = clean_html_tags(html)
        
        assert "<" not in clean
        assert ">" not in clean
        assert "This is bold text with link" == clean
    
    def test_validate_password_strength(self):
        """Test password strength validation."""
        is_valid, issues = validate_password_strength("StrongP@ss123")
        assert is_valid
        assert len(issues) == 0
        
        is_valid, issues = validate_password_strength("weak")
        assert not is_valid
        assert len(issues) > 0
    
    def test_truncate_with_ellipsis(self):
        """Test text truncation with ellipsis."""
        text = "This is a long text"
        truncated = truncate_with_ellipsis(text, 10)
        
        assert len(truncated) == 10
        assert truncated.endswith("...")
    
    def test_validate_sort_params(self):
        """Test sort parameter validation."""
        allowed_fields = ["name", "date", "size"]
        
        is_valid, error = validate_sort_params("name", "asc", allowed_fields)
        assert is_valid
        assert error is None
        
        is_valid, error = validate_sort_params("invalid", "asc", allowed_fields)
        assert not is_valid
        assert "Invalid sort field" in error
        
        is_valid, error = validate_sort_params("name", "invalid", allowed_fields)
        assert not is_valid
        assert "Sort order" in error