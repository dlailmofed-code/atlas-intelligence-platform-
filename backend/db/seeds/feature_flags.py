"""
ATLAS Platform - Feature Flags Seed

This module seeds the default feature flags.
Idempotent: Running multiple times will not duplicate records.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.monetization import FeatureFlag

logger = get_logger(__name__)


# Default feature flags
DEFAULT_FEATURE_FLAGS: list[dict[str, Any]] = [
    # Core Features
    {
        "key": "advanced_analytics",
        "name": "Advanced Analytics",
        "description": "Access to advanced analytics dashboards and visualizations",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "ai_insights",
        "name": "AI-Powered Insights",
        "description": "AI-generated insights and recommendations",
        "is_active": True,
        "is_rollout": True,
        "rollout_percentage": 50,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": True,
    },
    {
        "key": "custom_dashboards",
        "name": "Custom Dashboards",
        "description": "Create and customize personal dashboards",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "api_access",
        "name": "API Access",
        "description": "Access to the ATLAS API for integrations",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "webhook_integrations",
        "name": "Webhook Integrations",
        "description": "Configure webhook notifications for events",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "sso_saml",
        "name": "SSO/SAML Authentication",
        "description": "Single Sign-On with SAML 2.0",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "export_excel",
        "name": "Export to Excel",
        "description": "Export reports and data to Excel format",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "advanced_signals",
        "name": "Advanced Market Signals",
        "description": "Access to advanced market signal detection algorithms",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "concurrent_analyses",
        "name": "Concurrent Analyses",
        "description": "Run multiple analyses simultaneously",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "report_sharing",
        "name": "Report Sharing",
        "description": "Share reports with external stakeholders",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "priority_support",
        "name": "Priority Support",
        "description": "Access to priority customer support",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "knowledge_base",
        "name": "Knowledge Base",
        "description": "Access to the knowledge base and documentation",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["free", "starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "email_notifications",
        "name": "Email Notifications",
        "description": "Receive notifications via email",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["free", "starter", "professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "sms_notifications",
        "name": "SMS Notifications",
        "description": "Receive notifications via SMS",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "advanced_reporting",
        "name": "Advanced Reporting",
        "description": "Access to advanced report templates and options",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "data_export_api",
        "name": "Data Export via API",
        "description": "Export raw data through the API",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["professional", "enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "multi_user_workspace",
        "name": "Multi-User Workspace",
        "description": "Collaborate with multiple users in a shared workspace",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "audit_logs",
        "name": "Audit Logs",
        "description": "Access to user activity audit logs",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "custom_contracts",
        "name": "Custom Contracts",
        "description": "Support for custom billing contracts",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
    {
        "key": "on_premise_deployment",
        "name": "On-Premise Deployment",
        "description": "Deploy ATLAS on your own infrastructure",
        "is_active": True,
        "is_rollout": False,
        "rollout_percentage": 0,
        "enabled_plans": ["enterprise"],
        "enabled_roles": [],
        "enabled_regions": [],
        "is_beta": False,
    },
]


async def seed_feature_flags(db: AsyncSession) -> list[FeatureFlag]:
    """
    Seed feature flags.

    Idempotent: Will update existing flags instead of creating duplicates.

    Args:
        db: Database session

    Returns:
        List of seeded feature flags
    """
    seeded_flags = []

    for flag_data in DEFAULT_FEATURE_FLAGS:
        # Check if flag exists by key
        result = await db.execute(
            select(FeatureFlag).where(FeatureFlag.key == flag_data["key"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing flag
            for key, value in flag_data.items():
                if key not in ["key", "id"]:  # Don't update key or id
                    setattr(existing, key, value)
            logger.info(f"Updated feature flag: {flag_data['key']}")
            seeded_flags.append(existing)
        else:
            # Create new flag
            flag = FeatureFlag(**flag_data)
            db.add(flag)
            logger.info(f"Created feature flag: {flag_data['key']}")
            seeded_flags.append(flag)

    await db.commit()

    # Refresh all flags
    for flag in seeded_flags:
        await db.refresh(flag)

    logger.info(f"Seeded {len(seeded_flags)} feature flags")
    return seeded_flags


async def rollback_feature_flags(db: AsyncSession) -> None:
    """
    Rollback feature flag seeds.

    Args:
        db: Database session
    """
    for flag_data in DEFAULT_FEATURE_FLAGS:
        result = await db.execute(
            select(FeatureFlag).where(FeatureFlag.key == flag_data["key"])
        )
        flag = result.scalar_one_or_none()
        if flag:
            await db.delete(flag)
            logger.info(f"Deleted feature flag: {flag_data['key']}")

    await db.commit()
    logger.info("Rolled back feature flags")
