"""
Tests for notification types.
"""

import pytest
from uuid import uuid4

from backend.notifications.types import (
    EmailConfig,
    Notification,
    NotificationContent,
    NotificationEvent,
    NotificationPriority,
    NotificationRecipient,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
    SlackConfig,
    WebhookConfig,
)


class TestNotificationType:
    """Tests for NotificationType enum."""
    
    def test_all_types(self):
        """Test all notification type values."""
        assert NotificationType.EMAIL.value == "email"
        assert NotificationType.SLACK.value == "slack"
        assert NotificationType.WEBHOOK.value == "webhook"


class TestNotificationPriority:
    """Tests for NotificationPriority enum."""
    
    def test_all_priorities(self):
        """Test all priority values."""
        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.NORMAL.value == "normal"
        assert NotificationPriority.HIGH.value == "high"
        assert NotificationPriority.URGENT.value == "urgent"


class TestNotificationStatus:
    """Tests for NotificationStatus enum."""
    
    def test_all_statuses(self):
        """Test all status values."""
        assert NotificationStatus.PENDING.value == "pending"
        assert NotificationStatus.SENT.value == "sent"
        assert NotificationStatus.DELIVERED.value == "delivered"
        assert NotificationStatus.FAILED.value == "failed"


class TestNotificationEvent:
    """Tests for NotificationEvent enum."""
    
    def test_all_events(self):
        """Test all event values."""
        assert NotificationEvent.USER_CREATED.value == "user.created"
        assert NotificationEvent.REPORT_GENERATED.value == "report.generated"
        assert NotificationEvent.ALERT_TRIGGERED.value == "alert.triggered"


class TestNotificationContent:
    """Tests for NotificationContent dataclass."""
    
    def test_creation(self):
        """Test content creation."""
        content = NotificationContent(
            subject="Test Subject",
            title="Test Title",
            body="Test body content",
        )
        
        assert content.subject == "Test Subject"
        assert content.title == "Test Title"
        assert content.body == "Test body content"


class TestNotificationRecipient:
    """Tests for NotificationRecipient dataclass."""
    
    def test_creation(self):
        """Test recipient creation."""
        recipient = NotificationRecipient(
            type=NotificationType.EMAIL,
            address="test@example.com",
            name="Test User",
        )
        
        assert recipient.type == NotificationType.EMAIL
        assert recipient.address == "test@example.com"
        assert recipient.name == "Test User"


class TestNotification:
    """Tests for Notification dataclass."""
    
    def test_creation(self):
        """Test notification creation."""
        notification = Notification(
            id=uuid4(),
            type=NotificationType.EMAIL,
            event=NotificationEvent.USER_CREATED,
            priority=NotificationPriority.NORMAL,
            content=NotificationContent(
                subject="Test",
                body="Test body",
            ),
            recipients=[
                NotificationRecipient(
                    type=NotificationType.EMAIL,
                    address="test@example.com",
                )
            ],
            status=NotificationStatus.PENDING,
        )
        
        assert notification.type == NotificationType.EMAIL
        assert notification.event == NotificationEvent.USER_CREATED
        assert notification.status == NotificationStatus.PENDING


class TestEmailConfig:
    """Tests for EmailConfig dataclass."""
    
    def test_creation(self):
        """Test email config creation."""
        config = EmailConfig(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="password",
        )
        
        assert config.smtp_host == "smtp.example.com"
        assert config.smtp_port == 587
        assert config.smtp_use_tls is True


class TestSlackConfig:
    """Tests for SlackConfig dataclass."""
    
    def test_creation(self):
        """Test Slack config creation."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/xxx",
            channel="#alerts",
        )
        
        assert config.webhook_url == "https://hooks.slack.com/services/xxx"
        assert config.channel == "#alerts"


class TestWebhookConfig:
    """Tests for WebhookConfig dataclass."""
    
    def test_creation(self):
        """Test webhook config creation."""
        config = WebhookConfig(
            url="https://example.com/webhook",
            method="POST",
            secret="secret123",
        )
        
        assert config.url == "https://example.com/webhook"
        assert config.method == "POST"
        assert config.timeout == 30.0


class TestNotificationTemplate:
    """Tests for NotificationTemplate dataclass."""
    
    def test_creation(self):
        """Test template creation."""
        template = NotificationTemplate(
            id="welcome-email",
            event=NotificationEvent.USER_CREATED,
            type=NotificationType.EMAIL,
            subject_template="Welcome, {name}!",
            title_template="Welcome!",
            body_template="Hello {name}, welcome to ATLAS Platform.",
            variables=["name"],
        )
        
        assert template.id == "welcome-email"
        assert template.event == NotificationEvent.USER_CREATED
        assert len(template.variables) == 1
