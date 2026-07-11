"""
ATLAS Platform - Evidence Models

This module defines the database models for evidence management.
Based on the specifications: Evidence data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.signals.signal import Signal
    from backend.models.sources.source import Source


class Evidence(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Evidence model representing raw or processed evidence.

    Evidence is the supporting data behind intelligence signals.
    """

    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_reliability_created", "reliability", "created_at"),
        Index("ix_evidence_extracted_at", "extracted_at"),
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Source reference
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # news, academic, government, financial, social, web

    # Source reliability
    reliability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1
    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Evidence metrics
    relevance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1
    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1

    # Verification
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Extracted entities
    entities: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Signal relationship
    signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("signals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamps
    extracted_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    signal: Mapped[Optional["Signal"]] = relationship(
        "Signal",
        back_populates="evidence",
        lazy="selectin",
    )

    source: Mapped[Optional["Source"]] = relationship(
        "Source",
        back_populates="evidence",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Evidence(id={self.id}, source={self.source_name})>"


class EvidenceVersion(Base, UUIDMixin, TimestampMixin):
    """
    EvidenceVersion model for tracking evidence changes.

    Maintains historical versions of evidence for audit purposes.
    """

    __tablename__ = "evidence_versions"
    __table_args__ = ()

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    reliability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    change_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<EvidenceVersion(id={self.id}, evidence_id={self.evidence_id})>"
