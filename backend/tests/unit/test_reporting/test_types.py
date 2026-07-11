"""
Tests for reporting types.
"""


from uuid import uuid4

from backend.reporting.types import (
    ExportFormat,
    ReportData,
    ReportRequest,
    ReportSection,
    ReportSectionType,
    ReportStatus,
    ReportTemplate,
    ReportType,
    ScheduledReport,
)


class TestReportType:
    """Tests for ReportType enum."""

    def test_all_types(self):
        """Test all report type values."""
        assert ReportType.OPPORTUNITY_ANALYSIS.value == "opportunity_analysis"
        assert ReportType.MARKET_RESEARCH.value == "market_research"
        assert ReportType.TREND_ANALYSIS.value == "trend_analysis"
        assert ReportType.COMPANY_PROFILE.value == "company_profile"


class TestReportStatus:
    """Tests for ReportStatus enum."""

    def test_all_statuses(self):
        """Test all status values."""
        assert ReportStatus.PENDING.value == "pending"
        assert ReportStatus.PROCESSING.value == "processing"
        assert ReportStatus.COMPLETED.value == "completed"
        assert ReportStatus.FAILED.value == "failed"


class TestExportFormat:
    """Tests for ExportFormat enum."""

    def test_all_formats(self):
        """Test all format values."""
        assert ExportFormat.PDF.value == "pdf"
        assert ExportFormat.HTML.value == "html"
        assert ExportFormat.DOCX.value == "docx"
        assert ExportFormat.XLSX.value == "xlsx"
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.CSV.value == "csv"


class TestReportSectionType:
    """Tests for ReportSectionType enum."""

    def test_all_types(self):
        """Test all section type values."""
        assert ReportSectionType.EXECUTIVE_SUMMARY.value == "executive_summary"
        assert ReportSectionType.INTRODUCTION.value == "introduction"
        assert ReportSectionType.FINDINGS.value == "findings"
        assert ReportSectionType.ANALYSIS.value == "analysis"


class TestReportSection:
    """Tests for ReportSection dataclass."""

    def test_creation(self):
        """Test section creation."""
        section = ReportSection(
            id="test-1",
            type=ReportSectionType.EXECUTIVE_SUMMARY,
            title="Executive Summary",
            content="Test content",
            order=0,
        )

        assert section.id == "test-1"
        assert section.type == ReportSectionType.EXECUTIVE_SUMMARY
        assert section.content == "Test content"
        assert section.order == 0


class TestReportTemplate:
    """Tests for ReportTemplate dataclass."""

    def test_creation(self):
        """Test template creation."""
        template = ReportTemplate(
            id="template-1",
            name="Standard Report",
            description="Standard report template",
            type=ReportType.MARKET_RESEARCH,
            sections=[ReportSectionType.EXECUTIVE_SUMMARY],
        )

        assert template.id == "template-1"
        assert template.type == ReportType.MARKET_RESEARCH
        assert len(template.sections) == 1


class TestReportRequest:
    """Tests for ReportRequest dataclass."""

    def test_creation(self):
        """Test request creation."""
        request = ReportRequest(
            title="Test Report",
            type=ReportType.MARKET_RESEARCH,
            description="Test description",
        )

        assert request.title == "Test Report"
        assert request.type == ReportType.MARKET_RESEARCH
        assert request.export_format == ExportFormat.PDF


class TestReportData:
    """Tests for ReportData dataclass."""

    def test_creation(self):
        """Test data creation."""
        data = ReportData(
            report_id=uuid4(),
            title="Test Report",
            type=ReportType.MARKET_RESEARCH,
        )

        assert data.title == "Test Report"
        assert data.type == ReportType.MARKET_RESEARCH
        assert len(data.sections) == 0


class TestScheduledReport:
    """Tests for ScheduledReport dataclass."""

    def test_creation(self):
        """Test scheduled report creation."""
        report = ScheduledReport(
            id=uuid4(),
            title="Weekly Report",
            type=ReportType.TREND_ANALYSIS,
            schedule="weekly",
            parameters={},
            recipients=["test@example.com"],
        )

        assert report.title == "Weekly Report"
        assert report.schedule == "weekly"
        assert len(report.recipients) == 1
        assert report.is_active is True
