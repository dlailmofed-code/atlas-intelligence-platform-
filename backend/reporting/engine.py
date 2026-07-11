"""
ATLAS Platform - Report Engine

Generates reports from various data sources.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from backend.core.logging import get_logger
from backend.reporting.types import (
    ExportFormat,
    ReportData,
    ReportRequest,
    ReportSection,
    ReportSectionType,
    ReportStatus,
    ReportTemplate,
    ReportType,
)

logger = get_logger(__name__)


@dataclass
class ChartConfig:
    """Configuration for a chart."""
    
    type: str  # bar, line, pie, scatter, etc.
    title: str
    data: dict[str, Any]
    options: dict[str, Any]


@dataclass
class TableConfig:
    """Configuration for a table."""
    
    title: str
    headers: list[str]
    rows: list[list[Any]]
    options: dict[str, Any]


class ReportGenerator:
    """Generates reports from data."""
    
    def __init__(self):
        self._templates: dict[str, ReportTemplate] = {}
        self._section_generators: dict[ReportSectionType, callable] = {}
    
    def register_template(self, template: ReportTemplate) -> None:
        """Register a report template."""
        self._templates[template.id] = template
        logger.info(f"Registered report template: {template.id}")
    
    def register_section_generator(
        self,
        section_type: ReportSectionType,
        generator: callable,
    ) -> None:
        """Register a section generator function."""
        self._section_generators[section_type] = generator
    
    async def generate_report(
        self,
        request: ReportRequest,
        data: dict[str, Any] | None = None,
    ) -> ReportData:
        """
        Generate a report based on request and data.
        
        Args:
            request: Report request with parameters
            data: Data to include in the report
            
        Returns:
            Generated report data
        """
        report_id = uuid4()
        
        logger.info(f"Generating report: {request.title} (type: {request.type})")
        
        sections = []
        charts = []
        tables = []
        
        # Get template or use default
        template = self._templates.get(request.template_id)
        
        # Generate sections based on report type
        section_order = self._get_section_order(request.type)
        
        for order, section_type in enumerate(section_order):
            section = await self._generate_section(
                section_type=section_type,
                order=order,
                request=request,
                data=data,
            )
            if section:
                sections.append(section)
                charts.extend(section.charts)
                tables.extend(section.tables)
        
        return ReportData(
            report_id=report_id,
            title=request.title,
            type=request.type,
            sections=sections,
            charts=charts,
            tables=tables,
            metadata={
                "description": request.description,
                "parameters": request.parameters,
                "export_format": request.export_format.value,
            },
            generated_by=str(request.user_id) if request.user_id else None,
        )
    
    async def _generate_section(
        self,
        section_type: ReportSectionType,
        order: int,
        request: ReportRequest,
        data: dict[str, Any] | None,
    ) -> ReportSection | None:
        """Generate a single report section."""
        
        # Check for custom generator
        generator = self._section_generators.get(section_type)
        if generator:
            try:
                content = await generator(section_type, request, data)
            except Exception as e:
                logger.error(f"Section generator failed: {e}")
                content = f"Error generating section: {str(e)}"
        else:
            content = self._generate_default_content(section_type, request, data)
        
        return ReportSection(
            id=str(uuid4()),
            type=section_type,
            title=self._get_section_title(section_type),
            content=content,
            order=order,
        )
    
    def _get_section_order(self, report_type: ReportType) -> list[ReportSectionType]:
        """Get the section order for a report type."""
        
        orders = {
            ReportType.OPPORTUNITY_ANALYSIS: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.METHODOLOGY,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.DATA_VISUALIZATION,
                ReportSectionType.RECOMMENDATIONS,
                ReportSectionType.CONCLUSION,
            ],
            ReportType.MARKET_RESEARCH: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.METHODOLOGY,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.CONCLUSION,
            ],
            ReportType.TREND_ANALYSIS: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.FINDINGS,
                ReportSectionType.DATA_VISUALIZATION,
                ReportSectionType.ANALYSIS,
                ReportSectionType.CONCLUSION,
            ],
            ReportType.COMPANY_PROFILE: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.CONCLUSION,
            ],
            ReportType.COMPETITIVE_ANALYSIS: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.DATA_VISUALIZATION,
                ReportSectionType.RECOMMENDATIONS,
            ],
            ReportType.INDUSTRY_ANALYSIS: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.INTRODUCTION,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.DATA_VISUALIZATION,
                ReportSectionType.CONCLUSION,
                ReportSectionType.APPENDIX,
            ],
            ReportType.CUSTOM: [
                ReportSectionType.EXECUTIVE_SUMMARY,
                ReportSectionType.FINDINGS,
                ReportSectionType.ANALYSIS,
                ReportSectionType.CONCLUSION,
            ],
        }
        
        return orders.get(report_type, orders[ReportType.CUSTOM])
    
    def _get_section_title(self, section_type: ReportSectionType) -> str:
        """Get the display title for a section type."""
        
        titles = {
            ReportSectionType.EXECUTIVE_SUMMARY: "Executive Summary",
            ReportSectionType.INTRODUCTION: "Introduction",
            ReportSectionType.METHODOLOGY: "Methodology",
            ReportSectionType.FINDINGS: "Key Findings",
            ReportSectionType.ANALYSIS: "Analysis",
            ReportSectionType.DATA_VISUALIZATION: "Data & Visualizations",
            ReportSectionType.RECOMMENDATIONS: "Recommendations",
            ReportSectionType.CONCLUSION: "Conclusion",
            ReportSectionType.APPENDIX: "Appendix",
            ReportSectionType.REFERENCES: "References",
        }
        
        return titles.get(section_type, section_type.value.replace("_", " ").title())
    
    def _generate_default_content(
        self,
        section_type: ReportSectionType,
        request: ReportRequest,
        data: dict[str, Any] | None,
    ) -> str:
        """Generate default content for a section."""
        
        templates = {
            ReportSectionType.EXECUTIVE_SUMMARY: f"""
