"""
ATLAS Platform - Admin Feature Flags API

This module provides admin endpoints for managing feature flags.
Protected by RBAC - only Admin and Super Admin can access.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.admin.deps import get_admin_user as AdminUser
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.monetization import FeatureFlag, FeatureFlagOverride

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/feature-flags", tags=["admin-feature-flags"])


# =============================================================================
# Request/Response Models
# =============================================================================

class FeatureFlagCreate(BaseModel):
    """Request model for creating a feature flag."""

    key: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_active: bool = True
    is_rollout: bool = False
    rollout_percentage: int = Field(default=0, ge=0, le=100)
    enabled_plans: list[str] = []
    enabled_roles: list[str] = []
    enabled_regions: list[str] = []
    experiment_group: str | None = None
    is_beta: bool = False
    documentation_url: str | None = None


class FeatureFlagUpdate(BaseModel):
    """Request model for updating a feature flag."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    is_rollout: bool | None = None
    rollout_percentage: int | None = Field(None, ge=0, le=100)
    enabled_plans: list[str] | None = None
    enabled_roles: list[str] | None = None
    enabled_regions: list[str] | None = None
    experiment_group: str | None = None
    is_beta: bool | None = None
    documentation_url: str | None = None


class FeatureFlagResponse(BaseModel):
    """Response model for a feature flag."""

    id: str
    key: str
    name: str
    description: str | None
    is_active: bool
    is_rollout: bool
    rollout_percentage: int
    enabled_plans: list[str]
    enabled_roles: list[str]
    enabled_regions: list[str]
    experiment_group: str | None
    is_beta: bool
    documentation_url: str | None
    created_at: str
    updated_at: str


class OverrideCreate(BaseModel):
    """Request model for creating a user override."""

    user_id: UUID
    is_enabled: bool
    reason: str | None = None
    expires_at: datetime | None = None


class OverrideResponse(BaseModel):
    """Response model for a user override."""

    id: str
    user_id: str
    feature_flag_id: str
    is_enabled: bool
    reason: str | None
    expires_at: str | None
    created_by_id: str | None
    created_at: str


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
    include_inactive: bool = Query(default=False),
    include_beta: bool = Query(default=True),
) -> list[FeatureFlagResponse]:
    """
    List all feature flags.

    Admin only.
    """
    query = select(FeatureFlag)

    if not include_inactive:
        query = query.where(FeatureFlag.is_active)

    if not include_beta:
        query = query.where(not FeatureFlag.is_beta)

    query = query.order_by(FeatureFlag.name)

    result = await db.execute(query)
    flags = result.scalars().all()

    return [FeatureFlagResponse(
        id=str(flag.id),
        key=flag.key,
        name=flag.name,
        description=flag.description,
        is_active=flag.is_active,
        is_rollout=flag.is_rollout,
        rollout_percentage=flag.rollout_percentage,
        enabled_plans=flag.enabled_plans or [],
        enabled_roles=flag.enabled_roles or [],
        enabled_regions=flag.enabled_regions or [],
        experiment_group=flag.experiment_group,
        is_beta=flag.is_beta,
        documentation_url=flag.documentation_url,
        created_at=flag.created_at.isoformat() if flag.created_at else "",
        updated_at=flag.updated_at.isoformat() if flag.updated_at else "",
    ) for flag in flags]


@router.get("/{flag_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> FeatureFlagResponse:
    """
    Get a specific feature flag.

    Admin only.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Feature flag not found"},
        )

    return FeatureFlagResponse(
        id=str(flag.id),
        key=flag.key,
        name=flag.name,
        description=flag.description,
        is_active=flag.is_active,
        is_rollout=flag.is_rollout,
        rollout_percentage=flag.rollout_percentage,
        enabled_plans=flag.enabled_plans or [],
        enabled_roles=flag.enabled_roles or [],
        enabled_regions=flag.enabled_regions or [],
        experiment_group=flag.experiment_group,
        is_beta=flag.is_beta,
        documentation_url=flag.documentation_url,
        created_at=flag.created_at.isoformat() if flag.created_at else "",
        updated_at=flag.updated_at.isoformat() if flag.updated_at else "",
    )


@router.post("/", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> FeatureFlagResponse:
    """
    Create a new feature flag.

    Admin only.
    """
    # Check for duplicate key
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.key == flag_data.key)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Feature flag with this key already exists"},
        )

    flag = FeatureFlag(
        key=flag_data.key,
        name=flag_data.name,
        description=flag_data.description,
        is_active=flag_data.is_active,
        is_rollout=flag_data.is_rollout,
        rollout_percentage=flag_data.rollout_percentage,
        enabled_plans=flag_data.enabled_plans,
        enabled_roles=flag_data.enabled_roles,
        enabled_regions=flag_data.enabled_regions,
        experiment_group=flag_data.experiment_group,
        is_beta=flag_data.is_beta,
        documentation_url=flag_data.documentation_url,
    )

    db.add(flag)
    await db.commit()
    await db.refresh(flag)

    logger.info(
        "Feature flag created",
        flag_id=str(flag.id),
        flag_key=flag.key,
        admin_id=str(admin.id),
    )

    return FeatureFlagResponse(
        id=str(flag.id),
        key=flag.key,
        name=flag.name,
        description=flag.description,
        is_active=flag.is_active,
        is_rollout=flag.is_rollout,
        rollout_percentage=flag.rollout_percentage,
        enabled_plans=flag.enabled_plans or [],
        enabled_roles=flag.enabled_roles or [],
        enabled_regions=flag.enabled_regions or [],
        experiment_group=flag.experiment_group,
        is_beta=flag.is_beta,
        documentation_url=flag.documentation_url,
        created_at=flag.created_at.isoformat() if flag.created_at else "",
        updated_at=flag.updated_at.isoformat() if flag.updated_at else "",
    )


@router.patch("/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: UUID,
    flag_data: FeatureFlagUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> FeatureFlagResponse:
    """
    Update a feature flag.

    Admin only.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Feature flag not found"},
        )

    # Update only provided fields
    update_data = flag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flag, field, value)

    await db.commit()
    await db.refresh(flag)

    logger.info(
        "Feature flag updated",
        flag_id=str(flag.id),
        admin_id=str(admin.id),
    )

    return FeatureFlagResponse(
        id=str(flag.id),
        key=flag.key,
        name=flag.name,
        description=flag.description,
        is_active=flag.is_active,
        is_rollout=flag.is_rollout,
        rollout_percentage=flag.rollout_percentage,
        enabled_plans=flag.enabled_plans or [],
        enabled_roles=flag.enabled_roles or [],
        enabled_regions=flag.enabled_regions or [],
        experiment_group=flag.experiment_group,
        is_beta=flag.is_beta,
        documentation_url=flag.documentation_url,
        created_at=flag.created_at.isoformat() if flag.created_at else "",
        updated_at=flag.updated_at.isoformat() if flag.updated_at else "",
    )


