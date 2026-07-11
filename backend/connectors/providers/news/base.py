"""
ATLAS Platform - News Connector Base

Base class for news data providers.
"""

from typing import Any

from pydantic import BaseModel

from backend.connectors.base import BaseConnector, ConnectorConfig, ProviderInfo, ProviderType
from backend.connectors.base.types import ConnectorResponse


class NewsArticle(BaseModel):
    """Schema for a news article."""
    
    title: str
    description: str | None = None
    content: str | None = None
    url: str
    source: str | None = None
    author: str | None = None
    published_at: str | None = None
    image_url: str | None = None


class BaseNewsConnector(BaseConnector):
    """
    Base connector for news data providers.
    
    Provides common functionality for news connectors.
    """
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.NEWS
    
    async def fetch_news(
        self,
        query: str | None = None,
        keywords: list[str] | None = None,
        limit: int = 10,
        **kwargs: Any,
    ) -> ConnectorResponse:
        """
        Fetch news articles.
        
        Args:
            query: Search query
            keywords: List of keywords
            limit: Maximum number of results
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ConnectorResponse with list of NewsArticle
        """
        raise NotImplementedError
    
    async def fetch_by_source(
        self,
        source: str,
        limit: int = 10,
    ) -> ConnectorResponse:
        """
        Fetch news from a specific source.
        
        Args:
            source: Source identifier
            limit: Maximum number of results
            
        Returns:
            ConnectorResponse with list of NewsArticle
        """
        raise NotImplementedError
    
    async def fetch_headlines(
        self,
        country: str = "us",
        category: str | None = None,
        limit: int = 10,
    ) -> ConnectorResponse:
        """
        Fetch headlines.
        
        Args:
            country: Country code
            category: News category
            limit: Maximum number of results
            
        Returns:
            ConnectorResponse with list of NewsArticle
        """
        raise NotImplementedError
