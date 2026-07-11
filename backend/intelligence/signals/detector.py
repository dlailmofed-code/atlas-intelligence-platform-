"""
ATLAS Platform - Signal Detector

This module implements signal detection from evidence.
Based on the Intelligence Signals Framework from the specifications.
"""

from datetime import datetime, timedelta
from typing import Any

from backend.core.logging import get_logger
from backend.intelligence.base import (
    Evidence,
    IntelligenceSignal,
    SignalCategory,
    SignalTrend,
    SignalType,
)

logger = get_logger(__name__)


class SignalDetector:
    """
    Detects intelligence signals from evidence.

    Implements the Signal Detection phase of the Intelligence Lifecycle:
    Raw Information -> Evidence -> Signals
    """

    # Keywords associated with each signal type
    SIGNAL_KEYWORDS = {
        SignalType.DEMAND: [
            "demand", "need", "want", "require", "searching for",
            "shortage", "scarcity", "bottleneck", "pain point"
        ],
        SignalType.GROWTH: [
            "growth", "expansion", "increase", "surge", "boom",
            "accelerating", "scaling", "revenue increase", "market share"
        ],
        SignalType.INNOVATION: [
            "innovation", "patent", "breakthrough", "novel", "creative",
            "disruptive", "new solution", "technology advancement"
        ],
        SignalType.INVESTMENT: [
            "funding", "investment", "venture capital", "series",
            "acquisition", "merger", "ipo", "valuation"
        ],
        SignalType.REGULATORY: [
            "regulation", "law", "policy", "compliance", "requirement",
            "mandate", "legislation", "government", "approval"
        ],
        SignalType.COMPETITION: [
            "competitor", "market entry", "expansion", "launch",
            "partnership", "alliance", "market share"
        ],
        SignalType.SOCIAL: [
            "trend", "viral", "social media", "awareness", "movement",
            "preference shift", "lifestyle", "behavior change"
        ],
        SignalType.ECONOMIC: [
            "gdp", "inflation", "interest rate", "unemployment",
            "consumer spending", "economic indicator", "market index"
        ],
        SignalType.TECHNOLOGY: [
            "technology", "ai", "machine learning", "automation",
            "digital", "software", "platform", "cloud"
        ],
    }

    def __init__(self):
        """Initialize signal detector."""
        self._signal_cache: dict[str, IntelligenceSignal] = {}

    def detect_signals(
        self,
        evidence: list[Evidence],
        min_intensity: float = 50.0,
    ) -> list[IntelligenceSignal]:
        """
        Detect signals from a list of evidence.

        Args:
            evidence: List of evidence to analyze
            min_intensity: Minimum intensity threshold

        Returns:
            List of detected signals
        """
        detected_signals = []
        signal_scores: dict[SignalType, list[tuple[Evidence, float]]] = {}

        # Score each evidence piece for each signal type
        for e in evidence:
            for signal_type, keywords in self.SIGNAL_KEYWORDS.items():
                score = self._calculate_signal_score(e, keywords)
                if score > 0.3:  # Minimum threshold
                    if signal_type not in signal_scores:
                        signal_scores[signal_type] = []
                    signal_scores[signal_type].append((e, score))

        # Generate signals from scored evidence
        for signal_type, scored_evidence in signal_scores.items():
            if not scored_evidence:
                continue

            # Aggregate evidence for this signal type
            weighted_intensity = sum(
                e.relevance * score * e.weight
                for e, score in scored_evidence
            ) / sum(e.relevance * e.weight for e, _ in scored_evidence)

            if weighted_intensity * 100 >= min_intensity:
                signal = self._create_signal(
                    signal_type=signal_type,
                    evidence=[e for e, _ in scored_evidence],
                    intensity=weighted_intensity * 100,
                    content_analysis=self._analyze_content(scored_evidence),
                )
                detected_signals.append(signal)

        logger.info(
            "Signals detected",
            evidence_count=len(evidence),
            signals_count=len(detected_signals),
        )

        return detected_signals

    def _calculate_signal_score(
        self,
        evidence: Evidence,
        keywords: list[str],
    ) -> float:
        """
        Calculate signal score for evidence based on keywords.

        Args:
            evidence: Evidence to score
            keywords: Keywords for the signal type

        Returns:
            Score between 0 and 1
        """
        content_lower = evidence.content.lower()
        summary_lower = evidence.summary.lower()

        # Count keyword matches
        matches = sum(
            1 for kw in keywords
            if kw in content_lower or kw in summary_lower
        )

        # Calculate score based on matches and relevance
        keyword_score = min(matches / 3.0, 1.0)  # Normalize to 0-1
        relevance_factor = evidence.relevance

        return keyword_score * 0.7 + relevance_factor * 0.3

    def _analyze_content(
        self,
        scored_evidence: list[tuple[Evidence, float]],
    ) -> dict[str, Any]:
        """Analyze content to extract additional insights."""
        all_entities = []
        content_samples = []

        for evidence, _ in scored_evidence[:5]:  # Top 5 pieces
            all_entities.extend(evidence.entities)
            content_samples.append(evidence.summary[:200])

        # Extract common themes
        themes = self._extract_themes(content_samples)

        return {
            "entities": list(set(all_entities)),
            "themes": themes,
            "sample_content": content_samples[:3],
        }

    def _extract_themes(self, content_samples: list[str]) -> list[str]:
        """Extract common themes from content samples."""
        # Simple theme extraction - in production would use NLP
        themes = []
        keywords = ["growth", "demand", "opportunity", "market", "technology"]

        for sample in content_samples:
            sample_lower = sample.lower()
            for keyword in keywords:
                if keyword in sample_lower and keyword not in themes:
                    themes.append(keyword)

        return themes

    def _create_signal(
        self,
        signal_type: SignalType,
        evidence: list[Evidence],
        intensity: float,
        content_analysis: dict[str, Any],
    ) -> IntelligenceSignal:
        """Create a signal from evidence."""
        category = self._determine_category(signal_type)
        trend = self._determine_trend(evidence)

        signal = IntelligenceSignal(
            type=signal_type,
            category=category,
            name=f"{signal_type.value.capitalize()} Signal",
            description=self._generate_description(signal_type, evidence),
            intensity=intensity,
            confidence=self._calculate_confidence(evidence),
            trend=trend,
            evidence=evidence,
            entities=content_analysis.get("entities", []),
        )

        self._signal_cache[signal.id] = signal
        return signal

    def _determine_category(self, signal_type: SignalType) -> SignalCategory:
        """Map signal type to category."""
        category_mapping = {
            SignalType.DEMAND: SignalCategory.MARKET,
            SignalType.GROWTH: SignalCategory.MARKET,
            SignalType.INNOVATION: SignalCategory.TECHNOLOGY,
            SignalType.INVESTMENT: SignalCategory.FINANCIAL,
            SignalType.REGULATORY: SignalCategory.REGULATION,
            SignalType.COMPETITION: SignalCategory.COMPETITION,
            SignalType.SOCIAL: SignalCategory.SOCIAL,
            SignalType.ECONOMIC: SignalCategory.GEOSPATIAL,  # Fixed: use correct enum
            SignalType.TECHNOLOGY: SignalCategory.TECHNOLOGY,
        }
        return category_mapping.get(signal_type, SignalCategory.MARKET)

    def _determine_trend(self, evidence: list[Evidence]) -> SignalTrend:
        """Determine trend from evidence timestamps."""
        if len(evidence) < 2:
            return SignalTrend.STABLE

        # Sort by extraction time
        sorted_evidence = sorted(
            evidence,
            key=lambda e: e.extracted_at,
            reverse=True
        )

        # Check recency
        latest = sorted_evidence[0].extracted_at
        if latest > datetime.utcnow() - timedelta(days=7):
            return SignalTrend.UP
        elif latest > datetime.utcnow() - timedelta(days=30):
            return SignalTrend.STABLE
        else:
            return SignalTrend.DOWN

    def _calculate_confidence(self, evidence: list[Evidence]) -> float:
        """Calculate confidence based on evidence quality."""
        if not evidence:
            return 0.0

        # Average reliability
        avg_reliability = sum(e.source.reliability for e in evidence) / len(evidence)

        # Number of sources
        source_diversity = min(len({e.source.source_id for e in evidence}) / 5.0, 1.0)

        # Verification status
        verification_rate = sum(1 for e in evidence if e.verified) / len(evidence)

        return (
            avg_reliability * 0.5 +
            source_diversity * 0.3 +
            verification_rate * 0.2
        )

    def _generate_description(
        self,
        signal_type: SignalType,
        evidence: list[Evidence],
    ) -> str:
        """Generate a description from evidence summaries."""
        summaries = [e.summary for e in evidence[:3]]
        combined = " ".join(summaries)

        # Truncate if too long
        if len(combined) > 500:
            combined = combined[:497] + "..."

        return combined or f"Detected {signal_type.value} signal"

    def update_signal_from_evidence(
        self,
        signal_id: str,
        new_evidence: list[Evidence],
    ) -> IntelligenceSignal | None:
        """
        Update an existing signal with new evidence.

        Args:
            signal_id: ID of signal to update
            new_evidence: New evidence to add

        Returns:
            Updated signal or None if not found
        """
        if signal_id not in self._signal_cache:
            return None

        signal = self._signal_cache[signal_id]

        # Add new evidence
        for e in new_evidence:
            signal.add_evidence(e)

        # Update intensity based on trend
        new_intensity = signal.intensity
        for e in new_evidence:
            score = self._calculate_signal_score(
                e,
                self.SIGNAL_KEYWORDS.get(signal.type, [])
            )
            new_intensity = max(new_intensity, score * 100)

        signal.update_intensity(new_intensity)

        logger.info(
            "Signal updated",
            signal_id=signal_id,
            new_evidence_count=len(new_evidence),
            new_intensity=signal.intensity,
        )

        return signal


