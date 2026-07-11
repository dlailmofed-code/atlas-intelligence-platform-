"""
ATLAS Platform - Payment Webhook Handler

This module provides webhook handling for payment events.
Based on the specifications: Webhook Architecture for secure payment processing.
"""

import hashlib
import hmac
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.subscriptions import Invoice, Payment, Subscription
from backend.monetization.adapters.factory import (
    SubscriptionStatus,
    WebhookEventType,
)

logger = get_logger(__name__)


class WebhookHandler:
    """
    Handler for payment provider webhooks.

    Processes webhook events and updates local database accordingly.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the webhook handler.

        Args:
            db: Database session
        """
        self.db = db
        self._event_handlers: dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # Subscription handlers
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_CREATED,
            self._handle_subscription_created
        )
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_UPDATED,
            self._handle_subscription_updated
        )
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_DELETED,
            self._handle_subscription_deleted
        )
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_PAUSED,
            self._handle_subscription_paused
        )
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_RESUMED,
            self._handle_subscription_resumed
        )

        # Invoice handlers
        self.register_handler(
            WebhookEventType.INVOICE_CREATED,
            self._handle_invoice_created
        )
        self.register_handler(
            WebhookEventType.INVOICE_PAID,
            self._handle_invoice_paid
        )
        self.register_handler(
            WebhookEventType.INVOICE_PAYMENT_FAILED,
            self._handle_invoice_payment_failed
        )

        # Payment handlers
        self.register_handler(
            WebhookEventType.PAYMENT_SUCCEEDED,
            self._handle_payment_succeeded
        )
        self.register_handler(
            WebhookEventType.PAYMENT_FAILED,
            self._handle_payment_failed
        )
        self.register_handler(
            WebhookEventType.PAYMENT_REFUNDED,
            self._handle_payment_refunded
        )

        # Trial handlers
        self.register_handler(
            WebhookEventType.SUBSCRIPTION_TRIAL_ENDING,
            self._handle_trial_ending
        )

    def register_handler(
        self,
        event_type: str,
        handler: Callable[[dict], None],
    ) -> None:
        """
        Register a webhook event handler.

        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        self._event_handlers[event_type] = handler

    async def handle_event(
        self,
        event_type: str,
        event_data: dict,
        raw_payload: bytes | None = None,
    ) -> dict:
        """
        Handle a webhook event.

        Args:
            event_type: Event type
            event_data: Event data
            raw_payload: Original payload for verification

        Returns:
            Result of handling
        """
        logger.info(
            "Handling webhook event",
            event_type=event_type,
            event_id=event_data.get("id"),
        )

        handler = self._event_handlers.get(event_type)

        if handler is None:
            logger.warning(f"No handler for event type: {event_type}")
            return {"status": "ignored", "reason": "No handler"}

        try:
            await handler(event_data)
            return {"status": "processed"}
        except Exception as e:
            logger.error(
                "Error handling webhook event",
                event_type=event_type,
                error=str(e),
            )
            return {"status": "error", "error": str(e)}

    # -------------------------------------------------------------------------
    # Subscription Handlers
    # -------------------------------------------------------------------------

    async def _handle_subscription_created(self, data: dict) -> None:
        """Handle subscription creation."""
        external_id = data.get("id")

        # Find subscription by external ID
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.external_subscription_id == external_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = data.get("status", "active")
            subscription.current_period_start = self._parse_datetime(
                data.get("current_period_start")
            )
            subscription.current_period_end = self._parse_datetime(
                data.get("current_period_end")
            )

            if data.get("trial_end"):
                subscription.trial_end = self._parse_datetime(
                    data.get("trial_end")
                )

            await self.db.commit()
            logger.info("Subscription created from webhook", id=external_id)

    async def _handle_subscription_updated(self, data: dict) -> None:
        """Handle subscription update."""
        external_id = data.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.external_subscription_id == external_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = data.get("status", "active")
            subscription.current_period_start = self._parse_datetime(
                data.get("current_period_start")
            )
            subscription.current_period_end = self._parse_datetime(
                data.get("current_period_end")
            )
            await self.db.commit()

    async def _handle_subscription_deleted(self, data: dict) -> None:
        """Handle subscription cancellation."""
        external_id = data.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.external_subscription_id == external_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.now(UTC)
            await self.db.commit()

    async def _handle_subscription_paused(self, data: dict) -> None:
        """Handle subscription pause."""
        external_id = data.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.external_subscription_id == external_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.PAUSED
            await self.db.commit()

    async def _handle_subscription_resumed(self, data: dict) -> None:
        """Handle subscription resume."""
        external_id = data.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.external_subscription_id == external_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            await self.db.commit()

    # -------------------------------------------------------------------------
    # Invoice Handlers
    # -------------------------------------------------------------------------

    async def _handle_invoice_created(self, data: dict) -> None:
        """Handle invoice creation."""
        invoice_id = data.get("id")

        result = await self.db.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            # Create new invoice record
            subscription_id = data.get("subscription")
            subscription = None

            if subscription_id:
                sub_result = await self.db.execute(
                    select(Subscription).where(
                        Subscription.external_subscription_id == subscription_id
                    )
                )
                subscription = sub_result.scalar_one_or_none()

            if subscription:
                invoice = Invoice(
                    subscription_id=subscription.id,
                    invoice_number=invoice_id,
                    subtotal=data.get("subtotal", 0),
                    tax=data.get("tax", 0),
                    total=data.get("total", 0),
                    currency=data.get("currency", "USD"),
                    status="pending",
                    issue_date=datetime.now(UTC),
                    due_date=self._parse_datetime(data.get("due_date")),
                    line_items=data.get("lines", []),
                )
                self.db.add(invoice)
                await self.db.commit()

    async def _handle_invoice_paid(self, data: dict) -> None:
        """Handle successful invoice payment."""
        invoice_id = data.get("id")

        result = await self.db.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if invoice:
            invoice.status = "paid"
            invoice.paid_at = datetime.now(UTC)
            invoice.payment_method = data.get("payment_method")
            await self.db.commit()

            # Also update subscription status
            if invoice.subscription_id:
                sub_result = await self.db.execute(
                    select(Subscription).where(
                        Subscription.id == invoice.subscription_id
                    )
                )
                subscription = sub_result.scalar_one_or_none()

                if subscription:
                    subscription.status = SubscriptionStatus.ACTIVE
                    await self.db.commit()

    async def _handle_invoice_payment_failed(self, data: dict) -> None:
        """Handle failed invoice payment."""
        invoice_id = data.get("id")

        result = await self.db.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if invoice:
            invoice.status = "overdue"
            await self.db.commit()

            # Update subscription to past_due
            if invoice.subscription_id:
                sub_result = await self.db.execute(
                    select(Subscription).where(
                        Subscription.id == invoice.subscription_id
                    )
                )
                subscription = sub_result.scalar_one_or_none()

                if subscription:
                    subscription.status = SubscriptionStatus.PAST_DUE
                    await self.db.commit()

    # -------------------------------------------------------------------------
    # Payment Handlers
    # -------------------------------------------------------------------------

    async def _handle_payment_succeeded(self, data: dict) -> None:
        """Handle successful payment."""
        payment_id = data.get("id")

        result = await self.db.execute(
            select(Payment).where(
                Payment.external_payment_id == payment_id
            )
        )
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "completed"
            payment.processed_at = datetime.now(UTC)
            await self.db.commit()

    async def _handle_payment_failed(self, data: dict) -> None:
        """Handle failed payment."""
        payment_id = data.get("id")

        result = await self.db.execute(
            select(Payment).where(
                Payment.external_payment_id == payment_id
            )
        )
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "failed"
            payment.error_code = data.get("error", {}).get("code")
            payment.error_message = data.get("error", {}).get("message")
            await self.db.commit()

    async def _handle_payment_refunded(self, data: dict) -> None:
        """Handle refund."""
        payment_id = data.get("id")

        result = await self.db.execute(
            select(Payment).where(
                Payment.external_payment_id == payment_id
            )
        )
        payment = result.scalar_one_or_none()

        if payment:
            payment.status = "refunded"
            await self.db.commit()

    # -------------------------------------------------------------------------
    # Trial Handlers
    # -------------------------------------------------------------------------

    async def _handle_trial_ending(self, data: dict) -> None:
        """Handle trial ending notification."""
        # This is typically used to send email reminders
        # Implementation depends on notification system
        logger.info(
            "Trial ending",
            subscription_id=data.get("subscription"),
            trial_end=data.get("trial_end"),
        )

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def _parse_datetime(self, value: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=UTC)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def _generate_webhook_secret(self, payload: bytes, timestamp: int) -> str:
        """
        Generate webhook secret for verification.

        Args:
            payload: Request payload
            timestamp: Request timestamp

        Returns:
            Secret signature
        """
        # This should be overridden by specific adapters
        # with their own signing methods
        secret = get_settings().payment.stripe_webhook_secret
        signed_payload = f"{timestamp}.{payload.decode()}"
        return hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()


def generate_idempotency_key(event_type: str, event_id: str) -> str:
    """
    Generate an idempotency key for webhook processing.

    Prevents duplicate processing of the same event.

    Args:
        event_type: Event type
        event_id: Event ID from provider

    Returns:
        Idempotency key
    """
    return f"{event_type}:{event_id}"
