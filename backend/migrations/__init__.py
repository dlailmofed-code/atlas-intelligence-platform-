"""
ATLAS Platform - Alembic Module

This module provides Alembic configuration and utilities for database migrations.
"""

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.core.config import get_settings


def get_alembic_config() -> Config:
    """
    Get Alembic configuration.

    Returns:
        Configured Alembic Config object
    """
    settings = get_settings()

    config = Config(
        file_="/workspace/project/atlas_platform/backend/alembic.ini",
        ini_section="alembic",
    )

    # Set the database URL
    config.set_main_option("sqlalchemy.url", settings.database.url)

    return config


async def get_async_migration_context(engine: AsyncEngine) -> MigrationContext:
    """
    Get an async migration context.

    Args:
        engine: Async engine

    Returns:
        MigrationContext for running migrations
    """
    async with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context


__all__ = [
    "Config",
    "MigrationContext",
    "get_alembic_config",
    "get_async_migration_context",
]
