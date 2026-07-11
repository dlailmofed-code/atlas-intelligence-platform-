"""
ATLAS Platform - News Connectors

News data provider connectors.
"""

from backend.connectors.providers.news.base import BaseNewsConnector, NewsArticle
from backend.connectors.providers.news.gdelt import GDELTConnector
from backend.connectors.providers.news.google_news import GoogleNewsConnector
from backend.connectors.providers.news.newsapi import NewsAPIConnector
from backend.connectors.providers.news.serpapi import SerpAPIConnector
from backend.connectors.providers.news.tavily import TavilyConnector

__all__ = [
    "BaseNewsConnector",
    "NewsArticle",
    "GDELTConnector",
    "GoogleNewsConnector",
    "NewsAPIConnector",
    "SerpAPIConnector",
    "TavilyConnector",
]
