"""
ATLAS Platform - Report Engine Module

Report generation, scheduling, and export.
"""

from backend.reporting.engine import ReportGenerator, get_report_generator
from backend.reporting.export import ReportExporter, get_report_exporter
from backend.reporting.scheduler import ReportScheduler, get_report_scheduler
from backend.reporting.types import (
    ChartConfig,
    ExportFormat,
    ReportData,
    ReportExport,
    ReportRequest,
    ReportSection,
    ReportSectionType,
    ReportStatus,
    ReportTemplate,
    ReportType,
    ScheduledReport,
    TableConfig,
)

__all__ = [
    # Types
    "ReportType",
    "ReportStatus",
    "ExportFormat",
    "ReportSectionType",
    "ReportSection",
    "ReportTemplate",
    "ReportRequest",
    "ReportData",
    "ScheduledReport",
    "ReportExport",
    "ChartConfig",
    "TableConfig",
    # Engine
    "ReportGenerator",
    "get_report_generator",
    # Export
    "ReportExporter",
    "get_report_exporter",
    # Scheduler
    "ReportScheduler",
    "get_report_scheduler",
]
