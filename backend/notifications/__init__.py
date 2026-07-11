"""
ATLAS Platform - Notifications Module

Notification service for sending alerts via email, Slack, and webhooks.
"""

from backend.notifications.service import NotificationService, get_notification_service
from backend.notifications.types import (
    EmailConfig,
    Notification,
    NotificationContent,
    NotificationEvent,
    NotificationPreference,
    NotificationPriority,
    NotificationRecipient,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
    SlackConfig,
    WebhookConfig,
)

__all__ = [
    # Types
    "NotificationType",
    "NotificationPriority",
    "NotificationStatus",
    "NotificationEvent",
    "NotificationContent",
    "NotificationRecipient",
    "Notification",
    "EmailConfig",
    "SlackConfig",
    "WebhookConfig",
    "NotificationTemplate",
    "NotificationPreference",
    # Service
    "NotificationService",
    "get_notification_service",
]
