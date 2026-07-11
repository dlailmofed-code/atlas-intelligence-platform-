"""
ATLAS Platform - Base Connector

Base connector class providing common functionality for all providers.
"""

import asyncio
import hashlib
import json
import time
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any, Generic, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from backend.connectors.base.types import (
    ConnectorConfig,
    ConnectorHealth,
    ConnectorMetrics,
    ConnectorResponse,
    HealthStatus,
    ProviderInfo,
    ProviderType,
)
from backend.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        max_backoff: float = 60.0,
        retry_on_status: tuple[int, ...] = (429, 500, 502, 503, 504),
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.retry_on_status = retry_on_status


class BaseConnector(ABC, Generic[T]):
    """
    Base connector providing common functionality.
    
    All provider connectors should inherit from this class.
    """

    def __init__(
        self,
        config: ConnectorConfig | None = None,
        retry_config: RetryConfig | None = None,
    ):
        self.config = config or ConnectorConfig(provider_name=self.provider_name)
        self.retry_config = retry_config or RetryConfig(
            max_retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
        )

        self._metrics = ConnectorMetrics()
        self._health = ConnectorHealth()
        self._http_client: httpx.AsyncClient | None = None
        self._rate_limiter: dict[str, list[datetime]] = {
            "minute": [],
            "day": [],
        }
        self._cache: dict[str, tuple[Any, datetime]] = {}

        self._logger = get_logger(f"{__name__}.{self.provider_name}")

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name identifier."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Provider type classification."""
        pass

    @property
    @abstractmethod
    def provider_info(self) -> ProviderInfo:
        """Provider information."""
        pass

    @property
    def health(self) -> ConnectorHealth:
        """Get current health status."""
        return self._health

    @property
    def metrics(self) -> ConnectorMetrics:
        """Get current metrics."""
        return self._metrics

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                headers={
                    "User-Agent": f"ATLAS-Platform/{self.provider_name}/1.0",
                    **self.config.extra_headers,
                },
            )
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    async def _check_rate_limit(self) -> bool:
        """
        Check if rate limit would be exceeded.
        
        Returns True if request can proceed, False if rate limited.
        """
        now = datetime.now(UTC)

        # Clean old entries
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)

        self._rate_limiter["minute"] = [
            ts for ts in self._rate_limiter["minute"] if ts > minute_ago
        ]
        self._rate_limiter["day"] = [
            ts for ts in self._rate_limiter["day"] if ts > day_ago
        ]

        # Check limits
        if len(self._rate_limiter["minute"]) >= self.config.rate_limit_per_minute:
            logger.warning(
                "Rate limit per minute exceeded",
                extra={"provider": self.provider_name, "limit": self.config.rate_limit_per_minute}
            )
            self._metrics.rate_limit_hits += 1
            return False

        if len(self._rate_limiter["day"]) >= self.config.rate_limit_per_day:
            logger.warning(
                "Rate limit per day exceeded",
                extra={"provider": self.provider_name, "limit": self.config.rate_limit_per_day}
            )
            self._metrics.rate_limit_hits += 1
            return False

        # Record request
        self._rate_limiter["minute"].append(now)
        self._rate_limiter["day"].append(now)

        return True

    def _get_cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        """Generate cache key for request."""
        cache_data = json.dumps({"endpoint": endpoint, "params": params}, sort_keys=True)
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> tuple[Any, bool]:
        """
        Get cached response if available and not expired.
        
        Returns (data, found) tuple.
        """
        if cache_key not in self._cache:
            self._metrics.cache_misses += 1
            return None, False

        data, cached_at = self._cache[cache_key]
        expires_at = cached_at + timedelta(seconds=self.config.cache_ttl)

        if datetime.now(UTC) > expires_at:
            del self._cache[cache_key]
            self._metrics.cache_misses += 1
            return None, False

        self._metrics.cache_hits += 1
        return data, True

    def _set_cached_response(self, cache_key: str, data: Any) -> None:
        """Cache response."""
        self._cache[cache_key] = (data, datetime.now(UTC))

    def _validate_response(self, response_data: Any, schema: type[T] | None = None) -> Any:
        """
        Validate response against schema.
        
        Returns validated data or raw data if no schema provided.
        """
        if schema is None:
            return response_data

        try:
            if isinstance(response_data, dict):
                return schema.model_validate(response_data)
            elif isinstance(response_data, list):
                return [schema.model_validate(item) for item in response_data]
            return response_data
        except ValidationError as e:
            logger.error(
                "Response validation failed",
                extra={
                    "provider": self.provider_name,
                    "error": str(e),
                }
            )
            raise

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        schema: type[T] | None = None,
        use_cache: bool = True,
    ) -> ConnectorResponse:
        """
        Make HTTP request with automatic retry and exponential backoff.
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Check rate limit
        if not await self._check_rate_limit():
            return ConnectorResponse(
                data=None,
                status_code=429,
                success=False,
                error_message="Rate limit exceeded",
                request_id=request_id,
            )

        # Check cache
        cache_key = self._get_cache_key(url, params or {})
        if use_cache:
            cached_data, found = self._get_cached_response(cache_key)
            if found:
                self._metrics.last_request_at = datetime.now(UTC)
                return ConnectorResponse(
                    data=cached_data,
                    success=True,
                    from_cache=True,
                    cached_at=self._cache.get(cache_key, (None, None))[1],
                    request_id=request_id,
                )

        # Prepare headers
        request_headers = headers or {}
        await self._add_auth_headers(request_headers)

        # Make request with retries
        client = await self._get_http_client()
        last_error: Exception | None = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                self._logger.debug(
                    "Making request",
                    extra={
                        "provider": self.provider_name,
                        "method": method,
                        "url": url,
                        "attempt": attempt + 1,
                        "request_id": request_id,
                    }
                )

                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )

                response_time_ms = (time.time() - start_time) * 1000

                # Update metrics
                self._metrics.total_requests += 1
                self._metrics.total_response_time_ms += response_time_ms
                self._metrics.last_request_at = datetime.now(UTC)

                # Check response status
                if response.status_code == 200:
                    self._metrics.successful_requests += 1
                    self._metrics.last_success_at = datetime.now(UTC)

                    response_data = response.json()
                    validated_data = self._validate_response(response_data, schema)

                    # Cache successful response
                    if use_cache:
                        self._set_cached_response(cache_key, validated_data)

                    self._update_health(HealthStatus.HEALTHY, response_time_ms)

                    return ConnectorResponse(
                        data=validated_data,
                        status_code=200,
                        success=True,
                        request_id=request_id,
                        metadata={"response_time_ms": response_time_ms},
                    )

                elif response.status_code == 429:
                    # Rate limited by provider
                    self._metrics.rate_limit_hits += 1

                    # Calculate retry delay
                    retry_after = float(response.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    continue

                elif response.status_code in self.retry_config.retry_on_status:
                    # Server error, retry
                    last_error = Exception(f"HTTP {response.status_code}: {response.text}")

                    if attempt < self.retry_config.max_retries:
                        delay = min(
                            self.retry_config.backoff_factor * (2 ** attempt),
                            self.retry_config.max_backoff,
                        )
                        self._logger.warning(
                            "Request failed, retrying",
                            extra={
                                "provider": self.provider_name,
                                "status_code": response.status_code,
                                "attempt": attempt + 1,
                                "delay": delay,
                            }
                        )
                        await asyncio.sleep(delay)
                        continue

                else:
                    # Client error
                    self._metrics.failed_requests += 1
                    self._metrics.last_failure_at = datetime.now(UTC)
                    self._health.consecutive_failures += 1
                    self._update_health(HealthStatus.UNHEALTHY, response_time_ms)

                    return ConnectorResponse(
                        data=None,
                        status_code=response.status_code,
                        success=False,
                        error_message=f"HTTP {response.status_code}: {response.text[:500]}",
                        request_id=request_id,
                    )

            except TimeoutError:
                self._metrics.failed_requests += 1
                self._metrics.last_failure_at = datetime.now(UTC)
                last_error = Exception("Request timeout")

                if attempt < self.retry_config.max_retries:
                    delay = min(
                        self.retry_config.backoff_factor * (2 ** attempt),
                        self.retry_config.max_backoff,
                    )
                    await asyncio.sleep(delay)
                    continue

            except httpx.RequestError as e:
                self._metrics.failed_requests += 1
                self._metrics.last_failure_at = datetime.now(UTC)
                last_error = e

                if attempt < self.retry_config.max_retries:
                    delay = min(
                        self.retry_config.backoff_factor * (2 ** attempt),
                        self.retry_config.max_backoff,
                    )
                    await asyncio.sleep(delay)
                    continue

            except Exception as e:
                self._metrics.failed_requests += 1
                self._metrics.last_failure_at = datetime.now(UTC)
                last_error = e
                self._logger.exception(
                    "Unexpected error during request",
                    extra={"provider": self.provider_name}
                )
                break

        # All retries exhausted
        self._health.consecutive_failures += 1
        self._update_health(HealthStatus.UNHEALTHY)

        return ConnectorResponse(
            data=None,
            status_code=500,
            success=False,
            error_message=str(last_error) if last_error else "Unknown error",
            request_id=request_id,
        )

    def _update_health(self, status: HealthStatus, latency_ms: float | None = None) -> None:
        """Update health status."""
        self._health.status = status
        self._health.latency_ms = latency_ms
        self._health.last_check_at = datetime.now(UTC)

        if status == HealthStatus.HEALTHY:
            self._health.consecutive_failures = 0
            self._health.error_message = None
            self._health.is_available = True
        elif self._health.consecutive_failures >= 3:
            self._health.status = HealthStatus.UNHEALTHY
            self._health.is_available = False

    async def health_check(self) -> ConnectorHealth:
        """
        Perform health check on the provider.
        
        Override in subclasses to provide custom health check.
        """
        start_time = time.time()

        try:
            result = await self.health_check_impl()
            latency_ms = (time.time() - start_time) * 1000
            self._update_health(HealthStatus.HEALTHY, latency_ms)
            return self._health

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._health.status = HealthStatus.UNHEALTHY
            self._health.latency_ms = latency_ms
            self._health.last_check_at = datetime.now(UTC)
            self._health.error_message = str(e)
            self._health.is_available = False
            return self._health

    async def health_check_impl(self) -> bool:
        """
        Implementation of health check.
        
        Override in subclasses to provide custom health check logic.
        Default implementation returns True.
        """
        return True

    async def _add_auth_headers(self, headers: dict[str, str]) -> None:
        """
        Add authentication headers to request.
        
        Override in subclasses for custom auth.
        """
        if self.config.api_key:
            # Common API key header patterns
            if "X-API-Key" in self.provider_info.supported_endpoints:
                headers["X-API-Key"] = self.config.api_key
            elif "Authorization" in self.provider_info.supported_endpoints:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            else:
                # Try query param
                pass

    @abstractmethod
    async def fetch(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        schema: type[T] | None = None,
    ) -> ConnectorResponse:
        """
        Fetch data from the provider.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            schema: Response schema for validation
            
        Returns:
            ConnectorResponse with fetched data
        """
        pass

    async def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics = ConnectorMetrics()

    async def clear_cache(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get connector statistics."""
        return {
            "provider": self.provider_name,
            "provider_type": self.provider_type.value,
            "health": {
                "status": self.health.status.value,
                "latency_ms": self.health.latency_ms,
                "last_check_at": self.health.last_check_at.isoformat() if self.health.last_check_at else None,
                "is_available": self.health.is_available,
                "consecutive_failures": self.health.consecutive_failures,
            },
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
                "average_response_time_ms": self.metrics.average_response_time_ms,
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "rate_limit_hits": self.metrics.rate_limit_hits,
            },
        }
