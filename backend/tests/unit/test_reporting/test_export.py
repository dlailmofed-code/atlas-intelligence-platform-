"""
Tests for report export.
"""

import json
from uuid import uuid4

import pytest

from backend.reporting.export import ReportExporter, get_report_exporter
from backend.reporting.types import (
    ExportFormat,
    ReportData,
    ReportSection,
    ReportSectionType,
    ReportType,
)


class TestReportExporter:
    """Tests for ReportExporter."""

    @pytest.fixture
    def exporter(self):
        return ReportExporter()

    @pytest.fixture
    def sample_report(self):
        return ReportData(
            report_id=uuid4(),
            title="Test Report",
            type=ReportType.MARKET_RESEARCH,
            sections=[
                ReportSection(
                    id="sec-1",
                    type=ReportSectionType.EXECUTIVE_SUMMARY,
                    title="Executive Summary",
                    content="This is the executive summary.",
                    order=0,
                ),
            ],
        )

    def test_creation(self, exporter):
        """Test exporter creation."""
        assert exporter is not None

    def test_export_json(self, exporter, sample_report):
        """Test JSON export."""
        result = exporter.export(sample_report, ExportFormat.JSON)

        assert result.format == ExportFormat.JSON
        assert result.content_type == "application/json"
        assert b"Test Report" in result.content

        # Verify JSON is valid
        data = json.loads(result.content)
        assert data["title"] == "Test Report"

    def test_export_csv(self, exporter, sample_report):
        """Test CSV export."""
        result = exporter.export(sample_report, ExportFormat.CSV)

        assert result.format == ExportFormat.CSV
        assert result.content_type == "text/csv"
        assert b"Section,Title" in result.content

    def test_export_html(self, exporter, sample_report):
        """Test HTML export."""
        result = exporter.export(sample_report, ExportFormat.HTML)

        assert result.format == ExportFormat.HTML
        assert result.content_type == "text/html"
        assert b"<!DOCTYPE html>" in result.content
        assert b"Test Report" in result.content

    def test_export_unsupported(self, exporter, sample_report):
        """Test unsupported format."""
        with pytest.raises(ValueError):
            exporter.export(sample_report, "unsupported")


class TestGetReportExporter:
    """Tests for get_report_exporter function."""

    def test_get_exporter(self):
        """Test getting global exporter."""
        exp1 = get_report_exporter()
        exp2 = get_report_exporter()

        assert exp1 is exp2
