"""
ATLAS Platform - Connectors Module

This module provides a unified interface for connecting to external data providers.
It includes connectors for news, financial data, and government/legal data sources.

Example usage:
    from backend.connectors import get_connector, ALL_CONNECTORS
    
    # Get a specific connector
    connector = get_connector("newsapi")()
    
    # Fetch news
    response = await connector.fetch_news(query="AI startups")
    
    # Get connector stats
    stats = connector.get_stats()
"""

from backend.connectors.base import (
    BaseConnector,
    ConnectorConfig,
    ConnectorHealth,
    ConnectorMetrics,
    ConnectorRegistry,
    ConnectorResponse,
    HealthStatus,
    ProviderInfo,
    ProviderType,
    RetryConfig,
    get_registry,
)
from backend.connectors.providers import (
    ALL_CONNECTORS,
    get_all_connector_names,
    get_connector,
    get_connectors_by_type,
)

__all__ = [
    # Base
    "BaseConnector",
    "ConnectorConfig",
    "ConnectorHealth",
    "ConnectorMetrics",
    "ConnectorRegistry",
    "ConnectorResponse",
    "HealthStatus",
    "ProviderInfo",
    "ProviderType",
    "RetryConfig",
    "get_registry",
    # Providers
    "get_connector",
    "get_all_connector_names",
    "get_connectors_by_type",
    "ALL_CONNECTORS",
]
