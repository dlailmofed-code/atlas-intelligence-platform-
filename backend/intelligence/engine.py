"""
ATLAS Platform - Intelligence Engine Orchestrator

This module orchestrates all intelligence components into a unified engine.
Based on the Intelligence Lifecycle from the specifications:
1. Raw Information -> 2. Evidence -> 3. Signals -> 4. Patterns -> 5. Insights
-> 6. Hypotheses -> 7. Validation -> 8. Ranking -> 9. Recommendation -> 10. Report
"""

from datetime import datetime
from typing import Any

from backend.core.logging import get_logger
from backend.intelligence.base import (
    Evidence,
    Insight,
    IntelligenceSignal,
    OpportunityCandidate,
    Pattern,
    SignalCategory,
    SignalType,
)
from backend.intelligence.causal.reasoning import CausalReasoner
from backend.intelligence.indicators.engine import (
    IndicatorEngine,
    IndicatorTrendAnalyzer,
    IntelligenceIndicators,
)
from backend.intelligence.knowledge.graph import KnowledgeGraph
from backend.intelligence.patterns.detector import InsightGenerator, PatternDetector
from backend.intelligence.signals.detector import SignalAggregator, SignalDetector

logger = get_logger(__name__)


class IntelligenceEngine:
    """
    Main intelligence engine orchestrator.

    Coordinates all intelligence components to transform
    raw data into actionable business intelligence.

    Intelligence Lifecycle:
    1. Raw Information -> 2. Evidence
    3. Signals
    4. Patterns
    5. Insights
    6. Hypotheses
    7. Validation
    8. Ranking
    9. Recommendations
    10. Reports
    """

    def __init__(self):
        """Initialize the intelligence engine."""
        # Initialize components
        self._signal_detector = SignalDetector()
        self._signal_aggregator = SignalAggregator()
        self._pattern_detector = PatternDetector()
        self._insight_generator = InsightGenerator()
        self._causal_reasoner = CausalReasoner()
        self._knowledge_graph = KnowledgeGraph()
        self._indicator_engine = IndicatorEngine()
        self._trend_analyzer = IndicatorTrendAnalyzer()

        # State
        self._current_signals: list[IntelligenceSignal] = []
        self._current_patterns: list[Pattern] = []
        self._current_insights: list[Insight] = []
        self._current_opportunities: list[OpportunityCandidate] = []

    def process_raw_data(
        self,
        raw_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Process raw data through the intelligence lifecycle.

        Args:
            raw_data: List of raw data items

        Returns:
            Dictionary containing all intelligence outputs
        """
        logger.info("Processing raw data", item_count=len(raw_data))

        # Step 1: Extract evidence
        evidence = self._extract_evidence(raw_data)
        logger.info("Evidence extracted", count=len(evidence))

        # Step 2-3: Detect signals
        signals = self._signal_detector.detect_signals(evidence)
        self._current_signals = signals
        logger.info("Signals detected", count=len(signals))

        # Step 4: Detect patterns
        patterns = self._pattern_detector.detect_patterns(signals)
        self._current_patterns = patterns
        logger.info("Patterns detected", count=len(patterns))

        # Step 5: Generate insights
        insights = self._insight_generator.generate_insights(signals, patterns)
        self._current_insights = insights
        logger.info("Insights generated", count=len(insights))

        # Step 6-8: Generate and rank opportunities
        opportunities = self._generate_opportunities(signals, patterns, insights)
        self._current_opportunities = opportunities
        logger.info("Opportunities generated", count=len(opportunities))

        # Calculate indicators
        indicators = self._indicator_engine.calculate_indicators(signals, patterns)
        self._trend_analyzer.add_indicators(indicators)

        return {
            "evidence": evidence,
            "signals": signals,
            "patterns": patterns,
            "insights": insights,
            "opportunities": opportunities,
            "indicators": indicators,
        }

    def _extract_evidence(self, raw_data: list[dict[str, Any]]) -> list[Evidence]:
        """
        Extract evidence from raw data.

        In production, this would use NLP and extraction models.
        """
        from backend.intelligence.base import EvidenceSource

        evidence_list = []

        for item in raw_data:
            # Extract content
            content = item.get("content", "")
            summary = item.get("summary", content[:200])
            source_type = item.get("source_type", "unknown")
            source_name = item.get("source_name", "Unknown Source")

            # Create evidence source
            source = EvidenceSource(
                source_id=item.get("source_id", "unknown"),
                source_name=source_name,
                source_type=source_type,
                reliability=item.get("reliability", 0.5),
                last_updated=item.get("updated_at", datetime.utcnow()),
                url=item.get("url"),
            )

            # Create evidence
            evidence = Evidence(
                content=content,
                summary=summary,
                source=source,
                relevance=item.get("relevance", 0.5),
                weight=item.get("weight", 1.0),
                entities=item.get("entities", []),
                verified=item.get("verified", False),
            )

            evidence_list.append(evidence)

        return evidence_list

    def _generate_opportunities(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
        insights: list[Insight],
    ) -> list[OpportunityCandidate]:
        """Generate and rank opportunity candidates."""
        from backend.intelligence.base import SignalCategory

        opportunities = []

        # Group signals by category
        by_category: dict[SignalCategory, list[IntelligenceSignal]] = {}
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal)

        # Generate opportunity for each category with strong signals
        for category, category_signals in by_category.items():
            avg_intensity = sum(s.intensity for s in category_signals) / len(category_signals)

            if avg_intensity >= 60:  # Threshold for opportunity generation
                opportunity = self._create_opportunity(
                    category=category,
                    signals=category_signals,
                    patterns=[p for p in patterns if p.strength >= 0.5],
                    insights=[i for i in insights if i.confidence >= 0.5],
                )
                opportunities.append(opportunity)

        # Rank opportunities
        opportunities.sort(key=lambda o: o.opportunity_score, reverse=True)

        return opportunities

    def _create_opportunity(
        self,
        category: SignalCategory,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
        insights: list[Insight],
    ) -> OpportunityCandidate:
        """Create an opportunity candidate from signals."""
        from backend.intelligence.base import OpportunityCandidate

        # Calculate scores
        opportunity_score = sum(s.intensity for s in signals) / len(signals)

        # Demand signals
        demand_signals = [s for s in signals if s.type == SignalType.DEMAND]
        demand_score = sum(s.intensity for s in demand_signals) / len(demand_signals) if demand_signals else 50

        # Growth signals
        growth_signals = [s for s in signals if s.type == SignalType.GROWTH]
        growth_score = sum(s.intensity for s in growth_signals) / len(growth_signals) if growth_signals else 50

        # Competition signals
        competition_signals = [s for s in signals if s.type == SignalType.COMPETITION]
        competition_score = sum(s.intensity for s in competition_signals) / len(competition_signals) if competition_signals else 50

        # Risk assessment
        risk_score = 100 - opportunity_score * 0.3

        # Confidence
        confidence = sum(s.confidence for s in signals) / len(signals)

        # Collect evidence and insight IDs
        evidence_ids = [e.id for s in signals for e in s.evidence]
        signal_ids = [s.id for s in signals]
        insight_ids = [i.id for i in insights]
        pattern_ids = [p.id for p in patterns]

        # Generate insights
        key_insights = [i.title for i in insights[:5]]
        recommended_actions = self._generate_recommendations(signals, patterns)

        return OpportunityCandidate(
            title=f"{category.value.capitalize()} Opportunity",
            description=self._generate_description(signals, category),
            category=category,
            industry=self._extract_industry(signals),
            opportunity_score=opportunity_score,
            demand_score=demand_score,
            growth_score=growth_score,
            competition_score=competition_score,
            risk_score=risk_score,
            overall_confidence=confidence,
            evidence=evidence_ids[:10],
            signals=signal_ids,
            insights=insight_ids[:5],
            patterns=pattern_ids,
            key_insights=key_insights,
            recommended_actions=recommended_actions,
        )

    def _generate_description(
        self,
        signals: list[IntelligenceSignal],
        category: SignalCategory,
    ) -> str:
        """Generate opportunity description from signals."""
        summaries = [s.description[:100] for s in signals[:3]]
        return f"{category.value.capitalize()} opportunity identified based on: " + "; ".join(summaries)

    def _extract_industry(self, signals: list[IntelligenceSignal]) -> str:
        """Extract dominant industry from signals."""
        industries = [s.industry for s in signals if s.industry]
        if not industries:
            return "General"

        from collections import Counter
        return Counter(industries).most_common(1)[0][0]

    def _generate_recommendations(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> list[str]:
        """Generate recommended actions."""
        recommendations = []

        # Based on signal types
        signal_types = {s.type for s in signals}

        if SignalType.DEMAND in signal_types:
            recommendations.append("Investigate market demand drivers and validate opportunity")

        if SignalType.GROWTH in signal_types:
            recommendations.append("Assess growth potential and competitive landscape")

        if SignalType.INVESTMENT in signal_types:
            recommendations.append("Explore funding opportunities and investor interest")

        if SignalType.INNOVATION in signal_types:
            recommendations.append("Evaluate innovation potential and technology readiness")

        if SignalType.REGULATORY in signal_types:
            recommendations.append("Review regulatory requirements and compliance needs")

        # Based on patterns
        if any(p.pattern_type == "convergence" for p in patterns):
            recommendations.append("Strong convergence suggests high confidence - consider rapid action")

        if any(p.pattern_type == "burst" for p in patterns):
            recommendations.append("Signal burst detected - monitor for emerging trends")

        return recommendations[:5]  # Return top 5 recommendations

    def get_current_state(self) -> dict[str, Any]:
        """Get current intelligence state."""
        return {
            "signal_count": len(self._current_signals),
            "pattern_count": len(self._current_patterns),
            "insight_count": len(self._current_insights),
            "opportunity_count": len(self._current_opportunities),
        }

    def get_indicators(self) -> IntelligenceIndicators:
        """Get current intelligence indicators."""
        return self._indicator_engine.calculate_indicators(
            self._current_signals,
            self._current_patterns,
        )

    def get_trends(self) -> dict[str, Any]:
        """Get indicator trends over time."""
        return self._trend_analyzer.get_trends()


def create_intelligence_engine() -> IntelligenceEngine:
    """Factory function to create an intelligence engine instance."""
    return IntelligenceEngine()
