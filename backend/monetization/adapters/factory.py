"""
ATLAS Platform - Payment Adapter Factory

This module provides a factory for creating payment provider adapters.
Based on the specifications: Adapter Pattern and Dependency Injection.
"""


from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class PaymentAdapterFactory:
    """
    Factory for creating payment provider adapters.

    Uses the Adapter Pattern to provide a unified interface
    to different payment providers while allowing easy switching.
    """

    _adapters: dict[str, type] = {}
    _current_adapter: str | None = None

    @classmethod
    def register(cls, name: str, adapter_class: type) -> None:
        """
        Register a payment adapter.

        Args:
            name: Adapter name (e.g., 'stripe', 'paypal')
            adapter_class: Adapter class
        """
        cls._adapters[name.lower()] = adapter_class
        logger.info(f"Registered payment adapter: {name}")

    @classmethod
    def get_adapter(cls, name: str | None = None):
        """
        Get a payment adapter instance.

        Args:
            name: Adapter name. If None, uses configured default.

        Returns:
            Payment adapter instance

        Raises:
            ValueError: If adapter not found or not configured
        """
        if name is None:
            name = cls._current_adapter or get_settings().payment.default_provider

        adapter_class = cls._adapters.get(name.lower())

        if adapter_class is None:
            raise ValueError(
                f"Payment adapter '{name}' not found. "
                f"Available adapters: {list(cls._adapters.keys())}"
            )

        return adapter_class()

    @classmethod
    def set_default(cls, name: str) -> None:
        """
        Set the default payment adapter.

        Args:
            name: Adapter name
        """
        if name.lower() not in cls._adapters:
            raise ValueError(f"Unknown adapter: {name}")

        cls._current_adapter = name.lower()
        logger.info(f"Default payment adapter set to: {name}")

    @classmethod
    def get_default_name(cls) -> str:
        """Get the name of the default adapter."""
        return cls._current_adapter or get_settings().payment.default_provider

    @classmethod
    def list_adapters(cls) -> list[str]:
        """List all registered adapters."""
        return list(cls._adapters.keys())


# =============================================================================
# Webhook Event Types (Provider-Independent)
# =============================================================================

class WebhookEventType:
    """Standard webhook event types across all providers."""

    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"

    # Payment method events
    PAYMENT_METHOD_ATTACHED = "payment_method.attached"
    PAYMENT_METHOD_DETACHED = "payment_method.detached"
    PAYMENT_METHOD_UPDATED = "payment_method.updated"

    # Subscription events
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_DELETED = "subscription.deleted"
    SUBSCRIPTION_PAUSED = "subscription.paused"
    SUBSCRIPTION_RESUMED = "subscription.resumed"

    # Billing events
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    INVOICE_VOIDED = "invoice.voided"

    # Payment events
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"

    # Status events
    SUBSCRIPTION_TRIAL_ENDING = "subscription.trial_ending"
    SUBSCRIPTION_RENEWED = "subscription.renewed"


# =============================================================================
# Subscription Status (Provider-Independent)
# =============================================================================

class SubscriptionStatus:
    """Standard subscription status values."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    PAUSED = "paused"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


# =============================================================================
# Payment Status (Provider-Independent)
# =============================================================================

class PaymentStatus:
    """Standard payment status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
