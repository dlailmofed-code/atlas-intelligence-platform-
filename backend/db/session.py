"""
ATLAS Platform - Database Session Management

This module manages database connections and sessions using SQLAlchemy async engine.
Implements connection pooling and session factory for the application.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from backend.core.config import DatabaseSettings, get_settings
from backend.core.logging import get_logger
from backend.models.common.base import Base

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, settings: DatabaseSettings | None = None):
        """
        Initialize database manager.

        Args:
            settings: Database settings. If None, loads from app settings.
        """
        if settings is None:
            settings = get_settings().database

        self.settings = settings
        self._async_engine: AsyncEngine | None = None
        self._sync_engine = None
        self._async_session_factory: async_sessionmaker | None = None
        self._sync_session_factory: sessionmaker | None = None

    @property
    def async_engine(self) -> AsyncEngine:
        """Get or create async engine."""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.settings.get_url(),
                pool_size=self.settings.pool_size,
                max_overflow=self.settings.max_overflow,
                pool_timeout=self.settings.pool_timeout,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.pool_size <= 5,  # Echo SQL in debug mode
            )
        return self._async_engine

    @property
    def sync_engine(self):
        """Get or create sync engine (for migrations)."""
        if self._sync_engine is None:
            # Import sync driver
            url = self.settings.get_url_sync()
            self._sync_engine = create_engine(
                url,
                pool_size=self.settings.pool_size,
                max_overflow=self.settings.max_overflow,
                pool_timeout=self.settings.pool_timeout,
                pool_pre_ping=True,
                echo=False,
            )
        return self._sync_engine

    @property
    def async_session_factory(self) -> async_sessionmaker:
        """Get or create async session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self._async_session_factory

    @property
    def sync_session_factory(self) -> sessionmaker:
        """Get or create sync session factory (for migrations)."""
        if self._sync_session_factory is None:
            self._sync_session_factory = sessionmaker(
                bind=self.sync_engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self._sync_session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session.

        Yields:
            AsyncSession instance
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for database session.

        Yields:
            AsyncSession instance with automatic commit/rollback
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database connections."""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            self._async_session_factory = None

        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
            self._sync_session_factory = None

        logger.info("Database connections closed")

    async def create_tables(self) -> None:
        """Create all tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def drop_tables(self) -> None:
        """Drop all tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database session.

    Yields:
        AsyncSession instance
    """
    db = get_db_manager()
    async for session in db.get_session():
        yield session


async def init_db() -> None:
    """Initialize database on application startup."""
    db = get_db_manager()
    await db.create_tables()
    logger.info("Database initialized")


async def close_db() -> None:
    """Close database on application shutdown."""
    db = get_db_manager()
    await db.close()
    logger.info("Database connection closed")
