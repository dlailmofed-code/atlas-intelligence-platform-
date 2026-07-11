"""
Tests for government and legal provider connectors.
"""

import pytest

from backend.connectors.base import ProviderType
from backend.connectors.providers.government import (
    OpenCorporatesConnector,
    SECEdgarConnector,
    USPTOConnector,
)


class TestSECEdgarConnector:
    """Tests for SECEdgarConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create an SECEdgarConnector instance."""
        return SECEdgarConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "sec_edgar"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.GOVERNMENT_LEGAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "SEC EDGAR"
        assert info.provider_type == ProviderType.GOVERNMENT_LEGAL
        assert "sec.gov" in info.docs_url
        assert info.requires_api_key is False
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_search(self, connector):
        """Test search method."""
        response = await connector.search("Apple")
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_get_details(self, connector):
        """Test get_details method."""
        response = await connector.get_details("0000320193")  # Apple CIK
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_company_filings(self, connector):
        """Test get_company_filings method."""
        response = await connector.get_company_filings("0000320193")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_financial_reports(self, connector):
        """Test get_financial_reports method."""
        response = await connector.get_financial_reports("0000320193")
        assert response.success is True


class TestUSPTOConnector:
    """Tests for USPTOConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create a USPTOConnector instance."""
        return USPTOConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "uspto"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.GOVERNMENT_LEGAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "USPTO"
        assert info.provider_type == ProviderType.GOVERNMENT_LEGAL
        assert "uspto.gov" in info.docs_url
        assert info.requires_api_key is False
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_search(self, connector):
        """Test search method."""
        response = await connector.search("machine learning")
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_get_details(self, connector):
        """Test get_details method."""
        response = await connector.get_details("10123456")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_search_trademarks(self, connector):
        """Test search_trademarks method."""
        response = await connector.search_trademarks("Apple")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_patent_applications(self, connector):
        """Test get_patent_applications method."""
        response = await connector.get_patent_applications(limit=10)
        assert response.success is True


class TestOpenCorporatesConnector:
    """Tests for OpenCorporatesConnector."""
    
    @pytest.fixture
    def connector(self):
        """Create an OpenCorporatesConnector instance."""
        return OpenCorporatesConnector()
    
    def test_provider_name(self, connector):
        """Test provider name."""
        assert connector.provider_name == "opencorporates"
    
    def test_provider_type(self, connector):
        """Test provider type."""
        assert connector.provider_type == ProviderType.GOVERNMENT_LEGAL
    
    def test_provider_info(self, connector):
        """Test provider info."""
        info = connector.provider_info
        assert info.name == "OpenCorporates"
        assert info.provider_type == ProviderType.GOVERNMENT_LEGAL
        assert "opencorporates" in info.docs_url
        assert info.requires_api_key is True
        assert info.is_free_tier is True
    
    @pytest.mark.asyncio
    async def test_search(self, connector):
        """Test search method."""
        response = await connector.search("Apple Inc")
        assert response.success is True
        assert response.data["status"] == "placeholder"
    
    @pytest.mark.asyncio
    async def test_get_details(self, connector):
        """Test get_details method."""
        response = await connector.get_details("us_de/1234567")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_officers(self, connector):
        """Test get_officers method."""
        response = await connector.get_officers("us_de/1234567")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_filings(self, connector):
        """Test get_filings method."""
        response = await connector.get_filings("us_de/1234567")
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_network(self, connector):
        """Test get_network method."""
        response = await connector.get_network("us_de/1234567", depth=1)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_get_jurisdictions(self, connector):
        """Test get_jurisdictions method."""
        response = await connector.get_jurisdictions()
        assert response.success is True
