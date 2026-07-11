"""
ATLAS Platform - Pipeline Engine

Main orchestration engine for the data pipeline.
Wires all modules together for end-to-end processing.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

from backend.core.logging import get_logger
from backend.pipeline.cleaning import get_cleaner
from backend.pipeline.collection import create_orchestrator
from backend.pipeline.deduplication import get_deduplicator
from backend.pipeline.extraction import get_extractor
from backend.pipeline.graph import get_knowledge_graph
from backend.pipeline.metrics import get_metrics_collector
from backend.pipeline.normalization import get_normalizer
from backend.pipeline.scheduler import get_scheduler
from backend.pipeline.storage import get_storage
from backend.pipeline.types import (
    DeduplicationResult,
    ExtractedEvidence,
    PipelineConfig,
    PipelineRecord,
    PipelineStage,
    SourceType,
    ValidationResult,
)
from backend.pipeline.validation import (
    get_malformed_detector,
    get_schema_validator,
    get_source_validator,
)

logger = get_logger(__name__)


class PipelineEngine:
    """
    Main pipeline engine that orchestrates all processing stages.
    
    Coordinates:
    - Scheduling
    - Collection
    - Validation
    - Cleaning
    - Normalization
    - Deduplication
    - Evidence extraction
    - Knowledge graph updates
    - Storage
    - Metrics
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
    ):
        self.config = config or PipelineConfig()

        # Initialize components
        self.scheduler = get_scheduler()
        self.collector = create_orchestrator(
            batch_size=self.config.batch_size,
            timeout=self.config.job_timeout_seconds,
        )
        self.cleaner = get_cleaner()
        self.normalizer = get_normalizer()
        self.deduplicator = get_deduplicator()
        self.extractor = get_extractor()
        self.knowledge_graph = get_knowledge_graph()
        self.storage = get_storage()
        self.metrics = get_metrics_collector()

        # Validators
        self.schema_validator = get_schema_validator()
        self.source_validator = get_source_validator()
        self.malformed_detector = get_malformed_detector()

        self._running = False
        self._workers: list[asyncio.Task] = []

    async def process_record(
        self,
        record: PipelineRecord,
    ) -> PipelineRecord:
        """
        Process a single record through all pipeline stages.
        
        Args:
            record: The record to process
            
        Returns:
            Processed record with all stages populated
        """
        start_time = datetime.now(UTC)

        try:
            # Stage 1: Validation
            record.stage = PipelineStage.RAW
            await self._validate_stage(record)

            # Stage 2: Cleaning
            record.stage = PipelineStage.COLLECTED
            await self._clean_stage(record)

            # Stage 3: Normalization
            record.stage = PipelineStage.CLEANED
            await self._normalize_stage(record)

            # Stage 4: Deduplication
            record.stage = PipelineStage.NORMALIZED
            dedup_result = await self._deduplicate_stage(record)

            if dedup_result.is_duplicate:
                logger.info(
                    "Duplicate record detected",
                    extra={
                        "record_id": str(record.id),
                        "duplicate_id": str(dedup_result.duplicate_id),
                    }
                )
                record.processing_errors.append(
                    f"Duplicate of {dedup_result.duplicate_id} ({dedup_result.method})"
                )
                self.metrics.record_deduplication()

            # Stage 5: Evidence Extraction
            if self.config.enable_evidence_extraction:
                record.stage = PipelineStage.DEDUPLICATED
                evidence = await self._extract_stage(record)

                # Update knowledge graph
                if self.config.enable_graph_update and evidence:
                    await self._update_graph(record, evidence)

            # Stage 6: Storage
            record.stage = PipelineStage.STORED
            await self._store_stage(record)

            record.updated_at = datetime.now(UTC)

            # Record metrics
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.metrics.record_stage_end(
                PipelineStage.STORED,
                start_time.timestamp(),
                success=True,
            )
            self.metrics.record_record_count(PipelineStage.STORED)

            logger.info(
                "Record processed",
                extra={
                    "record_id": str(record.id),
                    "stage": record.stage.value,
                    "confidence": record.confidence_score,
                    "processing_time_ms": processing_time,
                }
            )

        except Exception as e:
            logger.exception(
                "Record processing failed",
                extra={
                    "record_id": str(record.id),
                    "error": str(e),
                }
            )
            record.processing_errors.append(str(e))
            self.metrics.record_stage_end(
                record.stage,
                start_time.timestamp(),
                success=False,
                error=str(e),
            )

        return record

    async def _validate_stage(self, record: PipelineRecord) -> ValidationResult:
        """Process validation stage."""
        start = self.metrics.record_stage_start(PipelineStage.RAW)

        # Schema validation
        schema_result = self.schema_validator.validate_record(record)

        # Source validation
        source_result = self.source_validator.validate_source(record)

        # Malformed record detection
        is_malformed, issues = self.malformed_detector.detect(record)

        if is_malformed:
            schema_result.errors.extend(issues)
            schema_result.is_valid = False

        # Combine results
        if schema_result.is_valid and source_result.is_valid:
            record.validated_data = schema_result.validated_data or record.collected_data or record.raw_data
            record.confidence_score = (
                schema_result.confidence_score * 0.7 +
                source_result.confidence_score * 0.3
            )
            record.validation_errors = schema_result.errors + source_result.errors
        else:
            record.validation_errors = schema_result.errors + source_result.errors
            record.confidence_score = 0.0

        self.metrics.record_stage_end(PipelineStage.RAW, start, success=schema_result.is_valid)
        self.metrics.record_record_count(PipelineStage.RAW)

        return schema_result

    async def _clean_stage(self, record: PipelineRecord) -> None:
        """Process cleaning stage."""
        start = self.metrics.record_stage_start(PipelineStage.COLLECTED)

        try:
            record.cleaned_data = self.cleaner.clean_record(record)
            self.metrics.record_stage_end(PipelineStage.COLLECTED, start, success=True)
            self.metrics.record_record_count(PipelineStage.COLLECTED)
        except Exception as e:
            self.metrics.record_stage_end(
                PipelineStage.COLLECTED,
                start,
                success=False,
                error=str(e),
            )
            raise

    async def _normalize_stage(self, record: PipelineRecord) -> None:
        """Process normalization stage."""
        start = self.metrics.record_stage_start(PipelineStage.CLEANED)

        try:
            record.normalized_data = self.normalizer.normalize_record(record)
            self.metrics.record_stage_end(PipelineStage.CLEANED, start, success=True)
            self.metrics.record_record_count(PipelineStage.CLEANED)
        except Exception as e:
            self.metrics.record_stage_end(
                PipelineStage.CLEANED,
                start,
                success=False,
                error=str(e),
            )
            raise

    async def _deduplicate_stage(self, record: PipelineRecord) -> DeduplicationResult:
        """Process deduplication stage."""
        start = self.metrics.record_stage_start(PipelineStage.NORMALIZED)

        try:
            if not self.config.enable_deduplication:
                return DeduplicationResult(is_duplicate=False)

            result = await self.deduplicator.check_duplicate(record)

            if not result.is_duplicate:
                # Register record for future deduplication
                self.deduplicator.register_record(record)

            self.metrics.record_stage_end(
                PipelineStage.NORMALIZED,
                start,
                success=True,
            )
            self.metrics.record_record_count(PipelineStage.NORMALIZED)

            return result

        except Exception as e:
            self.metrics.record_stage_end(
                PipelineStage.NORMALIZED,
                start,
                success=False,
                error=str(e),
            )
            raise

    async def _extract_stage(self, record: PipelineRecord) -> list[ExtractedEvidence]:
        """Process evidence extraction stage."""
        start = self.metrics.record_stage_start(PipelineStage.EXTRACTED)

        try:
            evidence = self.extractor.extract_evidence(record)

            # Save evidence
            for e in evidence:
                await self.storage.save_evidence(e)

            record.extracted_data = {
                "entities": [e.entity_id for e in evidence],
                "evidence_count": len(evidence),
            }

            self.metrics.record_stage_end(PipelineStage.EXTRACTED, start, success=True)
            self.metrics.record_record_count(PipelineStage.EXTRACTED)
            self.metrics.record_evidence_extraction(len(evidence))

            return evidence

        except Exception as e:
            self.metrics.record_stage_end(
                PipelineStage.EXTRACTED,
                start,
                success=False,
                error=str(e),
            )
            raise

    async def _update_graph(
        self,
        record: PipelineRecord,
        evidence: list[ExtractedEvidence],
    ) -> None:
        """Update knowledge graph with extracted evidence."""
        start = self.metrics.record_stage_start(PipelineStage.ENRICHED)

        try:
            stats = self.knowledge_graph.update_from_evidence(record, evidence)

            # Update metrics
            self.metrics.record_record_count(PipelineStage.ENRICHED)
            self.metrics.record_stage_end(PipelineStage.ENRICHED, start, success=True)

        except Exception as e:
            self.metrics.record_stage_end(
                PipelineStage.ENRICHED,
                start,
                success=False,
                error=str(e),
            )

    async def _store_stage(self, record: PipelineRecord) -> None:
        """Process storage stage."""
        try:
            await self.storage.save_pipeline_record(record)
        except Exception as e:
            logger.error(
                "Failed to store record",
                extra={
                    "record_id": str(record.id),
                    "error": str(e),
                }
            )
            raise

    async def process_batch(
        self,
        records: list[PipelineRecord],
    ) -> list[PipelineRecord]:
        """Process multiple records in parallel."""
        tasks = [self.process_record(record) for record in records]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                records[i].processing_errors.append(str(result))
                processed.append(records[i])
            else:
                processed.append(result)

        return processed

    async def collect_and_process(
        self,
        source_name: str,
        source_type: SourceType,
        params: dict[str, Any] | None = None,
    ) -> list[PipelineRecord]:
        """
        Collect data from a source and process through the pipeline.
        
        Args:
            source_name: Name of the data source
            source_type: Type of the data source
            params: Collection parameters
            
        Returns:
            List of processed records
        """
        logger.info(
            "Collecting and processing",
            extra={"source_name": source_name, "source_type": source_type.value}
        )

        # Collect data
        collection_result = await self.collector.collect(
            source_name=source_name,
            source_type=source_type,
            params=params,
        )

        if not collection_result.success:
            logger.error(
                "Collection failed",
                extra={
                    "source_name": source_name,
                    "errors": collection_result.errors,
                }
            )
            return []

        # Process records
        processed = await self.process_batch(collection_result.records)

        return processed

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "pipeline_metrics": self.metrics.get_summary(),
            "storage_stats": self.storage.storage.get_stats(),
            "graph_stats": self.knowledge_graph.get_stats(),
            "deduplication_stats": self.deduplicator.get_stats(),
        }

    async def start(self) -> None:
        """Start the pipeline engine."""
        if self._running:
            return

        self._running = True
        logger.info("Pipeline engine started")

    async def stop(self) -> None:
        """Stop the pipeline engine."""
        self._running = False

        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        logger.info("Pipeline engine stopped")

    async def health_check(self) -> dict[str, Any]:
        """Check pipeline health."""
        return {
            "status": "healthy" if self._running else "stopped",
            "components": {
                "scheduler": "healthy",
                "collector": "healthy",
                "cleaner": "healthy",
                "normalizer": "healthy",
                "deduplicator": "healthy",
                "extractor": "healthy",
                "knowledge_graph": "healthy",
                "storage": "healthy",
            },
            "metrics": self.get_stats(),
        }


# Global pipeline instance
_pipeline: PipelineEngine | None = None


def get_pipeline_engine() -> PipelineEngine:
    """Get the global pipeline engine."""
    global _pipeline
    if _pipeline is None:
        _pipeline = PipelineEngine()
    return _pipeline
