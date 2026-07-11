"""
ATLAS Platform - Connector Providers

Provider-specific connector implementations.
"""

from backend.connectors.providers.financial import (
    AlphaVantageConnector,
    CoinGeckoConnector,
    FinnhubConnector,
    FREDConnector,
    PolygonConnector,
)
from backend.connectors.providers.government import (
    OpenCorporatesConnector,
    SECEdgarConnector,
    USPTOConnector,
)
from backend.connectors.providers.news import (
    GDELTConnector,
    GoogleNewsConnector,
    NewsAPIConnector,
    SerpAPIConnector,
    TavilyConnector,
)

# All available connectors
ALL_CONNECTORS = {
    # News
    "google_news": GoogleNewsConnector,
    "newsapi": NewsAPIConnector,
    "gdelt": GDELTConnector,
    "tavily": TavilyConnector,
    "serpapi": SerpAPIConnector,
    # Financial
    "alpha_vantage": AlphaVantageConnector,
    "polygon": PolygonConnector,
    "finnhub": FinnhubConnector,
    "coingecko": CoinGeckoConnector,
    "fred": FREDConnector,
    # Government/Legal
    "sec_edgar": SECEdgarConnector,
    "uspto": USPTOConnector,
    "opencorporates": OpenCorporatesConnector,
}


def get_connector(name: str):
    """Get a connector class by name."""
    return ALL_CONNECTORS.get(name)


def get_all_connector_names() -> list[str]:
    """Get list of all available connector names."""
    return list(ALL_CONNECTORS.keys())


def get_connectors_by_type(provider_type: str) -> list:
    """Get connectors by provider type."""
    from backend.connectors.base.types import ProviderType

    result = []
    for connector in ALL_CONNECTORS.values():
        # Create temporary instance to check type
        # In production, these would be singletons
        instance = connector()
        if instance.provider_type.value == provider_type:
            result.append(connector)

    return result


__all__ = [
    # News
    "GoogleNewsConnector",
    "NewsAPIConnector",
    "GDELTConnector",
    "TavilyConnector",
    "SerpAPIConnector",
    # Financial
    "AlphaVantageConnector",
    "PolygonConnector",
    "FinnhubConnector",
    "CoinGeckoConnector",
    "FREDConnector",
    # Government/Legal
    "SECEdgarConnector",
    "USPTOConnector",
    "OpenCorporatesConnector",
    # Utilities
    "ALL_CONNECTORS",
    "get_connector",
    "get_all_connector_names",
    "get_connectors_by_type",
]
