"""
ATLAS Platform - Report Engine Types

Type definitions for the report engine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class ReportType(str, Enum):
    """Report types."""
    
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    MARKET_RESEARCH = "market_research"
    TREND_ANALYSIS = "trend_analysis"
    COMPANY_PROFILE = "company_profile"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Report generation status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExportFormat(str, Enum):
    """Export formats."""
    
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"
    JSON = "json"
    CSV = "csv"


class ReportSectionType(str, Enum):
    """Report section types."""
    
    EXECUTIVE_SUMMARY = "executive_summary"
    INTRODUCTION = "introduction"
    METHODOLOGY = "methodology"
    FINDINGS = "findings"
    ANALYSIS = "analysis"
    DATA_VISUALIZATION = "data_visualization"
    RECOMMENDATIONS = "recommendations"
    CONCLUSION = "conclusion"
    APPENDIX = "appendix"
    REFERENCES = "references"


@dataclass
class ReportSection:
    """A section within a report."""
    
    id: str
    type: ReportSectionType
    title: str
    content: str
    order: int
    metadata: dict[str, Any] = field(default_factory=dict)
    charts: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ReportTemplate:
    """Template for generating reports."""
    
    id: str
    name: str
    description: str
    type: ReportType
    sections: list[ReportSectionType]
    default_format: ExportFormat = ExportFormat.PDF
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportRequest:
    """Request to generate a report."""
    
    title: str
    type: ReportType
    description: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    template_id: str | None = None
    export_format: ExportFormat = ExportFormat.PDF
    user_id: UUID | None = None
    organization_id: UUID | None = None
    project_id: UUID | None = None


@dataclass
class ReportData:
    """Report data container."""
    
    report_id: UUID
    title: str
    type: ReportType
    sections: list[ReportSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    charts: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str | None = None


@dataclass
class ScheduledReport:
    """Scheduled report configuration."""
    
    id: UUID
    title: str
    type: ReportType
    schedule: str  # cron expression
    parameters: dict[str, Any]
    recipients: list[str]
    format: ExportFormat = ExportFormat.PDF
    is_active: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None


@dataclass
class ReportExport:
    """Exported report."""
    
    report_id: UUID
    format: ExportFormat
    content: bytes
    filename: str
    content_type: str
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChartConfig:
    """Configuration for a chart."""
    
    type: str  # bar, line, pie, scatter, etc.
    title: str
    data: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class TableConfig:
    """Configuration for a table."""
    
    title: str
    headers: list[str]
    rows: list[list[Any]]
    options: dict[str, Any] = field(default_factory=dict)
