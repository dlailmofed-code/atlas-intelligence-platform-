"""
ATLAS Platform - Association Tables

This module defines all many-to-many association tables.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID

from backend.models.common.base import Base

# User-Organization relationship
organization_members = Table(
    "organization_members",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("is_owner", Boolean, default=False, nullable=False),
    Column("role", String(50), default="member", nullable=False),  # owner, admin, member
)


# User-Role relationship
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


# Role-Permission relationship
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


# Project-Member relationship
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(50), default="member", nullable=False),  # owner, admin, member, viewer
    Column("can_edit", Boolean, default=True, nullable=False),
    Column("can_delete", Boolean, default=False, nullable=False),
)


# User-FavoriteOpportunity relationship
user_favorite_opportunities = Table(
    "user_favorite_opportunities",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("opportunity_id", UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
)


# Signal-Tag relationship
signal_tags = Table(
    "signal_tags",
    Base.metadata,
    Column("signal_id", UUID(as_uuid=True), ForeignKey("signals.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


# Evidence-Source relationship
evidence_sources = Table(
    "evidence_sources",
    Base.metadata,
    Column("evidence_id", UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


# Report-Tag relationship
report_tags = Table(
    "report_tags",
    Base.metadata,
    Column("report_id", UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("report_tag_values.id", ondelete="CASCADE"), primary_key=True),
)


# Notification-User relationship (for batch notifications)
notification_recipients = Table(
    "notification_recipients",
    Base.metadata,
    Column("notification_id", UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("read_at", Boolean, default=False, nullable=True),
    Column("read_at_timestamp", DateTime(timezone=True), nullable=True),
)
