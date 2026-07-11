"""
ATLAS Platform - Pipeline Types

Type definitions for the data pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class PipelineStage(str, Enum):
    """Pipeline processing stages."""

    RAW = "raw"
    COLLECTED = "collected"
    VALIDATED = "validated"
    CLEANED = "cleaned"
    NORMALIZED = "normalized"
    DEDUPLICATED = "deduplicated"
    EXTRACTED = "extracted"
    ENRICHED = "enriched"
    STORED = "stored"


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    """Job priority levels (higher = more urgent)."""

    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class SourceType(str, Enum):
    """Data source types."""

    NEWS = "news"
    FINANCIAL = "financial"
    GOVERNMENT = "government"
    SOCIAL = "social"
    ACADEMIC = "academic"
    WEB = "web"
    DATABASE = "database"


class EntityType(str, Enum):
    """Knowledge graph entity types."""

    COMPANY = "company"
    ORGANIZATION = "organization"
    PERSON = "person"
    PRODUCT = "product"
    COUNTRY = "country"
    INDUSTRY = "industry"
    TECHNOLOGY = "technology"
    LOCATION = "location"
    EVENT = "event"
    CURRENCY = "currency"


class RelationshipType(str, Enum):
    """Knowledge graph relationship types."""

    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"
    COMPETITION = "competition"
    SUPPLY = "supply"
    FUNDING = "funding"
    EMPLOYMENT = "employment"
    OWNERSHIP = "ownership"
    LOCATION = "location"
    INDUSTRY = "industry"
    PRODUCT = "product"
    SIMILARITY = "similarity"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""

    max_parallel_jobs: int = 10
    job_timeout_seconds: int = 300
    retry_max_attempts: int = 3
    retry_backoff_seconds: int = 60
    batch_size: int = 100
    enable_deduplication: bool = True
    enable_evidence_extraction: bool = True
    enable_graph_update: bool = True
    confidence_threshold: float = 0.7
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600


@dataclass
class PipelineJob:
    """A pipeline job representing a unit of work."""

    id: UUID
    job_type: str
    source_name: str
    source_type: SourceType
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    params: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    result: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRecord:
    """A record being processed through the pipeline."""

    id: UUID
    source_name: str
    source_type: SourceType
    stage: PipelineStage
    raw_data: dict[str, Any] | None = None
    collected_data: dict[str, Any] | None = None
    validated_data: dict[str, Any] | None = None
    cleaned_data: dict[str, Any] | None = None
    normalized_data: dict[str, Any] | None = None
    deduplicated_data: dict[str, Any] | None = None
    extracted_data: dict[str, Any] | None = None
    enriched_data: dict[str, Any] | None = None
    confidence_score: float = 0.0
    validation_errors: list[str] = field(default_factory=list)
    processing_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExtractedEvidence:
    """Evidence extracted from a record."""

    entity_type: EntityType
    entity_id: str
    entity_name: str
    confidence: float
    source_record_id: UUID
    source_field: str
    context: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraphEntity:
    """An entity in the knowledge graph."""

    id: str
    entity_type: EntityType
    name: str
    normalized_name: str
    properties: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source_count: int = 0
    first_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    """A relationship in the knowledge graph."""

    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    properties: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    evidence_ids: list[UUID] = field(default_factory=list)
    first_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PipelineMetrics:
    """Metrics for pipeline monitoring."""

    jobs_total: int = 0
    jobs_completed: int = 0
    jobs_failed: int = 0
    jobs_running: int = 0
    jobs_pending: int = 0
    jobs_retried: int = 0

    records_processed: int = 0
    records_validated: int = 0
    records_rejected: int = 0
    records_deduplicated: int = 0

    evidence_extracted: int = 0
    entities_created: int = 0
    entities_updated: int = 0
    relationships_created: int = 0

    total_processing_time_ms: float = 0.0
    avg_processing_time_ms: float = 0.0

    connector_latencies: dict[str, list[float]] = field(default_factory=dict)

    cache_hits: int = 0
    cache_misses: int = 0

    stage_durations_ms: dict[PipelineStage, float] = field(default_factory=dict)

    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    confidence_score: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validated_data: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeduplicationResult:
    """Result of deduplication check."""

    is_duplicate: bool
    duplicate_id: UUID | None = None
    similarity_score: float = 0.0
    method: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageRecord:
    """A record stored in the data store."""

    id: UUID
    stage: PipelineStage
    source_name: str
    source_type: SourceType
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    checksum: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
