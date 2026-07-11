"""
ATLAS Platform - Admin Dependencies

This module provides dependency injection for admin-only endpoints.
Includes RBAC protection for Admin and Super Admin roles.
"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.common.associations import organization_members
from backend.models.users import User

logger = get_logger(__name__)


async def get_current_user_from_auth(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current user from authorization header.

    Args:
        authorization: Bearer token
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException 401: If not authenticated
    """
    from backend.core.security import decode_access_token

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")
    token_data = decode_access_token(token)

    if not token_data or not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await db.execute(
        select(User).where(User.id == token_data.sub)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_admin_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get admin user from authorization header.

    Args:
        authorization: Bearer token
        db: Database session

    Returns:
        Admin user object

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not admin
    """
    # Get current user
    user = await get_current_user_from_auth(authorization, db)

    # Superusers have all permissions
    if user.is_superuser:
        return user

    # Check if user is owner or admin in any organization
    result = await db.execute(
        select(organization_members.c.role).where(
            organization_members.c.user_id == user.id,
            organization_members.c.role.in_(["admin", "owner"]),
        )
    )
    row = result.fetchone()

    if row:
        return user

    logger.warning(
        "Non-admin user attempted to access admin endpoint",
        user_id=str(user.id),
    )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin or Super Admin permission required",
    )
