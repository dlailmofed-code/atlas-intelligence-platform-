"""
ATLAS Platform - Knowledge Graph

This module implements the Knowledge Graph for the intelligence engine.
Based on the specifications - Intelligence Knowledge Graph section.

The Knowledge Graph represents entities and their relationships,
enabling complex queries and cross-domain intelligence.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.core.logging import get_logger

logger = get_logger(__name__)


class EntityType(StrEnum):
    """Types of entities in the knowledge graph."""

    PERSON = "person"
    ORGANIZATION = "organization"
    COMPANY = "company"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    MARKET = "market"
    INDUSTRY = "industry"
    GEOGRAPHY = "geography"
    REGULATION = "regulation"
    EVENT = "event"
    TREND = "trend"
    CONCEPT = "concept"


class RelationshipType(StrEnum):
    """Types of relationships between entities."""

    # Company relationships
    ACQUIRES = "acquires"
    ACQUIRED_BY = "acquired_by"
    PARTNERS_WITH = "partners_with"
    COMPETES_WITH = "competes_with"
    INVESTS_IN = "invests_in"
    FUNDED_BY = "funded_by"

    # Product relationships
    OFFERS = "offers"
    USES_TECHNOLOGY = "uses_technology"
    TARGETS_MARKET = "targets_market"

    # Market relationships
    LOCATED_IN = "located_in"
    OPERATES_IN = "operates_in"
    SERVES_REGION = "serves_region"

    # Regulatory relationships
    REGULATES = "regulates"
    REGULATED_BY = "regulated_by"
    COMPLIANT_WITH = "compliant_with"

    # Causal relationships
    CAUSES = "causes"
    ENABLES = "enables"
    PREVENTS = "prevents"

    # Temporal relationships
    TRENDS_TOWARD = "trends_toward"
    EVOLVED_FROM = "evolved_from"
    PRECEDES = "precedes"


class Entity(BaseModel):
    """Entity in the knowledge graph."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EntityType
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    description: str | None = None
    aliases: list[str] = Field(default_factory=list)
    external_ids: dict[str, str] = Field(default_factory=dict)  # e.g., {"wiki": "Q123"}

    # Graph metrics
    connection_count: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_mentioned_at: datetime | None = None


