"""
ATLAS Platform - Pipeline Storage Module

Handles storage of pipeline data at each stage:
- Raw data
- Normalized data
- Validated data
- Evidence data
- Knowledge graph data
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator
from uuid import UUID

from backend.core.logging import get_logger
from backend.pipeline.extraction.extractor import ExtractedEvidence
from backend.pipeline.graph.knowledge_graph import GraphEntity, GraphRelationship
from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType, StorageRecord

logger = get_logger(__name__)


class InMemoryStorage:
    """In-memory storage for pipeline data."""
    
    def __init__(self):
        self._records: dict[UUID, dict[str, Any]] = {}
        self._entities: dict[str, GraphEntity] = {}
        self._relationships: dict[str, GraphRelationship] = {}
        self._evidence: dict[UUID, ExtractedEvidence] = {}
        self._storage_records: dict[UUID, StorageRecord] = {}
    
    # Record storage
    async def save_record(self, record: PipelineRecord) -> None:
        """Save a pipeline record."""
        self._records[record.id] = {
            "id": record.id,
            "source_name": record.source_name,
            "source_type": record.source_type.value,
            "stage": record.stage.value,
            "raw_data": record.raw_data,
            "collected_data": record.collected_data,
            "validated_data": record.validated_data,
            "cleaned_data": record.cleaned_data,
            "normalized_data": record.normalized_data,
            "deduplicated_data": record.deduplicated_data,
            "extracted_data": record.extracted_data,
            "enriched_data": record.enriched_data,
            "confidence_score": record.confidence_score,
            "validation_errors": record.validation_errors,
            "processing_errors": record.processing_errors,
            "metadata": record.metadata,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        
        # Also save as storage record
        storage_record = StorageRecord(
            id=record.id,
            stage=record.stage,
            source_name=record.source_name,
            source_type=record.source_type,
            content=self._get_stage_data(record),
            metadata=record.metadata,
            checksum=self._generate_checksum(record),
            created_at=record.created_at,
        )
        self._storage_records[record.id] = storage_record
        
        logger.debug(
            "Record saved",
            extra={"record_id": str(record.id), "stage": record.stage.value}
        )
    
    def _get_stage_data(self, record: PipelineRecord) -> dict[str, Any]:
        """Get data for current stage."""
        return (
            record.enriched_data
            or record.extracted_data
            or record.deduplicated_data
            or record.normalized_data
            or record.cleaned_data
            or record.validated_data
            or record.collected_data
            or record.raw_data
            or {}
        )
    
    def _generate_checksum(self, record: PipelineRecord) -> str:
        """Generate checksum for record."""
        data = self._get_stage_data(record)
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def get_record(self, record_id: UUID) -> PipelineRecord | None:
        """Get a record by ID."""
        if record_id not in self._records:
            return None
        
        data = self._records[record_id]
        
        return PipelineRecord(
            id=data["id"],
            source_name=data["source_name"],
            source_type=SourceType(data["source_type"]),
            stage=PipelineStage(data["stage"]),
            raw_data=data.get("raw_data"),
            collected_data=data.get("collected_data"),
            validated_data=data.get("validated_data"),
            cleaned_data=data.get("cleaned_data"),
            normalized_data=data.get("normalized_data"),
            deduplicated_data=data.get("deduplicated_data"),
            extracted_data=data.get("extracted_data"),
            enriched_data=data.get("enriched_data"),
            confidence_score=data.get("confidence_score", 0.0),
            validation_errors=data.get("validation_errors", []),
            processing_errors=data.get("processing_errors", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
    
    async def list_records(
        self,
        stage: PipelineStage | None = None,
        source_name: str | None = None,
        limit: int = 100,
    ) -> list[PipelineRecord]:
        """List records with optional filtering."""
        results = []
        
        for record_data in self._records.values():
            if stage and record_data["stage"] != stage.value:
                continue
            if source_name and record_data["source_name"] != source_name:
                continue
            
            record = await self.get_record(UUID(str(record_data["id"])))
            if record:
                results.append(record)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def delete_record(self, record_id: UUID) -> bool:
        """Delete a record."""
        if record_id in self._records:
            del self._records[record_id]
        if record_id in self._storage_records:
            del self._storage_records[record_id]
        return True
    
    # Entity storage
    async def save_entity(self, entity: GraphEntity) -> None:
        """Save a graph entity."""
        self._entities[entity.id] = entity
        logger.debug(
            "Entity saved",
            extra={"entity_id": entity.id, "type": entity.entity_type.value}
        )
    
    async def get_entity(self, entity_id: str) -> GraphEntity | None:
        """Get an entity by ID."""
        return self._entities.get(entity_id)
    
    async def list_entities(
        self,
        entity_type: str | None = None,
        limit: int = 100,
    ) -> list[GraphEntity]:
        """List entities with optional filtering."""
        results = []
        
        for entity in self._entities.values():
            if entity_type and entity.entity_type.value != entity_type:
                continue
            results.append(entity)
            
            if len(results) >= limit:
                break
        
        return results
    
    # Relationship storage
    async def save_relationship(self, relationship: GraphRelationship) -> None:
        """Save a graph relationship."""
        self._relationships[relationship.id] = relationship
        logger.debug(
            "Relationship saved",
            extra={
                "rel_id": relationship.id,
                "type": relationship.relationship_type.value,
            }
        )
    
    async def get_relationship(self, rel_id: str) -> GraphRelationship | None:
        """Get a relationship by ID."""
        return self._relationships.get(rel_id)
    
    async def list_relationships(
        self,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[GraphRelationship]:
        """List relationships with optional filtering."""
        results = []
        
        for rel in self._relationships.values():
            if entity_id:
                if rel.source_entity_id != entity_id and rel.target_entity_id != entity_id:
                    continue
            results.append(rel)
            
            if len(results) >= limit:
                break
        
        return results
    
    # Evidence storage
    async def save_evidence(self, evidence: ExtractedEvidence) -> None:
        """Save extracted evidence."""
        self._evidence[evidence.source_record_id] = evidence
        logger.debug(
            "Evidence saved",
            extra={
                "source_id": str(evidence.source_record_id),
                "entity_id": evidence.entity_id,
            }
        )
    
    async def get_evidence_for_record(
        self,
        record_id: UUID,
    ) -> list[ExtractedEvidence]:
        """Get all evidence for a record."""
        return [e for e in self._evidence.values() if e.source_record_id == record_id]
    
    # Storage record operations
    async def get_storage_record(self, record_id: UUID) -> StorageRecord | None:
        """Get a storage record."""
        return self._storage_records.get(record_id)
    
    async def list_storage_records(
        self,
        stage: PipelineStage | None = None,
        older_than: datetime | None = None,
        limit: int = 100,
    ) -> list[StorageRecord]:
        """List storage records with optional filtering."""
        results = []
        
        for record in self._storage_records.values():
            if stage and record.stage != stage:
                continue
            if older_than and record.created_at < older_than:
                continue
            
            results.append(record)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def cleanup_expired(self, ttl_hours: int = 24) -> int:
        """Remove expired storage records."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        expired_ids = [
            rid for rid, rec in self._storage_records.items()
            if rec.created_at < cutoff
        ]
        
        for rid in expired_ids:
            del self._storage_records[rid]
        
        if expired_ids:
            logger.info(
                "Expired records cleaned up",
                extra={"count": len(expired_ids)}
            )
        
        return len(expired_ids)
    
    # Stats
    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics."""
        return {
            "total_records": len(self._records),
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "total_evidence": len(self._evidence),
            "total_storage_records": len(self._storage_records),
            "records_by_stage": {
                stage.value: sum(
                    1 for r in self._records.values()
                    if r["stage"] == stage.value
                )
                for stage in PipelineStage
            },
            "records_by_source": {
                source: sum(
                    1 for r in self._records.values()
                    if r["source_name"] == source
                )
                for source in set(r["source_name"] for r in self._records.values())
            },
        }
    
    def clear(self) -> None:
        """Clear all stored data."""
        self._records.clear()
        self._entities.clear()
        self._relationships.clear()
        self._evidence.clear()
        self._storage_records.clear()
        logger.info("Storage cleared")


class StorageManager:
    """Manages storage operations with transaction support."""
    
    def __init__(self, storage: InMemoryStorage | None = None):
        self.storage = storage or InMemoryStorage()
    
    async def save_pipeline_record(self, record: PipelineRecord) -> None:
        """Save a complete pipeline record."""
        await self.storage.save_record(record)
    
    async def save_evidence_batch(self, evidence_list: list[ExtractedEvidence]) -> None:
        """Save a batch of evidence."""
        for evidence in evidence_list:
            await self.storage.save_evidence(evidence)
    
    async def save_graph_data(
        self,
        entities: list[GraphEntity],
        relationships: list[GraphRelationship],
    ) -> None:
        """Save graph entities and relationships."""
        for entity in entities:
            await self.storage.save_entity(entity)
        for rel in relationships:
            await self.storage.save_relationship(rel)
    
    async def get_complete_record(self, record_id: UUID) -> dict[str, Any] | None:
        """Get a complete record with all stages."""
        record = await self.storage.get_record(record_id)
        if not record:
            return None
        
        evidence = await self.storage.get_evidence_for_record(record_id)
        
        return {
            "record": record,
            "evidence": evidence,
        }
    
    async def search_records(
        self,
        query: str,
        stage: PipelineStage | None = None,
    ) -> list[PipelineRecord]:
        """Search records by content."""
        all_records = await self.storage.list_records(stage=stage, limit=1000)
        
        query_lower = query.lower()
        matching = []
        
        for record in all_records:
            data = record.raw_data or {}
            content = " ".join(
                str(v) for v in data.values()
                if isinstance(v, str)
            )
            if query_lower in content.lower():
                matching.append(record)
        
        return matching


# Global storage instance
_storage: StorageManager | None = None


def get_storage() -> StorageManager:
    """Get the global storage manager."""
    global _storage
    if _storage is None:
        _storage = StorageManager()
    return _storage