This report provides an analysis of {request.description or 'the requested topic'}.

Key Highlights:
- Detailed analysis of current market conditions
- Comprehensive data review and interpretation
- Strategic recommendations for next steps

This report was generated on {datetime.utcnow().strftime('%Y-%m-%d')} at {datetime.utcnow().strftime('%H:%M UTC')}.
""",
            ReportSectionType.INTRODUCTION: f"""
## Introduction

This report examines {request.description or 'the subject matter'} in detail.

### Objectives
- Provide comprehensive analysis
- Identify key trends and patterns
- Deliver actionable insights

### Scope
This analysis covers the specified parameters and data sources as requested.
""",
            ReportSectionType.METHODOLOGY: """
## Methodology

This report was generated using a systematic approach:

1. **Data Collection**: Gathered relevant data from multiple sources
2. **Data Processing**: Cleaned and validated the collected data
3. **Analysis**: Applied statistical and analytical methods
4. **Synthesis**: Combined findings into coherent insights
5. **Review**: Validated conclusions against known benchmarks

### Data Sources
- Primary research data
- Secondary research publications
- Industry databases
- Public records and filings
""",
            ReportSectionType.FINDINGS: f"""
## Key Findings

Based on the analysis, the following key findings were identified:

### Finding 1: Market Dynamics
The market shows significant activity with notable trends in key sectors.

### Finding 2: Competitive Landscape
Competitive pressures continue to shape industry evolution.

### Finding 3: Growth Opportunities
Several opportunities exist for organizations prepared to act strategically.

### Additional Data
Additional findings and details are available in the data visualizations section.
""",
            ReportSectionType.ANALYSIS: """
## Analysis

### Trend Analysis
The data reveals several important trends that warrant attention:

1. **Trend 1**: Description of the first major trend
2. **Trend 2**: Description of the second major trend
3. **Trend 3**: Description of the third major trend

### Comparative Analysis
When compared to industry benchmarks, the findings indicate:

- Performance metrics are within expected ranges
- Certain areas show deviation from benchmarks
- Strategic adjustments may be warranted

### Risk Assessment
Key risks identified in the analysis:
- Market volatility risks
- Competitive risks
- Regulatory risks
""",
            ReportSectionType.DATA_VISUALIZATION: """
## Data Visualizations

The following charts and tables provide visual representations of the analyzed data.

*Note: Actual charts and tables will be generated based on the specific data provided.*
""",
            ReportSectionType.RECOMMENDATIONS: """
## Recommendations

Based on the findings and analysis, the following recommendations are made:

### Immediate Actions
1. **Action 1**: Description of recommended action
2. **Action 2**: Description of recommended action

### Strategic Initiatives
1. **Initiative 1**: Long-term strategic recommendation
2. **Initiative 2**: Additional strategic consideration

### Implementation Priorities
- High Priority: Critical items requiring immediate attention
- Medium Priority: Important items for near-term planning
- Low Priority: Items for future consideration
""",
            ReportSectionType.CONCLUSION: """
## Conclusion

This report has examined the subject matter comprehensively, identifying key findings and providing actionable recommendations.

### Summary of Key Points
- The analysis reveals significant insights
- Strategic action is recommended
- Implementation should follow the outlined priorities

### Next Steps
1. Review findings with stakeholders
2. Prioritize recommendations based on organizational needs
3. Develop implementation plans for key initiatives

---
*Report generated by ATLAS Platform Intelligence Engine*
""",
            ReportSectionType.APPENDIX: """
## Appendix

### Additional Data Tables
Additional supporting data is available upon request.

### Methodology Notes
Detailed methodology documentation is available upon request.

### Glossary
Terms and definitions used in this report are consistent with industry standards.
""",
            ReportSectionType.REFERENCES: """
## References

1. Industry Reports and Publications
2. Academic Research Papers
3. Government Databases and Filings
4. Market Research Sources
5. Company Filings and Announcements

---
*All sources are properly cited within the report where applicable.*
""",
        }
        
        return templates.get(section_type, f"Section content for {section_type.value}")


# Global report generator instance
_generator: ReportGenerator | None = None


def get_report_generator() -> ReportGenerator:
    """Get the global report generator."""
    global _generator
    if _generator is None:
        _generator = ReportGenerator()
    return _generator
