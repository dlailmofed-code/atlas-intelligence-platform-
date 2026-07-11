"""
ATLAS Platform - User Service

This service handles user-related business logic.
"""

from datetime import UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.core.security import hash_password, validate_password, verify_password
from backend.models import User
from backend.schemas import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize user service.

        Args:
            session: Database session
        """
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user
        """
        # Validate password
        is_valid, errors = validate_password(user_data.password)
        if not is_valid:
            raise ValueError(f"Invalid password: {', '.join(errors)}")

        # Check if email already exists
        existing = await self.get_by_email(user_data.email)
        if existing:
            raise ValueError("User with this email already exists")

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            company=user_data.company,
        )

        self.session.add(user)
        await self.session.flush()

        logger.info("User created", user_id=user.id, email=user.email)

        return user

    async def update(self, user: User, user_data: UserUpdate) -> User:
        """
        Update user.

        Args:
            user: User to update
            user_data: Update data

        Returns:
            Updated user
        """
        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.flush()

        logger.info("User updated", user_id=user.id)

        return user

    async def delete(self, user: User) -> None:
        """
        Soft delete user.

        Args:
            user: User to delete
        """
        from datetime import datetime

        user.deleted_at = datetime.now(UTC)
        await self.session.flush()

        logger.info("User deleted", user_id=user.id)

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Authenticate user by email and password.

        Args:
            email: User email
            password: Plain password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_by_email(email)

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        logger.info("User authenticated", user_id=user.id)

        return user
