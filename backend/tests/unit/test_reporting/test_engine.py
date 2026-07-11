"""
Tests for report engine.
"""

import pytest

from backend.reporting.engine import ReportGenerator, get_report_generator
from backend.reporting.types import (
    ReportRequest,
    ReportSectionType,
    ReportType,
)


class TestReportGenerator:
    """Tests for ReportGenerator."""

    @pytest.fixture
    def generator(self):
        return ReportGenerator()

    def test_creation(self, generator):
        """Test generator creation."""
        assert generator is not None

    def test_get_section_order(self, generator):
        """Test section order generation."""
        order = generator._get_section_order(ReportType.MARKET_RESEARCH)
        assert len(order) > 0
        assert order[0] == ReportSectionType.EXECUTIVE_SUMMARY

    def test_get_section_title(self, generator):
        """Test section title generation."""
        title = generator._get_section_title(ReportSectionType.EXECUTIVE_SUMMARY)
        assert title == "Executive Summary"

        title = generator._get_section_title(ReportSectionType.FINDINGS)
        assert title == "Key Findings"

    def test_generate_default_content(self, generator):
        """Test default content generation."""
        request = ReportRequest(
            title="Test Report",
            type=ReportType.MARKET_RESEARCH,
            description="Test description",
        )

        content = generator._generate_default_content(
            ReportSectionType.EXECUTIVE_SUMMARY,
            request,
            None,
        )

        assert "Test Report" in content or "Test description" in content

    @pytest.mark.asyncio
    async def test_generate_report(self, generator):
        """Test report generation."""
        request = ReportRequest(
            title="Test Report",
            type=ReportType.MARKET_RESEARCH,
            description="Test description",
        )

        report = await generator.generate_report(request)

        assert report.title == "Test Report"
        assert report.type == ReportType.MARKET_RESEARCH
        assert len(report.sections) > 0

    @pytest.mark.asyncio
    async def test_generate_report_with_data(self, generator):
        """Test report generation with data."""
        request = ReportRequest(
            title="Test Report",
            type=ReportType.TREND_ANALYSIS,
        )

        data = {"key": "value"}
        report = await generator.generate_report(request, data)

        assert report.title == "Test Report"
        assert report.metadata.get("parameters") is not None


class TestGetReportGenerator:
    """Tests for get_report_generator function."""

    def test_get_generator(self):
        """Test getting global generator."""
        gen1 = get_report_generator()
        gen2 = get_report_generator()

        assert gen1 is gen2
