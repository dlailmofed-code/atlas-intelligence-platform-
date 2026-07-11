"""
Tests for financial provider connectors.
"""

import pytest

from backend.connectors.base import ProviderType
from backend.connectors.providers.financial import (
    AlphaVantageConnector,
    CoinGeckoConnector,
    FinnhubConnector,
    FREDConnector,
    PolygonConnector,
)


class TestAlphaVantageConnector:
    """Tests for AlphaVantageConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create an AlphaVantageConnector instance."""
        return AlphaVantageConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "alpha_vantage"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.FINANCIAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "Alpha Vantage"
        assert info.provider_type == ProviderType.FINANCIAL
        assert "alphavantage" in info.docs_url
        assert info.requires_api_key is True
    
    @pytest.mark.asyncio
    async def test_fetch_quote(self, connector):
        """Test fetch_quote method."""
        response = await connector.fetch_quote("IBM")
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_fetch_historical(self, connector):
        """Test fetch_historical method."""
        response = await connector.fetch_historical("AAPL", interval="daily")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_symbols(self, connector):
        """Test search_symbols method."""
        response = await connector.search_symbols("Apple")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_forex_rate(self, connector):
        """Test fetch_forex_rate method."""
        response = await connector.fetch_forex_rate("EUR", "USD")
        assert response.success is True


class TestPolygonConnector:
    """Tests for PolygonConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a PolygonConnector instance."""
        return PolygonConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "polygon"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.FINANCIAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "Polygon"
        assert info.provider_type == ProviderType.FINANCIAL
        assert "polygon.io" in info.docs_url
    
    @pytest.mark.asyncio
    async def test_fetch_quote(self, connector):
        """Test fetch_quote method."""
        response = await connector.fetch_quote("AAPL")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_historical(self, connector):
        """Test fetch_historical method."""
        response = await connector.fetch_historical("MSFT", interval="day")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_symbols(self, connector):
        """Test search_symbols method."""
        response = await connector.search_symbols("Microsoft")
        assert response.success is True


class TestFinnhubConnector:
    """Tests for FinnhubConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a FinnhubConnector instance."""
        return FinnhubConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "finnhub"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.FINANCIAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "Finnhub"
        assert info.provider_type == ProviderType.FINANCIAL
        assert "finnhub" in info.docs_url
    
    @pytest.mark.asyncio
    async def test_fetch_quote(self, connector):
        """Test fetch_quote method."""
        response = await connector.fetch_quote("AAPL")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_historical(self, connector):
        """Test fetch_historical method."""
        response = await connector.fetch_historical("GOOGL", interval="D")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_symbols(self, connector):
        """Test search_symbols method."""
        response = await connector.search_symbols("Google")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_company_profile(self, connector):
        """Test fetch_company_profile method."""
        response = await connector.fetch_company_profile("AAPL")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_market_news(self, connector):
        """Test fetch_market_news method."""
        response = await connector.fetch_market_news(category="general")
        assert response.success is True


class TestCoinGeckoConnector:
    """Tests for CoinGeckoConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a CoinGeckoConnector instance."""
        return CoinGeckoConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "coingecko"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.FINANCIAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "CoinGecko"
        assert info.provider_type == ProviderType.FINANCIAL
        assert "coingecko" in info.docs_url
        assert info.requires_api_key is False
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_fetch_quote(self, connector):
        """Test fetch_quote method."""
        response = await connector.fetch_quote("bitcoin")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_historical(self, connector):
        """Test fetch_historical method."""
        response = await connector.fetch_historical("ethereum", interval="daily")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_symbols(self, connector):
        """Test search_symbols method."""
        response = await connector.search_symbols("Bitcoin")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_market_data(self, connector):
        """Test fetch_market_data method."""
        response = await connector.fetch_market_data(limit=10)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_trending(self, connector):
        """Test fetch_trending method."""
        response = await connector.fetch_trending()
        assert response.success is True


class TestFREDConnector:
    """Tests for FREDConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create an FREDConnector instance."""
        return FREDConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "fred"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.FINANCIAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "FRED"
        assert info.provider_type == ProviderType.FINANCIAL
        assert "stlouisfed" in info.docs_url
        assert info.requires_api_key is True
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_fetch_quote(self, connector):
        """Test fetch_quote method."""
        response = await connector.fetch_quote("GDP")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_historical(self, connector):
        """Test fetch_historical method."""
        response = await connector.fetch_historical("UNRATE")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_indicators(self, connector):
        """Test search_indicators method."""
        response = await connector.search_indicators("unemployment")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_fetch_releases(self, connector):
        """Test fetch_releases method."""
        response = await connector.fetch_releases()
        assert response.success is True
