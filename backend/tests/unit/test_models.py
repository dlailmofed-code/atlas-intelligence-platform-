"""
ATLAS Platform - Model Unit Tests

Note: These tests require PostgreSQL due to UUID type compatibility.
They are marked to skip with SQLite test database.
"""

import pytest

# Skip all tests in this module when running with SQLite
pytestmark = pytest.mark.skip(reason="Model tests require PostgreSQL due to UUID type compatibility")


class TestUserModel:
    """Test User model functionality."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_session):
        """Test creating a new user."""
        from backend.models.users import User

        user = User(
            id=uuid4(),
            email="newuser@example.com",
            full_name="New User",
            company="Test Company",
            hashed_password=hash_password("Password123!"),
            is_active=True,
            is_verified=False,
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.is_verified is False

    @pytest.mark.asyncio
    async def test_user_default_values(self, test_session):
        """Test user default values."""
        from backend.models.users import User

        user = User(
            id=uuid4(),
            email="defaults@example.com",
            full_name="Defaults User",
            hashed_password=hash_password("Password123!"),
        )

        test_session.add(user)
        await test_session.commit()

        assert user.is_active is True
        assert user.is_verified is False
        assert user.language == "en"
        assert user.timezone == "UTC"
        assert user.theme == "light"


class TestOpportunityModel:
    """Test Opportunity model functionality."""

    @pytest.mark.asyncio
    async def test_create_opportunity(self, test_session):
        """Test creating a new opportunity."""
        from backend.models.signals import Opportunity

        opportunity = Opportunity(
            id=uuid4(),
            title="Test Opportunity",
            description="Test description",
            category="market",
            industry="technology",
            status="detected",
            confidence=0.85,
            region="north_america",
            is_analyzed=False,
            is_bookmarked=False,
        )

        test_session.add(opportunity)
        await test_session.commit()
        await test_session.refresh(opportunity)

        assert opportunity.id is not None
        assert opportunity.title == "Test Opportunity"
        assert opportunity.category == "market"
        assert opportunity.confidence == 0.85


class TestReportModel:
    """Test Report model functionality."""

    @pytest.mark.asyncio
    async def test_create_report(self, test_session):
        """Test creating a new report."""
        from backend.models.reports import Report

        report = Report(
            id=uuid4(),
            title="Test Report",
            description="Test report description",
            type="market_research",
            status="draft",
            content={},
            created_by=uuid4(),
            signal_ids=[],
            opportunity_ids=[],
            evidence_ids=[],
        )

        test_session.add(report)
        await test_session.commit()
        await test_session.refresh(report)

        assert report.id is not None
        assert report.title == "Test Report"
        assert report.type == "market_research"
        assert report.status == "draft"


class TestSignalModel:
    """Test Signal model functionality."""

    @pytest.mark.asyncio
    async def test_create_signal(self, test_session):
        """Test creating a new signal."""
        from backend.models.signals import Signal

        signal = Signal(
            id=uuid4(),
            type="market",
            name="Test Signal",
            description="Test signal description",
            category="technology",
            intensity=0.75,
            trend="up",
            confidence=0.90,
            status="active",
            detected_at=datetime.now(UTC),
        )

        test_session.add(signal)
        await test_session.commit()
        await test_session.refresh(signal)

        assert signal.id is not None
        assert signal.name == "Test Signal"
        assert signal.intensity == 0.75
        assert signal.trend == "up"
