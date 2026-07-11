"""
ATLAS Platform - Authentication Endpoints
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    validate_password,
    verify_password,
)
from backend.db.session import get_async_session as get_db
from backend.models.users import User
from backend.schemas import RefreshTokenRequest

logger = get_logger(__name__)

router = APIRouter()


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=100)
    company: str | None = Field(default=None, max_length=200)


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Response model for user information."""

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
    created_at: str | None = None


class AuthResponse(BaseModel):
    """Combined auth response with tokens and user info."""

    tokens: TokenResponse
    user: UserResponse


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user.

    Args:
        authorization: Authorization header with Bearer token
        db: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication fails
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Missing or invalid authorization header"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")

    try:
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == token_data.sub)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "User not found"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "User account is inactive"},
            )

        return user

    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Authentication failed"},
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    Optional authentication - returns None if not authenticated.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user.

    Args:
        request: Registration request with email, password, and user details
        db: Database session

    Returns:
        Auth tokens and user information
    """
    from backend.core.config import get_settings

    settings = get_settings()

    # Validate password
    is_valid, errors = validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid password", "errors": errors},
        )

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "User with this email already exists"},
        )

    # Create user
    user = User(
        email=request.email,
        full_name=request.full_name,
        company=request.company,
        hashed_password=hash_password(request.password),
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("User registered", user_id=user.id, email=request.email)

    # Create tokens
    token_data = {
        "sub": user.id,
        "email": user.email,
        "roles": ["user"],
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes),
    )

    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=settings.security.refresh_token_expire_days),
    )

    return AuthResponse(
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60,
        ),
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            bio=user.bio,
            avatar_url=user.avatar_url,
            timezone=user.timezone or "UTC",
            language=user.language or "en",
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate user and return access token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        Auth tokens and user information
    """
    from backend.core.config import get_settings

    settings = get_settings()

    # Get user
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "User account is inactive"},
        )

    # Create tokens
    token_data = {
        "sub": user.id,
        "email": user.email,
        "roles": ["user"],
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes),
    )

    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=settings.security.refresh_token_expire_days),
    )

    logger.info("User logged in", user_id=user.id)

    return AuthResponse(
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60,
        ),
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            bio=user.bio,
            avatar_url=user.avatar_url,
            timezone=user.timezone or "UTC",
            language=user.language or "en",
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Logout current user.

    In production, this would invalidate the refresh token.
    """
    logger.info("User logged out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        New access token
    """
    from backend.core.config import get_settings

    settings = get_settings()

    try:
        token_data = decode_access_token(request.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid or expired refresh token"},
            )

        # Get user
        result = await db.execute(
            select(User).where(User.id == token_data.sub)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "User not found or inactive"},
            )

        # Create new access token
        new_token_data = {
            "sub": user.id,
            "email": user.email,
            "roles": ["user"],
        }

        access_token = create_access_token(
            data=new_token_data,
            expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes),
        )

        logger.info("Token refreshed", user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60,
        )

    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Token refresh failed"},
        )


