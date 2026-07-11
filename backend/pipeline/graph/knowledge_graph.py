"""
ATLAS Platform - Knowledge Graph Module

Handles knowledge graph updates including:
- Entities (create/update)
- Relationships (create/update)
- Evidence links
- Confidence scoring
- Timestamps
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from backend.core.logging import get_logger
from backend.pipeline.extraction.extractor import ExtractedEvidence
from backend.pipeline.types import (
    EntityType,
    ExtractedEvidence,
    GraphEntity,
    GraphRelationship,
    PipelineRecord,
    RelationshipType,
)

logger = get_logger(__name__)


class EntityManager:
    """Manages entities in the knowledge graph."""

    def __init__(self):
        self._entities: dict[str, GraphEntity] = {}

    def get_or_create(
        self,
        entity_id: str,
        entity_type: EntityType,
        name: str,
        properties: dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> GraphEntity:
        """
        Get an existing entity or create a new one.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            name: Entity name
            properties: Optional entity properties
            confidence: Initial confidence score
            
        Returns:
            GraphEntity instance
        """
        if entity_id in self._entities:
            entity = self._entities[entity_id]
            entity.source_count += 1
            entity.last_updated_at = datetime.now(UTC)

            # Update properties
            if properties:
                entity.properties.update(properties)

            return entity

        # Create new entity
        entity = GraphEntity(
            id=entity_id,
            entity_type=entity_type,
            name=name,
            normalized_name=name.lower().strip(),
            properties=properties or {},
            confidence=confidence,
            source_count=1,
            first_seen_at=datetime.now(UTC),
            last_updated_at=datetime.now(UTC),
        )

        self._entities[entity_id] = entity

        logger.debug(
            "Entity created",
            extra={
                "entity_id": entity_id,
                "entity_type": entity_type.value,
                "name": name,
            }
        )

        return entity

    def get(self, entity_id: str) -> GraphEntity | None:
        """Get an entity by ID."""
        return self._entities.get(entity_id)

    def update_confidence(
        self,
        entity_id: str,
        new_confidence: float,
    ) -> bool:
        """Update entity confidence score."""
        entity = self._entities.get(entity_id)
        if not entity:
            return False

        # Update confidence as weighted average
        # More evidence = higher confidence
        total_sources = entity.source_count
        old_weight = total_sources - 1
        new_weight = 1

        entity.confidence = (
            (entity.confidence * old_weight + new_confidence * new_weight)
            / (old_weight + new_weight)
        )
        entity.confidence = max(0.0, min(1.0, entity.confidence))

        entity.last_updated_at = datetime.now(UTC)

        return True

    def get_all(self) -> list[GraphEntity]:
        """Get all entities."""
        return list(self._entities.values())

    def get_by_type(self, entity_type: EntityType) -> list[GraphEntity]:
        """Get all entities of a specific type."""
        return [
            e for e in self._entities.values()
            if e.entity_type == entity_type
        ]

    def search(self, query: str) -> list[GraphEntity]:
        """Search entities by name."""
        query_lower = query.lower()
        return [
            e for e in self._entities.values()
            if query_lower in e.name.lower() or query_lower in e.normalized_name
        ]

    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()


class RelationshipManager:
    """Manages relationships in the knowledge graph."""

    def __init__(self):
        self._relationships: dict[str, GraphRelationship] = {}

    def get_or_create(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        properties: dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> GraphRelationship:
        """
        Get an existing relationship or create a new one.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            confidence: Initial confidence score
            
        Returns:
            GraphRelationship instance
        """
        rel_id = self._generate_id(source_id, target_id, relationship_type)

        if rel_id in self._relationships:
            rel = self._relationships[rel_id]
            rel.last_updated_at = datetime.now(UTC)

            # Update properties
            if properties:
                rel.properties.update(properties)

            return rel

        # Create new relationship
        rel = GraphRelationship(
            id=rel_id,
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {},
            confidence=confidence,
            evidence_ids=[],
            first_seen_at=datetime.now(UTC),
            last_updated_at=datetime.now(UTC),
        )

        self._relationships[rel_id] = rel

        logger.debug(
            "Relationship created",
            extra={
                "rel_id": rel_id,
                "source_id": source_id,
                "target_id": target_id,
                "type": relationship_type.value,
            }
        )

        return rel

    def _generate_id(
        self,
        source_id: str,
        target_id: str,
        rel_type: RelationshipType,
    ) -> str:
        """Generate a unique relationship ID."""
        import hashlib

        parts = sorted([source_id, target_id])
        id_string = f"{rel_type.value}:{parts[0]}:{parts[1]}"
        return hashlib.md5(id_string.encode()).hexdigest()[:16]

    def add_evidence(
        self,
        rel_id: str,
        evidence_id: UUID,
    ) -> bool:
        """Add evidence to a relationship."""
        rel = self._relationships.get(rel_id)
        if not rel:
            return False

        if evidence_id not in rel.evidence_ids:
            rel.evidence_ids.append(evidence_id)
            rel.last_updated_at = datetime.now(UTC)

        return True

    def update_confidence(
        self,
        rel_id: str,
        new_confidence: float,
    ) -> bool:
        """Update relationship confidence score."""
        rel = self._relationships.get(rel_id)
        if not rel:
            return False

        # Weighted average update
        num_evidence = len(rel.evidence_ids)
        old_weight = max(num_evidence - 1, 1)
        new_weight = 1

        rel.confidence = (
            (rel.confidence * old_weight + new_confidence * new_weight)
            / (old_weight + new_weight)
        )
        rel.confidence = max(0.0, min(1.0, rel.confidence))

        rel.last_updated_at = datetime.now(UTC)

        return True

    def get(self, rel_id: str) -> GraphRelationship | None:
        """Get a relationship by ID."""
        return self._relationships.get(rel_id)

    def get_by_entity(self, entity_id: str) -> list[GraphRelationship]:
        """Get all relationships involving an entity."""
        return [
            r for r in self._relationships.values()
            if r.source_entity_id == entity_id or r.target_entity_id == entity_id
        ]

    def get_all(self) -> list[GraphRelationship]:
        """Get all relationships."""
        return list(self._relationships.values())

    def clear(self) -> None:
        """Clear all relationships."""
        self._relationships.clear()


class EvidenceLinker:
    """Links evidence to entities and relationships."""

    def __init__(self):
        self._links: dict[UUID, dict[str, Any]] = {}

    def link_evidence_to_entity(
        self,
        evidence: ExtractedEvidence,
        entity_id: str,
    ) -> None:
        """Link evidence to an entity."""
        if evidence.source_record_id not in self._links:
            self._links[evidence.source_record_id] = {
                "entity_ids": [],
                "relationship_ids": [],
                "evidence": evidence,
            }

        if entity_id not in self._links[evidence.source_record_id]["entity_ids"]:
            self._links[evidence.source_record_id]["entity_ids"].append(entity_id)

    def link_evidence_to_relationship(
        self,
        evidence: ExtractedEvidence,
        rel_id: str,
    ) -> None:
        """Link evidence to a relationship."""
        if evidence.source_record_id not in self._links:
            self._links[evidence.source_record_id] = {
                "entity_ids": [],
                "relationship_ids": [],
                "evidence": evidence,
            }

        if rel_id not in self._links[evidence.source_record_id]["relationship_ids"]:
            self._links[evidence.source_record_id]["relationship_ids"].append(rel_id)

    def get_entity_links(self, record_id: UUID) -> list[str]:
        """Get entity IDs linked to a record."""
        if record_id in self._links:
            return self._links[record_id]["entity_ids"]
        return []

    def get_relationship_links(self, record_id: UUID) -> list[str]:
        """Get relationship IDs linked to a record."""
        if record_id in self._links:
            return self._links[record_id]["relationship_ids"]
        return []

    def get_evidence(self, record_id: UUID) -> ExtractedEvidence | None:
        """Get evidence for a record."""
        if record_id in self._links:
            return self._links[record_id]["evidence"]
        return None


class KnowledgeGraph:
    """
    Main knowledge graph that coordinates all graph operations.
    """

    def __init__(self):
        self.entity_manager = EntityManager()
        self.relationship_manager = RelationshipManager()
        self.evidence_linker = EvidenceLinker()

    def update_from_evidence(
        self,
        record: PipelineRecord,
        evidence_list: list[ExtractedEvidence],
    ) -> dict[str, Any]:
        """
        Update the knowledge graph from extracted evidence.
        
        Args:
            record: Source record
            evidence_list: List of extracted evidence
            
        Returns:
            Update statistics
        """
        stats = {
            "entities_created": 0,
            "entities_updated": 0,
            "relationships_created": 0,
            "relationships_updated": 0,
        }

        # Group evidence by entity
        entities_by_type: dict[EntityType, list[ExtractedEvidence]] = {}
        for evidence in evidence_list:
            if evidence.entity_type not in entities_by_type:
                entities_by_type[evidence.entity_type] = []
            entities_by_type[evidence.entity_type].append(evidence)

        # Process entities
        for entity_type, evidences in entities_by_type.items():
            # Get unique entities
            unique_entities: dict[str, ExtractedEvidence] = {}
            for evidence in evidences:
                if evidence.entity_id not in unique_entities:
                    unique_entities[evidence.entity_id] = evidence

            # Create or update entities
            for entity_id, evidence in unique_entities.items():
                existing = self.entity_manager.get(entity_id)

                if existing:
                    self.entity_manager.update_confidence(
                        entity_id, evidence.confidence
                    )
                    stats["entities_updated"] += 1
                else:
                    self.entity_manager.get_or_create(
                        entity_id=entity_id,
                        entity_type=evidence.entity_type,
                        name=evidence.entity_name,
                        properties=evidence.properties,
                        confidence=evidence.confidence,
                    )
                    stats["entities_created"] += 1

                # Link evidence to entity
                self.evidence_linker.link_evidence_to_entity(
                    evidence, entity_id
                )

        # Infer relationships from entity co-occurrences
        relationship_map = self._infer_relationships(evidence_list)

        for rel_type, (source_id, target_id, properties) in relationship_map.items():
            rel_id = self.relationship_manager._generate_id(
                source_id, target_id, rel_type
            )

            existing = self.relationship_manager.get(rel_id)
            if existing:
                self.relationship_manager.update_confidence(rel_id, 0.8)
                stats["relationships_updated"] += 1
            else:
                self.relationship_manager.get_or_create(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=rel_type,
                    properties=properties,
                    confidence=0.8,
                )
                stats["relationships_created"] += 1

        logger.info(
            "Knowledge graph updated",
            extra={
                "record_id": str(record.id),
                "evidence_count": len(evidence_list),
                **stats,
            }
        )

        return stats

    def _infer_relationships(
        self,
        evidence_list: list[ExtractedEvidence],
    ) -> dict[RelationshipType, tuple[str, str, dict[str, Any]]]:
        """
        Infer relationships from evidence co-occurrences.
        
        Returns:
            Dictionary of inferred relationships
        """
        relationships: dict[str, tuple[RelationshipType, str, str, dict[str, Any]]] = {}

        # Group evidence by source record
        by_source: dict[UUID, list[ExtractedEvidence]] = {}
        for evidence in evidence_list:
            if evidence.source_record_id not in by_source:
                by_source[evidence.source_record_id] = []
            by_source[evidence.source_record_id].append(evidence)

        # Find co-occurring entities
        for source_id, evidences in by_source.items():
            entities = [e for e in evidences if e.entity_type in (
                EntityType.COMPANY,
                EntityType.ORGANIZATION,
                EntityType.PERSON,
            )]

            # Create co-occurrence relationships
            for i, e1 in enumerate(entities):
                for e2 in entities[i + 1:]:
                    # Determine relationship type based on entity types
                    rel_type = self._determine_relationship_type(e1.entity_type, e2.entity_type)

                    # Create unique key for relationship
                    key_parts = sorted([e1.entity_id, e2.entity_id])
                    key = f"{rel_type.value}:{key_parts[0]}:{key_parts[1]}"

                    if key not in relationships:
                        relationships[key] = (
                            rel_type,
                            key_parts[0],
                            key_parts[1],
                            {
                                "source_count": 1,
                                "context": e1.context,
                            }
                        )
                    else:
                        # Increment source count
                        rel_type, s, t, props = relationships[key]
                        props["source_count"] = props.get("source_count", 1) + 1

        # Convert to return format
        result: dict[RelationshipType, tuple[str, str, dict[str, Any]]] = {}
        for key, (rel_type, s, t, props) in relationships.items():
            result[key] = (s, t, props)

        return result

    def _determine_relationship_type(
        self,
        type1: EntityType,
        type2: EntityType,
    ) -> RelationshipType:
        """Determine relationship type based on entity types."""
        if EntityType.PERSON in (type1, type2):
            if EntityType.COMPANY in (type1, type2):
                return RelationshipType.EMPLOYMENT
            return RelationshipType.PARTNERSHIP

        if EntityType.COMPANY in (type1, type2):
            if EntityType.INDUSTRY in (type1, type2):
                return RelationshipType.INDUSTRY
            return RelationshipType.PARTNERSHIP

        return RelationshipType.SIMILARITY

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge graph statistics."""
        return {
            "total_entities": len(self.entity_manager.get_all()),
            "entities_by_type": {
                etype.value: len(self.entity_manager.get_by_type(etype))
                for etype in EntityType
            },
            "total_relationships": len(self.relationship_manager.get_all()),
            "total_evidence_links": len(self.evidence_linker._links),
        }

    def clear(self) -> None:
        """Clear all graph data."""
        self.entity_manager.clear()
        self.relationship_manager.clear()
        self._links.clear()


# Global knowledge graph instance
_graph: KnowledgeGraph | None = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the global knowledge graph."""
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph()
    return _graph
