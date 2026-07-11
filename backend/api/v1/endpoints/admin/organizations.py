"""
ATLAS Platform - Admin Organizations API

This module provides admin endpoints for managing organizations.
Protected by RBAC - only Admin and Super Admin can access.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.admin.deps import get_admin_user as AdminUser
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models import Organization

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/organizations", tags=["admin-organizations"])


# =============================================================================
# Request/Response Models
# =============================================================================

class OrganizationResponse(BaseModel):
    """Response model for an organization."""

    id: str
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    website: str | None
    is_active: bool
    member_count: int
    created_at: str


class OrganizationListResponse(BaseModel):
    """Paginated organization list response."""

    items: list[OrganizationResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=OrganizationListResponse)
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by name or slug"),
    is_active: bool | None = Query(default=None),
) -> OrganizationListResponse:
    """
    List all organizations with pagination.

    Admin only.
    """
    from backend.models.common.associations import organization_members

    query = select(Organization)
    count_query = select(func.count()).select_from(Organization)

    # Apply filters
    if search:
        search_filter = Organization.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if is_active is not None:
        query = query.where(Organization.is_active == is_active)
        count_query = count_query.where(Organization.is_active == is_active)

    # Count total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Organization.created_at.desc())
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    organizations = result.scalars().all()

    # Get member counts
    org_responses = []
    for org in organizations:
        count_result = await db.execute(
            select(func.count()).select_from(organization_members).where(
                organization_members.c.organization_id == org.id
            )
        )
        member_count = count_result.scalar() or 0

        org_responses.append(OrganizationResponse(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            description=org.description,
            logo_url=org.logo_url,
            website=org.website,
            is_active=org.is_active,
            member_count=member_count,
            created_at=org.created_at.isoformat() if org.created_at else "",
        ))

    return OrganizationListResponse(
        items=org_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> OrganizationResponse:
    """
    Get a specific organization.

    Admin only.
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Organization not found"},
        )

    # Get member count
    from backend.models.common.associations import organization_members
    count_result = await db.execute(
        select(func.count()).select_from(organization_members).where(
            organization_members.c.organization_id == org.id
        )
    )
    member_count = count_result.scalar() or 0

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website=org.website,
        is_active=org.is_active,
        member_count=member_count,
        created_at=org.created_at.isoformat() if org.created_at else "",
    )


@router.post("/{org_id}/deactivate", response_model=OrganizationResponse)
async def deactivate_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> OrganizationResponse:
    """
    Deactivate an organization.

    Admin only.
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Organization not found"},
        )

    org.is_active = False
    await db.commit()
    await db.refresh(org)

    logger.info(
        "Organization deactivated",
        org_id=str(org.id),
        admin_id=str(admin.id),
    )

    # Get member count
    from backend.models.common.associations import organization_members
    count_result = await db.execute(
        select(func.count()).select_from(organization_members).where(
            organization_members.c.organization_id == org.id
        )
    )
    member_count = count_result.scalar() or 0

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website=org.website,
        is_active=org.is_active,
        member_count=member_count,
        created_at=org.created_at.isoformat() if org.created_at else "",
    )


@router.post("/{org_id}/activate", response_model=OrganizationResponse)
async def activate_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> OrganizationResponse:
    """
    Activate an organization.

    Admin only.
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Organization not found"},
        )

    org.is_active = True
    await db.commit()
    await db.refresh(org)

    logger.info(
        "Organization activated",
        org_id=str(org.id),
        admin_id=str(admin.id),
    )

    # Get member count
    from backend.models.common.associations import organization_members
    count_result = await db.execute(
        select(func.count()).select_from(organization_members).where(
            organization_members.c.organization_id == org.id
        )
    )
    member_count = count_result.scalar() or 0

    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website=org.website,
        is_active=org.is_active,
        member_count=member_count,
        created_at=org.created_at.isoformat() if org.created_at else "",
    )