class Relationship(BaseModel):
    """Relationship between entities in the knowledge graph."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: RelationshipType

    # Relationship properties
    properties: dict[str, Any] = Field(default_factory=dict)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Context
    evidence_ids: list[str] = Field(default_factory=list)
    context: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class KnowledgeGraph:
    """
    Knowledge Graph for managing entities and relationships.

    Features:
    - Entity management (CRUD operations)
    - Relationship management
    - Graph traversal and querying
    - Path finding
    - Cluster detection
    """

    def __init__(self):
        """Initialize knowledge graph."""
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._entity_index: dict[str, list[str]] = {}  # name -> entity_ids
        self._type_index: dict[EntityType, list[str]] = {}  # type -> entity_ids
        self._relationship_index: dict[tuple[str, str], list[str]] = {}  # (source, target) -> relationship_ids

    def add_entity(
        self,
        entity_type: EntityType,
        name: str,
        properties: dict[str, Any] | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
        external_ids: dict[str, str] | None = None,
    ) -> Entity:
        """
        Add an entity to the knowledge graph.

        Args:
            entity_type: Type of the entity
            name: Name of the entity
            properties: Additional properties
            description: Entity description
            aliases: Alternative names
            external_ids: External database IDs

        Returns:
            Created Entity
        """
        # Check for existing entity with same name
        existing_ids = self._entity_index.get(name.lower(), [])
        if existing_ids:
            entity = self._entities[existing_ids[0]]
            entity.last_mentioned_at = datetime.utcnow()
            return entity

        # Create entity
        entity = Entity(
            type=entity_type,
            name=name,
            properties=properties or {},
            description=description,
            aliases=aliases or [],
            external_ids=external_ids or {},
        )

        # Store entity
        self._entities[entity.id] = entity

        # Update indices
        if name.lower() not in self._entity_index:
            self._entity_index[name.lower()] = []
        self._entity_index[name.lower()].append(entity.id)

        if entity_type not in self._type_index:
            self._type_index[entity_type] = []
        self._type_index[entity_type].append(entity.id)

        logger.info(
            "Entity added to knowledge graph",
            entity_id=entity.id,
            entity_type=entity_type.value,
            entity_name=name,
        )

        return entity

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        properties: dict[str, Any] | None = None,
        weight: float = 1.0,
        confidence: float = 1.0,
        evidence_ids: list[str] | None = None,
        context: str | None = None,
    ) -> Relationship:
        """
        Add a relationship between entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional properties
            weight: Relationship weight (0-1)
            confidence: Confidence in the relationship (0-1)
            evidence_ids: Supporting evidence IDs
            context: Contextual information

        Returns:
            Created Relationship
        """
        # Verify entities exist
        if source_id not in self._entities:
            raise ValueError(f"Source entity not found: {source_id}")
        if target_id not in self._entities:
            raise ValueError(f"Target entity not found: {target_id}")

        # Create relationship
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            properties=properties or {},
            weight=weight,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
            context=context,
        )

        # Store relationship
        self._relationships[relationship.id] = relationship

        # Update entity connection counts
        self._entities[source_id].connection_count += 1
        self._entities[target_id].connection_count += 1

        # Update indices
        key = (source_id, target_id)
        if key not in self._relationship_index:
            self._relationship_index[key] = []
        self._relationship_index[key].append(relationship.id)

        logger.info(
            "Relationship added to knowledge graph",
            relationship_id=relationship.id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type.value,
        )

        return relationship

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def find_entities(
        self,
        name: str | None = None,
        entity_type: EntityType | None = None,
        min_connections: int = 0,
    ) -> list[Entity]:
        """
        Find entities matching criteria.

        Args:
            name: Name to search for (partial match)
            entity_type: Filter by type
            min_connections: Minimum connection count

        Returns:
            List of matching entities
        """
        results = list(self._entities.values())

        # Filter by name
        if name:
            name_lower = name.lower()
            results = [
                e for e in results
                if name_lower in e.name.lower() or
                   any(name_lower in a.lower() for a in e.aliases)
            ]

        # Filter by type
        if entity_type:
            results = [e for e in results if e.type == entity_type]

        # Filter by connections
        if min_connections > 0:
            results = [e for e in results if e.connection_count >= min_connections]

        return results

    def get_relationships(
        self,
        entity_id: str | None = None,
        relationship_type: RelationshipType | None = None,
        as_source: bool = True,
        as_target: bool = True,
    ) -> list[Relationship]:
        """
        Get relationships matching criteria.

        Args:
            entity_id: Filter by entity involvement
            relationship_type: Filter by type
            as_source: Include relationships where entity is source
            as_target: Include relationships where entity is target

        Returns:
            List of matching relationships
        """
        results = []

        for rel in self._relationships.values():
            # Filter by type
            if relationship_type and rel.type != relationship_type:
                continue

            # Filter by entity involvement
            if entity_id:
                is_source = rel.source_id == entity_id
                is_target = rel.target_id == entity_id

                if as_source and is_source:
                    results.append(rel)
                elif as_target and is_target:
                    results.append(rel)
            else:
                results.append(rel)

        return results

    def get_neighbors(
        self,
        entity_id: str,
        relationship_types: list[RelationshipType] | None = None,
        direction: str = "both",  # "outgoing", "incoming", "both"
    ) -> list[tuple[Entity, Relationship]]:
        """
        Get neighboring entities.

        Args:
            entity_id: Central entity ID
            relationship_types: Filter by relationship types
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of (neighbor_entity, relationship) tuples
        """
        neighbors = []

        for rel in self._relationships.values():
            # Filter by entity involvement
            if rel.source_id != entity_id and rel.target_id != entity_id:
                continue

            # Filter by direction
            if direction == "outgoing" and rel.source_id != entity_id:
                continue
            if direction == "incoming" and rel.target_id != entity_id:
                continue

            # Filter by relationship type
            if relationship_types and rel.type not in relationship_types:
                continue

            # Get the neighbor entity
            neighbor_id = rel.target_id if rel.source_id == entity_id else rel.source_id
            neighbor = self._entities.get(neighbor_id)

            if neighbor:
                neighbors.append((neighbor, rel))

        return neighbors

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> list[tuple[Entity, Relationship]] | None:
        """
        Find a path between two entities.

        Uses BFS to find the shortest path.

        Args:
            source_id: Start entity ID
            target_id: End entity ID
            max_depth: Maximum path length

        Returns:
            Path as list of (entity, relationship) tuples, or None
        """
        if source_id not in self._entities or target_id not in self._entities:
            return None

        if source_id == target_id:
            return [(self._entities[source_id], None)]

        # BFS
        visited = {source_id}
        queue = [(source_id, [])]  # (current_id, path_so_far)

        while queue:
            current_id, path = queue.pop(0)

            # Check depth limit
            if len(path) >= max_depth:
                continue

            # Get neighbors
            for neighbor, rel in self.get_neighbors(current_id):
                if neighbor.id == target_id:
                    return [*path, (neighbor, rel)]

                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, [*path, (neighbor, rel)]))

        return None

    def find_clusters(
        self,
        min_size: int = 3,
        max_distance: int = 2,
    ) -> list[list[Entity]]:
        """
        Find clusters of closely related entities.

        Args:
            min_size: Minimum cluster size
            max_distance: Maximum distance for clustering

        Returns:
            List of entity clusters
        """
        clusters = []
        assigned = set()

        for entity_id in self._entities:
            if entity_id in assigned:
                continue

            # BFS to find connected entities
            cluster = {entity_id}
            queue = [entity_id]

            while queue:
                current = queue.pop(0)

                for neighbor, rel in self.get_neighbors(current):
                    if neighbor.id not in cluster:
                        # Check if within distance threshold
                        if rel.weight >= (1.0 / max_distance):
                            cluster.add(neighbor.id)
                            queue.append(neighbor.id)

            # Add to assigned
            if len(cluster) >= min_size:
                clusters.append([self._entities[eid] for eid in cluster])
                assigned.update(cluster)

        return clusters

    def get_statistics(self) -> dict[str, Any]:
        """Get knowledge graph statistics."""
        entity_types = {}
        for entity in self._entities.values():
            entity_types[entity.type.value] = entity_types.get(entity.type.value, 0) + 1

        relationship_types = {}
        for rel in self._relationships.values():
            relationship_types[rel.type.value] = relationship_types.get(rel.type.value, 0) + 1

        return {
            "entity_count": len(self._entities),
            "relationship_count": len(self._relationships),
            "entity_types": entity_types,
            "relationship_types": relationship_types,
            "avg_connections": (
                sum(e.connection_count for e in self._entities.values()) /
                len(self._entities) if self._entities else 0
            ),
        }
