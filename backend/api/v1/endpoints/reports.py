"""
ATLAS Platform - Reports Endpoints
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.auth import get_current_user
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.users import User

logger = get_logger(__name__)

router = APIRouter(tags=["reports"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ReportCreate(BaseModel):
    """Request model for creating a report."""

    title: str = Field(max_length=500)
    description: str | None = None
    type: str = Field(max_length=50)  # opportunity_analysis, market_research, trend_analysis, company_profile, custom
    project_id: UUID | None = None
    is_public: bool = False
    export_formats: list[str] = ["pdf"]


class ReportUpdate(BaseModel):
    """Request model for updating a report."""

    title: str | None = Field(default=None, max_length=500)
    description: str | None = None
    is_public: bool | None = None


class ReportResponse(BaseModel):
    """Response model for a report."""

    id: str
    title: str
    description: str | None = None
    type: str
    status: str
    content: dict = {}
    summary: str | None = None
    project_id: str | None = None
    created_by: str
    signal_ids: list[str] = []
    opportunity_ids: list[str] = []
    evidence_ids: list[str] = []
    is_public: bool
    export_formats: list[str] = []
    generation_time_ms: int | None = None
    model_used: str | None = None
    created_at: str
    updated_at: str


class ReportTemplateResponse(BaseModel):
    """Response model for a report template."""

    id: str
    name: str
    description: str | None = None
    type: str
    template_config: dict = {}
    default_filters: dict = {}
    is_system: bool
    usage_count: int
    created_at: str
    updated_at: str


class PaginatedReportsResponse(BaseModel):
    """Paginated response for reports."""

    items: list[ReportResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class ReportGenerationRequest(BaseModel):
    """Request model for generating a report."""

    template_id: UUID | None = None
    report_type: str = Field(max_length=50)
    title: str | None = Field(default=None, max_length=500)
    filters: dict = {}
    export_format: str = "pdf"


class ReportGenerationResponse(BaseModel):
    """Response model for report generation job."""

    job_id: str
    report_id: str | None = None
    status: str
    progress: int
    created_at: str


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedReportsResponse)
async def list_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    report_type: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedReportsResponse:
    """
    List reports for the current user.

    Args:
        page: Page number (default 1)
        page_size: Items per page (default 20, max 100)
        report_type: Filter by report type
        status: Filter by status
        search: Search in title/description
        project_id: Filter by project
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of reports
    """
    from backend.models.reports import Report

    # Build query
    query = select(Report).where(
        (Report.created_by == current_user.id) | (Report.is_public)
    )

    if report_type:
        query = query.where(Report.type == report_type)

    if status_filter:
        query = query.where(Report.status == status_filter)

    if search:
        query = query.where(
            Report.title.ilike(f"%{search}%") |
            Report.description.ilike(f"%{search}%")
        )

    if project_id:
        query = query.where(Report.project_id == project_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Report.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    reports = result.scalars().all()

    return PaginatedReportsResponse(
        items=[ReportResponse(
            id=str(r.id),
            title=r.title,
            description=r.description,
            type=r.type,
            status=r.status,
            content=r.content,
            summary=r.summary,
            project_id=str(r.project_id) if r.project_id else None,
            created_by=str(r.created_by),
            signal_ids=r.signal_ids or [],
            opportunity_ids=r.opportunity_ids or [],
            evidence_ids=r.evidence_ids or [],
            is_public=r.is_public,
            export_formats=r.export_formats or [],
            generation_time_ms=r.generation_time_ms,
            model_used=r.model_used,
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
        ) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/templates", response_model=list[ReportTemplateResponse])
async def list_report_templates(
    template_type: str | None = Query(default=None, alias="type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReportTemplateResponse]:
    """
    List available report templates.

    Args:
        template_type: Filter by template type
        db: Database session
        current_user: Authenticated user

    Returns:
        List of report templates
    """
    from backend.models.reports import ReportTemplate

    query = select(ReportTemplate).where(ReportTemplate.is_active)

    if template_type:
        query = query.where(ReportTemplate.type == template_type)

    query = query.order_by(ReportTemplate.usage_count.desc())

    result = await db.execute(query)
    templates = result.scalars().all()

    return [ReportTemplateResponse(
        id=str(t.id),
        name=t.name,
        description=t.description,
        type=t.type,
        template_config=t.template_config or {},
        default_filters=t.default_filters or {},
        is_system=t.is_system,
        usage_count=t.usage_count,
        created_at=t.created_at.isoformat() if t.created_at else "",
        updated_at=t.updated_at.isoformat() if t.updated_at else "",
    ) for t in templates]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    """
    Get a specific report by ID.

    Args:
        report_id: Report UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        Report details
    """
    from backend.models.reports import Report

    query = select(Report).where(
        Report.id == report_id,
        (Report.created_by == current_user.id) | (Report.is_public)
    )

    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Report not found"},
        )

    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        type=report.type,
        status=report.status,
        content=report.content or {},
        summary=report.summary,
        project_id=str(report.project_id) if report.project_id else None,
        created_by=str(report.created_by),
        signal_ids=report.signal_ids or [],
        opportunity_ids=report.opportunity_ids or [],
        evidence_ids=report.evidence_ids or [],
        is_public=report.is_public,
        export_formats=report.export_formats or [],
        generation_time_ms=report.generation_time_ms,
        model_used=report.model_used,
        created_at=report.created_at.isoformat() if report.created_at else "",
        updated_at=report.updated_at.isoformat() if report.updated_at else "",
    )


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    """
    Create a new report.

    Args:
        request: Report creation request
        db: Database session
        current_user: Authenticated user

    Returns:
        Created report
    """
    import uuid

    from backend.models.reports import Report

    report = Report(
        id=uuid.uuid4(),
        title=request.title,
        description=request.description,
        type=request.type,
        project_id=request.project_id,
        created_by=current_user.id,
        is_public=request.is_public,
        export_formats=request.export_formats,
        status="draft",
        content={},
        signal_ids=[],
        opportunity_ids=[],
        evidence_ids=[],
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    logger.info("Report created", report_id=str(report.id), user_id=str(current_user.id))

    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        type=report.type,
        status=report.status,
        content=report.content or {},
        summary=report.summary,
        project_id=str(report.project_id) if report.project_id else None,
        created_by=str(report.created_by),
        signal_ids=report.signal_ids or [],
        opportunity_ids=report.opportunity_ids or [],
        evidence_ids=report.evidence_ids or [],
        is_public=report.is_public,
        export_formats=report.export_formats or [],
        generation_time_ms=report.generation_time_ms,
        model_used=report.model_used,
        created_at=report.created_at.isoformat() if report.created_at else "",
        updated_at=report.updated_at.isoformat() if report.updated_at else "",
    )


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    request: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    """
    Update an existing report.

    Args:
        report_id: Report UUID
        request: Report update request
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated report
    """
    from backend.models.reports import Report

    query = select(Report).where(
        Report.id == report_id,
        Report.created_by == current_user.id
    )

    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Report not found or access denied"},
        )

    if request.title is not None:
        report.title = request.title
    if request.description is not None:
        report.description = request.description
    if request.is_public is not None:
        report.is_public = request.is_public

    await db.commit()
    await db.refresh(report)

    logger.info("Report updated", report_id=str(report.id))

    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        type=report.type,
        status=report.status,
        content=report.content or {},
        summary=report.summary,
        project_id=str(report.project_id) if report.project_id else None,
        created_by=str(report.created_by),
        signal_ids=report.signal_ids or [],
        opportunity_ids=report.opportunity_ids or [],
        evidence_ids=report.evidence_ids or [],
        is_public=report.is_public,
        export_formats=report.export_formats or [],
        generation_time_ms=report.generation_time_ms,
        model_used=report.model_used,
        created_at=report.created_at.isoformat() if report.created_at else "",
        updated_at=report.updated_at.isoformat() if report.updated_at else "",
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a report.

    Args:
        report_id: Report UUID
        db: Database session
        current_user: Authenticated user
    """
    from backend.models.reports import Report

    query = select(Report).where(
        Report.id == report_id,
        Report.created_by == current_user.id
    )

    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Report not found or access denied"},
        )

    await db.delete(report)
    await db.commit()

    logger.info("Report deleted", report_id=str(report_id))


