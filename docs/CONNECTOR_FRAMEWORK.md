# ATLAS Platform - Connector Framework

## Overview

The Connector Framework provides a unified, extensible interface for connecting to external data providers. It implements industry best practices for reliability, observability, and maintainability.

## Features

- **Provider Abstraction Layer**: Common base class for all connectors
- **Configuration Management**: Environment-based configuration with sensible defaults
- **Automatic Retry**: Exponential backoff with configurable retry policies
- **Timeout Handling**: Request timeout management with graceful failure
- **Structured Logging**: Comprehensive logging with context
- **Response Validation**: Pydantic-based schema validation
- **Caching Support**: In-memory response caching with TTL
- **Rate Limiting**: Per-provider rate limit enforcement
- **Health Checks**: Provider availability monitoring
- **Metrics Collection**: Request/response performance metrics

## Architecture

```
backend/
├── connectors/
│   ├── base/
│   │   ├── connector.py      # Base connector class
│   │   ├── registry.py       # Connector registry
│   │   ├── types.py          # Type definitions
│   │   └── __init__.py
│   ├── providers/
│   │   ├── news/             # News connectors
│   │   ├── financial/        # Financial data connectors
│   │   └── government/       # Government/legal connectors
│   └── utils/
│       └── helpers.py         # Utility functions
│   └── __init__.py
```

## Available Providers

### News Providers

| Provider | Description | API Key Required |
|----------|-------------|------------------|
| Google News | Real-time news from Google News (via SerpAPI) | Yes |
| NewsAPI | News from thousands of sources | Yes |
| GDELT | Global Database of Events, Language, and Tone | No |
| Tavily | AI-powered search and news API | Yes |
| SerpAPI | General search engine results API | Yes |

### Financial Providers

| Provider | Description | API Key Required |
|----------|-------------|------------------|
| Alpha Vantage | Real-time and historical stock data | Yes |
| Polygon | Real-time and historical stock data | Yes |
| Finnhub | Real-time quotes and company data | Yes |
| CoinGecko | Cryptocurrency price data | No (optional) |
| FRED | Federal Reserve Economic Data | Yes |

### Government & Legal Providers

| Provider | Description | API Key Required |
|----------|-------------|------------------|
| SEC EDGAR | Company filings database | No |
| USPTO | Patent and trademark data | No |
| OpenCorporates | Global company registration data | Yes |

## Usage

### Basic Usage

```python
from backend.connectors import get_connector

# Get a specific connector
connector = get_connector("newsapi")()

# Fetch news
response = await connector.fetch_news(query="AI startups")

if response.success:
    articles = response.data
else:
    print(f"Error: {response.error_message}")
```

### Working with Multiple Connectors

```python
from backend.connectors import get_registry

registry = get_registry()

# Register connectors
from backend.connectors.providers.news import NewsAPIConnector, GDELTConnector
registry.register("newsapi", NewsAPIConnector())
registry.register("gdelt", GDELTConnector())

# Get connector stats
stats = registry.get_all_stats()

# Health check all connectors
health_status = await registry.health_check_all()
```

### Custom Connector Configuration

```python
from backend.connectors import ConnectorConfig, AlphaVantageConnector

# Create custom config
config = ConnectorConfig(
    provider_name="alpha_vantage",
    base_url="https://www.alphavantage.co/query",
    api_key="your-api-key",
    timeout=60,
    max_retries=5,
    rate_limit_per_minute=10,
)

connector = AlphaVantageConnector(config)
```

## Configuration

### Environment Variables

All connectors can be configured using environment variables with the following naming convention:

```
{PROVIDER}_{SETTING}
```

Example for Alpha Vantage:
```
ALPHA_VANTAGE_API_KEY=your-api-key
ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co/query
ALPHA_VANTAGE_TIMEOUT=30
ALPHA_VANTAGE_MAX_RETRIES=3
ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE=5
ALPHA_VANTAGE_RATE_LIMIT_PER_DAY=500
```

