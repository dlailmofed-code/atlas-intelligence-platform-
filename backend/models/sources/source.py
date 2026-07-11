"""
ATLAS Platform - Source Models

This module defines the database models for data sources management.
Based on the specifications: Sources data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import ActiveMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.evidence.evidence import Evidence


class Source(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Source model representing an external data source.

    Sources are external services or websites that provide data.
    """

    __tablename__ = "sources"
    __table_args__ = (
        Index("ix_sources_type_active", "type", "is_active"),
    )

    # Source identification
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Source type
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # news, academic, government, financial, social, web, api, database

    # Connection details
    base_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    api_endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Authentication
    auth_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # none, api_key, oauth2, basic, bearer
    auth_config: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )  # Encrypted credentials

    # Rate limiting
    rate_limit_per_minute: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    rate_limit_per_day: Mapped[int] = mapped_column(
        Integer,
        default=1000,
        nullable=False,
    )

    # Reliability metrics
    reliability_score: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )  # 0-1

    # Status
    is_crawlable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    requires_proxy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Scheduling
    schedule_type: Mapped[str] = mapped_column(
        String(50),
        default="manual",
        nullable=False,
    )  # manual, hourly, daily, weekly, realtime
    schedule_config: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    last_crawled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_crawl_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Statistics
    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    successful_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    failed_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="source",
        lazy="selectin",
    )

    connectors: Mapped[list["Connector"]] = relationship(
        "Connector",
        back_populates="source",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name={self.name})>"


class Connector(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Connector model for managing data collection from sources.

    Connectors handle the technical aspects of data collection.
    """

    __tablename__ = "connectors"
    __table_args__ = ()

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Connector type
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # api, crawler, webhook, file_import

    # Source relationship
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Configuration
    config: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="idle",
        nullable=False,
    )  # idle, running, paused, error

    # Health
    health_status: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        nullable=False,
    )  # healthy, degraded, unhealthy, unknown
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    consecutive_failures: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Performance
    avg_response_time_ms: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    success_rate: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    # Relationships
    source: Mapped["Source"] = relationship(
        "Source",
        back_populates="connectors",
        lazy="selectin",
    )

    crawl_jobs: Mapped[list["CrawlJob"]] = relationship(
        "CrawlJob",
        back_populates="connector",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Connector(id={self.id}, name={self.name})>"


class CrawlJob(Base, UUIDMixin, TimestampMixin):
    """
    CrawlJob model for tracking data collection jobs.
    """

    __tablename__ = "crawl_jobs"
    __table_args__ = (
        Index("ix_crawl_jobs_status_started", "status", "started_at"),
    )

    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Job details
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, running, completed, failed, cancelled

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Results
    records_processed: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    records_created: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    records_updated: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    records_failed: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Error
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Configuration snapshot
    config_snapshot: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    connector: Mapped["Connector"] = relationship(
        "Connector",
        back_populates="crawl_jobs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CrawlJob(id={self.id}, status={self.status})>"
