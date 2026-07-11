"""
ATLAS Platform - Intelligence Indicators Engine

This module implements the Intelligence Indicators Framework.
Based on the specifications - Intelligence Indicators Framework section.

The indicators provide a dashboard of composite metrics for
opportunity assessment across multiple dimensions.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.core.logging import get_logger
from backend.intelligence.base import (
    IntelligenceSignal,
    Pattern,
)

logger = get_logger(__name__)


class IntelligenceIndicators(BaseModel):
    """
    Intelligence indicators dashboard.

    Provides a comprehensive view of market conditions
    across multiple dimensions.
    """

    # Performance & Attractiveness Indicators
    opportunity_score: float = Field(
        ge=0.0, le=100.0,
        description="Overall opportunity attractiveness score"
    )
    demand_index: float = Field(
        ge=0.0, le=100.0,
        description="Market demand intensity"
    )
    market_momentum: float = Field(
        ge=0.0, le=100.0,
        description="Market velocity and direction"
    )
    capital_attraction: float = Field(
        ge=0.0, le=100.0,
        description="Investment activity level"
    )

    # Competitive & Innovation Indicators
    competition_index: float = Field(
        ge=0.0, le=100.0,
        description="Competition intensity"
    )
    innovation_index: float = Field(
        ge=0.0, le=100.0,
        description="Innovation and technology advancement"
    )
    technology_maturity: float = Field(
        ge=0.0, le=100.0,
        description="Technology readiness level"
    )

    # Risk & Stability Indicators
    risk_index: float = Field(
        ge=0.0, le=100.0,
        description="Overall risk assessment"
    )
    regulatory_stability: float = Field(
        ge=0.0, le=100.0,
        description="Regulatory environment stability"
    )
    supply_stability: float = Field(
        ge=0.0, le=100.0,
        description="Supply chain stability"
    )

    # Geographic & Readiness Indicators
    geographic_opportunity: float = Field(
        ge=0.0, le=100.0,
        description="Best regions for opportunity"
    )
    expansion_readiness: float = Field(
        ge=0.0, le=100.0,
        description="Readiness for expansion"
    )
    strategic_fit: float = Field(
        ge=0.0, le=100.0,
        description="Alignment with strategy"
    )

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the indicators"
    )
    region: str | None = None
    industry: str | None = None


class IndicatorEngine:
    """
    Engine for calculating intelligence indicators.

    Aggregates signals and patterns into composite metrics.
    """

    def __init__(self):
        """Initialize indicator engine."""
        pass

    def calculate_indicators(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
        context: dict[str, Any] | None = None,
    ) -> IntelligenceIndicators:
        """
        Calculate intelligence indicators from signals and patterns.

        Args:
            signals: List of intelligence signals
            patterns: List of detected patterns
            context: Optional context (region, industry)

        Returns:
            IntelligenceIndicators dashboard
        """
        # Calculate component indicators
        opportunity_score = self._calculate_opportunity_score(signals, patterns)
        demand_index = self._calculate_demand_index(signals)
        market_momentum = self._calculate_market_momentum(signals, patterns)
        capital_attraction = self._calculate_capital_attraction(signals)

        competition_index = self._calculate_competition_index(signals)
        innovation_index = self._calculate_innovation_index(signals)
        technology_maturity = self._calculate_technology_maturity(signals)

        risk_index = self._calculate_risk_index(signals)
        regulatory_stability = self._calculate_regulatory_stability(signals)
        supply_stability = self._calculate_supply_stability(signals)

        geographic_opportunity = self._calculate_geographic_opportunity(signals, context)
        expansion_readiness = self._calculate_expansion_readiness(signals, patterns)
        strategic_fit = self._calculate_strategic_fit(signals, context)

        # Calculate overall confidence
        confidence = self._calculate_confidence(signals, patterns)

        indicators = IntelligenceIndicators(
            opportunity_score=opportunity_score,
            demand_index=demand_index,
            market_momentum=market_momentum,
            capital_attraction=capital_attraction,
            competition_index=competition_index,
            innovation_index=innovation_index,
            technology_maturity=technology_maturity,
            risk_index=risk_index,
            regulatory_stability=regulatory_stability,
            supply_stability=supply_stability,
            geographic_opportunity=geographic_opportunity,
            expansion_readiness=expansion_readiness,
            strategic_fit=strategic_fit,
            confidence=confidence,
            region=context.get("region") if context else None,
            industry=context.get("industry") if context else None,
        )

        logger.info(
            "Intelligence indicators calculated",
            opportunity_score=opportunity_score,
            demand_index=demand_index,
            signal_count=len(signals),
            pattern_count=len(patterns),
        )

        return indicators

    def _calculate_opportunity_score(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> float:
        """Calculate overall opportunity score."""
        if not signals:
            return 0.0

        # Weighted combination of factors
        demand_score = self._calculate_demand_index(signals)
        growth_score = self._calculate_growth_index(signals)
        competition_score = self._calculate_competition_index(signals)
        risk_score = self._calculate_risk_index(signals)

        # Pattern boost
        pattern_boost = 0.0
        if patterns:
            avg_pattern_strength = sum(p.strength for p in patterns) / len(patterns)
            pattern_boost = avg_pattern_strength * 10

        # Calculate score
        score = (
            demand_score * 0.30 +
            growth_score * 0.25 +
            (100 - competition_score) * 0.20 +
            (100 - risk_score) * 0.15 +
            pattern_boost
        )

        return min(max(score, 0.0), 100.0)

    def _calculate_demand_index(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate demand intensity index."""
        from backend.intelligence.base import SignalType

        demand_signals = [s for s in signals if s.type == SignalType.DEMAND]

        if not demand_signals:
            return 50.0  # Neutral

        avg_intensity = sum(s.intensity for s in demand_signals) / len(demand_signals)
        return avg_intensity

    def _calculate_growth_index(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate growth potential index."""
        from backend.intelligence.base import SignalType

        growth_signals = [s for s in signals if s.type == SignalType.GROWTH]

        if not growth_signals:
            return 50.0

        # Weight by trend
        trend_weights = {"up": 1.2, "stable": 1.0, "down": 0.8, "volatile": 0.6}

        weighted_sum = sum(
            s.intensity * trend_weights.get(s.trend.value, 1.0)
            for s in growth_signals
        )

        return min(weighted_sum / len(growth_signals), 100.0)

    def _calculate_market_momentum(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> float:
        """Calculate market momentum index."""
        if not signals:
            return 50.0

        # Count trending signals
        trending_count = sum(1 for s in signals if s.trend.value == "up")
        total_signals = len(signals)

        trending_ratio = trending_count / total_signals if total_signals > 0 else 0

        # Calculate momentum
        avg_intensity = sum(s.intensity for s in signals) / len(signals)

        momentum = trending_ratio * avg_intensity * 1.5

        return min(max(momentum, 0.0), 100.0)

    def _calculate_capital_attraction(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate capital attraction index."""
        from backend.intelligence.base import SignalType

        investment_signals = [s for s in signals if s.type == SignalType.INVESTMENT]

        if not investment_signals:
            return 50.0

        avg_intensity = sum(s.intensity for s in investment_signals) / len(investment_signals)
        return avg_intensity

    def _calculate_competition_index(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate competition intensity index."""
        from backend.intelligence.base import SignalType

        competition_signals = [s for s in signals if s.type == SignalType.COMPETITION]

        if not competition_signals:
            return 50.0

        # Higher competition signals = higher index
        avg_intensity = sum(s.intensity for s in competition_signals) / len(competition_signals)
        return avg_intensity

    def _calculate_innovation_index(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate innovation index."""
        from backend.intelligence.base import SignalType

        innovation_signals = [
            s for s in signals
            if s.type in (SignalType.INNOVATION, SignalType.TECHNOLOGY)
        ]

        if not innovation_signals:
            return 50.0

        avg_intensity = sum(s.intensity for s in innovation_signals) / len(innovation_signals)
        return avg_intensity

    def _calculate_technology_maturity(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate technology maturity index."""
        from backend.intelligence.base import SignalType

        tech_signals = [s for s in signals if s.type == SignalType.TECHNOLOGY]

        if not tech_signals:
            return 50.0

        # High intensity with stable trend = mature
        # High intensity with volatile trend = emerging
        avg_intensity = sum(s.intensity for s in tech_signals) / len(tech_signals)

        stable_count = sum(1 for s in tech_signals if s.trend.value == "stable")
        stability_factor = stable_count / len(tech_signals)

        maturity = avg_intensity * (0.5 + stability_factor * 0.5)

        return min(maturity, 100.0)

    def _calculate_risk_index(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate overall risk index."""
        from backend.intelligence.base import SignalType

        # Risk comes from multiple sources
        risk_signals = []

        # Regulatory risks
        risk_signals.extend([s for s in signals if s.type == SignalType.REGULATORY])

        # Economic risks
        risk_signals.extend([s for s in signals if s.type == SignalType.ECONOMIC])

        if not risk_signals:
            return 25.0  # Low risk by default

        # Average intensity weighted by confidence
        weighted_sum = sum(
            s.intensity * s.confidence
            for s in risk_signals
        )
        total_confidence = sum(s.confidence for s in risk_signals)

        risk_index = weighted_sum / total_confidence if total_confidence > 0 else 0

        return min(max(risk_index, 0.0), 100.0)

    def _calculate_regulatory_stability(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate regulatory stability index."""
        from backend.intelligence.base import SignalType

        reg_signals = [s for s in signals if s.type == SignalType.REGULATORY]

        if not reg_signals:
            return 75.0  # Assumed stable if no regulatory signals

        # Regulatory signals indicate change = instability
        avg_intensity = sum(s.intensity for s in reg_signals) / len(reg_signals)

        # High regulatory activity = low stability
        stability = 100 - avg_intensity

        return min(max(stability, 0.0), 100.0)

    def _calculate_supply_stability(self, signals: list[IntelligenceSignal]) -> float:
        """Calculate supply chain stability index."""
        # This would typically use operational signals
        # Simplified implementation

        if not signals:
            return 75.0

        # Check for supply-related entities in signals
        supply_related = [
            s for s in signals
            if any("supply" in e.lower() for e in s.entities)
        ]

        if not supply_related:
            return 75.0

        avg_intensity = sum(s.intensity for s in supply_related) / len(supply_related)
        return 100 - avg_intensity

    def _calculate_geographic_opportunity(
        self,
        signals: list[IntelligenceSignal],
        context: dict[str, Any] | None,
    ) -> float:
        """Calculate geographic opportunity index."""
        # Count signals by geography
        geography_signals: dict[str, list[IntelligenceSignal]] = {}

        for signal in signals:
            if signal.geography:
                if signal.geography not in geography_signals:
                    geography_signals[signal.geography] = []
                geography_signals[signal.geography].append(signal)

        if not geography_signals:
            return 50.0

        # Calculate score for each geography
        scores = {}
        for geo, geo_signals in geography_signals.items():
            avg_intensity = sum(s.intensity for s in geo_signals) / len(geo_signals)
            # Boost if this matches context
            if context and context.get("region") == geo:
                avg_intensity *= 1.2
            scores[geo] = avg_intensity

        # Return best geography score
        return max(scores.values()) if scores else 50.0

    def _calculate_expansion_readiness(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> float:
        """Calculate expansion readiness index."""
        # Factors for expansion readiness
        demand = self._calculate_demand_index(signals)
        growth = self._calculate_growth_index(signals)
        risk = self._calculate_risk_index(signals)

        # Patterns suggesting readiness
        convergence_patterns = [p for p in patterns if p.pattern_type == "convergence"]
        pattern_factor = len(convergence_patterns) * 5  # Each convergence adds 5%

        readiness = (
            demand * 0.30 +
            growth * 0.30 +
            (100 - risk) * 0.30 +
            pattern_factor
        )

        return min(max(readiness, 0.0), 100.0)

    def _calculate_strategic_fit(
        self,
        signals: list[IntelligenceSignal],
        context: dict[str, Any] | None,
    ) -> float:
        """Calculate strategic fit index."""
        if not context:
            return 75.0  # Neutral if no context

        # Check alignment with stated strategy
        strategic_keywords = context.get("keywords", [])

        if not strategic_keywords:
            return 75.0

        # Count signals that match strategic keywords
        aligned_count = 0
        for signal in signals:
            for keyword in strategic_keywords:
                if keyword.lower() in signal.description.lower():
                    aligned_count += 1
                    break

        fit_ratio = aligned_count / len(signals) if signals else 0

        return fit_ratio * 100

    def _calculate_confidence(
        self,
        signals: list[IntelligenceSignal],
        patterns: list[Pattern],
    ) -> float:
        """Calculate overall confidence in the indicators."""
        if not signals:
            return 0.0

        # Average signal confidence
        avg_signal_confidence = sum(s.confidence for s in signals) / len(signals)

        # Pattern contribution
        pattern_confidence = 0.0
        if patterns:
            pattern_confidence = sum(p.confidence for p in patterns) / len(patterns)

        # Source diversity factor
        unique_sources = len({s.source.source_id for s in signals for s in signals})
        source_factor = min(unique_sources / 10.0, 1.0)

        confidence = (
            avg_signal_confidence * 0.5 +
            pattern_confidence * 0.3 +
            source_factor * 0.2
        )

        return min(max(confidence, 0.0), 1.0)


class IndicatorTrendAnalyzer:
    """
    Analyzes trends in intelligence indicators over time.
    """

    def __init__(self):
        """Initialize trend analyzer."""
        self._historical_indicators: list[IntelligenceIndicators] = []

    def add_indicators(
        self,
        indicators: IntelligenceIndicators,
    ) -> None:
        """Add indicators to historical record."""
        self._historical_indicators.append(indicators)

        # Keep only last 100 records
        if len(self._historical_indicators) > 100:
            self._historical_indicators = self._historical_indicators[-100:]

    def get_trends(self) -> dict[str, dict[str, Any]]:
        """
        Calculate trends for each indicator.

        Returns:
            Dictionary of indicator trends
        """
        if len(self._historical_indicators) < 2:
            return {}

        trends = {}
        fields = [
            "opportunity_score", "demand_index", "market_momentum",
            "capital_attraction", "competition_index", "innovation_index",
            "risk_index", "geographic_opportunity"
        ]

        for field in fields:
            values = [getattr(ind, field) for ind in self._historical_indicators]

            # Calculate moving average
            ma_short = sum(values[-3:]) / min(3, len(values))
            ma_long = sum(values[-10:]) / min(10, len(values))

            # Determine trend direction
            if ma_short > ma_long * 1.05:
                direction = "up"
            elif ma_short < ma_long * 0.95:
                direction = "down"
            else:
                direction = "stable"

            trends[field] = {
                "current": values[-1],
                "moving_average_short": ma_short,
                "moving_average_long": ma_long,
                "direction": direction,
                "volatility": self._calculate_volatility(values),
            }

        return trends

    def _calculate_volatility(self, values: list[float]) -> float:
        """Calculate volatility (standard deviation) of values."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)

        return variance ** 0.5
