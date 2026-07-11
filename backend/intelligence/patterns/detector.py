"""
ATLAS Platform - Pattern Detector

This module implements pattern detection from signals.
Based on the Intelligence Signals Framework from the specifications.

Implements the Pattern Discovery phase:
Signals -> Patterns -> Insights
"""

from datetime import datetime, timedelta

from backend.core.logging import get_logger
from backend.intelligence.base import (
    Insight,
    IntelligenceSignal,
    Pattern,
    SignalCategory,
    SignalTrend,
    SignalType,
)

logger = get_logger(__name__)


class PatternDetector:
    """
    Detects patterns from intelligence signals.

    Implements pattern discovery to identify:
    - Converging trends
    - Diverging indicators
    - Cyclical patterns
    - Emerging clusters
    - Anomalies
    """

    # Minimum signals required for pattern detection
    MIN_SIGNALS_FOR_PATTERN = 2

    # Signal type groupings for pattern detection
    SIGNAL_GROUPS = {
        "bullish": [SignalType.DEMAND, SignalType.GROWTH, SignalType.INVESTMENT],
        "bearish": [SignalType.COMPETITION, SignalType.REGULATORY],
        "innovation_driven": [SignalType.INNOVATION, SignalType.TECHNOLOGY],
        "market_sentiment": [SignalType.SOCIAL, SignalType.ECONOMIC],
    }

    def __init__(self):
        """Initialize pattern detector."""
        self._detected_patterns: list[Pattern] = []

    def detect_patterns(
        self,
        signals: list[IntelligenceSignal],
        min_strength: float = 0.5,
    ) -> list[Pattern]:
        """
        Detect patterns from signals.

        Args:
            signals: List of signals to analyze
            min_strength: Minimum pattern strength threshold

        Returns:
            List of detected patterns
        """
        patterns = []

        # Detect different pattern types
        convergence_patterns = self._detect_convergence(signals)
        patterns.extend(convergence_patterns)

        divergence_patterns = self._detect_divergence(signals)
        patterns.extend(divergence_patterns)

        trend_patterns = self._detect_trend_patterns(signals)
        patterns.extend(trend_patterns)

        temporal_patterns = self._detect_temporal_patterns(signals)
        patterns.extend(temporal_patterns)

        # Filter by minimum strength
        patterns = [p for p in patterns if p.strength >= min_strength]

        self._detected_patterns.extend(patterns)

        logger.info(
            "Patterns detected",
            signal_count=len(signals),
            pattern_count=len(patterns),
        )

        return patterns

    def _detect_convergence(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[Pattern]:
        """
        Detect converging signals indicating strong opportunity.

        Converging signals occur when multiple signals of the same
        trend (e.g., all trending up) point to the same conclusion.
        """
        patterns = []

        # Group signals by trend
        by_trend: dict[SignalTrend, list[IntelligenceSignal]] = {}
        for signal in signals:
            if signal.trend not in by_trend:
                by_trend[signal.trend] = []
            by_trend[signal.trend].append(signal)

        # Check for strong convergence (3+ signals with same trend)
        for trend, trend_signals in by_trend.items():
            if len(trend_signals) >= 3:
                # Check if signals are related (same category or entities)
                related_signals = self._filter_related_signals(trend_signals)

                if len(related_signals) >= 3:
                    strength = self._calculate_convergence_strength(related_signals)

                    pattern = Pattern(
                        name=f"Converging {trend.value} signals",
                        description=self._generate_convergence_description(
                            trend, related_signals
                        ),
                        pattern_type="convergence",
                        signal_ids=[s.id for s in related_signals],
                        strength=strength,
                        confidence=sum(s.confidence for s in related_signals) / len(related_signals),
                        implications=self._generate_implications(related_signals, trend),
                        opportunities=self._extract_opportunities(related_signals),
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_divergence(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[Pattern]:
        """
        Detect diverging signals indicating uncertainty or conflicting trends.
        """
        patterns = []

        # Look for conflicting signal types
        bullish_types = set(self.SIGNAL_GROUPS["bullish"])
        bearish_types = set(self.SIGNAL_GROUPS["bearish"])

        bullish_signals = [s for s in signals if s.type in bullish_types]
        bearish_signals = [s for s in signals if s.type in bearish_types]

        if len(bullish_signals) >= 2 and len(bearish_signals) >= 2:
            # Calculate divergence strength
            avg_bullish = sum(s.intensity for s in bullish_signals) / len(bullish_signals)
            avg_bearish = sum(s.intensity for s in bearish_signals) / len(bearish_signals)

            if abs(avg_bullish - avg_bearish) > 20:  # Significant difference
                pattern = Pattern(
                    name="Mixed market signals",
                    description=f"Conflicting signals detected: "
                               f"bullish indicators at {avg_bullish:.0f}%, "
                               f"bearish indicators at {avg_bearish:.0f}%",
                    pattern_type="divergence",
                    signal_ids=[s.id for s in bullish_signals + bearish_signals],
                    strength=min(avg_bullish, avg_bearish) / 100,
                    confidence=0.6,
                    implications=[
                        "Market uncertainty detected",
                        "Risk management should be heightened",
                        "Monitor for trend confirmation",
                    ],
                    risks=[
                        "Conflicting indicators suggest volatility",
                        "May indicate market transition",
                    ],
                )
                patterns.append(pattern)

        return patterns

    def _detect_trend_patterns(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[Pattern]:
        """Detect consistent trend patterns."""
        patterns = []

        # Sort signals by time
        time_sorted = sorted(signals, key=lambda s: s.detected_at)

        if len(time_sorted) < 3:
            return patterns

        # Check for consistent upward trend
        increasing_count = 0
        for i in range(len(time_sorted) - 1):
            if time_sorted[i + 1].intensity > time_sorted[i].intensity:
                increasing_count += 1

        if increasing_count >= len(time_sorted) * 0.7:
            pattern = Pattern(
                name="Sustained upward trend",
                description="Consistent increase in signal intensity over time",
                pattern_type="trend",
                signal_ids=[s.id for s in time_sorted],
                strength=increasing_count / len(time_sorted),
                confidence=sum(s.confidence for s in time_sorted) / len(time_sorted),
                implications=[
                    "Strong momentum detected",
                    "Trend likely to continue",
                ],
                opportunities=[
                    "Potential market expansion opportunity",
                    "Time-sensitive strategic positioning",
                ],
            )
            patterns.append(pattern)

        return patterns

    def _detect_temporal_patterns(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[Pattern]:
        """Detect temporal patterns like cycles or bursts."""
        patterns = []

        # Group signals by time periods
        now = datetime.utcnow()
        recent = [s for s in signals if now - s.detected_at < timedelta(days=7)]
        older = [s for s in signals if now - s.detected_at >= timedelta(days=30)]

        # Check for burst pattern (many recent signals)
        if len(recent) >= 5 and len(recent) > len(older):
            pattern = Pattern(
                name="Signal burst detected",
                description=f"{len(recent)} signals detected in the last 7 days",
                pattern_type="burst",
                signal_ids=[s.id for s in recent],
                strength=min(len(recent) / 10.0, 1.0),
                confidence=0.7,
                implications=[
                    "Rapid change detected in market conditions",
                    "May indicate emerging opportunity or risk",
                ],
            )
            patterns.append(pattern)

        return patterns

    def _filter_related_signals(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[IntelligenceSignal]:
        """Filter signals to find related ones."""
        if not signals:
            return []

        related = [signals[0]]  # Start with first signal

        for signal in signals[1:]:
            # Check for shared entities
            shared = set(signal.entities) & set(related[0].entities)

            # Check for same category
            same_category = signal.category == related[0].category

            # Check for temporal proximity
            time_diff = abs(
                (signal.detected_at - related[0].detected_at).total_seconds()
            )
            recent = time_diff < 7 * 24 * 3600  # Within a week

            if shared or same_category or recent:
                related.append(signal)

        return related

    def _calculate_convergence_strength(
        self,
        signals: list[IntelligenceSignal],
    ) -> float:
        """Calculate strength of converging signals."""
        if not signals:
            return 0.0

        # Average intensity
        avg_intensity = sum(s.intensity for s in signals) / len(signals)

        # Intensity variance (lower is better for convergence)
        variance = sum((s.intensity - avg_intensity) ** 2 for s in signals) / len(signals)
        consistency = max(0, 1 - variance / 1000)  # Normalize

        # Number of signals factor
        count_factor = min(len(signals) / 5.0, 1.0)

        return (avg_intensity / 100) * 0.5 + consistency * 0.3 + count_factor * 0.2

    def _generate_convergence_description(
        self,
        trend: SignalTrend,
        signals: list[IntelligenceSignal],
    ) -> str:
        """Generate description for convergence pattern."""
        avg_intensity = sum(s.intensity for s in signals) / len(signals)
        categories = {s.category.value for s in signals}

        return (
            f"Strong convergence of {trend.value} signals across "
            f"{len(signals)} indicators in {len(categories)} categories "
            f"with average intensity of {avg_intensity:.0f}%"
        )

    def _generate_implications(
        self,
        signals: list[IntelligenceSignal],
        trend: SignalTrend,
    ) -> list[str]:
        """Generate implications from signals."""
        implications = []

        categories = {s.category for s in signals}

        if SignalCategory.MARKET in categories:
            implications.append("Strong market movement expected")

        if SignalCategory.TECHNOLOGY in categories:
            implications.append("Technology-driven change anticipated")

        if SignalCategory.REGULATION in categories:
            implications.append("Regulatory changes may impact market")

        if trend == SignalTrend.UP:
            implications.append("Favorable conditions for action")
        else:
            implications.append("Caution warranted, monitor closely")

        return implications

    def _extract_opportunities(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[str]:
        """Extract potential opportunities from signals."""
        opportunities = []

        for signal in signals:
            if signal.type == SignalType.DEMAND:
                opportunities.append("Market demand opportunity identified")
            elif signal.type == SignalType.GROWTH:
                opportunities.append("Growth potential in target market")
            elif signal.type == SignalType.INNOVATION:
                opportunities.append("Innovation-based competitive advantage")
            elif signal.type == SignalType.INVESTMENT:
                opportunities.append("Investment activity signals opportunity")

        return list(set(opportunities))  # Remove duplicates

    def get_patterns(self) -> list[Pattern]:
        """Get all detected patterns."""
        return self._detected_patterns


class InsightGenerator:
    """
    Generates insights from patterns and signals.

    Implements the Insight Generation phase:
    Patterns -> Insights
    """

    def __init__(self):
        """Initialize insight generator."""
        self._generated_insights: list[Insight] = []

    def generate_insights(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> list[Insight]:
        """
        Generate insights from signals and patterns.

        Args:
            signals: List of signals
            patterns: List of detected patterns

        Returns:
            List of generated insights
        """
        insights = []

        # Generate insights from strong patterns
        strong_patterns = [p for p in patterns if p.strength >= 0.7]
        for pattern in strong_patterns:
            insight = self._generate_pattern_insight(pattern, signals)
            insights.append(insight)

        # Generate insights from signal convergence
        if len(signals) >= 5:
            insight = self._generate_convergence_insight(signals)
            insights.append(insight)

        # Generate insights from category analysis
        category_insights = self._generate_category_insights(signals)
        insights.extend(category_insights)

        self._generated_insights.extend(insights)

        logger.info(
            "Insights generated",
            signal_count=len(signals),
            pattern_count=len(patterns),
            insight_count=len(insights),
        )

        return insights

    def _generate_pattern_insight(
        self,
        pattern: Pattern,
        signals: list[IntelligenceSignal],
    ) -> Insight:
        """Generate insight from a pattern."""
        related_signals = [s for s in signals if s.id in pattern.signal_ids]
        avg_confidence = sum(s.confidence for s in related_signals) / len(related_signals)

        return Insight(
            title=f"Pattern detected: {pattern.name}",
            description=pattern.description,
            category=related_signals[0].category if related_signals else SignalCategory.MARKET,
            signal_ids=pattern.signal_ids,
            pattern_ids=[pattern.id],
            impact_level="high" if pattern.strength > 0.8 else "medium",
            urgency="immediate" if pattern.pattern_type == "burst" else "short_term",
            affected_sectors=list({s.category.value for s in related_signals}),
            confidence=pattern.confidence * avg_confidence,
            uncertainty_factors=pattern.risks,
        )

    def _generate_convergence_insight(
        self,
        signals: list[IntelligenceSignal],
    ) -> Insight:
        """Generate insight from signal convergence."""
        avg_intensity = sum(s.intensity for s in signals) / len(signals)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        types = {s.type for s in signals}

        return Insight(
            title="Multiple signals indicate strong opportunity",
            description=f"Analysis of {len(signals)} signals across {len(types)} categories "
                       f"reveals converging indicators with average intensity of {avg_intensity:.0f}%",
            category=SignalCategory.MARKET,
            signal_ids=[s.id for s in signals],
            impact_level="high",
            urgency="short_term",
            affected_sectors=list({s.category.value for s in signals}),
            confidence=avg_confidence,
            uncertainty_factors=[
                "Rapidly changing conditions",
                "Multiple unknown factors",
            ],
        )

    def _generate_category_insights(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[Insight]:
        """Generate insights from category analysis."""
        insights = []

        # Group by category
        by_category: dict[SignalCategory, list[IntelligenceSignal]] = {}
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal)

        # Generate insight for each category with strong signals
        for category, category_signals in by_category.items():
            avg_intensity = sum(s.intensity for s in category_signals) / len(category_signals)

            if avg_intensity >= 70:
                insight = Insight(
                    title=f"Strong {category.value} signals detected",
                    description=f"{len(category_signals)} signals in {category.value} "
                              f"category with average intensity of {avg_intensity:.0f}%",
                    category=category,
                    signal_ids=[s.id for s in category_signals],
                    impact_level="medium",
                    urgency="short_term",
                    affected_sectors=[category.value],
                    confidence=sum(s.confidence for s in category_signals) / len(category_signals),
                )
                insights.append(insight)

        return insights

    def get_insights(self) -> list[Insight]:
        """Get all generated insights."""
        return self._generated_insights
