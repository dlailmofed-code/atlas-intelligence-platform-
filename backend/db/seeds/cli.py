"""
ATLAS Platform - Seed CLI

This module provides a CLI for running database seeds.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


async def run_seeds() -> None:
    """
    Run all database seeds.
    """
    from backend.core.logging import get_logger
    from backend.db.seeds import (
        seed_feature_flags,
        seed_plans,
        seed_roles_permissions,
    )
    from backend.db.session import async_session_maker

    logger = get_logger("seed")

    async with async_session_maker() as db:
        try:
            logger.info("Starting database seeding...")

            # Seed in order (respecting dependencies)
            logger.info("Seeding subscription plans...")
            await seed_plans(db)

            logger.info("Seeding roles and permissions...")
            await seed_roles_permissions(db)

            logger.info("Seeding feature flags...")
            await seed_feature_flags(db)

            logger.info("Database seeding completed successfully!")

        except Exception as e:
            logger.error(f"Seed failed: {e}")
            await db.rollback()
            raise


async def rollback_seeds() -> None:
    """
    Rollback all database seeds.
    """
    from backend.core.logging import get_logger
    from backend.db.seeds import (
        rollback_feature_flags,
        rollback_plans,
        rollback_roles_permissions,
    )
    from backend.db.session import async_session_maker

    logger = get_logger("seed")

    async with async_session_maker() as db:
        try:
            logger.info("Starting database seed rollback...")

            # Rollback in reverse order
            logger.info("Rolling back feature flags...")
            await rollback_feature_flags(db)

            logger.info("Rolling back roles and permissions...")
            await rollback_roles_permissions(db)

            logger.info("Rolling back subscription plans...")
            await rollback_plans(db)

            logger.info("Database seed rollback completed!")

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_seeds())
    else:
        asyncio.run(run_seeds())
