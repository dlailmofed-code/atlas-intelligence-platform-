"""
ATLAS Platform - Monetization Organization Models

This module defines the database models for organization billing and seat management.
Extends the existing Organization model with billing-specific fields.

Based on the specifications: Enterprise Organization Support.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.common.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    pass


class BillingOrganization(Base, UUIDMixin, TimestampMixin):
    """
    BillingOrganization model for managing billing-related organization data.

    This is a separate model to avoid conflicts with the existing Organization model.
    It stores billing contacts, subscription tiers, and other billing metadata.
    """

    __tablename__ = "billing_organizations"
    __table_args__ = (
        Index("ix_billing_orgs_slug", "slug", unique=True),
        Index("ix_billing_orgs_subscription_tier", "subscription_tier"),
    )

    # Link to main organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Organization details
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # Billing contact
    billing_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    billing_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    billing_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Billing address
    billing_address_line1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    billing_address_line2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    billing_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    billing_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    billing_postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    billing_country: Mapped[str] = mapped_column(
        String(2),
        default="US",
        nullable=False,
    )

    # Subscription tier
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False,
    )  # free, starter, professional, enterprise

    # VAT/Tax
    tax_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    tax_exempt: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Payment settings
    default_payment_method: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    preferred_currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Settings
    settings: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Active flag
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<BillingOrganization(name={self.name}, tier={self.subscription_tier})>"


class Seat(Base, UUIDMixin, TimestampMixin):
    """
    Seat model for tracking organization seat usage.

    Tracks purchased vs. used seats for billing purposes.
    """

    __tablename__ = "organization_seats"
    __table_args__ = (
        Index("ix_organization_seats_org_type", "organization_id", "seat_type"),
    )

    # Organization relationship
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Seat details
    seat_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # standard, professional, admin, viewer

    # Seat limits
    total_seats: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    used_seats: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Pending invitations
    pending_seats: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Period
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    @property
    def available_seats(self) -> int:
        """Calculate available seats."""
        return max(0, self.total_seats - self.used_seats - self.pending_seats)

    def __repr__(self) -> str:
        return f"<Seat(type={self.seat_type}, total={self.total_seats}, used={self.used_seats})>"
