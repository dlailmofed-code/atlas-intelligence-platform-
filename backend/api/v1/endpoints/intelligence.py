"""
ATLAS Platform - Intelligence Engine Endpoints

This module contains endpoints for the intelligence engine,
signal processing, and causal reasoning capabilities.
"""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.core.logging import get_logger
from backend.intelligence import (
    IntelligenceEngine,
    create_intelligence_engine,
)

logger = get_logger(__name__)

router = APIRouter()

# Global intelligence engine instance
_intelligence_engine: IntelligenceEngine | None = None


def get_intelligence_engine() -> IntelligenceEngine:
    """Get or create intelligence engine instance."""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = create_intelligence_engine()
    return _intelligence_engine


class SignalSource(BaseModel):
    """Signal data source information."""

    source_id: str
    source_name: str
    source_type: str
    reliability: float = Field(description="Source reliability score (0-1)")
    last_updated: str


class IntelligenceSignal(BaseModel):
    """Intelligence signal model."""

    id: str
    type: str
    name: str
    description: str
    category: str
    intensity: float = Field(description="Signal intensity (0-100)")
    trend: str = Field(description="up, down, stable")
    confidence: float = Field(description="Confidence in the signal (0-1)")
    sources: list[SignalSource] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    geography: str | None = None
    industry: str | None = None
    detected_at: str
    updated_at: str


class PatternAnalysis(BaseModel):
    """Pattern analysis result."""

    id: str
    name: str
    description: str
    pattern_type: str
    signals: list[str] = Field(description="Signal IDs involved")
    strength: float = Field(description="Pattern strength (0-1)")
    implications: list[str]
    confidence: float
    created_at: str


class CausalLink(BaseModel):
    """Causal relationship between entities."""

    cause: str
    effect: str
    relationship_type: str = Field(
        description="correlation, possible_causation, strong_evidence, confirmed, unknown"
    )
    confidence: float
    evidence_summary: str
    confounding_factors: list[str] = Field(default_factory=list)


class KnowledgeGraphNode(BaseModel):
    """Knowledge graph node."""

    id: str
    type: str
    name: str
    properties: dict = Field(default_factory=dict)
    connections: int = 0


class KnowledgeGraphEdge(BaseModel):
    """Knowledge graph edge."""

    source: str
    target: str
    relationship: str
    weight: float = 1.0


class IntelligenceQuery(BaseModel):
    """Intelligence query for analysis."""

    query: str = Field(min_length=3, description="Natural language query")
    domain: str | None = Field(default=None, description="Domain filter")
    geography: str | None = Field(default=None, description="Geographic filter")
    industry: str | None = Field(default=None, description="Industry filter")
    max_results: int = Field(default=10, ge=1, le=50)


class IntelligenceAnalysis(BaseModel):
    """Intelligence analysis result."""

    query: str
    summary: str
    insights: list[str]
    related_signals: list[str]
    related_opportunities: list[str]
    confidence: float
    sources: list[str]
    generated_at: str


class IntelligenceIndicators(BaseModel):
    """Intelligence indicators dashboard."""

    opportunity_score: float
    demand_index: float
    market_momentum: float
    capital_attraction: float
    competition_index: float
    innovation_index: float
    risk_index: float
    geographic_opportunity: float
    generated_at: str


class ProcessDataRequest(BaseModel):
    """Request to process raw data through intelligence engine."""

    data: list[dict[str, Any]] = Field(description="Raw data to process")
    context: dict[str, Any] | None = Field(
        default=None,
        description="Optional context (region, industry, etc.)"
    )


class ProcessDataResponse(BaseModel):
    """Response from processing data."""

    signal_count: int
    pattern_count: int
    insight_count: int
    opportunity_count: int
    indicators: IntelligenceIndicators


@router.get("/signals/", response_model=list[IntelligenceSignal])
async def list_signals(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    category: str | None = None,
    type: str | None = None,
    min_intensity: float | None = Query(default=None, ge=0, le=100),
) -> list[IntelligenceSignal]:
    """
    List intelligence signals.

    Args:
        page: Page number
        page_size: Items per page
        category: Filter by category
        type: Filter by signal type
        min_intensity: Minimum intensity filter

    Returns:
        List of intelligence signals
    """
    # Get signals - in production, this would query the database
    # via the intelligence engine
    mock_signals = [
        IntelligenceSignal(
            id="sig_001",
            type="market",
            name="AI Healthcare Investment Surge",
            description="Significant increase in venture capital investment in AI-powered healthcare solutions.",
            category="Investment",
            intensity=85.0,
            trend="up",
            confidence=0.92,
            sources=[
                SignalSource(
                    source_id="src_001",
                    source_name="Crunchbase",
                    source_type="Financial",
                    reliability=0.9,
                    last_updated="2026-07-10",
                ),
            ],
            entities=["AI", "Healthcare", "Venture Capital"],
            geography="Global",
            industry="Healthcare",
            detected_at="2026-07-08T10:00:00Z",
            updated_at="2026-07-10T12:00:00Z",
        ),
        IntelligenceSignal(
            id="sig_002",
            type="regulatory",
            name="EU Green Deal Acceleration",
            description="EU accelerating green deal initiatives with new funding and regulations.",
            category="Regulation",
            intensity=78.0,
            trend="up",
            confidence=0.88,
            sources=[
                SignalSource(
                    source_id="src_002",
                    source_name="EU Official",
                    source_type="Government",
                    reliability=0.95,
                    last_updated="2026-07-09",
                ),
            ],
            entities=["EU", "Green Energy", "Sustainability"],
            geography="Europe",
            detected_at="2026-07-05T08:00:00Z",
            updated_at="2026-07-09T15:00:00Z",
        ),
    ]

    return mock_signals


