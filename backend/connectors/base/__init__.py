"""
ATLAS Platform - Connector Base Module

This module provides the base connector framework for all external data providers.
"""

from backend.connectors.base.connector import BaseConnector, RetryConfig
from backend.connectors.base.registry import ConnectorRegistry, get_registry
from backend.connectors.base.types import (
    ConnectionStatus,
    ConnectorConfig,
    ConnectorHealth,
    ConnectorMetrics,
    ConnectorResponse,
    HealthStatus,
    ProviderInfo,
    ProviderType,
)

__all__ = [
    # Base connector
    "BaseConnector",
    "RetryConfig",
    # Registry
    "ConnectorRegistry",
    "get_registry",
    # Types
    "ConnectorConfig",
    "ConnectorHealth",
    "ConnectorMetrics",
    "ConnectorResponse",
    "ConnectionStatus",
    "HealthStatus",
    "ProviderInfo",
    "ProviderType",
]
