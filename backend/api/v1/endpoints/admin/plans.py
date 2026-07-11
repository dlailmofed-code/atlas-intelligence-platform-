"""
ATLAS Platform - Admin Plans API

This module provides admin endpoints for managing subscription plans.
Protected by RBAC - only Admin and Super Admin can access.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.admin.deps import get_admin_user as AdminUser
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.subscriptions import Plan

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/plans", tags=["admin-plans"])


# =============================================================================
# Request/Response Models
# =============================================================================

class PlanCreate(BaseModel):
    """Request model for creating a plan."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    price_monthly: float = Field(..., ge=0)
    price_yearly: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = True
    is_featured: bool = False
    features: list[str] = []
    limits: dict = {}
    display_order: int = 0


class PlanUpdate(BaseModel):
    """Request model for updating a plan."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    price_monthly: float | None = Field(None, ge=0)
    price_yearly: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=3)
    is_active: bool | None = None
    is_featured: bool | None = None
    features: list[str] | None = None
    limits: dict | None = None
    display_order: int | None = None


class PlanResponse(BaseModel):
    """Response model for a plan."""

    id: str
    name: str
    slug: str
    description: str | None
    price_monthly: float
    price_yearly: float
    currency: str
    is_active: bool
    is_featured: bool
    features: list[str]
    limits: dict
    display_order: int
    created_at: str
    updated_at: str


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=list[PlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
    include_inactive: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[PlanResponse]:
    """
    List all subscription plans.

    Admin only.
    """
    query = select(Plan)

    if not include_inactive:
        query = query.where(Plan.is_active)

    query = query.order_by(Plan.display_order, Plan.name)

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    plans = result.scalars().all()

    return [PlanResponse(
        id=str(plan.id),
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        price_monthly=float(plan.price_monthly),
        price_yearly=float(plan.price_yearly),
        currency=plan.currency,
        is_active=plan.is_active,
        is_featured=plan.is_featured,
        features=plan.features or [],
        limits=plan.limits or {},
        display_order=plan.display_order,
        created_at=plan.created_at.isoformat() if plan.created_at else "",
        updated_at=plan.updated_at.isoformat() if plan.updated_at else "",
    ) for plan in plans]


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> PlanResponse:
    """
    Get a specific subscription plan.

    Admin only.
    """
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Plan not found"},
        )

    return PlanResponse(
        id=str(plan.id),
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        price_monthly=float(plan.price_monthly),
        price_yearly=float(plan.price_yearly),
        currency=plan.currency,
        is_active=plan.is_active,
        is_featured=plan.is_featured,
        features=plan.features or [],
        limits=plan.limits or {},
        display_order=plan.display_order,
        created_at=plan.created_at.isoformat() if plan.created_at else "",
        updated_at=plan.updated_at.isoformat() if plan.updated_at else "",
    )


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> PlanResponse:
    """
    Create a new subscription plan.

    Admin only.
    """
    # Check for duplicate slug
    result = await db.execute(
        select(Plan).where(Plan.slug == plan_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Plan with this slug already exists"},
        )

    plan = Plan(
        name=plan_data.name,
        slug=plan_data.slug,
        description=plan_data.description,
        price_monthly=plan_data.price_monthly,
        price_yearly=plan_data.price_yearly,
        currency=plan_data.currency,
        is_active=plan_data.is_active,
        is_featured=plan_data.is_featured,
        features=plan_data.features,
        limits=plan_data.limits,
        display_order=plan_data.display_order,
    )

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    logger.info(
        "Plan created",
        plan_id=str(plan.id),
        plan_slug=plan.slug,
        admin_id=str(admin.id),
    )

    return PlanResponse(
        id=str(plan.id),
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        price_monthly=float(plan.price_monthly),
        price_yearly=float(plan.price_yearly),
        currency=plan.currency,
        is_active=plan.is_active,
        is_featured=plan.is_featured,
        features=plan.features or [],
        limits=plan.limits or {},
        display_order=plan.display_order,
        created_at=plan.created_at.isoformat() if plan.created_at else "",
        updated_at=plan.updated_at.isoformat() if plan.updated_at else "",
    )


@router.patch("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: UUID,
    plan_data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> PlanResponse:
    """
    Update a subscription plan.

    Admin only.
    """
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Plan not found"},
        )

    # Update only provided fields
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)

    logger.info(
        "Plan updated",
        plan_id=str(plan.id),
        admin_id=str(admin.id),
    )

    return PlanResponse(
        id=str(plan.id),
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        price_monthly=float(plan.price_monthly),
        price_yearly=float(plan.price_yearly),
        currency=plan.currency,
        is_active=plan.is_active,
        is_featured=plan.is_featured,
        features=plan.features or [],
        limits=plan.limits or {},
        display_order=plan.display_order,
        created_at=plan.created_at.isoformat() if plan.created_at else "",
        updated_at=plan.updated_at.isoformat() if plan.updated_at else "",
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> None:
    """
    Delete a subscription plan.

    Admin only. This will fail if the plan has active subscriptions.
    """
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Plan not found"},
        )

    # Check for active subscriptions
    from backend.models.subscriptions import Subscription
    sub_result = await db.execute(
        select(func.count()).select_from(Subscription).where(
            Subscription.plan_id == plan.slug,
            Subscription.status.in_(["active", "trialing"]),
        )
    )
    active_count = sub_result.scalar()

    if active_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot delete plan with active subscriptions",
                "active_subscriptions": active_count,
            },
        )

    await db.delete(plan)
    await db.commit()

    logger.info(
        "Plan deleted",
        plan_id=str(plan_id),
        plan_slug=plan.slug,
        admin_id=str(admin.id),
    )