### Available Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `{PROVIDER}_API_KEY` | None | API key for authentication |
| `{PROVIDER}_BASE_URL` | Provider default | Base URL for API |
| `{PROVIDER}_TIMEOUT` | 30 | Request timeout in seconds |
| `{PROVIDER}_MAX_RETRIES` | 3 | Maximum retry attempts |
| `{PROVIDER}_RATE_LIMIT_PER_MINUTE` | 60 | Requests allowed per minute |
| `{PROVIDER}_RATE_LIMIT_PER_DAY` | 1000 | Requests allowed per day |

## Retry Policy

The framework implements automatic retry with exponential backoff:

```python
from backend.connectors import RetryConfig

config = RetryConfig(
    max_retries=3,              # Maximum retry attempts
    backoff_factor=0.5,         # Base backoff multiplier
    max_backoff=60.0,           # Maximum backoff time in seconds
    retry_on_status=(429, 500, 502, 503, 504),  # Status codes to retry
)
```

## Caching

Responses are cached in-memory with configurable TTL:

```python
# In-memory caching is automatic
# Configure TTL via environment
CACHE_TTL_SHORT=300       # 5 minutes
CACHE_TTL_MEDIUM=3600      # 1 hour
```

## Health Checks

```python
from backend.connectors import HealthStatus

# Check connector health
health = await connector.health_check()

if health.status == HealthStatus.HEALTHY:
    print(f"Latency: {health.latency_ms}ms")
elif health.status == HealthStatus.DEGRADED:
    print("Service degraded")
else:
    print(f"Error: {health.error_message}")
```

## Metrics

```python
# Get connector metrics
stats = connector.get_stats()

print(f"Total requests: {stats['metrics']['total_requests']}")
print(f"Success rate: {stats['metrics']['success_rate']:.2%}")
print(f"Cache hit rate: {stats['metrics']['cache_hit_rate']:.2%}")
print(f"Avg response time: {stats['metrics']['average_response_time_ms']:.2f}ms")
```

## Provider-Specific Examples

### NewsAPI

```python
from backend.connectors.providers.news import NewsAPIConnector

connector = NewsAPIConnector()

# Get headlines
response = await connector.fetch_headlines(
    country="us",
    category="technology",
    limit=10
)

# Search news
response = await connector.fetch_news(
    query="artificial intelligence",
    limit=20
)

# Get available sources
response = await connector.get_sources(category="business")
```

### CoinGecko

```python
from backend.connectors.providers.financial import CoinGeckoConnector

connector = CoinGeckoConnector()

# Get crypto price
response = await connector.fetch_quote("bitcoin")

# Get market data
response = await connector.fetch_market_data(limit=100)

# Get trending
response = await connector.fetch_trending()
```

### SEC EDGAR

```python
from backend.connectors.providers.government import SECEdgarConnector

connector = SECEdgarConnector()

# Search for company
response = await connector.search("Apple Inc")

# Get company filings
response = await connector.get_company_filings(
    cik="0000320193",
    form_type="10-K"
)
```

## Testing

Run the connector tests:

```bash
cd backend
pytest tests/unit/test_connectors/ -v
```

## Extending the Framework

To create a new connector:

1. Inherit from `BaseConnector`:

```python
from backend.connectors.base import BaseConnector, ConnectorConfig, ProviderInfo, ProviderType

class MyConnector(BaseConnector):
    @property
    def provider_name(self) -> str:
        return "my_connector"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.NEWS
    
    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="My Connector",
            provider_type=self.provider_type,
            description="My custom connector",
            requires_api_key=True,
        )
    
    async def fetch(self, endpoint, params=None, schema=None):
        # Implement fetch logic
        pass
```

2. Register the connector:

```python
from backend.connectors import get_registry

registry = get_registry()
registry.register("my_connector", MyConnector())
```

## Best Practices

1. **Always handle errors**: Check `response.success` before using data
2. **Use appropriate timeouts**: Set timeouts based on expected API response time
3. **Implement caching**: Use caching for frequently accessed data
4. **Monitor health**: Regularly check connector health status
5. **Log appropriately**: Use structured logging for debugging
6. **Respect rate limits**: Configure rate limits based on API tier
7. **Use connection pooling**: Reuse HTTP clients where possible

## License

This is part of the ATLAS Platform and is licensed under the MIT License.
