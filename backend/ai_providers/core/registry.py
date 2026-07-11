"""
ATLAS Platform - AI Provider Registry and Factory

Provider management with automatic failover and routing.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.ai_providers.core.base import BaseProvider
from backend.ai_providers.core.types import (
    CircuitBreakerState,
    ModelInfo,
    ProviderHealth,
    ProviderStatus,
    ProviderType,
    RoutingConfig,
)

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    
    provider_type: ProviderType
    api_key: str | None = None
    base_url: str | None = None
    enabled: bool = True
    priority: int = 0
    weight: float = 1.0
    timeout: float = 30.0
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


class CircuitBreaker:
    """Circuit breaker for provider health management."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = CircuitBreakerState()
        self._half_open_calls = 0
    
    @property
    def state(self) -> str:
        return self._state.state
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        if self._state.state == "closed":
            return True
        
        if self._state.state == "open":
            if self._state.next_attempt_time and datetime.now(timezone.utc) >= self._state.next_attempt_time:
                self._state.state = "half_open"
                self._half_open_calls = 0
                return True
            return False
        
        # half_open
        return self._half_open_calls < self.half_open_max_calls
    
    def record_success(self) -> None:
        """Record a successful call."""
        if self._state.state == "half_open":
            self._half_open_calls += 1
            self._state.success_count += 1
            
            if self._half_open_calls >= self.half_open_max_calls:
                self._state.state = "closed"
                self._state.failure_count = 0
                self._half_open_calls = 0
                logger.info("Circuit breaker closed after successful recovery")
        elif self._state.state == "closed":
            self._state.success_count += 1
            # Reset failure count after successes
            if self._state.success_count >= 3:
                self._state.failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed call."""
        self._state.failure_count += 1
        self._state.last_failure_time = datetime.now(timezone.utc)
        
        if self._state.state == "half_open":
            self._state.state = "open"
            self._state.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=self.recovery_timeout)
            self._half_open_calls = 0
            logger.warning("Circuit breaker reopened after half-open failure")
        elif self._state.failure_count >= self.failure_threshold:
            self._state.state = "open"
            self._state.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=self.recovery_timeout)
            logger.warning("Circuit breaker opened after threshold failures")
    
    def reset(self) -> None:
        """Reset the circuit breaker."""
        self._state = CircuitBreakerState()


class ProviderRegistry:
    """
    Registry for managing AI providers.
    
    Handles provider registration, health monitoring, and failover.
    """
    
    def __init__(self):
        self._providers: dict[ProviderType, BaseProvider] = {}
        self._configs: dict[ProviderType, ProviderConfig] = {}
        self._circuit_breakers: dict[ProviderType, CircuitBreaker] = {}
        self._health_status: dict[ProviderType, ProviderHealth] = {}
        self._lock = asyncio.Lock()
    
    def register(
        self,
        provider_type: ProviderType,
        provider: BaseProvider,
        config: ProviderConfig | None = None,
    ) -> None:
        """Register a provider."""
        self._providers[provider_type] = provider
        self._configs[provider_type] = config or ProviderConfig(provider_type=provider_type)
        self._circuit_breakers[provider_type] = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold if config else 5,
        )
        self._health_status[provider_type] = ProviderHealth(
            provider=provider_type,
            status=ProviderStatus.UNKNOWN,
        )
        logger.info(f"Provider registered: {provider_type.value}")
    
    def unregister(self, provider_type: ProviderType) -> None:
        """Unregister a provider."""
        if provider_type in self._providers:
            del self._providers[provider_type]
        if provider_type in self._configs:
            del self._configs[provider_type]
        if provider_type in self._circuit_breakers:
            del self._circuit_breakers[provider_type]
        logger.info(f"Provider unregistered: {provider_type.value}")
    
    def get(self, provider_type: ProviderType) -> BaseProvider | None:
        """Get a provider by type."""
        return self._providers.get(provider_type)
    
    def get_all(self) -> dict[ProviderType, BaseProvider]:
        """Get all registered providers."""
        return dict(self._providers)
    
    def get_available(
        self,
        preferred: list[ProviderType] | None = None,
    ) -> list[ProviderType]:
        """Get available providers sorted by preference."""
        available = []
        
        for provider_type in self._providers:
            config = self._configs.get(provider_type)
            if not config or not config.enabled:
                continue
            
            cb = self._circuit_breakers.get(provider_type)
            if cb and not cb.is_available():
                continue
            
            available.append(provider_type)
        
        # Sort by preference
        if preferred:
            def sort_key(pt: ProviderType) -> tuple[int, int]:
                priority = preferred.index(pt) if pt in preferred else len(preferred)
                config = self._configs.get(pt)
                return (priority, -config.priority if config else 0)
            
            available.sort(key=sort_key)
        
        return available
    
    def get_health(self, provider_type: ProviderType) -> ProviderHealth | None:
        """Get health status for a provider."""
        return self._health_status.get(provider_type)
    
    def get_all_health(self) -> dict[ProviderType, ProviderHealth]:
        """Get health status for all providers."""
        return dict(self._health_status)
    
    async def check_health(self, provider_type: ProviderType) -> ProviderHealth:
        """Check and update health status for a provider."""
        provider = self._providers.get(provider_type)
        if not provider:
            return ProviderHealth(
                provider=provider_type,
                status=ProviderStatus.UNKNOWN,
                is_available=False,
                error_message="Provider not registered",
            )
        
        try:
            start = asyncio.get_event_loop().time()
            is_healthy = await asyncio.wait_for(
                provider.health_check(),
                timeout=10.0,
            )
            latency_ms = (asyncio.get_event_loop().time() - start) * 1000
            
            metrics = provider.get_metrics()
            
            health = ProviderHealth(
                provider=provider_type,
                status=ProviderStatus.HEALTHY if is_healthy else ProviderStatus.DEGRADED,
                latency_ms=latency_ms,
                success_rate=metrics.success_rate,
                consecutive_failures=metrics.consecutive_failures,
                is_available=is_healthy,
                last_checked=datetime.now(timezone.utc),
            )
            
            # Update circuit breaker
            cb = self._circuit_breakers.get(provider_type)
            if cb:
                if is_healthy:
                    cb.record_success()
                else:
                    cb.record_failure()
            
            self._health_status[provider_type] = health
            return health
        
        except asyncio.TimeoutError:
            return ProviderHealth(
                provider=provider_type,
                status=ProviderStatus.UNHEALTHY,
                is_available=False,
                error_message="Health check timeout",
                last_checked=datetime.now(timezone.utc),
            )
        except Exception as e:
            return ProviderHealth(
                provider=provider_type,
                status=ProviderStatus.UNHEALTHY,
                is_available=False,
                error_message=str(e),
                last_checked=datetime.now(timezone.utc),
            )
    
    async def check_all_health(self) -> dict[ProviderType, ProviderHealth]:
        """Check health for all providers."""
        tasks = [
            self.check_health(pt)
            for pt in self._providers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for pt, result in zip(self._providers.keys(), results):
            if isinstance(result, Exception):
                self._health_status[pt] = ProviderHealth(
                    provider=pt,
                    status=ProviderStatus.UNHEALTHY,
                    is_available=False,
                    error_message=str(result),
                )
        
        return self._health_status


class ProviderFactory:
    """
    Factory for creating and managing providers.
    
    Handles provider creation, routing, and failover.
    """
    
    def __init__(self, registry: ProviderRegistry | None = None):
        self.registry = registry or ProviderRegistry()
        self._routing_config = RoutingConfig()
        self._provider_creator: dict[ProviderType, type] = {}
    
    def register_provider_type(
        self,
        provider_type: ProviderType,
        provider_class: type,
    ) -> None:
        """Register a provider class for a type."""
        self._provider_creator[provider_type] = provider_class
        logger.info(f"Provider type registered: {provider_type.value}")
    
    def create_from_config(self, config: ProviderConfig) -> BaseProvider | None:
        """Create a provider from configuration."""
        provider_class = self._provider_creator.get(config.provider_type)
        if not provider_class:
            logger.error(f"No provider class for type: {config.provider_type.value}")
            return None
        
        try:
            provider = provider_class(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout,
                max_retries=config.max_retries,
            )
            self.registry.register(config.provider_type, provider, config)
            return provider
        except Exception as e:
            logger.error(f"Failed to create provider: {e}")
            return None
    
    def set_routing_config(self, config: RoutingConfig) -> None:
        """Set routing configuration."""
        self._routing_config = config
    
    async def get_provider(
        self,
        preferred: list[ProviderType] | None = None,
    ) -> tuple[BaseProvider | None, ProviderType | None]:
        """Get the best available provider."""
        available = self.registry.get_available(preferred or self._routing_config.priority_providers)
        
        if not available:
            return None, None
        
        # If weighted routing is enabled
        if self._routing_config.weights:
            return self._weighted_selection(available)
        
        # Return highest priority available
        return self.registry.get(available[0]), available[0]
    
    def _weighted_selection(
        self,
        providers: list[ProviderType],
    ) -> tuple[BaseProvider | None, ProviderType | None]:
        """Select provider based on weights."""
        weights = {
            pt: self._routing_config.weights.get(pt, 1.0)
            for pt in providers
        }
        
        total_weight = sum(weights.values())
        import random
        r = random.random() * total_weight
        
        cumulative = 0
        for pt, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return self.registry.get(pt), pt
        
        return self.registry.get(providers[0]), providers[0]
    
    def set_provider_enabled(self, provider_type: ProviderType, enabled: bool) -> None:
        """Enable or disable a provider."""
        config = self.registry._configs.get(provider_type)
        if config:
            config.enabled = enabled
            logger.info(f"Provider {provider_type.value} {'enabled' if enabled else 'disabled'}")


# Global registry and factory
_registry: ProviderRegistry | None = None
_factory: ProviderFactory | None = None


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


def get_provider_factory() -> ProviderFactory:
    """Get the global provider factory."""
    global _factory
    if _factory is None:
        _factory = ProviderFactory(get_provider_registry())
    return _factory
