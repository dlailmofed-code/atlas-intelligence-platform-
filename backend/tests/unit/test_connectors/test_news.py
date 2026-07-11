"""
Tests for news provider connectors.
"""

import pytest

from backend.connectors.base import ConnectorConfig, ProviderType
from backend.connectors.providers.news import (
    BaseNewsConnector,
    GDELTConnector,
    GoogleNewsConnector,
    NewsAPIConnector,
    SerpAPIConnector,
    TavilyConnector,
)


class TestGoogleNewsConnector:
    """Tests for GoogleNewsConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a GoogleNewsConnector instance."""
        return GoogleNewsConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "google_news"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.NEWS
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "Google News"
        assert info.provider_type == ProviderType.NEWS
        assert "news" in info.description.lower()
        assert info.requires_api_key is True
        assert info.is_free_tier is False
    
    def test_config_from_env(self):
        """Test configuration from environment."""
        config = ConnectorConfig.from_env("GOOGLE_NEWS_")
        # The provider name is derived from the prefix (uppercase, stripped)
        assert config.provider_name == "GOOGLE_NEWS"
    
    @pytest.mark.asyncio
    async def test_fetch_returns_placeholder(self, connector):
        """Test that fetch returns placeholder response."""
        response = await connector.fetch("/search", {"q": "test"})
        assert response.success is True
        assert response.data["status"] == "placeholder"
        assert "Google News" in response.data["message"]
    
    @pytest.mark.asyncio
    async def test_fetch_news(self, connector):
        """Test fetch_news method."""
        response = await connector.fetch_news(query="AI startups", limit=10)
        assert response.success is True
        assert "params_received" in response.data
    
    @pytest.mark.asyncio
    async def test_fetch_headlines(self, connector):
        """Test fetch_headlines method."""
        response = await connector.fetch_headlines(country="us", limit=5)
        assert response.success is True


class TestNewsAPIConnector:
    """Tests for NewsAPIConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a NewsAPIConnector instance."""
        return NewsAPIConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "newsapi"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.NEWS
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "NewsAPI"
        assert info.provider_type == ProviderType.NEWS
        assert "newsapi" in info.docs_url
    
    @pytest.mark.asyncio
    async def test_fetch_returns_placeholder(self, connector):
        """Test that fetch returns placeholder response."""
        response = await connector.fetch("/top-headlines", {"country": "us"})
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_fetch_news(self, connector):
        """Test fetch_news method."""
        response = await connector.fetch_news(query="technology", limit=20)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_sources(self, connector):
        """Test get_sources method."""
        response = await connector.get_sources(category="technology")
        assert response.success is True


class TestGDELTConnector:
    """Tests for GDELTConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a GDELTConnector instance."""
        return GDELTConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "gdelt"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.NEWS
    
    def test_provider_info(self):
        """Test provider info."""
        connector = GDELTConnector()
        info = connector.provider_info
        assert info.name == "GDELT"
        assert info.requires_api_key is False
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_fetch_returns_placeholder(self, connector):
        """Test that fetch returns placeholder response."""
        response = await connector.fetch("/articles/articles", {"query": "climate"})
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_fetch_news(self, connector):
        """Test fetch_news method."""
        response = await connector.fetch_news(query="climate change", limit=5)
        assert response.success is True


class TestTavilyConnector:
    """Tests for TavilyConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a TavilyConnector instance."""
        return TavilyConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "tavily"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.NEWS
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "Tavily"
        assert info.requires_api_key is True
    
    @pytest.mark.asyncio
    async def test_fetch_returns_placeholder(self, connector):
        """Test that fetch returns placeholder response."""
        response = await connector.fetch("/search", {"query": "AI"})
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_fetch_news(self, connector):
        """Test fetch_news method."""
        response = await connector.fetch_news(query="machine learning", limit=10)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_deep_research(self, connector):
        """Test deep_research method."""
        response = await connector.deep_research(
            query="future of AI in healthcare",
            depth="basic"
        )
        assert response.success is True


class TestSerpAPIConnector:
    """Tests for SerpAPIConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a SerpAPIConnector instance."""
        return SerpAPIConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "serpapi"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        # SerpAPI can be used for news searches
        assert connector.provider_type == ProviderType.NEWS
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "SerpAPI"
        assert info.provider_type == ProviderType.SEARCH
    
    @pytest.mark.asyncio
    async def test_fetch_returns_placeholder(self, connector):
        """Test that fetch returns placeholder response."""
        response = await connector.fetch("/search", {"q": "test"})
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_search(self, connector):
        """Test search method."""
        response = await connector.search(query="artificial intelligence", engine="google")
        assert response.success is True
