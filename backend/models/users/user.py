"""
ATLAS Platform - User Models

This module defines the database models for user management.
Based on the specifications: Users data domain.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.associations import (
    organization_members,
    project_members,
    role_permissions,
    user_roles,
)
from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.knowledge.knowledge import UserActivity
    from backend.models.notifications.notification import Notification, UserNotificationPreference
    from backend.models.projects.project import Organization, Project
    from backend.models.subscriptions.subscription import Subscription


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    User model representing a platform user.

    Stores user profile information, authentication data, and preferences.
    """

    __tablename__ = "users"
    __table_args__ = ()

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile fields
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    job_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Preferences
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        nullable=False,
    )
    theme: Mapped[str] = mapped_column(
        String(20),
        default="light",
        nullable=False,
    )  # light, dark, system

    # Authentication
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 2FA
    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    two_factor_secret: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    backup_codes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON array of backup codes

    # OAuth
    oauth_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # google, github, linkedin
    oauth_provider_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary=organization_members,
        back_populates="members",
        lazy="selectin",
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        secondary=project_members,
        back_populates="members",
        lazy="selectin",
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        lazy="selectin",
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="selectin",
    )

    notification_preferences: Mapped[list["UserNotificationPreference"]] = relationship(
        "UserNotificationPreference",
        back_populates="user",
        lazy="selectin",
    )

    activities: Mapped[list["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Role(Base, UUIDMixin, TimestampMixin):
    """
    Role model for user authorization.

    Defines roles with specific permissions.
    """

    __tablename__ = "roles"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )  # System roles cannot be deleted

    # Relationships
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(Base, UUIDMixin, TimestampMixin):
    """
    Permission model for granular access control.

    Defines specific actions that can be performed on resources.
    """

    __tablename__ = "permissions"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # users, projects, reports, signals, etc.
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # create, read, update, delete, manage
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"
