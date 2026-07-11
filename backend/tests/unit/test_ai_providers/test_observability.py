"""
Tests for AI provider observability.
"""

import pytest

from backend.ai_providers.core.types import ProviderType
from backend.ai_providers.observability import (
    AIObserver,
    HealthMonitor,
    MetricsCollector,
    TraceCollector,
    TraceEvent,
)


class TestMetricsCollector:
    """Tests for MetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        return MetricsCollector()
    
    def test_record_success(self, collector):
        """Test recording successful request."""
        collector.record_request(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=True,
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.01,
        )
        
        metrics = collector.get_provider_metrics(ProviderType.OPENAI)
        assert metrics is not None
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
    
    def test_record_failure(self, collector):
        """Test recording failed request."""
        collector.record_request(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=False,
            error="Timeout",
        )
        
        metrics = collector.get_provider_metrics(ProviderType.OPENAI)
        assert metrics.failed_requests == 1
    
    def test_record_rate_limit(self, collector):
        """Test recording rate limit."""
        collector.record_request(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=100,
            success=False,
            error="Rate limit exceeded",
        )
        
        metrics = collector.get_provider_metrics(ProviderType.OPENAI)
        assert metrics.rate_limit_hits == 1
    
    def test_aggregated_metrics(self, collector):
        """Test aggregated metrics."""
        collector.record_request(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=True,
            cost=0.01,
        )
        collector.record_request(
            provider=ProviderType.ANTHROPIC,
            model="claude-3",
            latency_ms=2000,
            success=True,
            cost=0.02,
        )
        
        aggregated = collector.get_aggregated_metrics()
        
        assert aggregated.total_requests == 2
        assert aggregated.successful_requests == 2
        assert aggregated.total_cost == 0.03
    
    def test_reset(self, collector):
        """Test resetting metrics."""
        collector.record_request(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=True,
        )
        
        collector.reset()
        
        metrics = collector.get_provider_metrics(ProviderType.OPENAI)
        assert metrics is None or metrics.total_requests == 0


class TestTraceCollector:
    """Tests for TraceCollector."""
    
    @pytest.fixture
    def collector(self):
        return TraceCollector(max_traces=10)
    
    def test_start_trace(self, collector):
        """Test starting a trace."""
        event = collector.start_trace(
            trace_id="test-123",
            provider=ProviderType.OPENAI,
            model="gpt-4",
        )
        
        assert event.id == "test-123"
        assert event.event_type == "request_start"
    
    def test_end_trace(self, collector):
        """Test ending a trace."""
        event = collector.start_trace(
            trace_id="test-456",
            provider=ProviderType.OPENAI,
            model="gpt-4",
        )
        
        collector.end_trace(event, duration_ms=1000, success=True)
        
        assert event.event_type == "request_end"
        assert event.duration_ms == 1000
        assert event.metadata["success"] is True
    
    def test_get_traces(self, collector):
        """Test getting traces."""
        for i in range(5):
            event = collector.start_trace(
                trace_id=f"trace-{i}",
                provider=ProviderType.OPENAI,
                model="gpt-4",
            )
            collector.end_trace(event, duration_ms=100, success=True)
        
        traces = collector.get_traces(limit=3)
        assert len(traces) == 3


class TestHealthMonitor:
    """Tests for HealthMonitor."""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_update_health(self, monitor):
        """Test updating health status."""
        from backend.ai_providers.core.types import ProviderHealth, ProviderStatus
        
        health = ProviderHealth(
            provider=ProviderType.OPENAI,
            status=ProviderStatus.HEALTHY,
            latency_ms=100,
            success_rate=0.99,
            is_available=True,
        )
        
        monitor.update_health(ProviderType.OPENAI, health)
        
        result = monitor.get_health(ProviderType.OPENAI)
        assert result is not None
        assert result.status == ProviderStatus.HEALTHY
    
    def test_is_provider_available(self, monitor):
        """Test checking provider availability."""
        from backend.ai_providers.core.types import ProviderHealth, ProviderStatus
        
        # Unknown provider should be available
        assert monitor.is_provider_available(ProviderType.OPENAI) is True
        
        # Update to unhealthy
        health = ProviderHealth(
            provider=ProviderType.OPENAI,
            status=ProviderStatus.UNHEALTHY,
            is_available=False,
        )
        monitor.update_health(ProviderType.OPENAI, health)
        
        assert monitor.is_provider_available(ProviderType.OPENAI) is False


class TestAIObserver:
    """Tests for main AIObserver."""
    
    @pytest.fixture
    def observer(self):
        return AIObserver()
    
    def test_record(self, observer):
        """Test recording a request."""
        observer.record(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=True,
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.01,
        )
        
        metrics = observer.metrics.get_provider_metrics(ProviderType.OPENAI)
        assert metrics.total_requests == 1
    
    def test_get_dashboard_data(self, observer):
        """Test getting dashboard data."""
        observer.record(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            latency_ms=1000,
            success=True,
        )
        
        data = observer.get_dashboard_data()
        
        assert "summary" in data
        assert "providers" in data
        assert data["summary"]["total_requests"] == 1
