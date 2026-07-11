"""
ATLAS Platform - Notification Models

This module defines the database models for notification management.
Based on the specifications: Notifications data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.users.user import User


class Notification(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Notification model representing a user notification.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_type_created", "type", "created_at"),
    )

    # Notification identification
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Notification type
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # signal_alert, opportunity_update, report_ready, system, reminder

    # Priority
    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False,
    )  # low, normal, high, urgent

    # Related entities
    related_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # signal, opportunity, report, user
    related_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Status
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Action
    action_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    action_text: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, title={self.title})>"


class UserNotificationPreference(Base, UUIDMixin, TimestampMixin):
    """
    UserNotificationPreference model for managing user notification settings.
    """

    __tablename__ = "user_notification_preferences"
    __table_args__ = ()

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Notification type
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Channel preferences
    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    push_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    sms_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Frequency
    frequency: Mapped[str] = mapped_column(
        String(20),
        default="immediate",
        nullable=False,
    )  # immediate, daily_digest, weekly_digest

    # Filters
    filters: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notification_preferences",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserNotificationPreference(id={self.id}, type={self.notification_type})>"


class NotificationLog(Base, UUIDMixin, TimestampMixin):
    """
    NotificationLog model for tracking notification delivery.
    """

    __tablename__ = "notification_logs"
    __table_args__ = (
        Index("ix_notification_logs_status_sent_at", "status", "sent_at"),
    )

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Delivery details
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # email, push, sms, in_app

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, sent, delivered, failed, bounced

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Error tracking
    error_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # External tracking
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )  # Provider message ID

    # Retry tracking
    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    max_retries: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<NotificationLog(id={self.id}, status={self.status})>"
