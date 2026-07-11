"""
ATLAS Platform - Connector Utilities

Utility functions for connectors.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, TypeVar

from pydantic import BaseModel

from backend.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    max_backoff: float = 60.0,
    retry_on_exceptions: tuple[type[Exception], ...] = (Exception,),
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        backoff_factor: Base backoff factor
        max_backoff: Maximum backoff time in seconds
        retry_on_exceptions: Tuple of exception types to retry on
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of func
        
    Raises:
        Last exception if all retries fail
    """
    last_exception: Exception | None = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        
        except retry_on_exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                delay = min(
                    backoff_factor * (2 ** attempt),
                    max_backoff,
                )
                logger.warning(
                    "Retrying after error",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "delay": delay,
                        "error": str(e),
                    }
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "Max retries exceeded",
                    extra={
                        "max_retries": max_retries,
                        "error": str(e),
                    }
                )
    
    if last_exception:
        raise last_exception


def parse_date(date_str: str | None) -> datetime | None:
    """Parse date string to datetime."""
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    return None


def normalize_text(text: str | None) -> str:
    """Normalize text for consistent processing."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters that might cause issues
    text = text.replace("\x00", "")
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


class ResponseCache:
    """Simple in-memory response cache."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str, max_age: int | None = None) -> tuple[Any, bool]:
        """Get value from cache. Returns (value, found) tuple."""
        if key not in self._cache:
            return None, False
        
        data, cached_at = self._cache[key]
        ttl = max_age or self.default_ttl
        expires_at = cached_at.timestamp() + ttl
        
        if datetime.now(timezone.utc).timestamp() > expires_at:
            del self._cache[key]
            return None, False
        
        return data, True
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = (value, datetime.now(timezone.utc))
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    def cleanup(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        now = datetime.now(timezone.utc).timestamp()
        expired_keys = [
            key for key, (_, cached_at) in self._cache.items()
            if cached_at.timestamp() + self.default_ttl < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Get number of cached entries."""
        return len(self._cache)


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_day: int = 1000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self._minute_buckets: list[datetime] = []
        self._day_buckets: list[datetime] = []
    
    def is_allowed(self) -> bool:
        """Check if a request is allowed."""
        now = datetime.now(timezone.utc)
        
        # Clean old entries
        minute_ago = now.timestamp() - 60
        day_ago = now.timestamp() - 86400
        
        self._minute_buckets = [t for t in self._minute_buckets if t.timestamp() > minute_ago]
        self._day_buckets = [t for t in self._day_buckets if t.timestamp() > day_ago]
        
        # Check limits
        if len(self._minute_buckets) >= self.requests_per_minute:
            return False
        
        if len(self._day_buckets) >= self.requests_per_day:
            return False
        
        return True
    
    def record_request(self) -> None:
        """Record a request."""
        now = datetime.now(timezone.utc)
        self._minute_buckets.append(now)
        self._day_buckets.append(now)
    
    def get_remaining_minute(self) -> int:
        """Get remaining requests for current minute."""
        now = datetime.now(timezone.utc)
        minute_ago = now.timestamp() - 60
        self._minute_buckets = [t for t in self._minute_buckets if t.timestamp() > minute_ago]
        return max(0, self.requests_per_minute - len(self._minute_buckets))
    
    def get_remaining_day(self) -> int:
        """Get remaining requests for current day."""
        now = datetime.now(timezone.utc)
        day_ago = now.timestamp() - 86400
        self._day_buckets = [t for t in self._day_buckets if t.timestamp() > day_ago]
        return max(0, self.requests_per_day - len(self._day_buckets))
