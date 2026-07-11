"""
ATLAS Platform - Core Module

This module exports core configuration, security, and logging functionality.
"""

from .config import (
    AppSettings,
    Settings,
    get_settings,
)
from .logging import (
    LogContext,
    get_logger,
    setup_logging,
)
from .security import (
    TokenData,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    validate_password,
    verify_password,
)

__all__ = [
    "AppSettings",
    "LogContext",
    # Config
    "Settings",
    "TokenData",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    # Logging
    "get_logger",
    "get_settings",
    "hash_password",
    "setup_logging",
    "validate_password",
    # Security
    "verify_password",
]
