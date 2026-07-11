"""
Tests for notification service.
"""

import pytest

from backend.notifications.service import NotificationService, get_notification_service
from backend.notifications.types import (
    EmailConfig,
    NotificationRecipient,
    NotificationType,
    SlackConfig,
    WebhookConfig,
)


class TestNotificationService:
    """Tests for NotificationService."""

    @pytest.fixture
    def service(self):
        return NotificationService()

    def test_creation(self, service):
        """Test service creation."""
        assert service is not None

    def test_configure_email(self, service):
        """Test email configuration."""
        config = EmailConfig(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="password",
        )

        service.configure_email(config)
        assert service._email_config is not None

    def test_configure_slack(self, service):
        """Test Slack configuration."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/xxx",
            channel="#alerts",
        )

        service.configure_slack(config)
        assert service._slack_config is not None

    def test_configure_webhook(self, service):
        """Test webhook configuration."""
        config = WebhookConfig(
            url="https://example.com/webhook",
            secret="secret",
        )

        service.configure_webhook("test-webhook", config)
        assert "test-webhook" in service._webhook_configs

    def test_render_string(self, service):
        """Test string rendering."""
        result = service._render_string(
            "Hello {name}, welcome to {platform}!",
            {"name": "John", "platform": "ATLAS"},
        )

        assert result == "Hello John, welcome to ATLAS!"

    def test_render_string_no_variables(self, service):
        """Test string rendering with no variables."""
        result = service._render_string("Static message", {})
        assert result == "Static message"

    def test_get_notification_type(self, service):
        """Test notification type detection."""
        recipients = [
            NotificationRecipient(type=NotificationType.EMAIL, address="test@example.com"),
        ]

        notification_type = service._get_notification_type(recipients)
        assert notification_type == NotificationType.EMAIL

    def test_get_notification_type_empty(self, service):
        """Test notification type with empty recipients."""
        notification_type = service._get_notification_type([])
        assert notification_type == NotificationType.EMAIL

    def test_generate_signature(self, service):
        """Test webhook signature generation."""
        signature = service._generate_signature("payload", "secret")

        assert signature.startswith("sha256=")
        assert len(signature) > 10


class TestGetNotificationService:
    """Tests for get_notification_service function."""

    def test_get_service(self):
        """Test getting global service."""
        svc1 = get_notification_service()
        svc2 = get_notification_service()

        assert svc1 is svc2