class SignalAggregator:
    """
    Aggregates and correlates multiple signals.

    Implements cross-signal analysis to identify:
    - Converging signals indicating strong opportunities
    - Diverging signals indicating uncertainty
    - Emerging patterns across different signal types
    """

    def __init__(self):
        """Initialize signal aggregator."""
        self._correlations: dict[str, float] = {}

    def aggregate_signals(
        self,
        signals: list[IntelligenceSignal],
        time_window: timedelta = timedelta(days=30),
    ) -> dict[str, Any]:
        """
        Aggregate multiple signals into a composite view.

        Args:
            signals: List of signals to aggregate
            time_window: Time window for aggregation

        Returns:
            Aggregated signal analysis
        """
        if not signals:
            return {
                "signal_count": 0,
                "average_intensity": 0.0,
                "average_confidence": 0.0,
                "dominant_type": None,
                "trend": SignalTrend.STABLE,
                "correlations": [],
            }

        # Calculate averages
        avg_intensity = sum(s.intensity for s in signals) / len(signals)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        # Find dominant signal type
        type_counts: dict[SignalType, int] = {}
        for s in signals:
            type_counts[s.type] = type_counts.get(s.type, 0) + 1
        dominant_type = max(type_counts, key=type_counts.get)

        # Determine overall trend
        trend_counts: dict[SignalTrend, int] = {}
        for s in signals:
            trend_counts[s.trend] = trend_counts.get(s.trend, 0) + 1
        overall_trend = max(trend_counts, key=trend_counts.get)

        # Find correlations
        correlations = self._find_correlations(signals)

        return {
            "signal_count": len(signals),
            "average_intensity": avg_intensity,
            "average_confidence": avg_confidence,
            "dominant_type": dominant_type,
            "trend": overall_trend,
            "correlations": correlations,
            "signal_types": dict(type_counts),
            "trend_breakdown": dict(trend_counts),
        }

    def _find_correlations(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[dict[str, Any]]:
        """Find correlations between signals."""
        correlations = []

        for i, s1 in enumerate(signals):
            for s2 in signals[i + 1:]:
                correlation = self._calculate_correlation(s1, s2)
                if correlation > 0.5:  # Only significant correlations
                    correlations.append({
                        "signal1": s1.id,
                        "signal2": s2.id,
                        "strength": correlation,
                        "type": self._describe_correlation(s1, s2),
                    })

        return correlations

    def _calculate_correlation(
        self,
        s1: IntelligenceSignal,
        s2: IntelligenceSignal,
    ) -> float:
        """Calculate correlation between two signals."""
        # Entity overlap
        common_entities = set(s1.entities) & set(s2.entities)
        entity_score = len(common_entities) / max(len(s1.entities), len(s2.entities), 1)

        # Time proximity
        time_diff = abs((s1.detected_at - s2.detected_at).total_seconds())
        time_score = max(0, 1 - time_diff / (7 * 24 * 3600))  # Week normalization

        # Combined correlation
        return entity_score * 0.6 + time_score * 0.4

    def _describe_correlation(
        self,
        s1: IntelligenceSignal,
        s2: IntelligenceSignal,
    ) -> str:
        """Describe the relationship between two correlated signals."""
        if s1.trend == s2.trend:
            return "Same direction"
        return "Divergent trends"
