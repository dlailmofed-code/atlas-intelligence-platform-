"""
ATLAS Platform - Data Pipeline Module

Production-grade data pipeline for processing and enriching data from connectors.
"""

from backend.pipeline.types import (
    DeduplicationResult,
    EntityType,
    ExtractedEvidence,
    GraphEntity,
    GraphRelationship,
    JobPriority,
    JobStatus,
    PipelineConfig,
    PipelineJob,
    PipelineMetrics,
    PipelineRecord,
    PipelineStage,
    RelationshipType,
    SourceType,
    StorageRecord,
    ValidationResult,
)

__all__ = [
    # Enums
    "PipelineStage",
    "JobStatus",
    "JobPriority",
    "SourceType",
    "EntityType",
    "RelationshipType",
    # Data classes
    "PipelineConfig",
    "PipelineJob",
    "PipelineRecord",
    "ExtractedEvidence",
    "GraphEntity",
    "GraphRelationship",
    "PipelineMetrics",
    "ValidationResult",
    "DeduplicationResult",
    "StorageRecord",
]
