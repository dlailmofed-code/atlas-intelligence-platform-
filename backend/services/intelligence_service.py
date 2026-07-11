"""
ATLAS Platform - Intelligence Service

This service handles intelligence engine operations including
signal processing, pattern detection, and causal reasoning.
"""

from collections.abc import Sequence
from datetime import UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.intelligence.base import IntelligenceSignal
from backend.schemas import IntelligenceSignalBase

logger = get_logger(__name__)


class IntelligenceService:
    """Service for intelligence-related operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize intelligence service.

        Args:
            session: Database session
        """
        self.session = session

    async def get_signal_by_id(self, signal_id: str) -> IntelligenceSignal | None:
        """
        Get intelligence signal by ID.

        Args:
            signal_id: Signal ID

        Returns:
            Signal if found, None otherwise
        """
        result = await self.session.execute(
            select(IntelligenceSignal).where(IntelligenceSignal.id == signal_id)
        )
        return result.scalar_one_or_none()

    async def get_signals(
        self,
        category: str | None = None,
        signal_type: str | None = None,
        min_intensity: float | None = None,
        region: str | None = None,
        industry: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[IntelligenceSignal], int]:
        """
        Get intelligence signals with filters.

        Args:
            category: Category filter
            signal_type: Type filter
            min_intensity: Minimum intensity filter
            region: Region filter
            industry: Industry filter
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Tuple of (signals, total count)
        """
        from sqlalchemy import func

        stmt = select(IntelligenceSignal)

        # Apply filters
        if category:
            stmt = stmt.where(IntelligenceSignal.category == category)

        if signal_type:
            stmt = stmt.where(IntelligenceSignal.type == signal_type)

        if min_intensity is not None:
            stmt = stmt.where(IntelligenceSignal.intensity >= min_intensity)

        if region:
            stmt = stmt.where(IntelligenceSignal.region == region)

        if industry:
            stmt = stmt.where(IntelligenceSignal.industry == industry)

        # Get total count
        count_query = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_query)

        # Get paginated results
        stmt = stmt.order_by(IntelligenceSignal.intensity.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        signals = result.scalars().all()

        return signals, total or 0

    async def create_signal(
        self,
        signal_data: IntelligenceSignalBase,
    ) -> IntelligenceSignal:
        """
        Create a new intelligence signal.

        Args:
            signal_data: Signal creation data

        Returns:
            Created signal
        """
        from datetime import datetime

        signal = IntelligenceSignal(
            type=signal_data.type,
            name=signal_data.name,
            description=signal_data.description,
            category=signal_data.category,
            intensity=signal_data.intensity,
            trend=signal_data.trend,
            confidence=signal_data.confidence,
            region=signal_data.region,
            industry=signal_data.industry,
            detected_at=datetime.now(UTC),
        )

        self.session.add(signal)
        await self.session.flush()

        logger.info("Intelligence signal created", signal_id=signal.id)

        return signal

    async def update_signal(
        self,
        signal: IntelligenceSignal,
        signal_data: IntelligenceSignalBase,
    ) -> IntelligenceSignal:
        """
        Update intelligence signal.

        Args:
            signal: Signal to update
            signal_data: Update data

        Returns:
            Updated signal
        """
        for field, value in signal_data.model_dump().items():
            if hasattr(signal, field):
                setattr(signal, field, value)

        await self.session.flush()

        logger.info("Intelligence signal updated", signal_id=signal.id)

        return signal

    async def detect_patterns(
        self,
        signals: list[IntelligenceSignal],
    ) -> list[dict[str, Any]]:
        """
        Detect patterns from signals.

        This is a placeholder for the actual pattern detection logic.
        In production, this would use ML models and complex algorithms.

        Args:
            signals: List of signals to analyze

        Returns:
            List of detected patterns
        """
        # Placeholder implementation
        patterns = []

        # Group signals by category
        by_category: dict[str, list[IntelligenceSignal]] = {}
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal)

        # Detect patterns within categories
        for category, category_signals in by_category.items():
            if len(category_signals) >= 2:
                # Check for trend patterns
                trends = [s.trend for s in category_signals]
                if all(t == "up" for t in trends):
                    patterns.append({
                        "type": "upward_trend",
                        "category": category,
                        "strength": sum(s.intensity for s in category_signals) / len(category_signals),
                        "signals": [s.id for s in category_signals],
                    })

        logger.info("Patterns detected", count=len(patterns))

        return patterns

    async def analyze_causal_relationships(
        self,
        entity: str,
    ) -> list[dict[str, Any]]:
        """
        Analyze causal relationships for an entity.

        This is a placeholder for the actual causal reasoning logic.
        In production, this would implement sophisticated causal inference.

        Args:
            entity: Entity to analyze

        Returns:
            List of causal relationships
        """
        # Placeholder implementation
        return []

    async def generate_insights(
        self,
        signals: list[IntelligenceSignal],
        opportunities: list[dict[str, Any]],
    ) -> list[str]:
        """
        Generate insights from signals and opportunities.

        Args:
            signals: Related signals
            opportunities: Related opportunities

        Returns:
            List of generated insights
        """
        insights = []

        # Simple rule-based insight generation
        high_intensity_signals = [s for s in signals if s.intensity >= 80]
        if high_intensity_signals:
            insights.append(
                f"Detected {len(high_intensity_signals)} high-intensity signals "
                "indicating significant market activity."
            )

        # Check for convergence
        if len(opportunities) >= 3:
            insights.append(
                "Multiple opportunities detected in related areas, "
                "suggesting a potential market trend."
            )

        logger.info("Insights generated", count=len(insights))

        return insights
