"""
ATLAS Platform - Security Module

This module handles authentication, authorization, and cryptographic operations.
Implements JWT-based authentication with password hashing using argon2.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)

# Password hashing using argon2
ph = PasswordHasher(
    time_cost=3,      # Number of iterations
    memory_cost=65536, # 64 MB
    parallelism=4,    # Number of parallel threads
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.warning("Password verification error", error=str(e))
        return False


def hash_password(password: str) -> str:
    """
    Hash a password using argon2.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password string
    """
    return ph.hash(password)


def validate_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password against security policy.

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    settings = get_settings().security
    errors = []

    if len(password) < settings.password_min_length:
        errors.append(
            f"Password must be at least {settings.password_min_length} characters"
        )

    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if settings.password_require_lowercase and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if settings.password_require_digit and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if settings.password_require_special:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")

    return len(errors) == 0, errors


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    settings = get_settings().security

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded payload if valid, None otherwise
    """
    settings = get_settings().security

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        logger.warning("JWT decode error", error=str(e))
        return None


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    settings = get_settings().security

    to_encode = data.copy()
    to_encode["type"] = "refresh"

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT refresh token.

    Args:
        token: The JWT refresh token string to decode

    Returns:
        Decoded payload if valid and is refresh token, None otherwise
    """
    payload = decode_access_token(token)

    if payload is None:
        return None

    if payload.get("type") != "refresh":
        logger.warning("Token is not a refresh token")
        return None

    return payload


class TokenData:
    """Data class for validated token information."""

    def __init__(
        self,
        user_id: str,
        email: str | None = None,
        roles: list[str] | None = None,
        token_type: str = "access",
    ):
        self.user_id = user_id
        self.email = email
        self.roles = roles or []
        self.token_type = token_type

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Optional["TokenData"]:
        """
        Create TokenData from JWT payload.

        Args:
            payload: Decoded JWT payload

        Returns:
            TokenData instance if valid, None otherwise
        """
        user_id = payload.get("sub")
        if not user_id:
            return None

        return cls(
            user_id=user_id,
            email=payload.get("email"),
            roles=payload.get("roles", []),
            token_type=payload.get("type", "access"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "roles": self.roles,
            "token_type": self.token_type,
        }
