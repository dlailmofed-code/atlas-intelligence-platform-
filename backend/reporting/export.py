"""
ATLAS Platform - Report Export

Exports reports to various formats.
"""

import csv
import io
import json

from backend.core.logging import get_logger
from backend.reporting.types import ExportFormat, ReportData, ReportExport

logger = get_logger(__name__)


class ReportExporter:
    """Exports reports to various formats."""

    def export(
        self,
        report: ReportData,
        format: ExportFormat,
    ) -> ReportExport:
        """
        Export a report to the specified format.
        
        Args:
            report: Report data to export
            format: Export format
            
        Returns:
            Exported report
        """
        if format == ExportFormat.PDF:
            return self._export_pdf(report)
        elif format == ExportFormat.HTML:
            return self._export_html(report)
        elif format == ExportFormat.DOCX:
            return self._export_docx(report)
        elif format == ExportFormat.XLSX:
            return self._export_xlsx(report)
        elif format == ExportFormat.JSON:
            return self._export_json(report)
        elif format == ExportFormat.CSV:
            return self._export_csv(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_pdf(self, report: ReportData) -> ReportExport:
        """Export to PDF format."""
        # For production, integrate with a PDF library like reportlab or weasyprint
        # For now, return HTML as placeholder
        html_export = self._export_html(report)

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.PDF,
            content=html_export.content,
            filename=f"{report.title.replace(' ', '_')}.pdf",
            content_type="application/pdf",
        )

    def _export_html(self, report: ReportData) -> ReportExport:
        """Export to HTML format."""
        html_content = self._generate_html(report)

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.HTML,
            content=html_content.encode("utf-8"),
            filename=f"{report.title.replace(' ', '_')}.html",
            content_type="text/html",
        )

    def _export_docx(self, report: ReportData) -> ReportExport:
        """Export to DOCX format."""
        # For production, integrate with python-docx
        # For now, return text as placeholder
        text_content = self._generate_text(report)

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.DOCX,
            content=text_content.encode("utf-8"),
            filename=f"{report.title.replace(' ', '_')}.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    def _export_xlsx(self, report: ReportData) -> ReportExport:
        """Export to XLSX format."""
        # For production, integrate with openpyxl
        # For now, return CSV as placeholder
        csv_export = self._export_csv(report)

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.XLSX,
            content=csv_export.content,
            filename=f"{report.title.replace(' ', '_')}.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def _export_json(self, report: ReportData) -> ReportExport:
        """Export to JSON format."""
        report_dict = {
            "id": str(report.report_id),
            "title": report.title,
            "type": report.type.value,
            "sections": [
                {
                    "id": s.id,
                    "type": s.type.value,
                    "title": s.title,
                    "content": s.content,
                    "order": s.order,
                }
                for s in report.sections
            ],
            "charts": report.charts,
            "tables": report.tables,
            "metadata": report.metadata,
            "generated_at": report.generated_at.isoformat(),
            "generated_by": report.generated_by,
        }

        json_content = json.dumps(report_dict, indent=2)

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.JSON,
            content=json_content.encode("utf-8"),
            filename=f"{report.title.replace(' ', '_')}.json",
            content_type="application/json",
        )

    def _export_csv(self, report: ReportData) -> ReportExport:
        """Export to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write sections
        writer.writerow(["Section", "Title", "Content"])
        for section in report.sections:
            writer.writerow([section.type.value, section.title, section.content[:500]])

        csv_content = output.getvalue()

        return ReportExport(
            report_id=report.report_id,
            format=ExportFormat.CSV,
            content=csv_content.encode("utf-8"),
            filename=f"{report.title.replace(' ', '_')}.csv",
            content_type="text/csv",
        )

    def _generate_html(self, report: ReportData) -> str:
        """Generate HTML content for report."""
        sections_html = ""

        for section in report.sections:
            sections_html += f"""
            <section id="{section.id}">
                <h2>{section.title}</h2>
                <div class="content">
                    {section.content.replace(chr(10), '<br>')}
                </div>
            </section>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #444;
            margin-top: 30px;
        }}
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        section {{
            margin-bottom: 30px;
        }}
        .content {{
            text-align: justify;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
        }}
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    
    <div class="metadata">
        <p>Type: {report.type.value}</p>
        <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
        {f'<p>Generated by: {report.generated_by}</p>' if report.generated_by else ''}
    </div>
    
    {sections_html}
    
    <footer>
        <p>Generated by ATLAS Platform Intelligence Engine</p>
    </footer>
</body>
</html>
"""

    def _generate_text(self, report: ReportData) -> str:
        """Generate plain text content for report."""
        lines = [
            "=" * 80,
            report.title.upper(),
            "=" * 80,
            "",
            f"Type: {report.type.value}",
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "-" * 80,
        ]

        for section in report.sections:
            lines.append("")
            lines.append(section.title.upper())
            lines.append("-" * 40)
            lines.append(section.content.strip())
            lines.append("")

        lines.extend([
            "-" * 80,
            "",
            "Generated by ATLAS Platform Intelligence Engine",
        ])

        return "\n".join(lines)


# Global exporter instance
_exporter: ReportExporter | None = None


def get_report_exporter() -> ReportExporter:
    """Get the global report exporter."""
    global _exporter
    if _exporter is None:
        _exporter = ReportExporter()
    return _exporter
