"""
ATLAS Platform - Financial Connector Base

Base class for financial data providers.
"""

from datetime import datetime

from pydantic import BaseModel

from backend.connectors.base import BaseConnector, ProviderType
from backend.connectors.base.types import ConnectorResponse


class StockQuote(BaseModel):
    """Schema for a stock quote."""

    symbol: str
    price: float | None = None
    change: float | None = None
    change_percent: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: int | None = None
    timestamp: datetime | None = None


class HistoricalData(BaseModel):
    """Schema for historical price data."""

    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    adjusted_close: float | None = None
    volume: int | None = None


class CryptoQuote(BaseModel):
    """Schema for a cryptocurrency quote."""

    symbol: str
    price: float | None = None
    change_24h: float | None = None
    change_percent_24h: float | None = None
    market_cap: float | None = None
    volume_24h: float | None = None
    timestamp: datetime | None = None


class EconomicIndicator(BaseModel):
    """Schema for an economic indicator."""

    indicator_code: str
    value: float | None = None
    date: str | None = None
    unit: str | None = None
    country: str | None = None


class BaseFinancialConnector(BaseConnector):
    """
    Base connector for financial data providers.
    
    Provides common functionality for financial connectors.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.FINANCIAL

    async def fetch_quote(self, symbol: str) -> ConnectorResponse:
        """
        Fetch real-time quote for a symbol.
        
        Args:
            symbol: Stock/crypto symbol (e.g., "AAPL", "BTC")
            
        Returns:
            ConnectorResponse with quote data
        """
        raise NotImplementedError

    async def fetch_historical(
        self,
        symbol: str,
        interval: str = "daily",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> ConnectorResponse:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock/crypto symbol
            interval: Data interval (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            ConnectorResponse with historical data
        """
        raise NotImplementedError

    async def search_symbols(self, query: str) -> ConnectorResponse:
        """
        Search for symbols.
        
        Args:
            query: Search query
            
        Returns:
            ConnectorResponse with matching symbols
        """
        raise NotImplementedError
