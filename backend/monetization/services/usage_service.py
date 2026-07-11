"""
ATLAS Platform - Usage Service

This module provides the Usage service for tracking and limiting resource usage.
Based on the specifications: Usage Limits system.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.monetization import UsageRecord, UsageSummary

logger = get_logger(__name__)


class UsageService:
    """
    Service for tracking and managing usage limits.
    """

    # Default limits per plan
    DEFAULT_LIMITS = {
        "free": {
            "analysis": {"daily": 1, "monthly": 1},
            "report": {"monthly": 1},
            "api_call": {"daily": 100, "monthly": 1000},
        },
        "starter": {
            "analysis": {"daily": 5, "monthly": 100},
            "report": {"monthly": 10},
            "api_call": {"daily": 1000, "monthly": 10000},
            "export": {"monthly": 50},
        },
        "professional": {
            "analysis": {"daily": 50, "monthly": 1000},
            "report": {"monthly": 100},
            "api_call": {"daily": 10000, "monthly": 100000},
            "export": {"monthly": 500},
        },
        "enterprise": {
            "analysis": {"daily": -1, "monthly": -1},  # Unlimited
            "report": {"monthly": -1},
            "api_call": {"daily": -1, "monthly": -1},
            "export": {"monthly": -1},
        },
    }

    def __init__(self, db: AsyncSession):
        """
        Initialize the usage service.

        Args:
            db: Database session
        """
        self.db = db

    async def check_limit(
        self,
        user_id: UUID,
        usage_type: str,
        plan: str = "free",
        amount: int = 1,
    ) -> tuple[bool, int, int]:
        """
        Check if a user has exceeded their usage limit.

        Args:
            user_id: User ID
            usage_type: Type of usage (analysis, report, api_call, etc.)
            plan: User's subscription plan
            amount: Amount to check against limit

        Returns:
            Tuple of (is_allowed, current_usage, limit)
        """
        # Get limits for the plan
        limits = self.DEFAULT_LIMITS.get(plan, self.DEFAULT_LIMITS["free"])
        type_limits = limits.get(usage_type, {})

        # Check daily limit
        if "daily" in type_limits:
            daily_limit = type_limits["daily"]
            daily_usage = await self._get_current_usage(user_id, usage_type, "daily")

            if daily_limit != -1 and (daily_usage + amount) > daily_limit:
                return False, daily_usage, daily_limit

        # Check monthly limit
        if "monthly" in type_limits:
            monthly_limit = type_limits["monthly"]
            monthly_usage = await self._get_current_usage(user_id, usage_type, "monthly")

            if monthly_limit != -1 and (monthly_usage + amount) > monthly_limit:
                return False, monthly_usage, monthly_limit

        return True, 0, 0

    async def record_usage(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int = 1,
        subscription_id: UUID | None = None,
        resource_id: str | None = None,
        extra_data: dict | None = None,
    ) -> UsageRecord:
        """
        Record a usage event.

        Args:
            user_id: User ID
            usage_type: Type of usage
            amount: Amount used
            subscription_id: Subscription ID for quota tracking
            resource_id: Optional resource identifier
            extra_data: Optional extra data

        Returns:
            Created usage record
        """
        now = datetime.now(UTC)
        reset_at = now + timedelta(days=1)  # Daily reset

        record = UsageRecord(
            user_id=user_id,
            subscription_id=subscription_id,
            usage_type=usage_type,
            amount=amount,
            resource_id=resource_id,
            reset_at=reset_at,
            extra_data=extra_data or {},
            is_processed=False,
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        # Update summary cache
        await self._update_summary(user_id, usage_type, amount)

        logger.info(
            "Usage recorded",
            user_id=str(user_id),
            type=usage_type,
            amount=amount,
        )

        return record

    async def _get_current_usage(
        self,
        user_id: UUID,
        usage_type: str,
        period: str,
    ) -> int:
        """
        Get current usage for a period.

        Args:
            user_id: User ID
            usage_type: Type of usage
            period: Period type (daily, weekly, monthly)

        Returns:
            Current usage count
        """
        now = datetime.now(UTC)
        period_start, _ = UsageSummary.get_period_bounds(period, now)

        # Check summary cache first
        result = await self.db.execute(
            select(UsageSummary).where(
                UsageSummary.user_id == user_id,
                UsageSummary.usage_type == usage_type,
                UsageSummary.period_type == period,
                UsageSummary.period_start == period_start,
            )
        )
        summary = result.scalar_one_or_none()

        if summary:
            return summary.total_usage

        # Fall back to counting records
        result = await self.db.execute(
            select(func.sum(UsageRecord.amount)).where(
                UsageRecord.user_id == user_id,
                UsageRecord.usage_type == usage_type,
                UsageRecord.created_at >= period_start,
            )
        )
        total = result.scalar() or 0

        return int(total)

    async def _update_summary(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int,
    ) -> None:
        """Update the usage summary cache."""
        now = datetime.now(UTC)

        for period in ["daily", "monthly"]:
            period_start, period_end = UsageSummary.get_period_bounds(period, now)

            result = await self.db.execute(
                select(UsageSummary).where(
                    UsageSummary.user_id == user_id,
                    UsageSummary.usage_type == usage_type,
                    UsageSummary.period_type == period,
                    UsageSummary.period_start == period_start,
                )
            )
            summary = result.scalar_one_or_none()

            if summary:
                summary.total_usage += amount
            else:
                summary = UsageSummary(
                    user_id=user_id,
                    usage_type=usage_type,
                    period_type=period,
                    period_start=period_start,
                    period_end=period_end,
                    total_usage=amount,
                    last_reset=now,
                )
                self.db.add(summary)

        await self.db.commit()

    async def get_usage_summary(
        self,
        user_id: UUID,
        usage_type: str | None = None,
    ) -> dict:
        """
        Get usage summary for a user.

        Args:
            user_id: User ID
            usage_type: Optional filter by usage type

        Returns:
            Dictionary of usage summaries by type
        """
        query = select(UsageSummary).where(
            UsageSummary.user_id == user_id,
            UsageSummary.period_type == "monthly",
        )

        if usage_type:
            query = query.where(UsageSummary.usage_type == usage_type)

        result = await self.db.execute(query)
        summaries = result.scalars().all()

        return {
            summary.usage_type: {
                "total_usage": summary.total_usage,
                "period_start": summary.period_start.isoformat(),
                "period_end": summary.period_end.isoformat(),
            }
            for summary in summaries
        }

    async def reset_usage(
        self,
        user_id: UUID,
        usage_type: str | None = None,
    ) -> None:
        """
        Reset usage counters for a user.

        Args:
            user_id: User ID
            usage_type: Optional specific usage type to reset
        """
        query = select(UsageSummary).where(UsageSummary.user_id == user_id)

        if usage_type:
            query = query.where(UsageSummary.usage_type == usage_type)

        result = await self.db.execute(query)
        summaries = result.scalars().all()

        for summary in summaries:
            summary.total_usage = 0
            summary.last_reset = datetime.now(UTC)

        await self.db.commit()

        logger.info("Usage reset", user_id=str(user_id), usage_type=usage_type)

    async def get_rate_limit_remaining(
        self,
        user_id: UUID,
        usage_type: str,
        window_seconds: int = 60,
    ) -> int:
        """
        Get remaining rate limit for a user.

        Args:
            user_id: User ID
            usage_type: Type of usage
            window_seconds: Rate limit window in seconds

        Returns:
            Remaining requests allowed
        """
        # Default rate limits
        rate_limits = {
            "api_call": 100,  # per minute
            "analysis": 10,   # per minute
            "report": 5,      # per minute
        }

        limit = rate_limits.get(usage_type, 100)

        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=window_seconds)

        result = await self.db.execute(
            select(func.count(UsageRecord.id)).where(
                UsageRecord.user_id == user_id,
                UsageRecord.usage_type == usage_type,
                UsageRecord.created_at >= window_start,
            )
        )
        used = result.scalar() or 0

        return max(0, limit - int(used))

    async def cleanup_old_records(self, days: int = 90) -> int:
        """
        Clean up old usage records.

        Args:
            days: Number of days to keep

        Returns:
            Number of records deleted
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)

        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.created_at < cutoff,
                UsageRecord.is_processed,
            )
        )
        records = result.scalars().all()

        count = len(records)
        for record in records:
            await self.db.delete(record)

        await self.db.commit()

        logger.info(f"Cleaned up {count} old usage records")

        return count
