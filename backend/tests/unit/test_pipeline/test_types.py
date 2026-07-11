"""
Tests for pipeline types.
"""

from uuid import uuid4

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
    ValidationResult,
)


class TestPipelineStage:
    """Tests for PipelineStage enum."""

    def test_all_stages(self):
        """Test all pipeline stage values."""
        assert PipelineStage.RAW.value == "raw"
        assert PipelineStage.COLLECTED.value == "collected"
        assert PipelineStage.VALIDATED.value == "validated"
        assert PipelineStage.CLEANED.value == "cleaned"
        assert PipelineStage.NORMALIZED.value == "normalized"
        assert PipelineStage.DEDUPLICATED.value == "deduplicated"
        assert PipelineStage.EXTRACTED.value == "extracted"
        assert PipelineStage.ENRICHED.value == "enriched"
        assert PipelineStage.STORED.value == "stored"


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_statuses(self):
        """Test all job status values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.RETRYING.value == "retrying"
        assert JobStatus.CANCELLED.value == "cancelled"


class TestJobPriority:
    """Tests for JobPriority enum."""

    def test_priority_order(self):
        """Test priority ordering."""
        assert JobPriority.CRITICAL > JobPriority.HIGH
        assert JobPriority.HIGH > JobPriority.NORMAL
        assert JobPriority.NORMAL > JobPriority.LOW


class TestSourceType:
    """Tests for SourceType enum."""

    def test_all_types(self):
        """Test all source type values."""
        assert SourceType.NEWS.value == "news"
        assert SourceType.FINANCIAL.value == "financial"
        assert SourceType.GOVERNMENT.value == "government"
        assert SourceType.SOCIAL.value == "social"
        assert SourceType.ACADEMIC.value == "academic"
        assert SourceType.WEB.value == "web"
        assert SourceType.DATABASE.value == "database"


class TestEntityType:
    """Tests for EntityType enum."""

    def test_all_types(self):
        """Test all entity type values."""
        assert EntityType.COMPANY.value == "company"
        assert EntityType.PERSON.value == "person"
        assert EntityType.COUNTRY.value == "country"
        assert EntityType.TECHNOLOGY.value == "technology"


class TestRelationshipType:
    """Tests for RelationshipType enum."""

    def test_all_types(self):
        """Test all relationship type values."""
        assert RelationshipType.ACQUISITION.value == "acquisition"
        assert RelationshipType.PARTNERSHIP.value == "partnership"
        assert RelationshipType.EMPLOYMENT.value == "employment"


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_defaults(self):
        """Test default configuration."""
        config = PipelineConfig()

        assert config.max_parallel_jobs == 10
        assert config.job_timeout_seconds == 300
        assert config.retry_max_attempts == 3
        assert config.batch_size == 100
        assert config.enable_deduplication is True
        assert config.enable_evidence_extraction is True
        assert config.confidence_threshold == 0.7

    def test_custom(self):
        """Test custom configuration."""
        config = PipelineConfig(
            max_parallel_jobs=20,
            job_timeout_seconds=600,
            enable_deduplication=False,
        )

        assert config.max_parallel_jobs == 20
        assert config.job_timeout_seconds == 600
        assert config.enable_deduplication is False


class TestPipelineJob:
    """Tests for PipelineJob."""

    def test_creation(self):
        """Test job creation."""
        job = PipelineJob(
            id=uuid4(),
            job_type="collect",
            source_name="newsapi",
            source_type=SourceType.NEWS,
        )

        assert job.job_type == "collect"
        assert job.source_name == "newsapi"
        assert job.source_type == SourceType.NEWS
        assert job.status == JobStatus.PENDING
        assert job.priority == JobPriority.NORMAL
        assert job.retry_count == 0


class TestPipelineRecord:
    """Tests for PipelineRecord."""

    def test_creation(self):
        """Test record creation."""
        record = PipelineRecord(
            id=uuid4(),
            source_name="newsapi",
            source_type=SourceType.NEWS,
            stage=PipelineStage.RAW,
        )

        assert record.source_name == "newsapi"
        assert record.source_type == SourceType.NEWS
        assert record.stage == PipelineStage.RAW
        assert record.confidence_score == 0.0
        assert len(record.validation_errors) == 0
        assert len(record.processing_errors) == 0

    def test_stage_progression(self):
        """Test record stage progression."""
        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.WEB,
            stage=PipelineStage.RAW,
        )

        record.raw_data = {"title": "Test"}
        record.stage = PipelineStage.COLLECTED
        record.collected_data = {"title": "Test"}

        assert record.raw_data is not None
        assert record.stage == PipelineStage.COLLECTED


class TestExtractedEvidence:
    """Tests for ExtractedEvidence."""

    def test_creation(self):
        """Test evidence creation."""
        evidence = ExtractedEvidence(
            entity_type=EntityType.COMPANY,
            entity_id="test123",
            entity_name="Test Corp",
            confidence=0.9,
            source_record_id=uuid4(),
            source_field="content",
        )

        assert evidence.entity_type == EntityType.COMPANY
        assert evidence.entity_name == "Test Corp"
        assert evidence.confidence == 0.9


class TestGraphEntity:
    """Tests for GraphEntity."""

    def test_creation(self):
        """Test entity creation."""
        entity = GraphEntity(
            id="test123",
            entity_type=EntityType.COMPANY,
            name="Test Corp",
            normalized_name="test corp",
        )

        assert entity.id == "test123"
        assert entity.entity_type == EntityType.COMPANY
        assert entity.name == "Test Corp"
        assert entity.confidence == 1.0
        assert entity.source_count == 0


class TestGraphRelationship:
    """Tests for GraphRelationship."""

    def test_creation(self):
        """Test relationship creation."""
        rel = GraphRelationship(
            id="rel123",
            source_entity_id="ent1",
            target_entity_id="ent2",
            relationship_type=RelationshipType.PARTNERSHIP,
        )

        assert rel.id == "rel123"
        assert rel.source_entity_id == "ent1"
        assert rel.target_entity_id == "ent2"
        assert rel.relationship_type == RelationshipType.PARTNERSHIP


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(
            is_valid=True,
            confidence_score=0.9,
        )

        assert result.is_valid is True
        assert result.confidence_score == 0.9
        assert len(result.errors) == 0

    def test_invalid_result(self):
        """Test invalid validation result."""
        result = ValidationResult(
            is_valid=False,
            confidence_score=0.3,
            errors=["Missing required field: title"],
        )

        assert result.is_valid is False
        assert result.confidence_score == 0.3
        assert len(result.errors) == 1


class TestDeduplicationResult:
    """Tests for DeduplicationResult."""

    def test_not_duplicate(self):
        """Test non-duplicate result."""
        result = DeduplicationResult(
            is_duplicate=False,
        )

        assert result.is_duplicate is False
        assert result.duplicate_id is None

    def test_duplicate(self):
        """Test duplicate result."""
        dup_id = uuid4()
        result = DeduplicationResult(
            is_duplicate=True,
            duplicate_id=dup_id,
            method="url_hash",
            similarity_score=1.0,
        )

        assert result.is_duplicate is True
        assert result.duplicate_id == dup_id
        assert result.method == "url_hash"


class TestPipelineMetrics:
    """Tests for PipelineMetrics."""

    def test_defaults(self):
        """Test default metrics."""
        metrics = PipelineMetrics()

        assert metrics.jobs_total == 0
        assert metrics.jobs_completed == 0
        assert metrics.records_processed == 0
        assert metrics.evidence_extracted == 0
