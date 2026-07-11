"""
ATLAS Platform - Report Models

This module defines the database models for report management.
Based on the specifications: Reports data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.associations import report_tags
from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.projects.project import Project


class Report(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Report model representing a generated report.

    Reports contain analyzed intelligence and insights.
    """

    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_type_created", "type", "created_at"),
        Index("ix_reports_status_created", "status", "created_at"),
    )

    # Report identification
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Report type
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # opportunity_analysis, market_research, trend_analysis, company_profile, custom

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )  # draft, generating, completed, failed

    # Content
    content: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Project relationship
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Creator
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Related data
    signal_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    opportunity_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Settings
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Export format
    export_formats: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # pdf, html, csv, json

    # Generation metadata
    generation_time_ms: Mapped[int | None] = mapped_column(
        nullable=True,
    )
    model_used: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="reports",
        lazy="selectin",
    )

    tags: Mapped[list["ReportTag"]] = relationship(
        "ReportTag",
        secondary=report_tags,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title={self.title})>"


class ReportTag(Base, UUIDMixin, TimestampMixin):
    """
    ReportTag model for categorizing reports.
    """

    __tablename__ = "report_tag_values"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ReportTag(id={self.id}, name={self.name})>"


class ReportTemplate(Base, UUIDMixin, TimestampMixin, ActiveMixin):
    """
    ReportTemplate model for report generation templates.
    """

    __tablename__ = "report_templates"
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

    # Template type
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Template configuration
    template_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Default filters
    default_filters: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Is system template
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Usage statistics
    usage_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ReportTemplate(id={self.id}, name={self.name})>"


class ReportGenerationJob(Base, UUIDMixin, TimestampMixin):
    """
    ReportGenerationJob model for tracking async report generation.
    """

    __tablename__ = "report_generation_jobs"
    __table_args__ = (
        Index("ix_report_jobs_status_created", "status", "created_at"),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Job details
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, running, completed, failed

    # Progress
    progress: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )  # 0-100

    # Configuration
    filters: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Error
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Processing details
    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ReportGenerationJob(id={self.id}, status={self.status})>"
