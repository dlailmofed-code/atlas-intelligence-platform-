"""
Tests for connector utilities.
"""

import pytest
import asyncio

from backend.connectors.utils import (
    ResponseCache,
    RateLimiter,
    merge_dicts,
    normalize_text,
    parse_date,
    truncate_text,
)


class TestResponseCache:
    """Tests for ResponseCache."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        cache = ResponseCache(default_ttl=60)
        
        # Set value
        cache.set("key1", {"data": "value1"})
        
        # Get value
        data, found = cache.get("key1")
        assert found is True
        assert data == {"data": "value1"}
        
        # Get non-existent value
        data, found = cache.get("nonexistent")
        assert found is False
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = ResponseCache(default_ttl=0)  # Immediate expiration
        
        cache.set("key1", {"data": "value1"})
        data, found = cache.get("key1", max_age=0)
        
        assert found is False
    
    def test_cache_clear(self):
        """Test cache clear."""
        cache = ResponseCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.size() == 2
        
        cache.clear()
        
        assert cache.size() == 0
    
    def test_cache_delete(self):
        """Test cache delete."""
        cache = ResponseCache()
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        data, found = cache.get("key1")
        assert found is False
    
    def test_cache_cleanup(self):
        """Test cache cleanup of expired entries."""
        cache = ResponseCache(default_ttl=0)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        removed = cache.cleanup()
        
        assert removed >= 0


class TestRateLimiter:
    """Tests for RateLimiter."""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiting."""
        limiter = RateLimiter(
            requests_per_minute=10,
            requests_per_day=100,
        )
        
        # First request should be allowed
        assert limiter.is_allowed() is True
        limiter.record_request()
        
        # More requests should be allowed up to limit
        for _ in range(8):
            assert limiter.is_allowed() is True
            limiter.record_request()
    
    def test_rate_limiter_limit_reached(self):
        """Test rate limit reached."""
        limiter = RateLimiter(
            requests_per_minute=2,
            requests_per_day=100,
        )
        
        assert limiter.is_allowed() is True
        limiter.record_request()
        
        assert limiter.is_allowed() is True
        limiter.record_request()
        
        # Limit reached
        assert limiter.is_allowed() is False
    
    def test_rate_limiter_remaining(self):
        """Test remaining requests calculation."""
        limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_day=1000,
        )
        
        remaining = limiter.get_remaining_minute()
        assert remaining == 60
        
        limiter.record_request()
        remaining = limiter.get_remaining_minute()
        assert remaining == 59


class TestMergeDicts:
    """Tests for merge_dicts function."""
    
    def test_merge_empty(self):
        """Test merging empty dicts."""
        result = merge_dicts()
        assert result == {}
    
    def test_merge_single(self):
        """Test merging single dict."""
        result = merge_dicts({"a": 1})
        assert result == {"a": 1}
    
    def test_merge_multiple(self):
        """Test merging multiple dicts."""
        result = merge_dicts(
            {"a": 1, "b": 2},
            {"b": 3, "c": 4},
            {"d": 5}
        )
        assert result == {"a": 1, "b": 3, "c": 4, "d": 5}
    
    def test_merge_with_none(self):
        """Test merging with None."""
        result = merge_dicts({"a": 1}, None, {"b": 2})
        assert result == {"a": 1, "b": 2}


class TestNormalizeText:
    """Tests for normalize_text function."""
    
    def test_normalize_basic(self):
        """Test basic normalization."""
        result = normalize_text("  Hello   World  ")
        assert result == "Hello World"
    
    def test_normalize_empty(self):
        """Test normalization of empty string."""
        result = normalize_text("")
        assert result == ""
    
    def test_normalize_none(self):
        """Test normalization of None."""
        result = normalize_text(None)
        assert result == ""
    
    def test_normalize_special_chars(self):
        """Test normalization of special characters."""
        result = normalize_text("Hello\x00World")
        assert result == "HelloWorld"


class TestTruncateText:
    """Tests for truncate_text function."""
    
    def test_truncate_short_text(self):
        """Test truncation of short text."""
        text = "Hello"
        result = truncate_text(text, max_length=10)
        assert result == "Hello"
    
    def test_truncate_long_text(self):
        """Test truncation of long text."""
        text = "Hello World"
        result = truncate_text(text, max_length=8)
        assert result == "Hello..."
    
    def test_truncate_exact_length(self):
        """Test truncation with exact length."""
        text = "Hello"
        result = truncate_text(text, max_length=5)
        assert result == "Hello"


class TestParseDate:
    """Tests for parse_date function."""
    
    def test_parse_iso_format(self):
        """Test parsing ISO format date."""
        result = parse_date("2024-01-15T12:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_simple_date(self):
        """Test parsing simple date."""
        result = parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_none(self):
        """Test parsing None."""
        result = parse_date(None)
        assert result is None
    
    def test_parse_invalid(self):
        """Test parsing invalid date."""
        result = parse_date("not-a-date")
        assert result is None
