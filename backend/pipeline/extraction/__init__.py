"""
ATLAS Platform - Evidence Extraction Module
"""

from backend.pipeline.extraction.extractor import (
    EntityExtractor,
    EntityMatch,
    EvidenceExtractor,
    ValueExtractor,
    get_extractor,
)

__all__ = [
    "EntityExtractor",
    "EntityMatch",
    "EvidenceExtractor",
    "ValueExtractor",
    "get_extractor",
]
