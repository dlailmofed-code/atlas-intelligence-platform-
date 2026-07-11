"""
ATLAS Platform - Usage Record Models

This module defines the database models for usage tracking and quotas.
Based on the specifications: Usage Limits system.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.subscriptions.subscription import Subscription
    from backend.models.users.user import User


class UsageRecord(Base, UUIDMixin, TimestampMixin):
    """
    UsageRecord model for tracking individual usage events.

    Records each usage event for rate limiting and quota tracking.
    """

    __tablename__ = "usage_records"
    __table_args__ = (
        Index("ix_usage_records_user_type_date", "user_id", "usage_type", "created_at"),
        Index("ix_usage_records_reset_at", "reset_at"),
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Subscription (for quota limits)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Usage type
    usage_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # analysis, report, api_call, export, etc.

    # Usage amount
    amount: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    # Resource identifier (optional)
    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Reset time (for rolling windows)
    reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Processed flag
    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UsageRecord(type={self.usage_type}, amount={self.amount})>"


class UsageSummary(Base, UUIDMixin, TimestampMixin):
    """
    UsageSummary model for caching aggregated usage data.

    Provides quick lookups for quota checking.
    """

    __tablename__ = "usage_summaries"
    __table_args__ = (
        Index("ix_usage_summaries_user_type_period", "user_id", "usage_type", "period_start"),
        Index("ix_usage_summaries_period_start", "period_start"),
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Usage type
    usage_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Period
    period_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # daily, weekly, monthly

    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Counts
    total_usage: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    last_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Concurrent usage (for concurrent analysis limits)
    concurrent_usage: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )

    @classmethod
    def get_period_bounds(cls, period_type: str, reference_time: datetime | None = None) -> tuple:
        """Calculate period start and end times."""
        if reference_time is None:
            reference_time = datetime.now(UTC)

        if period_type == "daily":
            period_start = reference_time.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period_type == "weekly":
            # Week starts on Monday
            days_since_monday = reference_time.weekday()
            period_start = (reference_time - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            period_end = period_start + timedelta(days=7)
        elif period_type == "monthly":
            period_start = reference_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Last day of month
            if reference_time.month == 12:
                period_end = reference_time.replace(year=reference_time.year + 1, month=1, day=1)
            else:
                period_end = reference_time.replace(month=reference_time.month + 1, day=1)
        else:
            raise ValueError(f"Unknown period type: {period_type}")

        return period_start, period_end

    def __repr__(self) -> str:
        return f"<UsageSummary(type={self.usage_type}, total={self.total_usage})>"
