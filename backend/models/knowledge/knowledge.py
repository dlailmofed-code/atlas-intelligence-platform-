"""
ATLAS Platform - Knowledge Models

This module defines the database models for knowledge graph and indicators.
Based on the specifications: Knowledge Graph and Indicators data domains.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.users.user import User


class KnowledgeEntity(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    KnowledgeEntity model representing an entity in the knowledge graph.
    """

    __tablename__ = "knowledge_entities"
    __table_args__ = (
        Index("ix_knowledge_entities_type_name", "type", "name"),
        Index("ix_knowledge_entities_external_id", "external_source", "external_id"),
    )

    # Entity identification
    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # person, organization, company, product, technology, market, industry, geography, regulation, event, trend, concept

    # External references
    external_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Properties
    properties: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Description
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Aliases
    aliases: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Metrics
    mention_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    relevance_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # Timestamps
    last_mentioned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    outgoing_relations: Mapped[list["KnowledgeRelation"]] = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.source_id",
        back_populates="source",
        lazy="selectin",
    )

    incoming_relations: Mapped[list["KnowledgeRelation"]] = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.target_id",
        back_populates="target",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeEntity(id={self.id}, name={self.name}, type={self.type})>"


class KnowledgeRelation(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    KnowledgeRelation model representing a relationship between entities.
    """

    __tablename__ = "knowledge_relations"
    __table_args__ = (
        Index("ix_knowledge_relations_type", "type"),
    )

    # Entity references
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship type
    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # acquires, acquired_by, partners_with, competes_with, invests_in, funded_by, offers, uses_technology, targets_market, located_in, operates_in, serves_region, regulates, regulated_by, causes, enables, prevents, trends_toward, evolved_from, precedes

    # Properties
    properties: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Metrics
    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )  # 0-1
    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )  # 0-1

    # Evidence
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Context
    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Validity
    valid_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    source: Mapped["KnowledgeEntity"] = relationship(
        "KnowledgeEntity",
        foreign_keys=[source_id],
        back_populates="outgoing_relations",
        lazy="selectin",
    )

    target: Mapped["KnowledgeEntity"] = relationship(
        "KnowledgeEntity",
        foreign_keys=[target_id],
        back_populates="incoming_relations",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeRelation(id={self.id}, type={self.type})>"


class IntelligenceIndicator(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    IntelligenceIndicator model for storing calculated indicators over time.
    """

    __tablename__ = "intelligence_indicators"
    __table_args__ = (
        Index("ix_indicators_indicator_type_timestamp", "indicator_type", "timestamp"),
    )

    # Indicator identification
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    indicator_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # opportunity_score, demand_index, market_momentum, capital_attraction, competition_index, innovation_index, risk_index, regulatory_stability, supply_stability, geographic_opportunity, expansion_readiness, strategic_fit

    # Value
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-100 typically

    # Context
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

    # Confidence
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Related signals
    signal_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<IntelligenceIndicator(id={self.id}, type={self.indicator_type}, value={self.value})>"


class UserActivity(Base, UUIDMixin, TimestampMixin):
    """
    UserActivity model for tracking user activities.
    """

    __tablename__ = "user_activities"
    __table_args__ = (
        Index("ix_user_activities_user_created", "user_id", "created_at"),
        Index("ix_user_activities_activity_type", "activity_type", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Activity details
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # login, logout, view_signal, view_opportunity, create_project, generate_report, etc.

    # Related entity
    entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Details
    details: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # IP and user agent
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="activities",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, type={self.activity_type})>"


class CausalLink(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    CausalLink model for storing causal relationships between entities.
    """

    __tablename__ = "causal_links"
    __table_args__ = (
        Index("ix_causal_links_confidence", "confidence"),
    )

    # Cause and effect
    cause_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    effect_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship classification
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # correlation, possible_causation, strong_evidence, confirmed, unknown

    # Confidence
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0-1

    # Evidence summary
    evidence_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Context
    confounding_factors: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    mechanism: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    time_lag: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Evidence
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CausalLink(id={self.id}, type={self.relationship_type})>"
