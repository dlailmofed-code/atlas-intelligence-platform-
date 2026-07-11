"""
ATLAS Platform - Connector Registry

Registry for managing all connector instances.
"""

from typing import Any

from backend.connectors.base.connector import BaseConnector
from backend.connectors.base.types import HealthStatus, ProviderType
from backend.core.logging import get_logger

logger = get_logger(__name__)


class ConnectorRegistry:
    """
    Registry for managing connector instances.
    
    Provides singleton access to all configured connectors.
    """
    
    _instance: "ConnectorRegistry | None" = None
    _connectors: dict[str, BaseConnector] = {}
    
    def __new__(cls) -> "ConnectorRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connectors = {}
        return cls._instance
    
    def register(self, name: str, connector: BaseConnector) -> None:
        """Register a connector."""
        self._connectors[name] = connector
        logger.info(
            "Registered connector",
            extra={"connector_name": name, "provider": connector.provider_name}
        )
    
    def unregister(self, name: str) -> None:
        """Unregister a connector."""
        if name in self._connectors:
            connector = self._connectors.pop(name)
            logger.info(
                "Unregistered connector",
                extra={"connector_name": name}
            )
    
    def get(self, name: str) -> BaseConnector | None:
        """Get a registered connector."""
        return self._connectors.get(name)
    
    def get_all(self) -> dict[str, BaseConnector]:
        """Get all registered connectors."""
        return dict(self._connectors)
    
    def get_by_type(self, provider_type: ProviderType) -> list[BaseConnector]:
        """Get all connectors of a specific type."""
        return [
            c for c in self._connectors.values()
            if c.provider_type == provider_type
        ]
    
    def get_healthy(self) -> dict[str, BaseConnector]:
        """Get all healthy connectors."""
        return {
            name: c for name, c in self._connectors.items()
            if c.health.status == HealthStatus.HEALTHY
        }
    
    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics for all connectors."""
        return {
            name: connector.get_stats()
            for name, connector in self._connectors.items()
        }
    
    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Perform health check on all connectors."""
        results = {}
        for name, connector in self._connectors.items():
            try:
                health = await connector.health_check()
                results[name] = {
                    "status": health.status.value,
                    "latency_ms": health.latency_ms,
                    "is_available": health.is_available,
                    "error": health.error_message,
                }
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(e),
                }
        return results
    
    async def close_all(self) -> None:
        """Close all registered connectors."""
        for name, connector in self._connectors.items():
            try:
                await connector.close()
            except Exception as e:
                logger.error(
                    "Error closing connector",
                    extra={"connector_name": name, "error": str(e)}
                )
        logger.info("Closed all connectors")


# Global registry instance
registry = ConnectorRegistry()


def get_registry() -> ConnectorRegistry:
    """Get the global connector registry."""
    return registry
