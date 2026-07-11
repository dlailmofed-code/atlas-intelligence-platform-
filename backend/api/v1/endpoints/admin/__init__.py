"""
ATLAS Platform - Admin API Endpoints

This module provides admin-only API endpoints for platform management.
All endpoints are protected with RBAC - only Admin and Super Admin can access.
"""

from backend.api.v1.endpoints.admin.feature_flags import router as feature_flags_router
from backend.api.v1.endpoints.admin.organizations import router as organizations_router
from backend.api.v1.endpoints.admin.plans import router as plans_router
from backend.api.v1.endpoints.admin.seats import router as seats_router
from backend.api.v1.endpoints.admin.users import router as users_router

__all__ = [
    "feature_flags_router",
    "organizations_router",
    "plans_router",
    "seats_router",
    "users_router",
]
