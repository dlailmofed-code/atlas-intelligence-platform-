"""
ATLAS Platform - Subscription Models

This module defines the database models for subscription and billing management.
Based on the specifications: Subscriptions data domain.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.users.user import User


class Subscription(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Subscription model representing a user's subscription.
    """

    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_status_started", "status", "started_at"),
    )

    # User relationship
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Plan details
    plan_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # free, starter, professional, enterprise
    plan_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
        index=True,
    )  # active, cancelled, expired, past_due, trialing

    # Billing
    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        default="monthly",
        nullable=False,
    )  # monthly, yearly

    # Dates
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Trial
    trial_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # External references
    external_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    payment_gateway: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # stripe, paypal

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="subscriptions",
        lazy="selectin",
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="subscription",
        lazy="selectin",
    )

    features: Mapped[list["SubscriptionFeature"]] = relationship(
        "SubscriptionFeature",
        back_populates="subscription",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, plan={self.plan_id}, status={self.status})>"


class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Invoice model representing a billing invoice.
    """

    __tablename__ = "invoices"
    __table_args__ = (
        Index("ix_invoices_status_due_date", "status", "due_date"),
    )

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Invoice details
    invoice_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # Amount
    subtotal: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    tax: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
    )
    total: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, paid, overdue, cancelled, refunded

    # Dates
    issue_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Payment info
    payment_method: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    external_payment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Line items
    line_items: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # PDF
    pdf_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="invoices",
        lazy="selectin",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="invoice",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, number={self.invoice_number}, status={self.status})>"


class Payment(Base, UUIDMixin, TimestampMixin):
    """
    Payment model representing a payment transaction.
    """

    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_status_created", "status", "created_at"),
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payment details
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, processing, completed, failed, refunded

    # Gateway info
    payment_gateway: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    external_payment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    external_charge_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Method
    payment_method: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    payment_method_details: Mapped[dict | None] = mapped_column(
        JSON,
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

    # Processed timestamps
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        back_populates="payments",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"


class SubscriptionFeature(Base, UUIDMixin, TimestampMixin):
    """
    SubscriptionFeature model for tracking enabled features per subscription.
    """

    __tablename__ = "subscription_features"
    __table_args__ = ()

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    feature_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Limits
    limit_value: Mapped[int | None] = mapped_column(
        nullable=True,
    )  # null means unlimited
    used_value: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="features",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SubscriptionFeature(id={self.id}, key={self.feature_key})>"


class Plan(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Plan model representing available subscription plans.
    """

    __tablename__ = "plans"
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
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Pricing
    price_monthly: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    price_yearly: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Features
    features: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Limits
    limits: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Order
    display_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, name={self.name})>"
