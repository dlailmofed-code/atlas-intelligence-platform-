"""
ATLAS Platform - Subscription Endpoints

This module provides API endpoints for subscription management.
Based on the specifications: Subscription lifecycle management.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.subscriptions import Invoice, Plan, Subscription
from backend.models.users import User
from backend.monetization import (
    SubscriptionValidationService,
    UsageService,
)

logger = get_logger(__name__)

router = APIRouter(tags=["subscriptions"])


# =============================================================================
# Request/Response Models
# =============================================================================

class PlanResponse(BaseModel):
    """Response model for a subscription plan."""

    id: str
    name: str
    slug: str
    description: str | None = None
    price_monthly: float
    price_yearly: float
    currency: str = "USD"
    is_active: bool
    is_featured: bool
    features: list[str] = []
    limits: dict = {}
    display_order: int


class SubscriptionResponse(BaseModel):
    """Response model for a subscription."""

    id: str
    plan_id: str
    plan_name: str
    status: str
    billing_cycle: str
    started_at: str
    current_period_start: str
    current_period_end: str
    trial_end: str | None = None
    cancelled_at: str | None = None
    is_active: bool


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list
    total: int
    page: int
    page_size: int
    has_next: bool


class UsageSummaryResponse(BaseModel):
    """Response model for usage summary."""

    usage_type: str
    total_usage: int
    limit: int
    remaining: int
    period_start: str
    period_end: str


class SubscriptionCreate(BaseModel):
    """Request model for creating a subscription."""

    plan_id: str
    billing_cycle: str = "monthly"
    payment_method_id: str | None = None


class SubscriptionCancel(BaseModel):
    """Request model for cancelling a subscription."""

    cancel_at_period_end: bool = True
    reason: str | None = None


class FeatureAccessResponse(BaseModel):
    """Response model for feature access check."""

    feature_key: str
    is_enabled: bool


# =============================================================================
# Dependency: Get current user
# =============================================================================

async def get_current_user(
    authorization: Annotated[str | None, ...] = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    from backend.api.v1.endpoints.auth import get_current_user as auth_get_user

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    return await auth_get_user(authorization, db)


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
) -> list[PlanResponse]:
    """
    List available subscription plans.

    Args:
        include_inactive: Include inactive plans
        db: Database session

    Returns:
        List of subscription plans
    """
    query = select(Plan)

    if not include_inactive:
        query = query.where(Plan.is_active)

    query = query.order_by(Plan.display_order)

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
    ) for plan in plans]


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionResponse:
    """
    Get current user's subscription.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        Current subscription or None for free users
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "trialing"]),
        ).order_by(Subscription.started_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        # Return free plan info
        return SubscriptionResponse(
            id="free",
            plan_id="free",
            plan_name="Free",
            status="active",
            billing_cycle="monthly",
            started_at=current_user.created_at.isoformat() if current_user.created_at else "",
            current_period_start="",
            current_period_end="",
        )

    return SubscriptionResponse(
        id=str(subscription.id),
        plan_id=subscription.plan_id,
        plan_name=subscription.plan_name,
        status=subscription.status,
        billing_cycle=subscription.billing_cycle,
        started_at=subscription.started_at.isoformat() if subscription.started_at else "",
        current_period_start=subscription.current_period_start.isoformat() if subscription.current_period_start else "",
        current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else "",
        trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
        cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
        is_active=subscription.status == "active",
    )


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionResponse:
    """
    Create a new subscription.

    Args:
        request: Subscription creation request
        db: Database session
        current_user: Authenticated user

    Returns:
        Created subscription
    """

    # Get the plan
    result = await db.execute(
        select(Plan).where(Plan.slug == request.plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Plan not found"},
        )

    if not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Plan is not available"},
        )

    # Check for existing active subscription
    existing = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "trialing"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Active subscription already exists"},
        )

    # Calculate period dates
    now = datetime.now(UTC)
    if request.billing_cycle == "yearly":
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        plan_id=plan.slug,
        plan_name=plan.name,
        status="active",
        billing_cycle=request.billing_cycle,
        started_at=now,
        current_period_start=now,
        current_period_end=period_end,
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    logger.info(
        "Subscription created",
        subscription_id=str(subscription.id),
        user_id=str(current_user.id),
        plan_id=plan.slug,
    )

    return SubscriptionResponse(
        id=str(subscription.id),
        plan_id=subscription.plan_id,
        plan_name=subscription.plan_name,
        status=subscription.status,
        billing_cycle=subscription.billing_cycle,
        started_at=subscription.started_at.isoformat() if subscription.started_at else "",
        current_period_start=subscription.current_period_start.isoformat() if subscription.current_period_start else "",
        current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else "",
    )


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    request: SubscriptionCancel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubscriptionResponse:
    """
    Cancel current subscription.

    Args:
        request: Cancellation request
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated subscription
    """

    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "trialing"]),
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "No active subscription found"},
        )

    if request.cancel_at_period_end:
        # Mark for cancellation at period end
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.now(UTC)
    else:
        # Cancel immediately
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(subscription)

    logger.info(
        "Subscription cancelled",
        subscription_id=str(subscription.id),
        user_id=str(current_user.id),
        cancel_at_period_end=request.cancel_at_period_end,
    )

    return SubscriptionResponse(
        id=str(subscription.id),
        plan_id=subscription.plan_id,
        plan_name=subscription.plan_name,
        status=subscription.status,
        billing_cycle=subscription.billing_cycle,
        started_at=subscription.started_at.isoformat() if subscription.started_at else "",
        current_period_start=subscription.current_period_start.isoformat() if subscription.current_period_start else "",
        current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else "",
        cancelled_at=subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
        is_active=False,
    )


