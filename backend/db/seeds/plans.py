"""
ATLAS Platform - Subscription Plans Seed

This module seeds the default subscription plans.
Idempotent: Running multiple times will not duplicate records.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.subscriptions import Plan

logger = get_logger(__name__)


# Default subscription plans
DEFAULT_PLANS: list[dict[str, Any]] = [
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "name": "Free",
        "slug": "free",
        "description": "Free tier for basic exploration and testing.",
        "price_monthly": 0.00,
        "price_yearly": 0.00,
        "currency": "USD",
        "is_active": True,
        "is_featured": False,
        "features": [
            "Basic market signals",
            "Limited reports",
            "Community support",
            "Basic analytics",
        ],
        "limits": {
            "analysis": {"daily": 1, "monthly": 10},
            "report": {"monthly": 1},
            "api_call": {"daily": 100, "monthly": 1000},
            "export": {"monthly": 5},
        },
        "display_order": 0,
    },
    {
        "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "name": "Starter",
        "slug": "starter",
        "description": "For individuals and small teams getting started.",
        "price_monthly": 29.00,
        "price_yearly": 290.00,
        "currency": "USD",
        "is_active": True,
        "is_featured": True,
        "features": [
            "All Free features",
            "Advanced market signals",
            "Up to 100 reports/month",
            "Priority email support",
            "API access",
            "Export to CSV",
        ],
        "limits": {
            "analysis": {"daily": 5, "monthly": 100},
            "report": {"monthly": 100},
            "api_call": {"daily": 1000, "monthly": 10000},
            "export": {"monthly": 50},
        },
        "display_order": 1,
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "name": "Professional",
        "slug": "professional",
        "description": "For growing businesses requiring advanced features.",
        "price_monthly": 99.00,
        "price_yearly": 990.00,
        "currency": "USD",
        "is_active": True,
        "is_featured": True,
        "features": [
            "All Starter features",
            "Unlimited market signals",
            "Unlimited reports",
            "Priority phone support",
            "Full API access",
            "Export to Excel",
            "Advanced analytics",
            "Custom dashboards",
            "Webhook integrations",
        ],
        "limits": {
            "analysis": {"daily": 50, "monthly": 1000},
            "report": {"monthly": -1},  # Unlimited
            "api_call": {"daily": 10000, "monthly": 100000},
            "export": {"monthly": 500},
        },
        "display_order": 2,
    },
    {
        "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "name": "Enterprise",
        "slug": "enterprise",
        "description": "For large organizations with custom requirements.",
        "price_monthly": 299.00,
        "price_yearly": 2990.00,
        "currency": "USD",
        "is_active": True,
        "is_featured": False,
        "features": [
            "All Professional features",
            "Unlimited everything",
            "Dedicated account manager",
            "Custom integrations",
            "SSO/SAML",
            "Advanced security",
            "SLA guarantee",
            "On-premise deployment option",
            "Custom contracts",
        ],
        "limits": {
            "analysis": {"daily": -1, "monthly": -1},  # Unlimited
            "report": {"monthly": -1},
            "api_call": {"daily": -1, "monthly": -1},
            "export": {"monthly": -1},
        },
        "display_order": 3,
    },
]


async def seed_plans(db: AsyncSession) -> list[Plan]:
    """
    Seed subscription plans.

    Idempotent: Will update existing plans instead of creating duplicates.

    Args:
        db: Database session

    Returns:
        List of seeded plans
    """
    seeded_plans = []

    for plan_data in DEFAULT_PLANS:
        # Check if plan exists
        result = await db.execute(
            select(Plan).where(Plan.slug == plan_data["slug"])
        )
        existing_plan = result.scalar_one_or_none()

        if existing_plan:
            # Update existing plan
            for key, value in plan_data.items():
                if key != "id":  # Don't update the ID
                    setattr(existing_plan, key, value)
            logger.info(f"Updated plan: {plan_data['slug']}")
            seeded_plans.append(existing_plan)
        else:
            # Create new plan
            plan = Plan(**plan_data)
            db.add(plan)
            logger.info(f"Created plan: {plan_data['slug']}")
            seeded_plans.append(plan)

    await db.commit()

    # Refresh all plans
    for plan in seeded_plans:
        await db.refresh(plan)

    logger.info(f"Seeded {len(seeded_plans)} subscription plans")
    return seeded_plans


async def rollback_plans(db: AsyncSession) -> None:
    """
    Rollback plan seeds.

    This removes all seeded plans (but won't delete user-created plans).

    Args:
        db: Database session
    """
    # Delete only the default seeded plans by their known IDs
    for plan_data in DEFAULT_PLANS:
        result = await db.execute(
            select(Plan).where(Plan.id == plan_data["id"])
        )
        plan = result.scalar_one_or_none()
        if plan:
            await db.delete(plan)
            logger.info(f"Deleted plan: {plan_data['slug']}")

    await db.commit()
    logger.info("Rolled back subscription plans")
