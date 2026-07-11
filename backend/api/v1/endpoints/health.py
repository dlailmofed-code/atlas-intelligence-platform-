"""
ATLAS Platform - Health Check Endpoint
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict:
    """
    Basic health check endpoint.

    Returns:
        Health status of the service
    """
    return {
        "status": "healthy",
        "service": "atlas-api",
    }
