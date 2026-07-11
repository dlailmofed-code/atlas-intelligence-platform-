"""
ATLAS Platform - Causal Reasoning Engine

This module implements causal reasoning for intelligence analysis.
Based on the Causal Intelligence Framework from the specifications.

Implements the principle: "Correlation does not imply causation"
by distinguishing between different types of relationships.
"""

from datetime import datetime
from typing import Any

from backend.core.logging import get_logger
from backend.intelligence.base import (
    CausalRelationship,
    Evidence,
    RelationshipType,
)

logger = get_logger(__name__)


class CausalReasoner:
    """
    Implements causal reasoning for intelligence analysis.

    Based on the Causal Intelligence Framework:
    - Classifies relationships between entities
    - Distinguishes correlation from causation
    - Identifies confounding factors
    - Communicates uncertainty transparently
    """

    # Minimum evidence required for different relationship types
    MIN_EVIDENCE_FOR_CORRELATION = 2
    MIN_EVIDENCE_FOR_POSSIBLE_CAUSATION = 3
    MIN_EVIDENCE_FOR_STRONG_EVIDENCE = 5

    def __init__(self):
        """Initialize causal reasoner."""
        self._relationships: list[CausalRelationship] = []

    def analyze_relationship(
        self,
        cause: str,
        effect: str,
        evidence: list[Evidence],
        temporal_data: list[dict] | None = None,
    ) -> CausalRelationship:
        """
        Analyze the relationship between two entities.

        Args:
            cause: The potential cause entity
            effect: The potential effect entity
            evidence: Evidence supporting the relationship
            temporal_data: Optional temporal sequence data

        Returns:
            CausalRelationship with classification and confidence
        """
        relationship_type = self._classify_relationship(evidence, temporal_data)
        confidence = self._calculate_confidence(relationship_type, evidence, temporal_data)

        relationship = CausalRelationship(
            cause=cause,
            effect=effect,
            relationship_type=relationship_type,
            confidence=confidence,
            evidence_summary=self._summarize_evidence(evidence),
            confounding_factors=self._identify_confounders(cause, effect, evidence),
            mechanism=self._infer_mechanism(evidence),
            time_lag=self._estimate_time_lag(temporal_data) if temporal_data else None,
        )

        self._relationships.append(relationship)

        logger.info(
            "Relationship analyzed",
            cause=cause,
            effect=effect,
            relationship_type=relationship_type.value,
            confidence=confidence,
        )

        return relationship

    def _classify_relationship(
        self,
        evidence: list[Evidence],
        temporal_data: list[dict] | None,
    ) -> RelationshipType:
        """
        Classify the type of relationship based on evidence.

        Classification hierarchy:
        1. UNKNOWN - Not enough evidence
        2. CORRELATION - Co-occurrence without causation
        3. POSSIBLE_CAUSATION - Some temporal and correlational support
        4. STRONG_EVIDENCE - Multiple independent sources supporting causation
        5. CONFIRMED - Known causal mechanism
        """
        if len(evidence) < self.MIN_EVIDENCE_FOR_CORRELATION:
            return RelationshipType.UNKNOWN

        # Calculate correlation strength
        correlation_strength = self._calculate_correlation_strength(evidence)

        # Check temporal precedence if data available
        has_temporal_precedence = False
        if temporal_data:
            has_temporal_precedence = self._check_temporal_precedence(temporal_data)

        # Check for confounding factors
        confounders = self._identify_confounders("", "", evidence)
        low_confounders = len(confounders) <= 1

        # Classify based on evidence
        if len(evidence) >= self.MIN_EVIDENCE_FOR_STRONG_EVIDENCE:
            if has_temporal_precedence and low_confounders and correlation_strength > 0.7:
                return RelationshipType.STRONG_EVIDENCE
            elif correlation_strength > 0.5:
                return RelationshipType.POSSIBLE_CAUSATION

        if len(evidence) >= self.MIN_EVIDENCE_FOR_POSSIBLE_CAUSATION:
            if has_temporal_precedence or low_confounders:
                return RelationshipType.POSSIBLE_CAUSATION

        if correlation_strength > 0.5:
            return RelationshipType.CORRELATION

        return RelationshipType.UNKNOWN

    def _calculate_correlation_strength(self, evidence: list[Evidence]) -> float:
        """Calculate correlation strength from evidence."""
        if not evidence:
            return 0.0

        # Weight by relevance and source reliability
        total_score = sum(
            e.relevance * e.weight * e.source.reliability
            for e in evidence
        )

        max_possible = len(evidence)

        return min(total_score / max_possible if max_possible > 0 else 0, 1.0)

    def _check_temporal_precedence(self, temporal_data: list[dict]) -> bool:
        """
        Check if cause precedes effect in temporal data.

        Args:
            temporal_data: List of temporal observations

        Returns:
            True if temporal precedence is detected
        """
        if len(temporal_data) < 2:
            return False

        # Sort by timestamp
        sorted_data = sorted(
            temporal_data,
            key=lambda x: x.get("timestamp", datetime.min),
        )

        # Check if cause typically appears before effect
        cause_times = [
            d["timestamp"]
            for d in sorted_data
            if d.get("type") == "cause"
        ]
        effect_times = [
            d["timestamp"]
            for d in sorted_data
            if d.get("type") == "effect"
        ]

        if not cause_times or not effect_times:
            return False

        avg_cause_time = sum(t for t in cause_times) / len(cause_times)
        avg_effect_time = sum(t for t in effect_times) / len(effect_times)

        return avg_cause_time < avg_effect_time

    def _identify_confounders(
        self,
        cause: str,
        effect: str,
        evidence: list[Evidence],
    ) -> list[str]:
        """
        Identify potential confounding factors.

        A confounder is a variable that influences both the cause and effect,
        creating a spurious correlation.
        """
        confounders = []

        # Common confounders to check
        common_confounders = [
            "economic conditions",
            "market sentiment",
            "seasonal factors",
            "regulatory changes",
            "technological advancement",
            "demographic shifts",
        ]

        # Check evidence for mentions of common confounders
        evidence_text = " ".join(e.content.lower() for e in evidence)

        for confounder in common_confounders:
            if confounder in evidence_text:
                confounders.append(confounder)

        return confounders

    def _summarize_evidence(self, evidence: list[Evidence]) -> str:
        """Generate a summary of the evidence."""
        if not evidence:
            return "No evidence available"

        # Group by source type
        by_type: dict[str, list[Evidence]] = {}
        for e in evidence:
            if e.source.source_type not in by_type:
                by_type[e.source.source_type] = []
            by_type[e.source.source_type].append(e)

        summary_parts = []
        for source_type, type_evidence in by_type.items():
            summary_parts.append(
                f"{len(type_evidence)} from {source_type}"
            )

        return "; ".join(summary_parts)

    def _infer_mechanism(self, evidence: list[Evidence]) -> str | None:
        """Infer the mechanism connecting cause and effect."""
        # Look for mechanism indicators in evidence
        mechanism_indicators = [
            "leads to",
            "causes",
            "results in",
            "enables",
            "drives",
            "creates",
            "prevents",
            "reduces",
            "increases",
        ]

        for e in evidence:
            content_lower = e.content.lower()
            for indicator in mechanism_indicators:
                if indicator in content_lower:
                    return f"Mechanism involves: {indicator}"

        return None

    def _estimate_time_lag(self, temporal_data: list[dict]) -> str | None:
        """Estimate time lag between cause and effect."""
        if len(temporal_data) < 2:
            return None

        sorted_data = sorted(
            temporal_data,
            key=lambda x: x.get("timestamp", datetime.min),
        )

        cause_times = [
            d["timestamp"]
            for d in sorted_data
            if d.get("type") == "cause"
        ]
        effect_times = [
            d["timestamp"]
            for d in sorted_data
            if d.get("type") == "effect"
        ]

        if cause_times and effect_times:
            avg_diff = (
                sum(e - c for c in cause_times for e in effect_times) /
                (len(cause_times) * len(effect_times))
            )

            # Convert to human-readable format
            days = avg_diff.total_seconds() / 86400

            if days < 1:
                return "immediate"
            elif days < 7:
                return f"{int(days)} days"
            elif days < 30:
                return f"{int(days / 7)} weeks"
            else:
                return f"{int(days / 30)} months"

        return None

    def _calculate_confidence(
        self,
        relationship_type: RelationshipType,
        evidence: list[Evidence],
        temporal_data: list[dict] | None,
    ) -> float:
        """Calculate confidence in the relationship classification."""
        # Base confidence by relationship type
        type_confidence = {
            RelationshipType.UNKNOWN: 0.1,
            RelationshipType.CORRELATION: 0.3,
            RelationshipType.POSSIBLE_CAUSATION: 0.5,
            RelationshipType.STRONG_EVIDENCE: 0.8,
            RelationshipType.CONFIRMED: 0.95,
        }

        base = type_confidence.get(relationship_type, 0.1)

        # Adjust for evidence quality
        if evidence:
            avg_reliability = sum(e.source.reliability for e in evidence) / len(evidence)
            verification_rate = sum(1 for e in evidence if e.verified) / len(evidence)

            evidence_factor = (
                avg_reliability * 0.7 +
                verification_rate * 0.3
            )

            base = base * 0.7 + evidence_factor * 0.3

        # Adjust for temporal data
        if temporal_data:
            base = min(base + 0.1, 1.0)

        return base

    def get_relationships(self) -> list[CausalRelationship]:
        """Get all analyzed relationships."""
        return self._relationships

    def get_relationships_by_entity(self, entity: str) -> list[CausalRelationship]:
        """Get relationships involving a specific entity."""
        return [
            r for r in self._relationships
            if r.cause == entity or r.effect == entity
        ]


class CausalGraph:
    """
    Manages a graph of causal relationships.

    Enables complex causal reasoning across multiple entities.
    """

    def __init__(self):
        """Initialize causal graph."""
        self._reasoner = CausalReasoner()
        self._nodes: dict[str, dict] = {}
        self._edges: list[tuple[str, str]] = []

    def add_entity(
        self,
        entity: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Add an entity to the graph."""
        if entity not in self._nodes:
            self._nodes[entity] = {
                "properties": properties or {},
                "connections": 0,
            }

    def add_relationship(
        self,
        cause: str,
        effect: str,
        evidence: list[Evidence],
        temporal_data: list[dict] | None = None,
    ) -> CausalRelationship:
        """Add a causal relationship to the graph."""
        # Add nodes if they don't exist
        self.add_entity(cause)
        self.add_entity(effect)

        # Add edge
        self._edges.append((cause, effect))
        self._nodes[cause]["connections"] += 1
        self._nodes[effect]["connections"] += 1

        # Analyze and store relationship
        return self._reasoner.analyze_relationship(
            cause, effect, evidence, temporal_data
        )

    def get_causes(self, entity: str) -> list[CausalRelationship]:
        """Get all causes of an entity."""
        return [
            r for r in self._reasoner.get_relationships()
            if r.effect == entity
        ]

    def get_effects(self, entity: str) -> list[CausalRelationship]:
        """Get all effects of an entity."""
        return [
            r for r in self._reasoner.get_relationships()
            if r.cause == entity
        ]

    def find_path(self, source: str, target: str) -> list[str] | None:
        """
        Find a causal path between two entities.

        Uses BFS to find the shortest path.
        """
        if source not in self._nodes or target not in self._nodes:
            return None

        if source == target:
            return [source]

        visited = {source}
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)

            for _, neighbor in self._edges:
                if current == _ and neighbor not in visited:
                    new_path = [*path, neighbor]

                    if neighbor == target:
                        return new_path

                    visited.add(neighbor)
                    queue.append((neighbor, new_path))

        return None

    def get_influence_score(self, entity: str) -> float:
        """
        Calculate influence score for an entity.

        Based on number of connections and strength of relationships.
        """
        relationships = self.get_effects(entity)

        if not relationships:
            return 0.0

        total_strength = sum(r.confidence for r in relationships)
        connection_count = len(relationships)

        # Score = average confidence * log(connection count + 1)
        import math
        return total_strength * math.log(connection_count + 1, 2)
