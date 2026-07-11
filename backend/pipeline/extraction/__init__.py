"""
ATLAS Platform - Evidence Extraction Module
"""

from backend.pipeline.extraction.extractor import (
    EntityExtractor,
    EvidenceExtractor,
    EntityMatch,
    ValueExtractor,
    get_extractor,
)

__all__ = [
    "EntityExtractor",
    "EvidenceExtractor",
    "EntityMatch",
    "ValueExtractor",
    "get_extractor",
]
