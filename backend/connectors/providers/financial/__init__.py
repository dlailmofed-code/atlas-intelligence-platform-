"""
ATLAS Platform - Financial Connectors

Financial data provider connectors.
"""

from backend.connectors.providers.financial.alpha_vantage import AlphaVantageConnector
from backend.connectors.providers.financial.base import (
    BaseFinancialConnector,
    CryptoQuote,
    EconomicIndicator,
    HistoricalData,
    StockQuote,
)
from backend.connectors.providers.financial.coingecko import CoinGeckoConnector
from backend.connectors.providers.financial.finnhub import FinnhubConnector
from backend.connectors.providers.financial.fred import FREDConnector
from backend.connectors.providers.financial.polygon import PolygonConnector

__all__ = [
    "BaseFinancialConnector",
    "StockQuote",
    "HistoricalData",
    "CryptoQuote",
    "EconomicIndicator",
    "AlphaVantageConnector",
    "CoinGeckoConnector",
    "FinnhubConnector",
    "FREDConnector",
    "PolygonConnector",
]