@router.get("/signals/{signal_id}", response_model=IntelligenceSignal)
async def get_signal(signal_id: str) -> IntelligenceSignal:
    """
    Get detailed information about a signal.

    Args:
        signal_id: Signal ID

    Returns:
        Signal details
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Signal not found",
    )


@router.get("/patterns/", response_model=list[PatternAnalysis])
async def list_patterns(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[PatternAnalysis]:
    """
    List detected patterns.

    Args:
        limit: Maximum number of patterns

    Returns:
        List of detected patterns
    """
    return []


@router.get("/causal-links/", response_model=list[CausalLink])
async def list_causal_links(
    entity: str | None = None,
    relationship_type: str | None = None,
    min_confidence: float = Query(default=0.5, ge=0, le=1),
) -> list[CausalLink]:
    """
    List causal relationships.

    Args:
        entity: Filter by entity
        relationship_type: Filter by relationship type
        min_confidence: Minimum confidence threshold

    Returns:
        List of causal links
    """
    return []


@router.get("/knowledge-graph/nodes", response_model=list[KnowledgeGraphNode])
async def list_graph_nodes(
    type: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[KnowledgeGraphNode]:
    """
    List knowledge graph nodes.

    Args:
        type: Filter by node type
        limit: Maximum nodes to return

    Returns:
        List of graph nodes
    """
    return []


@router.get("/knowledge-graph/edges", response_model=list[KnowledgeGraphEdge])
async def list_graph_edges(
    source: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[KnowledgeGraphEdge]:
    """
    List knowledge graph edges.

    Args:
        source: Filter by source node
        limit: Maximum edges to return

    Returns:
        List of graph edges
    """
    return []


@router.post("/process", response_model=ProcessDataResponse)
async def process_data(request: ProcessDataRequest) -> ProcessDataResponse:
    """
    Process raw data through the intelligence engine.

    This endpoint transforms raw data into intelligence through the full lifecycle:
    Evidence -> Signals -> Patterns -> Insights -> Opportunities -> Indicators

    Args:
        request: Process data request

    Returns:
        Intelligence processing results
    """
    engine = get_intelligence_engine()

    try:
        # Process data through intelligence engine
        results = engine.process_raw_data(request.data)

        # Extract indicators
        indicators = results["indicators"]

        logger.info(
            "Intelligence processing complete",
            signal_count=len(results["signals"]),
            pattern_count=len(results["patterns"]),
            insight_count=len(results["insights"]),
            opportunity_count=len(results["opportunities"]),
        )

        return ProcessDataResponse(
            signal_count=len(results["signals"]),
            pattern_count=len(results["patterns"]),
            insight_count=len(results["insights"]),
            opportunity_count=len(results["opportunities"]),
            indicators=IntelligenceIndicators(
                opportunity_score=indicators.opportunity_score,
                demand_index=indicators.demand_index,
                market_momentum=indicators.market_momentum,
                capital_attraction=indicators.capital_attraction,
                competition_index=indicators.competition_index,
                innovation_index=indicators.innovation_index,
                risk_index=indicators.risk_index,
                geographic_opportunity=indicators.geographic_opportunity,
                generated_at=indicators.generated_at.isoformat(),
            ),
        )

    except Exception as e:
        logger.error("Intelligence processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence processing failed: {e!s}",
        )


@router.post("/query", response_model=IntelligenceAnalysis)
async def query_intelligence(
    query: IntelligenceQuery,
) -> IntelligenceAnalysis:
    """
    Query the intelligence engine with natural language.

    Args:
        query: Intelligence query

    Returns:
        Analysis results
    """
    return IntelligenceAnalysis(
        query=query.query,
        summary="Based on our analysis, there are significant opportunities in the AI healthcare sector driven by increased investment and regulatory support.",
        insights=[
            "AI diagnostic tools show 94% accuracy in recent studies",
            "Regulatory bodies are increasingly approving AI medical devices",
            "Major tech companies are acquiring healthcare AI startups",
        ],
        related_signals=["sig_001", "sig_002"],
        related_opportunities=["opp_001"],
        confidence=0.85,
        sources=["PubMed", "Crunchbase", "FDA"],
        generated_at="2026-07-10T15:00:00Z",
    )


@router.get("/indicators", response_model=IntelligenceIndicators)
async def get_intelligence_indicators() -> IntelligenceIndicators:
    """
    Get current intelligence indicators dashboard.

    Returns:
        Current intelligence indicators
    """
    engine = get_intelligence_engine()
    indicators = engine.get_indicators()

    return IntelligenceIndicators(
        opportunity_score=indicators.opportunity_score,
        demand_index=indicators.demand_index,
        market_momentum=indicators.market_momentum,
        capital_attraction=indicators.capital_attraction,
        competition_index=indicators.competition_index,
        innovation_index=indicators.innovation_index,
        risk_index=indicators.risk_index,
        geographic_opportunity=indicators.geographic_opportunity,
        generated_at=indicators.generated_at.isoformat(),
    )


@router.get("/indicators/trends")
async def get_indicator_trends() -> dict[str, Any]:
    """
    Get trends for intelligence indicators over time.

    Returns:
        Indicator trends
    """
    engine = get_intelligence_engine()
    trends = engine.get_trends()
    return trends


@router.get("/state")
async def get_engine_state() -> dict[str, Any]:
    """
    Get current intelligence engine state.

    Returns:
        Current state including counts of signals, patterns, etc.
    """
    engine = get_intelligence_engine()
    return engine.get_current_state()
