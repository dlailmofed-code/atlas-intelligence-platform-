"""
ATLAS Platform - Feature Flag Service

This module provides the Feature Flag service for managing feature availability.
Based on the specifications: Feature Flags system.
"""

import hashlib
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.monetization import FeatureFlag, FeatureFlagOverride

logger = get_logger(__name__)


class FeatureFlagService:
    """
    Service for managing feature flags and checking feature availability.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the feature flag service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_flag(self, key: str) -> FeatureFlag | None:
        """
        Get a feature flag by key.

        Args:
            key: Feature flag key

        Returns:
            Feature flag or None if not found
        """
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        return result.scalar_one_or_none()

    async def is_feature_enabled(
        self,
        feature_key: str,
        user_id: UUID | None = None,
        user_plan: str | None = None,
        user_role: str | None = None,
        user_region: str | None = None,
    ) -> bool:
        """
        Check if a feature is enabled for a user.

        Args:
            feature_key: The feature flag key
            user_id: User ID for percentage rollouts and overrides
            user_plan: User's subscription plan
            user_role: User's role
            user_region: User's region

        Returns:
            True if feature is enabled, False otherwise
        """
        # Get the feature flag
        flag = await self.get_flag(feature_key)
        if not flag:
            logger.warning(f"Feature flag not found: {feature_key}")
            return False

        # Check if flag is globally disabled
        if not flag.is_active:
            return False

        # Check for user override
        if user_id:
            override = await self._get_user_override(user_id, flag.id)
            if override and override.expires_at:
                if override.expires_at < datetime.now(UTC):
                    # Override has expired, delete it
                    await self.db.delete(override)
                else:
                    return override.is_enabled

        # Check beta users
        if flag.is_beta and user_id:
            # Beta features require explicit override
            return False

        # Check rollout percentage
        if flag.is_rollout and flag.rollout_percentage < 100:
            if user_id:
                # Use deterministic hash for consistent rollout
                user_hash = int(hashlib.md5(str(user_id).encode()).hexdigest()[:8], 16)
                percentage = (user_hash % 100) + 1
                if percentage > flag.rollout_percentage:
                    return False
            else:
                return False

        # Check plan-based targeting
        if flag.enabled_plans and user_plan:
            if user_plan not in flag.enabled_plans:
                return False

        # Check role-based targeting
        if flag.enabled_roles and user_role:
            if user_role not in flag.enabled_roles:
                return False

        # Check region-based targeting
        if flag.enabled_regions and user_region:
            if user_region not in flag.enabled_regions:
                return False

        # Check experiment group (would need experiment assignment logic)
        # if flag.experiment_group and user_id:
        #     # Check if user is in the experiment group

        return True

    async def _get_user_override(
        self,
        user_id: UUID,
        flag_id: UUID
    ) -> FeatureFlagOverride | None:
        """Get a user's override for a feature flag."""
        result = await self.db.execute(
            select(FeatureFlagOverride).where(
                FeatureFlagOverride.user_id == user_id,
                FeatureFlagOverride.feature_flag_id == flag_id
            )
        )
        return result.scalar_one_or_none()

    async def set_user_override(
        self,
        user_id: UUID,
        feature_key: str,
        is_enabled: bool,
        reason: str | None = None,
        expires_at: datetime | None = None,
        created_by_id: UUID | None = None,
    ) -> FeatureFlagOverride:
        """
        Set a user-specific override for a feature flag.

        Args:
            user_id: User ID
            feature_key: Feature flag key
            is_enabled: Whether to enable or disable the feature
            reason: Reason for the override
            expires_at: When the override expires
            created_by_id: Admin who created the override

        Returns:
            The created or updated override
        """
        flag = await self.get_flag(feature_key)
        if not flag:
            raise ValueError(f"Feature flag not found: {feature_key}")

        # Check for existing override
        existing = await self._get_user_override(user_id, flag.id)

        if existing:
            existing.is_enabled = is_enabled
            existing.reason = reason
            existing.expires_at = expires_at
            existing.created_by_id = created_by_id
            await self.db.commit()
            await self.db.refresh(existing)
            override = existing
        else:
            override = FeatureFlagOverride(
                user_id=user_id,
                feature_flag_id=flag.id,
                is_enabled=is_enabled,
                reason=reason,
                expires_at=expires_at,
                created_by_id=created_by_id,
            )
            self.db.add(override)
            await self.db.commit()
            await self.db.refresh(override)

        logger.info(
            "Feature flag override set",
            user_id=str(user_id),
            feature_key=feature_key,
            is_enabled=is_enabled,
        )

        return override

    async def remove_user_override(
        self,
        user_id: UUID,
        feature_key: str,
    ) -> bool:
        """
        Remove a user's override for a feature flag.

        Args:
            user_id: User ID
            feature_key: Feature flag key

        Returns:
            True if override was removed, False if not found
        """
        flag = await self.get_flag(feature_key)
        if not flag:
            return False

        override = await self._get_user_override(user_id, flag.id)
        if override:
            await self.db.delete(override)
            await self.db.commit()
            logger.info(
                "Feature flag override removed",
                user_id=str(user_id),
                feature_key=feature_key,
            )
            return True

        return False

    async def list_flags(self, include_inactive: bool = False) -> list[FeatureFlag]:
        """
        List all feature flags.

        Args:
            include_inactive: Whether to include inactive flags

        Returns:
            List of feature flags
        """
        query = select(FeatureFlag)

        if not include_inactive:
            query = query.where(FeatureFlag.is_active)

        query = query.order_by(FeatureFlag.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_flag(
        self,
        key: str,
        name: str,
        description: str | None = None,
        enabled_plans: list | None = None,
        enabled_roles: list | None = None,
        rollout_percentage: int = 0,
        is_beta: bool = False,
    ) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            key: Unique key for the flag
            name: Display name
            description: Description of the feature
            enabled_plans: List of plan IDs that can use this feature
            enabled_roles: List of roles that can use this feature
            rollout_percentage: Percentage of users to enable (0-100)
            is_beta: Whether this is a beta feature

        Returns:
            Created feature flag
        """
        flag = FeatureFlag(
            key=key,
            name=name,
            description=description,
            is_active=True,
            is_rollout=rollout_percentage > 0 and rollout_percentage < 100,
            rollout_percentage=rollout_percentage,
            enabled_plans=enabled_plans or [],
            enabled_roles=enabled_roles or [],
            is_beta=is_beta,
        )

        self.db.add(flag)
        await self.db.commit()
        await self.db.refresh(flag)

        logger.info("Feature flag created", key=key)

        return flag

    async def update_flag(
        self,
        key: str,
        **kwargs
    ) -> FeatureFlag | None:
        """
        Update a feature flag.

        Args:
            key: Feature flag key
            **kwargs: Fields to update

        Returns:
            Updated feature flag or None if not found
        """
        flag = await self.get_flag(key)
        if not flag:
            return None

        allowed_fields = [
            "name", "description", "is_active", "is_rollout",
            "rollout_percentage", "enabled_plans", "enabled_roles",
            "enabled_regions", "is_beta", "documentation_url",
        ]

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(flag, field):
                setattr(flag, field, value)

        await self.db.commit()
        await self.db.refresh(flag)

        logger.info("Feature flag updated", key=key)

        return flag
