"""
ATLAS Platform - Data Deduplication Module
"""

from backend.pipeline.deduplication.deduplicator import (
    ContentHasher,
    Deduplicator,
    SemanticSimilarityChecker,
    TimeWindowDetector,
    URLHasher,
    get_deduplicator,
)

__all__ = [
    "ContentHasher",
    "Deduplicator",
    "SemanticSimilarityChecker",
    "TimeWindowDetector",
    "URLHasher",
    "get_deduplicator",
]
