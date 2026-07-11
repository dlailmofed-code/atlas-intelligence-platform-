"""
ATLAS Platform - Feature Flag Models

This module defines the database models for feature flags and feature management.
Based on the specifications: Feature Flags system.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.users.user import User


class FeatureFlag(Base, UUIDMixin, TimestampMixin):
    """
    FeatureFlag model for controlling feature availability.

    Supports various targeting rules:
    - By subscription plan
    - By user role
    - By experiment group
    - By geographic region
    - By percentage of users
    """

    __tablename__ = "feature_flags"
    __table_args__ = (
        Index("ix_feature_flags_key", "key", unique=True),
        Index("ix_feature_flags_is_active", "is_active"),
    )

    # Flag identification
    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_rollout: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )  # If true, gradually rolling out to users

    # Targeting rules
    rollout_percentage: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )  # 0-100, percentage of users to enable

    # Plan-based targeting
    enabled_plans: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # List of plan IDs: ["free", "starter", "professional", "enterprise"]

    # Role-based targeting
    enabled_roles: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # List of role names that can access this feature

    # Region-based targeting
    enabled_regions: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # List of region codes: ["US", "EU", "APAC"]

    # Experiment group
    experiment_group: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Beta testers
    is_beta: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Display info
    documentation_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    overrides: Mapped[list["FeatureFlagOverride"]] = relationship(
        "FeatureFlagOverride",
        back_populates="feature_flag",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<FeatureFlag(key={self.key}, is_active={self.is_active})>"


class FeatureFlagOverride(Base, UUIDMixin, TimestampMixin):
    """
    FeatureFlagOverride model for user-specific feature flag overrides.

    Allows admins to force-enable or force-disable a feature for specific users.
    """

    __tablename__ = "feature_flag_overrides"
    __table_args__ = (
        Index("ix_feature_flag_overrides_user_flag", "user_id", "feature_flag_id", unique=True),
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Feature flag relationship
    feature_flag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feature_flags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Override value
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )  # True = force enable, False = force disable

    # Reason
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Expires at (optional)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Created by (admin)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="selectin",
    )
    feature_flag: Mapped["FeatureFlag"] = relationship(
        "FeatureFlag",
        back_populates="overrides",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<FeatureFlagOverride(user_id={self.user_id}, flag={self.feature_flag_id})>"