@router.get("/usage", response_model=list[UsageSummaryResponse])
async def get_usage(
    usage_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UsageSummaryResponse]:
    """
    Get usage summary for current user.

    Args:
        usage_type: Filter by usage type
        db: Database session
        current_user: Authenticated user

    Returns:
        List of usage summaries
    """
    usage_service = UsageService(db)
    summaries = await usage_service.get_usage_summary(current_user.id, usage_type)

    # Get plan for limits
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "trialing"]),
        )
    )
    subscription = result.scalar_one_or_none()
    plan_id = subscription.plan_id if subscription else "free"

    # Get limits
    limits = usage_service.DEFAULT_LIMITS.get(plan_id, usage_service.DEFAULT_LIMITS["free"])

    response = []
    for usage_type_key, data in summaries.items():
        type_limits = limits.get(usage_type_key, {})
        monthly_limit = type_limits.get("monthly", 0)

        response.append(UsageSummaryResponse(
            usage_type=usage_type_key,
            total_usage=data["total_usage"],
            limit=monthly_limit if monthly_limit != -1 else 999999,
            remaining=max(0, (monthly_limit if monthly_limit != -1 else 999999) - data["total_usage"]),
            period_start=data["period_start"],
            period_end=data["period_end"],
        ))

    return response


@router.get("/features", response_model=list[FeatureAccessResponse])
async def check_features(
    features: str = Query(..., description="Comma-separated feature keys"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FeatureAccessResponse]:
    """
    Check access to multiple features.

    Args:
        features: Comma-separated feature keys
        db: Database session
        current_user: Authenticated user

    Returns:
        List of feature access results
    """
    validation_service = SubscriptionValidationService(db)

    feature_keys = [f.strip() for f in features.split(",")]
    results = []

    for key in feature_keys:
        is_enabled = await validation_service.check_feature_access(
            current_user.id,
            key,
        )
        results.append(FeatureAccessResponse(
            feature_key=key,
            is_enabled=is_enabled,
        ))

    return results


@router.get("/invoices", response_model=PaginatedResponse)
async def list_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    List user's invoices.

    Args:
        page: Page number
        page_size: Items per page
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of invoices
    """
    # Get user's subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        return PaginatedResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            has_next=False
        )

    # Get invoices
    query = select(Invoice).where(
        Invoice.subscription_id == subscription.id
    ).order_by(Invoice.issue_date.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    invoices = result.scalars().all()

    return PaginatedResponse(
        items=[{
            "id": str(inv.id),
            "invoice_number": inv.invoice_number,
            "total": float(inv.total),
            "currency": inv.currency,
            "status": inv.status,
            "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
        } for inv in invoices],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )
