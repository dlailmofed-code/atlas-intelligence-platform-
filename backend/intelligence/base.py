"""
ATLAS Platform - Intelligence Engine

This module implements the core intelligence engine for business opportunity analysis.
Based on the specifications, it includes:
- Intelligence Signals Framework
- Causal Intelligence Framework
- Knowledge Graph
- Cross-Domain Intelligence
- Intelligence Lifecycle

The engine transforms raw data into actionable business intelligence through
a multi-stage process: Raw Information -> Evidence -> Signals -> Patterns -> Insights.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SignalType(StrEnum):
    """Types of intelligence signals."""

    DEMAND = "demand"           # Market demand indicators
    GROWTH = "growth"          # Growth indicators
    INNOVATION = "innovation"  # Innovation and technology
    INVESTMENT = "investment"  # Investment activity
    REGULATORY = "regulatory" # Regulatory changes
    COMPETITION = "competition"  # Competitive landscape
    SOCIAL = "social"          # Social trends
    ECONOMIC = "economic"      # Economic indicators
    TECHNOLOGY = "technology"  # Technology adoption


class SignalCategory(StrEnum):
    """Categories for signal classification."""

    MARKET = "market"
    REGULATION = "regulation"
    TECHNOLOGY = "technology"
    FINANCIAL = "financial"
    SOCIAL = "social"
    COMPETITION = "competition"
    OPERATIONAL = "operational"
    GEOPOLITICAL = "geopolitical"


class SignalTrend(StrEnum):
    """Trend direction for signals."""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"


class RelationshipType(StrEnum):
    """Types of causal relationships."""

    CORRELATION = "correlation"
    POSSIBLE_CAUSATION = "possible_causation"
    STRONG_EVIDENCE = "strong_evidence"
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"


class ConfidenceLevel(StrEnum):
    """Confidence levels for intelligence."""

    VERY_LOW = "very_low"      # < 0.2
    LOW = "low"               # 0.2 - 0.4
    MEDIUM = "medium"         # 0.4 - 0.6
    HIGH = "high"            # 0.6 - 0.8
    VERY_HIGH = "very_high"   # > 0.8


class EvidenceSource(BaseModel):
    """Evidence source information."""

    source_id: str
    source_name: str
    source_type: str  # news, academic, government, financial, social
    reliability: float = Field(ge=0.0, le=1.0)
    last_updated: datetime
    url: str | None = None


class Evidence(BaseModel):
    """Evidence supporting intelligence."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    summary: str
    source: EvidenceSource
    relevance: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    entities: list[str] = Field(default_factory=list)
    verified: bool = False


class IntelligenceSignal(BaseModel):
    """Intelligence signal model."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: SignalType
    category: SignalCategory
    name: str
    description: str

    # Intensity and confidence
    intensity: float = Field(ge=0.0, le=100.0, description="Signal intensity (0-100)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the signal (0-1)")
    trend: SignalTrend = SignalTrend.STABLE

    # Evidence supporting the signal
    evidence: list[Evidence] = Field(default_factory=list)

    # Context
    entities: list[str] = Field(default_factory=list)
    geography: str | None = None
    industry: str | None = None
    region: str | None = None

    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    def update_intensity(self, new_intensity: float) -> None:
        """Update signal intensity with smoothing."""
        self.intensity = (self.intensity * 0.7) + (new_intensity * 0.3)
        self.updated_at = datetime.utcnow()

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the signal."""
        self.evidence.append(evidence)
        self._recalculate_confidence()
        self.updated_at = datetime.utcnow()

    def _recalculate_confidence(self) -> None:
        """Recalculate confidence based on evidence."""
        if not self.evidence:
            self.confidence = 0.0
            return

        # Weight by reliability and number of sources
        total_reliability = sum(e.source.reliability for e in self.evidence)
        avg_reliability = total_reliability / len(self.evidence)

        # Factor in number of sources (more sources = higher confidence)
        source_factor = min(len(self.evidence) / 5.0, 1.0)

        # Factor in verification status
        verified_count = sum(1 for e in self.evidence if e.verified)
        verification_factor = verified_count / len(self.evidence) if self.evidence else 0

        self.confidence = (
            avg_reliability * 0.4 +
            source_factor * 0.3 +
            verification_factor * 0.3
        )


class Pattern(BaseModel):
    """Detected pattern from multiple signals."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    pattern_type: str  # trend, convergence, divergence, cycle, anomaly

    # Related signals
    signal_ids: list[str] = Field(default_factory=list)

    # Pattern metrics
    strength: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    # Implications
    implications: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)


class CausalRelationship(BaseModel):
    """Causal relationship between entities."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    cause: str
    effect: str
    relationship_type: RelationshipType

    # Evidence and confidence
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_summary: str

    # Additional context
    confounding_factors: list[str] = Field(default_factory=list)
    mechanism: str | None = None
    time_lag: str | None = None  # e.g., "2-3 months", "1 year"

    created_at: datetime = Field(default_factory=datetime.utcnow)


class Insight(BaseModel):
    """Generated insight from analysis."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    category: SignalCategory

    # Supporting data
    evidence_ids: list[str] = Field(default_factory=list)
    signal_ids: list[str] = Field(default_factory=list)
    pattern_ids: list[str] = Field(default_factory=list)

    # Impact assessment
    impact_level: str = Field(description="high, medium, low")
    urgency: str = Field(description="immediate, short_term, long_term")
    affected_sectors: list[str] = Field(default_factory=list)

    # Confidence
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty_factors: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)


class OpportunityCandidate(BaseModel):
    """Opportunity candidate identified by the intelligence engine."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str

    # Classification
    category: SignalCategory
    industry: str
    geography: str | None = None

    # Scoring
    opportunity_score: float = Field(ge=0.0, le=100.0)
    demand_score: float = Field(ge=0.0, le=100.0)
    growth_score: float = Field(ge=0.0, le=100.0)
    competition_score: float = Field(ge=0.0, le=100.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    overall_confidence: float = Field(ge=0.0, le=1.0)

    # Supporting intelligence
    evidence: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)

    # Analysis
    key_insights: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
