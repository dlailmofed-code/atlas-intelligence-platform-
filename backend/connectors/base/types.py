"""
ATLAS Platform - Connector Types

Type definitions for the connector framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Provider type classification."""
    
    NEWS = "news"
    FINANCIAL = "financial"
    GOVERNMENT = "government"
    SOCIAL = "social"
    ACADEMIC = "academic"
    SEARCH = "search"
    GOVERNMENT_LEGAL = "government_legal"
    COMPANY_DATA = "company_data"


class HealthStatus(str, Enum):
    """Provider health status."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ConnectionStatus(str, Enum):
    """Connection status."""
    
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    
    provider_name: str
    base_url: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 1000
    cache_ttl: int = 300
    validate_ssl: bool = True
    extra_headers: dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, prefix: str) -> "ConnectorConfig":
        """Create config from environment variables."""
        import os
        from pydantic import BaseModel
        
        # Get all env vars with the prefix
        env_vars = {}
        for key, value in os.environ.items():
            if key.upper().startswith(prefix.upper()):
                clean_key = key[len(prefix):].lower()
                env_vars[clean_key] = value
        
        # Map common fields
        config_data = {}
        field_mapping = {
            "api_key": f"{prefix}API_KEY",
            "api_secret": f"{prefix}API_SECRET",
            "base_url": f"{prefix}BASE_URL",
            "timeout": f"{prefix}TIMEOUT",
            "max_retries": f"{prefix}MAX_RETRIES",
            "rate_limit_per_minute": f"{prefix}RATE_LIMIT_PER_MINUTE",
            "rate_limit_per_day": f"{prefix}RATE_LIMIT_PER_DAY",
        }
        
        for field, env_key in field_mapping.items():
            if env_key in os.environ:
                value = os.environ[env_key]
                if field in ("timeout", "max_retries", "rate_limit_per_minute", "rate_limit_per_day"):
                    value = int(value)
                config_data[field] = value
        
        return cls(provider_name=prefix.rstrip("_"), **config_data)


@dataclass
class ConnectorMetrics:
    """Metrics for connector performance."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limit_hits: int = 0
    last_request_at: datetime | None = None
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_response_time_ms(self) -> float:
        """Calculate average response time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time_ms / self.successful_requests
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache = self.cache_hits + self.cache_misses
        if total_cache == 0:
            return 0.0
        return self.cache_hits / total_cache


@dataclass
class ConnectorHealth:
    """Health status for a connector."""
    
    status: HealthStatus = HealthStatus.UNKNOWN
    latency_ms: float | None = None
    last_check_at: datetime | None = None
    error_message: str | None = None
    consecutive_failures: int = 0
    is_available: bool = True


@dataclass
class ConnectorResponse:
    """Response from a connector."""
    
    data: Any
    status_code: int = 200
    success: bool = True
    error_message: str | None = None
    from_cache: bool = False
    cached_at: datetime | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if response is rate limited."""
        return self.status_code == 429


@dataclass
class ProviderInfo:
    """Information about a provider."""
    
    name: str
    provider_type: ProviderType
    description: str
    docs_url: str | None = None
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 1000
    requires_api_key: bool = True
    is_free_tier: bool = False
    supported_endpoints: list[str] = field(default_factory=list)
