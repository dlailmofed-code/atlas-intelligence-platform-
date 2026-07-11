"""
ATLAS Platform - Payment Adapters Package

This package provides payment provider abstraction for Stripe, PayPal, and Paddle.
"""

from backend.monetization.adapters.base import (
    PaymentError,
    PaymentProvider,
    WebhookError,
)
from backend.monetization.adapters.factory import PaymentAdapterFactory
from backend.monetization.adapters.webhook import WebhookHandler

__all__ = [
    "PaymentAdapterFactory",
    "PaymentError",
    "PaymentProvider",
    "WebhookError",
    "WebhookHandler",
]

