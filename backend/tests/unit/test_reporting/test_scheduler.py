"""
Tests for report scheduler.
"""

from uuid import uuid4

import pytest

from backend.reporting.scheduler import ReportScheduler, get_report_scheduler
from backend.reporting.types import ReportType


class TestReportScheduler:
    """Tests for ReportScheduler."""

    @pytest.fixture
    def scheduler(self):
        return ReportScheduler()

    def test_creation(self, scheduler):
        """Test scheduler creation."""
        assert scheduler is not None
        assert len(scheduler._scheduled_reports) == 0

    def test_schedule_report(self, scheduler):
        """Test scheduling a report."""
        report = scheduler.schedule_report(
            title="Weekly Report",
            report_type=ReportType.TREND_ANALYSIS,
            schedule="weekly",
            parameters={"key": "value"},
            recipients=["test@example.com"],
        )

        assert report.title == "Weekly Report"
        assert report.schedule == "weekly"
        assert report.is_active is True
        assert len(scheduler._scheduled_reports) == 1

    def test_unschedule_report(self, scheduler):
        """Test unscheduling a report."""
        report = scheduler.schedule_report(
            title="Test Report",
            report_type=ReportType.MARKET_RESEARCH,
            schedule="daily",
            parameters={},
            recipients=[],
        )

        result = scheduler.unschedule_report(report.id)
        assert result is True
        assert len(scheduler._scheduled_reports) == 0

    def test_unschedule_nonexistent(self, scheduler):
        """Test unscheduling non-existent report."""
        result = scheduler.unschedule_report(uuid4())
        assert result is False

    def test_get_scheduled_report(self, scheduler):
        """Test getting a scheduled report."""
        report = scheduler.schedule_report(
            title="Test Report",
            report_type=ReportType.MARKET_RESEARCH,
            schedule="daily",
            parameters={},
            recipients=[],
        )

        retrieved = scheduler.get_scheduled_report(report.id)
        assert retrieved is not None
        assert retrieved.title == "Test Report"

    def test_get_all_scheduled_reports(self, scheduler):
        """Test getting all scheduled reports."""
        scheduler.schedule_report(
            title="Report 1",
            report_type=ReportType.MARKET_RESEARCH,
            schedule="daily",
            parameters={},
            recipients=[],
        )
        scheduler.schedule_report(
            title="Report 2",
            report_type=ReportType.TREND_ANALYSIS,
            schedule="weekly",
            parameters={},
            recipients=[],
        )

        reports = scheduler.get_all_scheduled_reports()
        assert len(reports) == 2

        reports_active = scheduler.get_all_scheduled_reports(active_only=True)
        assert len(reports_active) == 2

    def test_pause_report(self, scheduler):
        """Test pausing a report."""
        report = scheduler.schedule_report(
            title="Test Report",
            report_type=ReportType.MARKET_RESEARCH,
            schedule="daily",
            parameters={},
            recipients=[],
        )

        result = scheduler.pause_report(report.id)
        assert result is True
        assert scheduler.get_scheduled_report(report.id).is_active is False

    def test_resume_report(self, scheduler):
        """Test resuming a report."""
        report = scheduler.schedule_report(
            title="Test Report",
            report_type=ReportType.MARKET_RESEARCH,
            schedule="daily",
            parameters={},
            recipients=[],
        )

        scheduler.pause_report(report.id)
        result = scheduler.resume_report(report.id)
        assert result is True
        assert scheduler.get_scheduled_report(report.id).is_active is True

    def test_calculate_next_run_daily(self, scheduler):
        """Test daily schedule next run calculation."""
        next_run = scheduler._calculate_next_run("daily")
        assert next_run is not None

    def test_calculate_next_run_weekly(self, scheduler):
        """Test weekly schedule next run calculation."""
        next_run = scheduler._calculate_next_run("weekly")
        assert next_run is not None

    def test_calculate_next_run_monthly(self, scheduler):
        """Test monthly schedule next run calculation."""
        next_run = scheduler._calculate_next_run("monthly")
        assert next_run is not None


class TestGetReportScheduler:
    """Tests for get_report_scheduler function."""

    def test_get_scheduler(self):
        """Test getting global scheduler."""
        sched1 = get_report_scheduler()
        sched2 = get_report_scheduler()

        assert sched1 is sched2