@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportGenerationResponse:
    """
    Generate a new report asynchronously.

    Args:
        request: Report generation request
        db: Database session
        current_user: Authenticated user

    Returns:
        Generation job details
    """
    import uuid

    from backend.models.reports import Report, ReportGenerationJob

    # Create report record
    title = request.title or f"Generated {request.report_type} Report"
    report = Report(
        id=uuid.uuid4(),
        title=title,
        type=request.report_type,
        created_by=current_user.id,
        status="generating",
        content={},
        signal_ids=[],
        opportunity_ids=[],
        evidence_ids=[],
    )
    db.add(report)

    # Create generation job
    job = ReportGenerationJob(
        id=uuid.uuid4(),
        report_id=report.id,
        status="pending",
        progress=0,
        filters=request.filters or {},
    )
    db.add(job)

    await db.commit()

    logger.info(
        "Report generation started",
        report_id=str(report.id),
        job_id=str(job.id),
        user_id=str(current_user.id),
    )

    # In a real implementation, this would queue a background task
    # For now, we return the job info

    return ReportGenerationResponse(
        job_id=str(job.id),
        report_id=str(report.id),
        status=job.status,
        progress=job.progress,
        created_at=job.created_at.isoformat() if job.created_at else "",
    )


@router.get("/jobs/{job_id}", response_model=ReportGenerationResponse)
async def get_generation_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportGenerationResponse:
    """
    Get the status of a report generation job.

    Args:
        job_id: Job UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        Job status details
    """
    from backend.models.reports import ReportGenerationJob

    query = select(ReportGenerationJob).where(ReportGenerationJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Job not found"},
        )

    return ReportGenerationResponse(
        job_id=str(job.id),
        report_id=str(job.report_id) if job.report_id else None,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at.isoformat() if job.created_at else "",
    )
