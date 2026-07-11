"""
ATLAS Platform - Database Seed Module

This module provides idempotent database seeding functionality.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.seeds.feature_flags import rollback_feature_flags, seed_feature_flags
from backend.db.seeds.plans import rollback_plans, seed_plans
from backend.db.seeds.roles_permissions import rollback_roles_permissions, seed_roles_permissions


async def run_all_seeds(session: AsyncSession) -> dict[str, bool]:
    """Run all database seeds in order.

    Returns dict with seed name and success status.
    """
    results = {}

    results["plans"] = await seed_plans(session)
    results["roles_permissions"] = await seed_roles_permissions(session)
    results["feature_flags"] = await seed_feature_flags(session)

    return results


async def rollback_all_seeds(session: AsyncSession) -> dict[str, bool]:
    """Rollback all database seeds in reverse order.

    Returns dict with seed name and success status.
    """
    results = {}

    results["feature_flags"] = await rollback_feature_flags(session)
    results["roles_permissions"] = await rollback_roles_permissions(session)
    results["plans"] = await rollback_plans(session)

    return results


__all__ = [
    "rollback_all_seeds",
    "rollback_feature_flags",
    "rollback_plans",
    "rollback_roles_permissions",
    "run_all_seeds",
    "seed_feature_flags",
    "seed_plans",
    "seed_roles_permissions",
]
