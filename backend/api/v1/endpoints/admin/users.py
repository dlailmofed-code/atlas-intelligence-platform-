"""
ATLAS Platform - Admin Users API

This module provides admin endpoints for managing users.
Protected by RBAC - only Admin and Super Admin can access.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.admin.deps import get_admin_user as AdminUser
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.subscriptions import Subscription
from backend.models.users import User

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


# =============================================================================
# Request/Response Models
# =============================================================================

class UserResponse(BaseModel):
    """Response model for a user."""

    id: str
    email: str
    username: str | None
    first_name: str | None
    last_name: str | None
    full_name: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: str
    last_login_at: str | None


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class UserUpdate(BaseModel):
    """Request model for updating a user."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=1, max_length=100)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    is_verified: bool | None = None


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=UserListResponse)
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by email or name"),
    is_active: bool | None = Query(default=None),
    is_verified: bool | None = Query(default=None),
) -> UserListResponse:
    """
    List all users with pagination.

    Admin only.
    """
    query = select(User)
    count_query = select(func.count()).select_from(User)

    # Apply filters
    if search:
        search_filter = User.email.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)
        count_query = count_query.where(User.is_verified == is_verified)

    # Count total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(User.created_at.desc())
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at.isoformat() if user.created_at else "",
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        ) for user in users],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> UserResponse:
    """
    Get a specific user.

    Admin only.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found"},
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> UserResponse:
    """
    Update a user.

    Admin only.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found"},
        )

    # Check for duplicate email if changing
    if user_data.email and user_data.email != user.email:
        email_result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if email_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Email already in use"},
            )

    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    logger.info(
        "User updated",
        user_id=str(user.id),
        admin_id=str(admin.id),
    )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> UserResponse:
    """
    Deactivate a user account.

    Admin only.
    """
    if str(user_id) == str(admin.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Cannot deactivate your own account"},
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found"},
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    logger.info(
        "User deactivated",
        user_id=str(user.id),
        admin_id=str(admin.id),
    )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> UserResponse:
    """
    Activate a user account.

    Admin only.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found"},
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    logger.info(
        "User activated",
        user_id=str(user.id),
        admin_id=str(admin.id),
    )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


@router.get("/{user_id}/subscription")
async def get_user_subscription(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> dict:
    """
    Get a user's subscription details.

    Admin only.
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status.in_(["active", "trialing"]),
        ).order_by(Subscription.started_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {"subscription": None}

    return {
        "subscription": {
            "id": str(subscription.id),
            "plan_id": subscription.plan_id,
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "billing_cycle": subscription.billing_cycle,
            "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        }
    }
