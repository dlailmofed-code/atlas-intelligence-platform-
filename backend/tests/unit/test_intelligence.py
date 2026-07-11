"""
ATLAS Platform - Intelligence Engine Unit Tests
"""

from datetime import datetime

from backend.intelligence.base import (
    Evidence,
    EvidenceSource,
    Insight,
    IntelligenceSignal,
    Pattern,
    SignalCategory,
    SignalTrend,
    SignalType,
)


def create_test_evidence():
    """Create test evidence with required fields."""
    return Evidence(
        content="Test evidence content",
        summary="Summary of evidence",
        source=EvidenceSource(
            source_id="source-1",
            source_name="Test News",
            source_type="news",
            reliability=0.8,
            last_updated=datetime.utcnow(),
            url="https://example.com",
        ),
        relevance=0.85,
        weight=0.5,
    )


class TestEvidence:
    """Test Evidence functionality."""

    def test_create_evidence(self):
        """Test creating evidence."""
        evidence = create_test_evidence()

        assert evidence.content == "Test evidence content"
        assert evidence.source.source_type == "news"
        assert evidence.relevance == 0.85
        assert evidence.verified is False

    def test_evidence_default_values(self):
        """Test evidence default values."""
        evidence = Evidence(
            content="Test content",
            summary="Test summary",
            source=EvidenceSource(
                source_id="source-2",
                source_name="Test",
                source_type="web",
                reliability=0.5,
                last_updated=datetime.utcnow(),
            ),
            relevance=0.5,
            weight=0.5,
        )

        assert evidence.relevance >= 0.0
        assert evidence.verified is False
        assert evidence.entities == []


class TestSignal:
    """Test Signal functionality."""

    def test_create_signal(self):
        """Test creating a signal."""
        signal = IntelligenceSignal(
            type=SignalType.GROWTH,
            category=SignalCategory.TECHNOLOGY,
            name="Test Signal",
            description="A test signal",
            intensity=75.0,
            confidence=0.90,
        )

        assert signal.name == "Test Signal"
        assert signal.intensity == 75.0
        assert signal.confidence == 0.90

    def test_signal_default_values(self):
        """Test signal default values."""
        signal = IntelligenceSignal(
            type=SignalType.DEMAND,
            category=SignalCategory.MARKET,
            name="Test",
            description="Test",
            intensity=50.0,
            confidence=0.5,
        )

        assert signal.intensity >= 0.0
        assert signal.confidence >= 0.0
        assert signal.trend == SignalTrend.STABLE

    def test_signal_to_dict(self):
        """Test signal serialization."""
        signal = IntelligenceSignal(
            id="test-id",
            type=SignalType.INVESTMENT,
            category=SignalCategory.MARKET,
            name="Test Signal",
            description="Test",
            intensity=50.0,
            confidence=0.5,
        )

        data = signal.model_dump()

        assert data["id"] == "test-id"
        assert data["name"] == "Test Signal"
        assert "intensity" in data
        assert "confidence" in data


class TestPattern:
    """Test Pattern functionality."""

    def test_create_pattern(self):
        """Test creating a pattern."""
        pattern = Pattern(
            name="Test Pattern",
            description="A test pattern",
            pattern_type="convergence",
            strength=0.85,
            confidence=0.85,
        )

        assert pattern.name == "Test Pattern"
        assert pattern.pattern_type == "convergence"
        assert pattern.confidence == 0.85

    def test_pattern_to_dict(self):
        """Test pattern serialization."""
        pattern = Pattern(
            id="pattern-id",
            name="Test Pattern",
            description="Test",
            pattern_type="trend",
            strength=0.5,
            confidence=0.5,
        )

        data = pattern.model_dump()

        assert data["id"] == "pattern-id"
        assert data["name"] == "Test Pattern"
        assert "created_at" in data


class TestInsight:
    """Test Insight functionality."""

    def test_create_insight(self):
        """Test creating an insight."""
        insight = Insight(
            title="Test Insight",
            description="A test insight",
            category=SignalCategory.MARKET,
            impact_level="high",
            urgency="short_term",
            confidence=0.90,
        )

        assert insight.title == "Test Insight"
        assert insight.impact_level == "high"
        assert insight.confidence == 0.90

    def test_insight_impact_levels(self):
        """Test insight impact levels."""
        high = Insight(
            title="High Impact",
            description="Test",
            category=SignalCategory.MARKET,
            impact_level="high",
            urgency="immediate",
            confidence=0.5,
        )
        assert high.impact_level == "high"

        low = Insight(
            title="Low Impact",
            description="Test",
            category=SignalCategory.MARKET,
            impact_level="low",
            urgency="long_term",
            confidence=0.5,
        )
        assert low.impact_level == "low"

    def test_insight_to_dict(self):
        """Test insight serialization."""
        insight = Insight(
            id="insight-id",
            title="Test Insight",
            description="Test",
            category=SignalCategory.MARKET,
            impact_level="medium",
            urgency="short_term",
            confidence=0.5,
        )

        data = insight.model_dump()

        assert data["id"] == "insight-id"
        assert data["title"] == "Test Insight"
        assert "confidence" in data
        assert "impact_level" in data


class TestIntelligencePipeline:
    """Test intelligence processing pipeline."""

    def test_evidence_to_signal(self):
        """Test processing evidence into signals."""
        evidence = create_test_evidence()

        # Simulate signal extraction
        signal = IntelligenceSignal(
            type=SignalType.GROWTH,
            category=SignalCategory.MARKET,
            name=f"Signal from {evidence.source.source_name}",
            description=evidence.content,
            intensity=evidence.relevance * 100,
            confidence=0.7,
        )

        assert signal.name == "Signal from Test News"
        assert signal.intensity >= 0

    def test_multiple_signals_to_pattern(self):
        """Test combining multiple signals into a pattern."""
        signals = [
            IntelligenceSignal(
                type=SignalType.TECHNOLOGY,
                category=SignalCategory.TECHNOLOGY,
                name=f"Signal {i}",
                description="Test",
                intensity=70.0,
                confidence=0.7,
            )
            for i in range(3)
        ]

        # Calculate pattern confidence from signals
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        avg_strength = avg_confidence

        pattern = Pattern(
            name="Combined Pattern",
            description="Pattern from multiple signals",
            pattern_type="convergence",
            strength=avg_strength,
            confidence=avg_confidence,
            signal_ids=[s.id for s in signals],
        )

        assert pattern.pattern_type == "convergence"
        assert pattern.strength >= 0