@router.delete("/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_flag(
    flag_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> None:
    """
    Delete a feature flag.

    Admin only.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Feature flag not found"},
        )

    await db.delete(flag)
    await db.commit()

    logger.info(
        "Feature flag deleted",
        flag_id=str(flag_id),
        flag_key=flag.key,
        admin_id=str(admin.id),
    )


# =============================================================================
# Override Endpoints
# =============================================================================

@router.get("/{flag_id}/overrides", response_model=list[OverrideResponse])
async def list_overrides(
    flag_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> list[OverrideResponse]:
    """
    List all user overrides for a feature flag.

    Admin only.
    """
    result = await db.execute(
        select(FeatureFlagOverride).where(
            FeatureFlagOverride.feature_flag_id == flag_id
        )
    )
    overrides = result.scalars().all()

    return [OverrideResponse(
        id=str(override.id),
        user_id=str(override.user_id),
        feature_flag_id=str(override.feature_flag_id),
        is_enabled=override.is_enabled,
        reason=override.reason,
        expires_at=override.expires_at.isoformat() if override.expires_at else None,
        created_by_id=str(override.created_by_id) if override.created_by_id else None,
        created_at=override.created_at.isoformat() if override.created_at else "",
    ) for override in overrides]


@router.post("/{flag_id}/overrides", response_model=OverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_override(
    flag_id: UUID,
    override_data: OverrideCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> OverrideResponse:
    """
    Create a user override for a feature flag.

    Admin only.
    """
    # Verify flag exists
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Feature flag not found"},
        )

    # Check for existing override
    result = await db.execute(
        select(FeatureFlagOverride).where(
            FeatureFlagOverride.user_id == override_data.user_id,
            FeatureFlagOverride.feature_flag_id == flag_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing override
        existing.is_enabled = override_data.is_enabled
        existing.reason = override_data.reason
        existing.expires_at = override_data.expires_at
        existing.created_by_id = admin.id
        override = existing
    else:
        # Create new override
        override = FeatureFlagOverride(
            user_id=override_data.user_id,
            feature_flag_id=flag_id,
            is_enabled=override_data.is_enabled,
            reason=override_data.reason,
            expires_at=override_data.expires_at,
            created_by_id=admin.id,
        )
        db.add(override)

    await db.commit()
    await db.refresh(override)

    logger.info(
        "Feature flag override created",
        flag_id=str(flag_id),
        user_id=str(override_data.user_id),
        is_enabled=override_data.is_enabled,
        admin_id=str(admin.id),
    )

    return OverrideResponse(
        id=str(override.id),
        user_id=str(override.user_id),
        feature_flag_id=str(override.feature_flag_id),
        is_enabled=override.is_enabled,
        reason=override.reason,
        expires_at=override.expires_at.isoformat() if override.expires_at else None,
        created_by_id=str(override.created_by_id) if override.created_by_id else None,
        created_at=override.created_at.isoformat() if override.created_at else "",
    )


@router.delete("/{flag_id}/overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_override(
    flag_id: UUID,
    override_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> None:
    """
    Delete a user override for a feature flag.

    Admin only.
    """
    result = await db.execute(
        select(FeatureFlagOverride).where(
            FeatureFlagOverride.id == override_id,
            FeatureFlagOverride.feature_flag_id == flag_id,
        )
    )
    override = result.scalar_one_or_none()

    if not override:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Override not found"},
        )

    await db.delete(override)
    await db.commit()

    logger.info(
        "Feature flag override deleted",
        flag_id=str(flag_id),
        override_id=str(override_id),
        admin_id=str(admin.id),
    )
