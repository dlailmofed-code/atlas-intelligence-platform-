"""
ATLAS Platform - Test Configuration

This module configures pytest for the ATLAS Platform tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.logging import setup_logging
from backend.db import Base
from backend.api.main import app


# =============================================================================
# Test Settings
# =============================================================================

@pytest.fixture(scope="session")
def test_settings() -> dict:
    """Get test settings."""
    return {
        "database": {
            "name": "atlas_test",
            "user": "test",
            "password": "test",
        }
    }


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def sync_engine():
    """Create sync engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(sync_engine) -> Generator:
    """Create a new database session for each test."""
    SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        yield session
    
    await engine.dispose()


# =============================================================================
# API Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    setup_logging()
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    setup_logging()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_user():
    """Create mock user data."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "full_name": "Test User",
        "company": "Test Company",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def mock_opportunity():
    """Create mock opportunity data."""
    return {
        "id": "test-opp-id",
        "title": "Test Opportunity",
        "description": "This is a test opportunity",
        "category": "Technology",
        "industry": "Software",
        "score_overall": 85.0,
        "score_demand": 90.0,
        "score_growth": 80.0,
        "score_competition": 60.0,
        "score_risk": 30.0,
        "confidence": 0.85,
    }


@pytest.fixture
def mock_signal():
    """Create mock signal data."""
    return {
        "id": "test-signal-id",
        "type": "market",
        "name": "Test Signal",
        "description": "This is a test signal",
        "category": "Investment",
        "intensity": 75.0,
        "trend": "up",
        "confidence": 0.80,
    }
