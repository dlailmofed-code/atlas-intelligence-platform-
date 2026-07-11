"""
ATLAS Platform - Signal Models

This module defines the database models for intelligence signals.
Based on the specifications: Signals data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.associations import signal_tags, user_favorite_opportunities
from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.evidence.evidence import Evidence
    from backend.models.projects.project import Project
    from backend.models.users.user import User


class Signal(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Signal model representing an intelligence signal.

    Signals are discovered patterns or indicators in data sources.
    """

    __tablename__ = "signals"
    __table_args__ = (
        Index("ix_signals_type_created", "type", "created_at"),
        Index("ix_signals_category_created", "category", "created_at"),
        Index("ix_signals_intensity", "intensity"),
        Index("ix_signals_confidence", "confidence"),
    )

    # Signal identification
    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Signal classification
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # demand, growth, innovation, investment, regulatory, competition, social, economic, technology

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # market, regulation, technology, financial, social, competition, operational, geopolitical

    # Signal metrics
    intensity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )  # 0-100

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )  # 0-1

    trend: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # up, down, stable, volatile

    # Context
    entities: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # List of entity names

    geography: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    region: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Source information
    source_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )  # List of source UUIDs

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=signal_tags,
        lazy="selectin",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="signal",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Signal(id={self.id}, name={self.name}, type={self.type})>"


class Tag(Base, UUIDMixin, TimestampMixin):
    """
    Tag model for categorizing signals.
    """

    __tablename__ = "tags"

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
    )  # hex color code

    # Relationships
    signals: Mapped[list["Signal"]] = relationship(
        "Signal",
        secondary=signal_tags,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class Opportunity(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Opportunity model representing a business opportunity.

    Opportunities are generated from signals and patterns.
    """

    __tablename__ = "opportunities"
    __table_args__ = (
        Index("ix_opportunities_status_created", "status", "created_at"),
        Index("ix_opportunities_score", "score_overall"),
    )

    # Opportunity identification
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Classification
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    geography: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Scores
    score_overall: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )  # 0-100

    score_demand: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    score_growth: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    score_competition: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    score_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Confidence
    overall_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
        nullable=False,
        index=True,
    )  # new, reviewed, pursuing, archived

    # Project relationship
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Related intelligence
    signal_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Insights
    key_insights: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    recommended_actions: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    risk_factors: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="opportunities",
        lazy="selectin",
    )

    favorited_by: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_favorite_opportunities,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, title={self.title})>"


class SavedFilter(Base, UUIDMixin, TimestampMixin, ActiveMixin):
    """
    SavedFilter model for storing user's filter configurations.
    """

    __tablename__ = "saved_filters"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Filter configuration
    filters: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Project relationship
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="saved_filters",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SavedFilter(id={self.id}, name={self.name})>"
