"""
ATLAS Platform - Government Connector Base

Base class for government and legal data providers.
"""

from typing import Any

from pydantic import BaseModel

from backend.connectors.base import BaseConnector, ProviderType
from backend.connectors.base.types import ConnectorResponse


class SECFiling(BaseModel):
    """Schema for an SEC filing."""

    accession_number: str | None = None
    filing_date: str | None = None
    company_name: str | None = None
    form_type: str | None = None
    description: str | None = None
    document_url: str | None = None


class PatentInfo(BaseModel):
    """Schema for a patent."""

    patent_number: str | None = None
    title: str | None = None
    abstract: str | None = None
    inventor: str | None = None
    assignee: str | None = None
    filing_date: str | None = None
    issue_date: str | None = None


class CompanyInfo(BaseModel):
    """Schema for company registration information."""

    company_number: str | None = None
    name: str | None = None
    jurisdiction: str | None = None
    status: str | None = None
    incorporation_date: str | None = None
    address: str | None = None
    officers: list[dict] | None = None


class BaseGovernmentConnector(BaseConnector):
    """
    Base connector for government and legal data providers.
    
    Provides common functionality for government/legal connectors.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOVERNMENT_LEGAL

    async def search(self, query: str, **kwargs: Any) -> ConnectorResponse:
        """
        Search for records.
        
        Args:
            query: Search query
            **kwargs: Additional parameters
            
        Returns:
            ConnectorResponse with search results
        """
        raise NotImplementedError

    async def get_details(self, identifier: str) -> ConnectorResponse:
        """
        Get details for a specific record.
        
        Args:
            identifier: Record identifier
            
        Returns:
            ConnectorResponse with record details
        """
        raise NotImplementedError
