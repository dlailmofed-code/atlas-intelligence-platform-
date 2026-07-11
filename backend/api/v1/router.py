"""
ATLAS Platform - API v1 Router

This module contains the main API v1 router and all sub-routers.
"""

from fastapi import APIRouter

from .endpoints import (
    auth,
    health,
    intelligence,
    opportunities,
    reports,
    subscriptions,
    users,
)
from .endpoints.admin import (
    feature_flags_router,
    organizations_router,
    plans_router,
    seats_router,
    users_router,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health, tags=["Health"])
api_router.include_router(auth, prefix="/auth", tags=["Authentication"])
api_router.include_router(users, prefix="/users", tags=["Users"])
api_router.include_router(opportunities, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(intelligence, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(reports, prefix="/reports", tags=["Reports"])
api_router.include_router(subscriptions, prefix="/subscriptions", tags=["Subscriptions"])

# Admin endpoints (protected by RBAC)
api_router.include_router(plans_router)
api_router.include_router(feature_flags_router)
api_router.include_router(users_router)
api_router.include_router(organizations_router)
api_router.include_router(seats_router)
