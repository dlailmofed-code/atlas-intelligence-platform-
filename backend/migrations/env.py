"""
ATLAS Platform - Alembic Environment Configuration

This module configures Alembic to work with the ATLAS platform database.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

# Third-party imports
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local imports - models (imported for side effects to register with Base.metadata)
from backend.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def get_url() -> str:
    """
    Get the database URL from environment or config.
    """
    import os

    # Try environment variable first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Parse components from environment
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    dbname = os.getenv("POSTGRES_DB", "atlas")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Support SQLite for testing
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run migrations with the given connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # Support SQLite for testing
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    from backend.core.config import get_settings

    settings = get_settings()
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database.url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
