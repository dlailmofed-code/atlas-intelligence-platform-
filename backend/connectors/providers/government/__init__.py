"""
ATLAS Platform - Government and Legal Connectors

Government and legal data provider connectors.
"""

from backend.connectors.providers.government.base import (
    BaseGovernmentConnector,
    CompanyInfo,
    PatentInfo,
    SECFiling,
)
from backend.connectors.providers.government.opencorporates import OpenCorporatesConnector
from backend.connectors.providers.government.sec_edgar import SECEdgarConnector
from backend.connectors.providers.government.uspto import USPTOConnector

__all__ = [
    "BaseGovernmentConnector",
    "SECFiling",
    "PatentInfo",
    "CompanyInfo",
    "SECEdgarConnector",
    "USPTOConnector",
    "OpenCorporatesConnector",
]
