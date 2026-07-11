"""
ATLAS Platform - Notification Service

Sends notifications via various channels.
"""

import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import httpx

from backend.core.logging import get_logger
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

logger = get_logger(__name__)


class NotificationService:
    """Service for sending notifications."""
    
    def __init__(self):
        self._templates: dict[str, NotificationTemplate] = {}
        self._email_config: EmailConfig | None = None
        self._slack_config: SlackConfig | None = None
        self._webhook_configs: dict[str, WebhookConfig] = {}
        self._queue: asyncio.Queue[Notification] = asyncio.Queue()
        self._running = False
    
    def configure_email(self, config: EmailConfig) -> None:
        """Configure email settings."""
        self._email_config = config
        logger.info("Email notification configured")
    
    def configure_slack(self, config: SlackConfig) -> None:
        """Configure Slack settings."""
        self._slack_config = config
        logger.info("Slack notification configured")
    
    def configure_webhook(self, name: str, config: WebhookConfig) -> None:
        """Configure a webhook."""
        self._webhook_configs[name] = config
        logger.info(f"Webhook configured: {name}")
    
    def register_template(self, template: NotificationTemplate) -> None:
        """Register a notification template."""
        self._templates[template.id] = template
        logger.info(f"Registered notification template: {template.id}")
    
    async def send(
        self,
        event: NotificationEvent,
        content: NotificationContent,
        recipients: list[NotificationRecipient],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """
        Send a notification.
        
        Args:
            event: Event type
            content: Notification content
            recipients: List of recipients
            priority: Priority level
            metadata: Additional metadata
            
        Returns:
            Created notification
        """
        notification = Notification(
            id=uuid4(),
            type=self._get_notification_type(recipients),
            event=event,
            priority=priority,
            content=content,
            recipients=recipients,
            status=NotificationStatus.PENDING,
            metadata=metadata or {},
        )
        
        await self._send_notification(notification)
        return notification
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> bool:
        """Send an email notification."""
        if not self._email_config:
            logger.error("Email not configured")
            return False
        
        recipient = NotificationRecipient(
            type=NotificationType.EMAIL,
            address=to,
        )
        
        content = NotificationContent(
            subject=subject,
            body=body,
            html_body=html_body,
        )
        
        notification = await self.send(
            event=NotificationEvent.USER_CREATED,
            content=content,
            recipients=[recipient],
            priority=priority,
        )
        
        return notification.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]
    
    async def send_slack(
        self,
        channel: str | None,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> bool:
        """Send a Slack notification."""
        if not self._slack_config:
            logger.error("Slack not configured")
            return False
        
        recipient = NotificationRecipient(
            type=NotificationType.SLACK,
            address=self._slack_config.webhook_url,
            name=channel or self._slack_config.channel,
        )
        
        content = NotificationContent(body=message)
        
        notification = await self.send(
            event=NotificationEvent.USER_CREATED,
            content=content,
            recipients=[recipient],
            priority=priority,
        )
        
        return notification.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]
    
    async def send_webhook(
        self,
        webhook_name: str,
        payload: dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> bool:
        """Send a webhook notification."""
        config = self._webhook_configs.get(webhook_name)
        if not config:
            logger.error(f"Webhook not configured: {webhook_name}")
            return False
        
        recipient = NotificationRecipient(
            type=NotificationType.WEBHOOK,
            address=config.url,
        )
        
        content = NotificationContent(
            body=json.dumps(payload),
        )
        
        notification = await self.send(
            event=NotificationEvent.USER_CREATED,
            content=content,
            recipients=[recipient],
            priority=priority,
            metadata={"webhook_name": webhook_name, "payload": payload},
        )
        
        return notification.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]
    
    async def _send_notification(self, notification: Notification) -> None:
        """Send notification to appropriate channel."""
        try:
            for recipient in notification.recipients:
                if recipient.type == NotificationType.EMAIL:
                    await self._send_email(notification, recipient)
                elif recipient.type == NotificationType.SLACK:
                    await self._send_slack(notification, recipient)
                elif recipient.type == NotificationType.WEBHOOK:
                    await self._send_webhook(notification, recipient)
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            logger.info(f"Sent notification: {notification.id}")
        
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            logger.error(f"Failed to send notification: {e}")
    
    async def _send_email(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
    ) -> None:
        """Send email notification."""
        if not self._email_config:
            raise ValueError("Email not configured")
        
        # In production, use aiosmtplib or similar
        # For now, just log
        logger.info(f"Email to {recipient.address}: {notification.content.subject}")
    
    async def _send_slack(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
    ) -> None:
        """Send Slack notification."""
        if not self._slack_config:
            raise ValueError("Slack not configured")
        
        payload = {
            "text": notification.content.body or notification.content.title or "Notification",
            "username": self._slack_config.bot_name,
        }
        
        if recipient.name:
            payload["channel"] = recipient.name
        
        if self._slack_config.bot_icon:
            payload["icon_emoji"] = self._slack_config.bot_icon
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._slack_config.webhook_url,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
            
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.now(timezone.utc)
            logger.info(f"Slack notification delivered to {recipient.name or 'default channel'}")
        
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            raise
    
    async def _send_webhook(
        self,
        notification: Notification,
        recipient: NotificationRecipient,
    ) -> None:
        """Send webhook notification."""
        config = self._webhook_configs.get(notification.metadata.get("webhook_name", ""))
        if not config:
            raise ValueError("Webhook not configured")
        
        headers = dict(config.headers)
        headers["Content-Type"] = "application/json"
        
        # Add signature if secret is configured
        payload = notification.metadata.get("payload", {})
        
        if config.secret:
            signature = self._generate_signature(json.dumps(payload), config.secret)
            headers["X-Webhook-Signature"] = signature
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    config.method,
                    config.url,
                    json=payload,
                    headers=headers,
                    timeout=config.timeout,
                )
                response.raise_for_status()
            
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.now(timezone.utc)
            logger.info(f"Webhook notification delivered: {config.url}")
        
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            raise
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook."""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={signature}"
    
    def _get_notification_type(
        self,
        recipients: list[NotificationRecipient],
    ) -> NotificationType:
        """Get notification type from recipients."""
        if not recipients:
            return NotificationType.EMAIL
        
        return recipients[0].type
    
    def render_template(
        self,
        template_id: str,
        variables: dict[str, Any],
    ) -> NotificationContent:
        """Render a notification template."""
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        content = NotificationContent()
        
        if template.subject_template:
            content.subject = self._render_string(template.subject_template, variables)
        if template.title_template:
            content.title = self._render_string(template.title_template, variables)
        if template.body_template:
            content.body = self._render_string(template.body_template, variables)
        if template.html_template:
            content.html_body = self._render_string(template.html_template, variables)
        
        return content
    
    def _render_string(self, template: str, variables: dict[str, Any]) -> str:
        """Render a template string with variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


# Global notification service instance
_service: NotificationService | None = None


def get_notification_service() -> NotificationService:
    """Get the global notification service."""
    global _service
    if _service is None:
        _service = NotificationService()
    return _service
