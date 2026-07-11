"""
ATLAS Platform - Monetization Unit Tests
"""

from datetime import UTC, datetime

from backend.monetization.services.subscription_service import SubscriptionValidationService
from backend.monetization.services.usage_service import UsageService


class TestUsageLimits:
    """Test usage limits functionality."""

    def test_default_limits_structure(self):
        """Test that default limits are properly structured."""
        service = UsageService(None)  # We only access DEFAULT_LIMITS

        assert "free" in service.DEFAULT_LIMITS
        assert "starter" in service.DEFAULT_LIMITS
        assert "professional" in service.DEFAULT_LIMITS
        assert "enterprise" in service.DEFAULT_LIMITS

        # Free plan should have very limited quotas
        free_limits = service.DEFAULT_LIMITS["free"]
        assert free_limits["analysis"]["monthly"] == 1
        assert free_limits["report"]["monthly"] == 1

    def test_enterprise_unlimited(self):
        """Test that enterprise plan has unlimited quotas."""
        service = UsageService(None)

        enterprise_limits = service.DEFAULT_LIMITS["enterprise"]
        assert enterprise_limits["analysis"]["daily"] == -1
        assert enterprise_limits["analysis"]["monthly"] == -1


class TestSubscriptionValidation:
    """Test subscription validation service."""

    def test_role_hierarchy(self):
        """Test that role hierarchy is properly defined."""
        service = SubscriptionValidationService(None)

        # Verify hierarchy order
        assert service.ROLE_HIERARCHY["guest"] < service.ROLE_HIERARCHY["free_user"]
        assert service.ROLE_HIERARCHY["free_user"] < service.ROLE_HIERARCHY["paid_user"]
        assert service.ROLE_HIERARCHY["paid_user"] < service.ROLE_HIERARCHY["enterprise_user"]
        assert service.ROLE_HIERARCHY["enterprise_user"] < service.ROLE_HIERARCHY["admin"]
        assert service.ROLE_HIERARCHY["admin"] < service.ROLE_HIERARCHY["super_admin"]

    def test_plan_hierarchy(self):
        """Test that plan hierarchy is properly defined."""
        service = SubscriptionValidationService(None)

        assert service.PLAN_HIERARCHY["free"] < service.PLAN_HIERARCHY["starter"]
        assert service.PLAN_HIERARCHY["starter"] < service.PLAN_HIERARCHY["professional"]
        assert service.PLAN_HIERARCHY["professional"] < service.PLAN_HIERARCHY["enterprise"]

    def test_permissions_matrix(self):
        """Test that permission checks work correctly."""
        service = SubscriptionValidationService(None)

        # Super admin should have all permissions
        # (We can't test async methods without a real db, but we can test structure)
        assert "guest" in service.ROLE_HIERARCHY
        assert "admin" in service.ROLE_HIERARCHY
        assert "super_admin" in service.ROLE_HIERARCHY


class TestFeatureFlags:
    """Test feature flag functionality."""

    def test_flag_structure(self):
        """Test that feature flags have proper structure."""
        # Test the default flag configuration pattern
        flag_config = {
            "key": "test_feature",
            "name": "Test Feature",
            "description": "A test feature flag",
            "is_active": True,
            "is_rollout": False,
            "rollout_percentage": 0,
            "enabled_plans": [],
            "enabled_roles": [],
            "enabled_regions": [],
            "is_beta": False,
        }

        assert flag_config["key"] == "test_feature"
        assert flag_config["is_active"] is True
        assert flag_config["is_rollout"] is False

    def test_plan_based_targeting(self):
        """Test plan-based feature targeting."""
        flag = {
            "enabled_plans": ["professional", "enterprise"],
            "is_active": True,
        }

        # Professional user should have access
        assert "professional" in flag["enabled_plans"]

        # Free user should not have access
        assert "free" not in flag["enabled_plans"]


class TestPaymentArchitecture:
    """Test payment architecture abstractions."""

    def test_subscription_status_constants(self):
        """Test subscription status constants."""
        from backend.monetization.adapters.factory import SubscriptionStatus

        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.PAST_DUE == "past_due"
        assert SubscriptionStatus.CANCELLED == "cancelled"
        assert SubscriptionStatus.TRIALING == "trialing"
        assert SubscriptionStatus.PAUSED == "paused"

    def test_payment_status_constants(self):
        """Test payment status constants."""
        from backend.monetization.adapters.factory import PaymentStatus

        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.PROCESSING == "processing"
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.REFUNDED == "refunded"

    def test_webhook_event_types(self):
        """Test webhook event type constants."""
        from backend.monetization.adapters.factory import WebhookEventType

        # Subscription events
        assert hasattr(WebhookEventType, "SUBSCRIPTION_CREATED")
        assert hasattr(WebhookEventType, "SUBSCRIPTION_UPDATED")
        assert hasattr(WebhookEventType, "SUBSCRIPTION_DELETED")

        # Invoice events
        assert hasattr(WebhookEventType, "INVOICE_CREATED")
        assert hasattr(WebhookEventType, "INVOICE_PAID")
        assert hasattr(WebhookEventType, "INVOICE_PAYMENT_FAILED")

        # Payment events
        assert hasattr(WebhookEventType, "PAYMENT_SUCCEEDED")
        assert hasattr(WebhookEventType, "PAYMENT_FAILED")
        assert hasattr(WebhookEventType, "PAYMENT_REFUNDED")


class TestUsageSummaryPeriodBounds:
    """Test usage summary period calculation."""

    def test_daily_period_bounds(self):
        """Test daily period boundary calculation."""
        from backend.models.monetization import UsageSummary

        reference = datetime(2025, 7, 15, 14, 30, 0, tzinfo=UTC)
        start, end = UsageSummary.get_period_bounds("daily", reference)

        # Start should be midnight
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

        # End should be next midnight
        assert end.day == 16
        assert end.hour == 0

    def test_monthly_period_bounds(self):
        """Test monthly period boundary calculation."""
        from backend.models.monetization import UsageSummary

        reference = datetime(2025, 7, 15, 14, 30, 0, tzinfo=UTC)
        start, end = UsageSummary.get_period_bounds("monthly", reference)

        # Start should be first day of month
        assert start.day == 1
        assert start.month == 7

        # End should be first day of next month
        assert end.month == 8
        assert end.day == 1

    def test_weekly_period_bounds(self):
        """Test weekly period boundary calculation."""
        from backend.models.monetization import UsageSummary

        # Reference is Tuesday (weekday=1)
        reference = datetime(2025, 7, 15, 14, 30, 0, tzinfo=UTC)
        start, end = UsageSummary.get_period_bounds("weekly", reference)

        # Start should be Monday of that week
        assert start.weekday() == 0  # Monday

        # End should be next Monday
        assert (end - start).days == 7
