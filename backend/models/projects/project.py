"""
ATLAS Platform - Project Models

This module defines the database models for project management.
Based on the specifications: Projects data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.associations import organization_members, project_members
from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.reports.report import Report
    from backend.models.signals.signal import Opportunity, SavedFilter
    from backend.models.users.user import User


class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Organization model representing a company or organization.

    Organizations can contain multiple users and projects.
    """

    __tablename__ = "organizations"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Address
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Industry
    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    company_size: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # startup, smb, enterprise

    # Settings
    settings: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=organization_members,
        back_populates="organizations",
        lazy="selectin",
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="organization",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name})>"


class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Project model representing a user's project or workspace.

    Projects contain opportunities, saved filters, and reports.
    """

    __tablename__ = "projects"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Organization relationship
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Project settings
    settings: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Project type
    project_type: Mapped[str] = mapped_column(
        String(50),
        default="default",
        nullable=False,
    )  # default, research, investment, monitoring

    # Geography filters
    geographies: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Industry filters
    industries: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Status
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="projects",
        lazy="selectin",
    )

    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=project_members,
        back_populates="projects",
        lazy="selectin",
    )

    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="project",
        lazy="selectin",
    )

    saved_filters: Mapped[list["SavedFilter"]] = relationship(
        "SavedFilter",
        back_populates="project",
        lazy="selectin",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="project",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"


class ProjectInvite(Base, UUIDMixin, TimestampMixin):
    """
    ProjectInvite model for inviting users to projects.
    """

    __tablename__ = "project_invites"
    __table_args__ = ()

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="member",
        nullable=False,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ProjectInvite(id={self.id}, email={self.email})>"
