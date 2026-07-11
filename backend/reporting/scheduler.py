"""
ATLAS Platform - Report Scheduler

Schedules and manages recurring report generation.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from backend.core.logging import get_logger
from backend.reporting.types import (
    ExportFormat,
    ReportRequest,
    ReportType,
    ScheduledReport,
)

logger = get_logger(__name__)


class ReportScheduler:
    """Schedules and manages recurring report generation."""

    def __init__(self):
        self._scheduled_reports: dict[UUID, ScheduledReport] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    def schedule_report(
        self,
        title: str,
        report_type: ReportType,
        schedule: str,  # cron expression (simplified)
        parameters: dict[str, Any],
        recipients: list[str],
        format: ExportFormat = ExportFormat.PDF,
        user_id: UUID | None = None,
        organization_id: UUID | None = None,
    ) -> ScheduledReport:
        """
        Schedule a recurring report.
        
        Args:
            title: Report title
            report_type: Type of report
            schedule: Cron expression (simplified: daily, weekly, monthly)
            parameters: Report parameters
            recipients: Email addresses to send report to
            format: Export format
            user_id: User ID
            organization_id: Organization ID
            
        Returns:
            Created scheduled report
        """
        report_id = UUID(int=len(self._scheduled_reports) + 1)

        next_run = self._calculate_next_run(schedule)

        scheduled = ScheduledReport(
            id=report_id,
            title=title,
            type=report_type,
            schedule=schedule,
            parameters=parameters,
            recipients=recipients,
            format=format,
            is_active=True,
            next_run=next_run,
        )

        self._scheduled_reports[report_id] = scheduled
        logger.info(f"Scheduled report: {title} (ID: {report_id}, next run: {next_run})")

        return scheduled

    def unschedule_report(self, report_id: UUID) -> bool:
        """
        Unschedule a report.
        
        Args:
            report_id: Report ID
            
        Returns:
            True if unscheduled, False if not found
        """
        if report_id in self._scheduled_reports:
            del self._scheduled_reports[report_id]
            logger.info(f"Unscheduled report: {report_id}")
            return True
        return False

    def get_scheduled_report(self, report_id: UUID) -> ScheduledReport | None:
        """Get a scheduled report."""
        return self._scheduled_reports.get(report_id)

    def get_all_scheduled_reports(
        self,
        active_only: bool = False,
    ) -> list[ScheduledReport]:
        """Get all scheduled reports."""
        reports = list(self._scheduled_reports.values())

        if active_only:
            reports = [r for r in reports if r.is_active]

        return reports

    def update_scheduled_report(
        self,
        report_id: UUID,
        **updates: Any,
    ) -> ScheduledReport | None:
        """Update a scheduled report."""
        report = self._scheduled_reports.get(report_id)
        if not report:
            return None

        for key, value in updates.items():
            if hasattr(report, key):
                setattr(report, key, value)

        # Recalculate next run if schedule changed
        if "schedule" in updates:
            report.next_run = self._calculate_next_run(report.schedule)

        return report

    def pause_report(self, report_id: UUID) -> bool:
        """Pause a scheduled report."""
        report = self._scheduled_reports.get(report_id)
        if report:
            report.is_active = False
            logger.info(f"Paused scheduled report: {report_id}")
            return True
        return False

    def resume_report(self, report_id: UUID) -> bool:
        """Resume a paused scheduled report."""
        report = self._scheduled_reports.get(report_id)
        if report:
            report.is_active = True
            report.next_run = self._calculate_next_run(report.schedule)
            logger.info(f"Resumed scheduled report: {report_id}")
            return True
        return False

    async def start(self, callback: callable) -> None:
        """
        Start the scheduler.
        
        Args:
            callback: Async function to call when a report should be generated
        """
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop(callback))
        logger.info("Report scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Report scheduler stopped")

    async def _run_loop(self, callback: callable) -> None:
        """Run the scheduler loop."""
        while self._running:
            try:
                now = datetime.now(UTC)

                for report in self._scheduled_reports.values():
                    if report.is_active and report.next_run and now >= report.next_run:
                        logger.info(f"Triggering scheduled report: {report.title}")

                        # Create report request
                        request = ReportRequest(
                            title=report.title,
                            type=report.type,
                            parameters=report.parameters,
                            export_format=report.format,
                        )

                        # Call callback to generate and send report
                        await callback(report, request)

                        # Update last run and calculate next run
                        report.last_run = now
                        report.next_run = self._calculate_next_run(report.schedule)

                        logger.info(f"Completed scheduled report: {report.title}, next run: {report.next_run}")

                # Check every minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    def _calculate_next_run(self, schedule: str) -> datetime:
        """
        Calculate next run time from schedule.
        
        Args:
            schedule: Schedule string (daily, weekly, monthly, or cron-like)
            
        Returns:
            Next run datetime
        """
        now = datetime.now(UTC)

        schedule_lower = schedule.lower()

        if schedule_lower in ["hourly", "0 * * * *"]:
            return now + timedelta(hours=1)
        elif schedule_lower in ["daily", "0 0 * * *"]:
            return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif schedule_lower in ["weekly", "0 0 * * 0"]:
            days_until_sunday = (6 - now.weekday()) % 7
            return (now + timedelta(days=days_until_sunday or 7)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif schedule_lower in ["monthly", "0 0 1 * *"]:
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to daily
            return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


# Global scheduler instance
_scheduler: ReportScheduler | None = None


def get_report_scheduler() -> ReportScheduler:
    """Get the global report scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportScheduler()
    return _scheduler
