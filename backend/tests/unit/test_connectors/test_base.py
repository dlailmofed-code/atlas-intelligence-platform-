"""
Tests for the base connector module.
"""


from backend.connectors.base import (
    ConnectorConfig,
    ConnectorHealth,
    ConnectorMetrics,
    ConnectorResponse,
    HealthStatus,
    ProviderInfo,
    ProviderType,
    RetryConfig,
)


class TestConnectorConfig:
    """Tests for ConnectorConfig."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = ConnectorConfig(provider_name="test")

        assert config.provider_name == "test"
        assert config.base_url is None
        assert config.api_key is None
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 0.5
        assert config.rate_limit_per_minute == 60
        assert config.rate_limit_per_day == 1000
        assert config.cache_ttl == 300
        assert config.validate_ssl is True

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = ConnectorConfig(
            provider_name="custom",
            base_url="https://api.example.com",
            api_key="test-key",
            timeout=60,
            max_retries=5,
            rate_limit_per_minute=100,
        )

        assert config.provider_name == "custom"
        assert config.base_url == "https://api.example.com"
        assert config.api_key == "test-key"
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.rate_limit_per_minute == 100


class TestConnectorMetrics:
    """Tests for ConnectorMetrics."""

    def test_metrics_defaults(self):
        """Test default metrics values."""
        metrics = ConnectorMetrics()

        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.rate_limit_hits == 0

    def test_success_rate_no_requests(self):
        """Test success rate with no requests."""
        metrics = ConnectorMetrics()

        assert metrics.success_rate == 0.0

    def test_success_rate_with_requests(self):
        """Test success rate calculation."""
        metrics = ConnectorMetrics()
        metrics.total_requests = 10
        metrics.successful_requests = 8
        metrics.failed_requests = 2

        assert metrics.success_rate == 0.8

    def test_average_response_time_no_requests(self):
        """Test average response time with no requests."""
        metrics = ConnectorMetrics()

        assert metrics.average_response_time_ms == 0.0

    def test_average_response_time_with_requests(self):
        """Test average response time calculation."""
        metrics = ConnectorMetrics()
        metrics.successful_requests = 2
        metrics.total_response_time_ms = 200.0

        assert metrics.average_response_time_ms == 100.0

    def test_cache_hit_rate_no_cache(self):
        """Test cache hit rate with no cache activity."""
        metrics = ConnectorMetrics()

        assert metrics.cache_hit_rate == 0.0

    def test_cache_hit_rate_with_activity(self):
        """Test cache hit rate calculation."""
        metrics = ConnectorMetrics()
        metrics.cache_hits = 8
        metrics.cache_misses = 2

        assert metrics.cache_hit_rate == 0.8


class TestConnectorHealth:
    """Tests for ConnectorHealth."""

    def test_health_defaults(self):
        """Test default health values."""
        health = ConnectorHealth()

        assert health.status == HealthStatus.UNKNOWN
        assert health.latency_ms is None
        assert health.last_check_at is None
        assert health.error_message is None
        assert health.consecutive_failures == 0
        assert health.is_available is True


class TestConnectorResponse:
    """Tests for ConnectorResponse."""

    def test_response_defaults(self):
        """Test default response values."""
        response = ConnectorResponse(data={"test": "data"})

        assert response.data == {"test": "data"}
        assert response.status_code == 200
        assert response.success is True
        assert response.error_message is None
        assert response.from_cache is False
        assert response.cached_at is None

    def test_response_rate_limited(self):
        """Test rate limited response check."""
        response = ConnectorResponse(
            data=None,
            status_code=429,
            success=False,
            error_message="Rate limited",
        )

        assert response.is_rate_limited is True

    def test_response_not_rate_limited(self):
        """Test non-rate limited response."""
        response = ConnectorResponse(
            data={"result": "ok"},
            status_code=200,
        )

        assert response.is_rate_limited is False


class TestProviderInfo:
    """Tests for ProviderInfo."""

    def test_provider_info_required_fields(self):
        """Test provider info with required fields only."""
        info = ProviderInfo(
            name="Test Provider",
            provider_type=ProviderType.NEWS,
            description="A test provider",
        )

        assert info.name == "Test Provider"
        assert info.provider_type == ProviderType.NEWS
        assert info.description == "A test provider"
        assert info.rate_limit_per_minute == 60
        assert info.rate_limit_per_day == 1000
        assert info.requires_api_key is True
        assert info.is_free_tier is False

    def test_provider_info_all_fields(self):
        """Test provider info with all fields."""
        info = ProviderInfo(
            name="Full Provider",
            provider_type=ProviderType.FINANCIAL,
            description="A full provider",
            docs_url="https://docs.example.com",
            rate_limit_per_minute=100,
            rate_limit_per_day=5000,
            requires_api_key=False,
            is_free_tier=True,
            supported_endpoints=["/search", "/quote"],
        )

        assert info.name == "Full Provider"
        assert info.docs_url == "https://docs.example.com"
        assert info.rate_limit_per_minute == 100
        assert info.requires_api_key is False
        assert info.is_free_tier is True
        assert len(info.supported_endpoints) == 2


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_retry_config_defaults(self):
        """Test default retry configuration."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.backoff_factor == 0.5
        assert config.max_backoff == 60.0
        assert 429 in config.retry_on_status
        assert 500 in config.retry_on_status

    def test_retry_config_custom(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=1.0,
            max_backoff=120.0,
            retry_on_status=(429, 500, 502),
        )

        assert config.max_retries == 5
        assert config.backoff_factor == 1.0
        assert config.max_backoff == 120.0
        assert 429 in config.retry_on_status
        assert 500 in config.retry_on_status
        assert 504 not in config.retry_on_status


class TestProviderType:
    """Tests for ProviderType enum."""

    def test_all_provider_types(self):
        """Test all provider type values."""
        assert ProviderType.NEWS.value == "news"
        assert ProviderType.FINANCIAL.value == "financial"
        assert ProviderType.GOVERNMENT.value == "government"
        assert ProviderType.SOCIAL.value == "social"
        assert ProviderType.ACADEMIC.value == "academic"
        assert ProviderType.SEARCH.value == "search"
        assert ProviderType.GOVERNMENT_LEGAL.value == "government_legal"
        assert ProviderType.COMPANY_DATA.value == "company_data"


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_all_health_statuses(self):
        """Test all health status values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"
