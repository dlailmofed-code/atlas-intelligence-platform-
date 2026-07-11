"""
ATLAS Platform - Notification Types

Type definitions for the notification system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class NotificationType(str, Enum):
    """Notification types."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationEvent(str, Enum):
    """Notification events."""

    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"

    # Subscription events
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_EXPIRING = "subscription.expiring"

    # Report events
    REPORT_GENERATED = "report.generated"
    REPORT_FAILED = "report.failed"
    REPORT_SCHEDULED = "report.scheduled"

    # Intelligence events
    SIGNAL_DETECTED = "signal.detected"
    OPPORTUNITY_FOUND = "opportunity.found"
    ALERT_TRIGGERED = "alert.triggered"

    # System events
    SYSTEM_ALERT = "system.alert"
    SECURITY_ALERT = "security.alert"
    MAINTENANCE = "maintenance"


@dataclass
class NotificationContent:
    """Content of a notification."""

    subject: str | None = None
    title: str | None = None
    body: str | None = None
    html_body: str | None = None
    template_id: str | None = None
    template_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationRecipient:
    """Recipient of a notification."""

    type: NotificationType
    address: str  # email address, phone number, webhook URL, etc.
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """A notification to be sent."""

    id: UUID
    type: NotificationType
    event: NotificationEvent
    priority: NotificationPriority
    content: NotificationContent
    recipients: list[NotificationRecipient]
    status: NotificationStatus
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmailConfig:
    """Email notification configuration."""

    smtp_host: str
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    from_email: str | None = None
    from_name: str = "ATLAS Platform"
    reply_to: str | None = None


@dataclass
class SlackConfig:
    """Slack notification configuration."""

    webhook_url: str
    channel: str | None = None
    bot_name: str = "ATLAS Bot"
    bot_icon: str | None = None


@dataclass
class WebhookConfig:
    """Webhook notification configuration."""

    url: str
    method: str = "POST"
    headers: dict[str, str] = field(default_factory=dict)
    secret: str | None = None
    timeout: float = 30.0


@dataclass
class NotificationTemplate:
    """Template for a notification."""

    id: str
    event: NotificationEvent
    type: NotificationType
    subject_template: str
    title_template: str
    body_template: str
    html_template: str | None = None
    variables: list[str] = field(default_factory=list)


@dataclass
class NotificationPreference:
    """User notification preferences."""

    user_id: UUID
    email_enabled: bool = True
    slack_enabled: bool = False
    webhook_enabled: bool = False
    enabled_events: list[NotificationEvent] = field(default_factory=list)
    quiet_hours_start: str | None = None  # HH:MM format
    quiet_hours_end: str | None = None
    timezone: str = "UTC"
