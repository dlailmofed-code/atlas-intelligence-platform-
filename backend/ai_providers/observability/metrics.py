"""
ATLAS Platform - AI Provider Observability

Metrics, tracing, and monitoring.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from backend.ai_providers.core.types import ProviderHealth, ProviderMetrics, ProviderType, ProviderStatus

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across all providers."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    average_latency_ms: float = 0.0
    by_provider: dict[str, ProviderMetrics] = field(default_factory=dict)
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TraceEvent:
    """A traced event."""
    
    id: str
    timestamp: datetime
    event_type: str
    provider: ProviderType | None
    model: str | None
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates AI provider metrics."""
    
    def __init__(self):
        self._provider_metrics: dict[ProviderType, ProviderMetrics] = {}
        self._model_metrics: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
        self._start_time = time.time()
    
    def record_request(
        self,
        provider: ProviderType,
        model: str,
        latency_ms: float,
        success: bool,
        error: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Record a request."""
        # Update provider metrics
        if provider not in self._provider_metrics:
            self._provider_metrics[provider] = ProviderMetrics(provider_name=provider.value)
        
        metrics = self._provider_metrics[provider]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
        
        if error and "rate limit" in error.lower():
            metrics.rate_limit_hits += 1
        
        metrics.total_prompt_tokens += prompt_tokens
        metrics.total_completion_tokens += completion_tokens
        metrics.total_cost += cost
        metrics.last_request_at = datetime.now(timezone.utc)
        
        if success:
            metrics.last_success_at = datetime.now(timezone.utc)
        else:
            metrics.last_failure_at = datetime.now(timezone.utc)
        
        # Update model metrics
        model_key = f"{provider.value}:{model}"
        self._model_metrics[model_key]["total_requests"] += 1
        self._model_metrics[model_key]["total_tokens"] += prompt_tokens + completion_tokens
        self._model_metrics[model_key]["total_cost"] += cost
    
    def get_provider_metrics(self, provider: ProviderType) -> ProviderMetrics | None:
        """Get metrics for a specific provider."""
        return self._provider_metrics.get(provider)
    
    def get_all_provider_metrics(self) -> dict[ProviderType, ProviderMetrics]:
        """Get metrics for all providers."""
        return dict(self._provider_metrics)
    
    def get_aggregated_metrics(self) -> AggregatedMetrics:
        """Get aggregated metrics across all providers."""
        total = AggregatedMetrics()
        
        for provider, metrics in self._provider_metrics.items():
            total.total_requests += metrics.total_requests
            total.successful_requests += metrics.successful_requests
            total.failed_requests += metrics.failed_requests
            total.total_cost += metrics.total_cost
            total.total_prompt_tokens += metrics.total_prompt_tokens
            total.total_completion_tokens += metrics.total_completion_tokens
            total.average_latency_ms += metrics.total_latency_ms
            total.by_provider[provider.value] = metrics
        
        if total.successful_requests > 0:
            total.average_latency_ms /= total.successful_requests
        
        total.by_model = dict(self._model_metrics)
        total.last_updated = datetime.now(timezone.utc)
        
        return total
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._provider_metrics.clear()
        self._model_metrics.clear()
        self._start_time = time.time()


class TraceCollector:
    """Collects traces for requests."""
    
    def __init__(self, max_traces: int = 10000):
        self.max_traces = max_traces
        self._traces: list[TraceEvent] = []
    
    def start_trace(
        self,
        trace_id: str,
        provider: ProviderType,
        model: str,
    ) -> TraceEvent:
        """Start a new trace."""
        event = TraceEvent(
            id=trace_id,
            timestamp=datetime.now(timezone.utc),
            event_type="request_start",
            provider=provider,
            model=model,
            duration_ms=0.0,
        )
        return event
    
    def end_trace(
        self,
        event: TraceEvent,
        duration_ms: float,
        success: bool,
        error: str | None = None,
    ) -> None:
        """End a trace."""
        event.event_type = "request_end"
        event.duration_ms = duration_ms
        event.metadata["success"] = success
        if error:
            event.metadata["error"] = error
        
        self._traces.append(event)
        
        # Trim if needed
        if len(self._traces) > self.max_traces:
            self._traces = self._traces[-self.max_traces:]
    
    def get_traces(
        self,
        limit: int = 100,
        provider: ProviderType | None = None,
    ) -> list[TraceEvent]:
        """Get recent traces."""
        traces = self._traces
        
        if provider:
            traces = [t for t in traces if t.provider == provider]
        
        return traces[-limit:]


class HealthMonitor:
    """Monitors provider health."""
    
    def __init__(self):
        self._health_status: dict[ProviderType, ProviderHealth] = {}
        self._last_check: dict[ProviderType, datetime] = {}
    
    def update_health(
        self,
        provider: ProviderType,
        status: ProviderHealth,
    ) -> None:
        """Update health status for a provider."""
        self._health_status[provider] = status
        self._last_check[provider] = datetime.now(timezone.utc)
    
    def get_health(self, provider: ProviderType) -> ProviderHealth | None:
        """Get health status for a provider."""
        return self._health_status.get(provider)
    
    def get_all_health(self) -> dict[ProviderType, ProviderHealth]:
        """Get health status for all providers."""
        return dict(self._health_status)
    
    def is_provider_available(self, provider: ProviderType) -> bool:
        """Check if a provider is available."""
        health = self._health_status.get(provider)
        if not health:
            return True  # Unknown = available
        return health.is_available


class AIObserver:
    """Main observability component."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.traces = TraceCollector()
        self.health = HealthMonitor()
    
    def record(
        self,
        provider: ProviderType,
        model: str,
        latency_ms: float,
        success: bool,
        error: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Record a request."""
        self.metrics.record_request(
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            success=success,
            error=error,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )
    
    def get_dashboard_data(self) -> dict[str, Any]:
        """Get dashboard data."""
        aggregated = self.metrics.get_aggregated_metrics()
        health = self.health.get_all_health()
        
        return {
            "summary": {
                "total_requests": aggregated.total_requests,
                "success_rate": (
                    aggregated.successful_requests / aggregated.total_requests
                    if aggregated.total_requests > 0 else 0
                ),
                "total_cost": aggregated.total_cost,
                "average_latency_ms": aggregated.average_latency_ms,
            },
            "providers": {
                provider.value: {
                    "status": h.status.value,
                    "latency_ms": h.latency_ms,
                    "success_rate": h.success_rate,
                    "is_available": h.is_available,
                }
                for provider, h in health.items()
            },
            "by_provider": {
                name: {
                    "total_requests": m.total_requests,
                    "successful_requests": m.successful_requests,
                    "failed_requests": m.failed_requests,
                    "success_rate": m.success_rate,
                    "average_latency_ms": m.average_latency_ms,
                    "total_cost": m.total_cost,
                }
                for name, m in aggregated.by_provider.items()
            },
            "by_model": aggregated.by_model,
        }


# Global observer instance
_observer: AIObserver | None = None


def get_ai_observer() -> AIObserver:
    """Get the global AI observer."""
    global _observer
    if _observer is None:
        _observer = AIObserver()
    return _observer
