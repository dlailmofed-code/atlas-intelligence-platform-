"""
ATLAS Platform - Subscription Validation Service

This module provides the Subscription Validation service for checking
user permissions, feature access, and usage limits.
Based on the specifications: Subscription validation and access control.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.common.associations import organization_members
from backend.models.subscriptions import Subscription
from backend.monetization.services.feature_flag_service import FeatureFlagService
from backend.monetization.services.usage_service import UsageService

logger = get_logger(__name__)


class SubscriptionValidationService:
    """
    Service for validating user subscriptions and feature access.
    """

    # Role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        "guest": 0,
        "free_user": 1,
        "paid_user": 2,
        "enterprise_user": 3,
        "admin": 4,
        "super_admin": 5,
    }

    # Plan hierarchy
    PLAN_HIERARCHY = {
        "free": 0,
        "starter": 1,
        "professional": 2,
        "enterprise": 3,
    }

    def __init__(self, db: AsyncSession):
        """
        Initialize the subscription validation service.

        Args:
            db: Database session
        """
        self.db = db
        self.feature_flag_service = FeatureFlagService(db)
        self.usage_service = UsageService(db)

    async def get_user_subscription(self, user_id: UUID) -> Subscription | None:
        """
        Get a user's active subscription.

        Args:
            user_id: User ID

        Returns:
            Active subscription or None
        """
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status.in_(["active", "trialing"]),
            ).order_by(Subscription.started_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_user_plan(self, user_id: UUID) -> str:
        """
        Get a user's subscription plan.

        Args:
            user_id: User ID

        Returns:
            Plan identifier (free, starter, professional, enterprise)
        """
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            return subscription.plan_id
        return "free"

    async def get_user_role(self, user_id: UUID) -> str:
        """
        Get a user's role.

        Args:
            user_id: User ID

        Returns:
            Role identifier
        """
        # Check for admin role using the organization_members table
        result = await self.db.execute(
            select(organization_members.c.role).where(
                organization_members.c.user_id == user_id,
                organization_members.c.role.in_(["admin", "owner"]),
            )
        )
        row = result.fetchone()

        if row:
            if row.role == "owner":
                return "super_admin"
            return "admin"

        # Check subscription for regular user role
        plan = await self.get_user_plan(user_id)
        if plan == "free":
            return "free_user"
        elif plan in ["starter", "professional", "enterprise"]:
            return "paid_user"

        return "guest"

    async def check_feature_access(
        self,
        user_id: UUID,
        feature_key: str,
    ) -> bool:
        """
        Check if a user has access to a feature.

        Args:
            user_id: User ID
            feature_key: Feature flag key

        Returns:
            True if user has access
        """
        plan = await self.get_user_plan(user_id)
        role = await self.get_user_role(user_id)

        # Admins always have access
        if role in ["admin", "super_admin"]:
            return True

        return await self.feature_flag_service.is_feature_enabled(
            feature_key=feature_key,
            user_id=user_id,
            user_plan=plan,
            user_role=role,
        )

    async def check_usage_limit(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int = 1,
    ) -> tuple[bool, str]:
        """
        Check if a user can use a resource based on limits.

        Args:
            user_id: User ID
            usage_type: Type of usage
            amount: Amount to use

        Returns:
            Tuple of (is_allowed, reason)
        """
        plan = await self.get_user_plan(user_id)

        is_allowed, current_usage, limit = await self.usage_service.check_limit(
            user_id=user_id,
            usage_type=usage_type,
            plan=plan,
            amount=amount,
        )

        if not is_allowed:
            if limit == 0:
                return False, f"Usage limit not configured for {usage_type}"
            return False, f"Usage limit exceeded: {current_usage}/{limit}"

        return True, "OK"

    async def require_feature_access(
        self,
        user_id: UUID,
        feature_key: str,
    ) -> None:
        """
        Require feature access or raise HTTPException.

        Args:
            user_id: User ID
            feature_key: Feature flag key

        Raises:
            HTTPException: If user doesn't have access
        """
        has_access = await self.check_feature_access(user_id, feature_key)

        if not has_access:
            logger.warning(
                "Feature access denied",
                user_id=str(user_id),
                feature_key=feature_key,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Feature not available",
                    "feature": feature_key,
                    "upgrade_required": True,
                },
            )

    async def require_usage_allowance(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int = 1,
    ) -> None:
        """
        Require usage allowance or raise HTTPException.

        Args:
            user_id: User ID
            usage_type: Type of usage
            amount: Amount to use

        Raises:
            HTTPException: If user has exceeded limits
        """
        is_allowed, reason = await self.check_usage_limit(user_id, usage_type, amount)

        if not is_allowed:
            plan = await self.get_user_plan(user_id)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Usage limit exceeded",
                    "reason": reason,
                    "usage_type": usage_type,
                    "upgrade_required": plan == "free",
                    "current_plan": plan,
                },
            )

    async def get_plan_comparison(
        self,
        user_id: UUID,
    ) -> dict:
        """
        Get feature comparison for user's plan vs others.

        Args:
            user_id: User ID

        Returns:
            Feature comparison data
        """
        user_plan = await self.get_user_plan(user_id)
        user_role = await self.get_user_role(user_id)

        features = await self.feature_flag_service.list_flags()

        return {
            "current_plan": user_plan,
            "current_role": user_role,
            "available_features": [
                {
                    "key": f.key,
                    "name": f.name,
                    "enabled": await self.check_feature_access(user_id, f.key),
                }
                for f in features
            ],
            "plan_limits": self.usage_service.DEFAULT_LIMITS.get(user_plan, {}),
        }

    async def check_permission(
        self,
        user_id: UUID,
        permission: str,
        resource_owner_id: UUID | None = None,
        organization_id: UUID | None = None,
    ) -> bool:
        """
        Check if a user has a specific permission.

        Based on the Permissions Matrix from the specification.

        Args:
            user_id: User ID
            permission: Permission identifier
            resource_owner_id: Owner of the resource
            organization_id: Organization context

        Returns:
            True if user has permission
        """
        role = await self.get_user_role(user_id)

        # Super admin has all permissions
        if role == "super_admin":
            return True

        # Owner always has access to their resources
        if resource_owner_id and user_id == resource_owner_id:
            return True

        # Permission matrix
        permissions = {
            # Guest permissions
            "guest": [
                "site:read",
                "content:read",
            ],
            # Free user permissions
            "free_user": [
                "site:read",
                "content:read",
                "analysis:create_limited",
                "report:read_basic",
            ],
            # Paid user permissions
            "paid_user": [
                "site:read",
                "content:read",
                "analysis:create",
                "analysis:create_concurrent",
                "report:read_basic",
                "report:read_detailed",
                "report:create",
                "export:pdf",
                "export:csv",
                "api:access",
            ],
            # Enterprise user permissions
            "enterprise_user": [
                "site:read",
                "content:read",
                "analysis:create",
                "analysis:create_concurrent",
                "report:read_basic",
                "report:read_detailed",
                "report:read_advanced",
                "report:create",
                "report:share",
                "export:pdf",
                "export:csv",
                "export:excel",
                "export:api",
                "api:access",
                "api:full",
                "org:dashboard",
            ],
            # Admin permissions
            "admin": [
                "site:read",
                "content:read",
                "analysis:create",
                "analysis:create_concurrent",
                "report:read_basic",
                "report:read_detailed",
                "report:read_advanced",
                "report:create",
                "report:share",
                "report:delete",
                "export:pdf",
                "export:csv",
                "export:excel",
                "export:api",
                "api:access",
                "api:full",
                "org:dashboard",
                "org:users:read",
                "org:users:manage",
                "settings:read",
            ],
            # Super admin permissions
            "super_admin": [
                "*",  # All permissions
            ],
        }

        user_permissions = permissions.get(role, [])

        # Check for wildcard
        if "*" in user_permissions:
            return True

        return permission in user_permissions

    async def require_permission(
        self,
        user_id: UUID,
        permission: str,
        **kwargs
    ) -> None:
        """
        Require a permission or raise HTTPException.

        Args:
            user_id: User ID
            permission: Permission identifier
            **kwargs: Additional context (resource_owner_id, organization_id)

        Raises:
            HTTPException: If user doesn't have permission
        """
        has_permission = await self.check_permission(user_id, permission, **kwargs)

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Permission denied",
                    "required_permission": permission,
                },
            )
