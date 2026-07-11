"""
ATLAS Platform - User Management Endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class UserProfile(BaseModel):
    """User profile model."""

    id: str
    email: EmailStr
    full_name: str
    company: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"
    is_active: bool = True
    is_verified: bool = False
    created_at: str
    updated_at: str


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""

    full_name: str | None = Field(default=None, max_length=100)
    company: str | None = Field(default=None, max_length=200)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    timezone: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, max_length=10)


class UserPreferences(BaseModel):
    """User preferences model."""

    email_notifications: bool = True
    push_notifications: bool = True
    weekly_digest: bool = True
    opportunity_alerts: bool = True
    market_updates: bool = False
    dark_mode: bool = False
    language: str = "en"


# Mock current user
async def get_current_user_id() -> str:
    """Get current authenticated user ID."""
    return "user_1"


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> UserProfile:
    """
    Get current user's profile.

    Returns:
        Current user's profile information
    """
    return UserProfile(
        id=user_id,
        email="demo@atlas-platform.ai",
        full_name="Demo User",
        company="ATLAS Inc.",
        bio="Business intelligence enthusiast",
        timezone="UTC",
        language="en",
        is_active=True,
        is_verified=True,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


@router.patch("/me", response_model=UserProfile)
async def update_current_user(
    request: UpdateProfileRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> UserProfile:
    """
    Update current user's profile.

    Args:
        request: Profile update data

    Returns:
        Updated user profile
    """
    return UserProfile(
        id=user_id,
        email="demo@atlas-platform.ai",
        full_name=request.full_name or "Demo User",
        company=request.company,
        bio=request.bio,
        avatar_url=request.avatar_url,
        timezone=request.timezone or "UTC",
        language=request.language or "en",
        is_active=True,
        is_verified=True,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-07-10T12:00:00Z",
    )


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> UserPreferences:
    """
    Get current user's preferences.

    Returns:
        User preferences
    """
    return UserPreferences()


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> UserPreferences:
    """
    Update current user's preferences.

    Args:
        preferences: New preferences

    Returns:
        Updated preferences
    """
    return preferences


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: str) -> UserProfile:
    """
    Get user by ID.

    Args:
        user_id: User ID

    Returns:
        User profile
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
