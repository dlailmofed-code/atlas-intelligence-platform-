"""
ATLAS Platform - Test Configuration

Pytest configuration and fixtures for testing.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.main import app
from backend.db.session import get_db_manager
from backend.models.common.base import Base

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db_manager] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company": "Test Company",
    }


@pytest.fixture
def test_opportunity_data() -> dict:
    """Test opportunity data."""
    return {
        "title": "Test Opportunity",
        "description": "This is a test opportunity description",
        "category": "market",
        "industry": "technology",
        "region": "north_america",
    }
