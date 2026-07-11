"""
ATLAS Platform - API Endpoints Package

This package contains all API endpoint modules.
"""

from .auth import router as auth
from .health import router as health
from .intelligence import router as intelligence
from .opportunities import router as opportunities
from .reports import router as reports
from .subscriptions import router as subscriptions
from .users import router as users

__all__ = [
    "auth",
    "health",
    "intelligence",
    "opportunities",
    "reports",
    "subscriptions",
    "users",
]
