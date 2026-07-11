"""
ATLAS Platform - Payment Provider Base Interface

This module defines the abstract interfaces for payment providers.
Based on the specifications: Payment Architecture - Provider-independent abstractions.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field

# =============================================================================
# Data Models
# =============================================================================

class Money(BaseModel):
    """Represents a monetary amount."""

    amount: float = Field(ge=0)
    currency: str = Field(default="USD", max_length=3)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


class BillingAddress(BaseModel):
    """Customer billing address."""

    name: str
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str


class CustomerInfo(BaseModel):
    """Customer information for billing."""

    id: str | None = None
    email: str
    name: str
    phone: str | None = None
    billing_address: BillingAddress | None = None
    metadata: dict = Field(default_factory=dict)


class SubscriptionInfo(BaseModel):
    """Subscription information."""

    plan_id: str
    plan_name: str
    interval: str = "month"  # month, year
    interval_count: int = 1
    quantity: int = 1
    trial_days: int = 0
    metadata: dict = Field(default_factory=dict)


class PaymentMethod(BaseModel):
    """Payment method information."""

    id: str
    type: str  # card, bank_account, etc.
    last4: str | None = None
    brand: str | None = None
    exp_month: int | None = None
    exp_year: int | None = None
    is_default: bool = False


class PaymentResult(BaseModel):
    """Result of a payment operation."""

    success: bool
    transaction_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    amount: Money | None = None
    payment_method: PaymentMethod | None = None
    metadata: dict = Field(default_factory=dict)


class SubscriptionResult(BaseModel):
    """Result of a subscription operation."""

    success: bool
    subscription_id: str | None = None
    external_subscription_id: str | None = None
    status: str = "unknown"
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    trial_end: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None


class WebhookEvent(BaseModel):
    """Webhook event from payment provider."""

    id: str
    type: str
    created_at: datetime
    data: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class InvoiceData(BaseModel):
    """Invoice data."""

    id: str | None = None
    number: str | None = None
    amount_due: Money
    amount_paid: float | None = None
    amount_due: Money
    currency: str = "USD"
    status: str  # draft, open, paid, void, uncollectible
    due_date: datetime | None = None
    paid_at: datetime | None = None
    lines: list[dict] = Field(default_factory=list)


# =============================================================================
# Provider Interface
# =============================================================================

class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.

    This interface defines the contract that all payment provider
    adapters must implement, enabling provider-independent code.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the payment provider."""
        pass

    @property
    @abstractmethod
    def supports_webhooks(self) -> bool:
        """Whether this provider supports webhooks."""
        pass

    # -------------------------------------------------------------------------
    # Customer Management
    # -------------------------------------------------------------------------

    @abstractmethod
    async def create_customer(
        self,
        customer_info: CustomerInfo,
    ) -> str:
        """
        Create a customer in the payment provider.

        Args:
            customer_info: Customer information

        Returns:
            Provider's customer ID
        """
        pass

    @abstractmethod
    async def get_customer(self, customer_id: str) -> CustomerInfo:
        """
        Get customer information from the provider.

        Args:
            customer_id: Provider's customer ID

        Returns:
            Customer information
        """
        pass

    @abstractmethod
    async def update_customer(
        self,
        customer_id: str,
        customer_info: CustomerInfo,
    ) -> None:
        """
        Update customer information.

        Args:
            customer_id: Provider's customer ID
            customer_info: Updated customer information
        """
        pass

    @abstractmethod
    async def delete_customer(self, customer_id: str) -> None:
        """
        Delete a customer.

        Args:
            customer_id: Provider's customer ID
        """
        pass

    # -------------------------------------------------------------------------
    # Payment Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def create_payment_method(
        self,
        customer_id: str,
        payment_method_data: dict,
    ) -> PaymentMethod:
        """
        Add a payment method to a customer.

        Args:
            customer_id: Provider's customer ID
            payment_method_data: Payment method details

        Returns:
            Created payment method
        """
        pass

    @abstractmethod
    async def get_payment_methods(
        self,
        customer_id: str,
    ) -> list[PaymentMethod]:
        """
        Get customer's payment methods.

        Args:
            customer_id: Provider's customer ID

        Returns:
            List of payment methods
        """
        pass

    @abstractmethod
    async def delete_payment_method(self, payment_method_id: str) -> None:
        """
        Delete a payment method.

        Args:
            payment_method_id: Payment method ID
        """
        pass

    @abstractmethod
    async def set_default_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> None:
        """
        Set the default payment method for a customer.

        Args:
            customer_id: Provider's customer ID
            payment_method_id: Payment method ID
        """
        pass

    # -------------------------------------------------------------------------
    # Subscriptions
    # -------------------------------------------------------------------------

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        subscription_info: SubscriptionInfo,
        payment_method_id: str | None = None,
    ) -> SubscriptionResult:
        """
        Create a subscription.

        Args:
            customer_id: Provider's customer ID
            subscription_info: Subscription details
            payment_method_id: Optional payment method

        Returns:
            Subscription creation result
        """
        pass

    @abstractmethod
    async def get_subscription(
        self,
        subscription_id: str,
    ) -> SubscriptionResult:
        """
        Get subscription information.

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            Subscription information
        """
        pass

    @abstractmethod
    async def update_subscription(
        self,
        subscription_id: str,
        subscription_info: SubscriptionInfo,
    ) -> SubscriptionResult:
        """
        Update a subscription.

        Args:
            subscription_id: Provider's subscription ID
            subscription_info: Updated subscription details

        Returns:
            Update result
        """
        pass

    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
    ) -> SubscriptionResult:
        """
        Cancel a subscription.

        Args:
            subscription_id: Provider's subscription ID
            cancel_at_period_end: Cancel at end of current period

        Returns:
            Cancellation result
        """
        pass

    @abstractmethod
    async def pause_subscription(
        self,
        subscription_id: str,
    ) -> SubscriptionResult:
        """
        Pause a subscription (if supported).

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            Pause result
        """
        pass

    @abstractmethod
    async def resume_subscription(
        self,
        subscription_id: str,
    ) -> SubscriptionResult:
        """
        Resume a paused subscription.

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            Resume result
        """
        pass

    # -------------------------------------------------------------------------
    # Payments
    # -------------------------------------------------------------------------

    @abstractmethod
    async def charge(
        self,
        customer_id: str,
        amount: Money,
        description: str | None = None,
        payment_method_id: str | None = None,
        metadata: dict | None = None,
    ) -> PaymentResult:
        """
        Charge a customer.

        Args:
            customer_id: Provider's customer ID
            amount: Amount to charge
            description: Charge description
            payment_method_id: Optional specific payment method
            metadata: Additional metadata

        Returns:
            Payment result
        """
        pass

    @abstractmethod
    async def refund(
        self,
        transaction_id: str,
        amount: Money | None = None,
        reason: str | None = None,
    ) -> PaymentResult:
        """
        Refund a payment.

        Args:
            transaction_id: Original transaction ID
            amount: Optional partial refund amount
            reason: Refund reason

        Returns:
            Refund result
        """
        pass

    # -------------------------------------------------------------------------
    # Invoices
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_invoice(
        self,
        invoice_id: str,
    ) -> InvoiceData:
        """
        Get invoice information.

        Args:
            invoice_id: Provider's invoice ID

        Returns:
            Invoice data
        """
        pass

    @abstractmethod
    async def get_upcoming_invoice(
        self,
        subscription_id: str,
    ) -> InvoiceData:
        """
        Get upcoming invoice for a subscription.

        Args:
            subscription_id: Provider's subscription ID

        Returns:
            Upcoming invoice data
        """
        pass

    # -------------------------------------------------------------------------
    # Webhooks
    # -------------------------------------------------------------------------

    @abstractmethod
    def construct_webhook_event(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        """
        Construct a webhook event from payload.

        Args:
            payload: Raw webhook payload
            signature: Webhook signature

        Returns:
            Parsed webhook event
        """
        pass

    @abstractmethod
    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw webhook payload
            signature: Webhook signature

        Returns:
            True if signature is valid
        """
        pass

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_portal_url(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """
        Get customer portal URL for self-service management.

        Args:
            customer_id: Provider's customer ID
            return_url: URL to return after portal

        Returns:
            Portal URL
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test the connection to the payment provider.

        Returns:
            True if connection is successful
        """
        pass


# =============================================================================
# Exceptions
# =============================================================================

class PaymentError(Exception):
    """Base exception for payment-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        provider_error: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.provider_error = provider_error


class WebhookError(Exception):
    """Exception for webhook-related errors."""

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        event_id: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.event_type = event_type
        self.event_id = event_id


class PaymentProviderError(PaymentError):
    """Exception for payment provider-specific errors."""

    def __init__(
        self,
        message: str,
        provider: str,
        error_code: str | None = None,
        provider_error: dict | None = None,
    ):
        super().__init__(message, error_code, provider_error)
        self.provider = provider


class SubscriptionError(PaymentError):
    """Exception for subscription-related errors."""

    def __init__(
        self,
        message: str,
        subscription_id: str | None = None,
        status: str | None = None,
    ):
        super().__init__(message)
        self.subscription_id = subscription_id
        self.status = status
