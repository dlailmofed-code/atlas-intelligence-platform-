"""
ATLAS Platform - Admin Seats API

This module provides admin endpoints for managing organization seats.
Protected by RBAC - only Admin and Super Admin can access.
"""

from datetime import UTC
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.endpoints.admin.deps import get_admin_user as AdminUser
from backend.core.logging import get_logger
from backend.db.session import get_async_session as get_db
from backend.models.monetization import Seat

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/seats", tags=["admin-seats"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SeatResponse(BaseModel):
    """Response model for a seat."""

    id: str
    organization_id: str
    seat_type: str
    total_seats: int
    used_seats: int
    pending_seats: int
    available_seats: int
    period_start: str
    period_end: str


class SeatUpdate(BaseModel):
    """Request model for updating seats."""

    total_seats: int = Field(..., ge=0)


class SeatPurchase(BaseModel):
    """Request model for purchasing seats."""

    seat_type: str
    quantity: int = Field(..., ge=1)


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/organization/{org_id}", response_model=list[SeatResponse])
async def list_organization_seats(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> list[SeatResponse]:
    """
    List all seats for an organization.

    Admin only.
    """
    result = await db.execute(
        select(Seat).where(Seat.organization_id == org_id)
    )
    seats = result.scalars().all()

    return [SeatResponse(
        id=str(seat.id),
        organization_id=str(seat.organization_id),
        seat_type=seat.seat_type,
        total_seats=seat.total_seats,
        used_seats=seat.used_seats,
        pending_seats=seat.pending_seats,
        available_seats=seat.available_seats,
        period_start=seat.period_start.isoformat() if seat.period_start else "",
        period_end=seat.period_end.isoformat() if seat.period_end else "",
    ) for seat in seats]


@router.patch("/{seat_id}", response_model=SeatResponse)
async def update_seats(
    seat_id: UUID,
    seat_data: SeatUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> SeatResponse:
    """
    Update seat allocation.

    Admin only.
    """
    result = await db.execute(
        select(Seat).where(Seat.id == seat_id)
    )
    seat = result.scalar_one_or_none()

    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Seat not found"},
        )

    # Validate that we're not reducing below used seats
    if seat_data.total_seats < seat.used_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot reduce seats below currently used count",
                "used_seats": seat.used_seats,
                "requested_total": seat_data.total_seats,
            },
        )

    seat.total_seats = seat_data.total_seats
    await db.commit()
    await db.refresh(seat)

    logger.info(
        "Seats updated",
        seat_id=str(seat.id),
        new_total=seat.total_seats,
        admin_id=str(admin.id),
    )

    return SeatResponse(
        id=str(seat.id),
        organization_id=str(seat.organization_id),
        seat_type=seat.seat_type,
        total_seats=seat.total_seats,
        used_seats=seat.used_seats,
        pending_seats=seat.pending_seats,
        available_seats=seat.available_seats,
        period_start=seat.period_start.isoformat() if seat.period_start else "",
        period_end=seat.period_end.isoformat() if seat.period_end else "",
    )


@router.post("/organization/{org_id}", response_model=SeatResponse)
async def create_seats(
    org_id: UUID,
    seat_data: SeatPurchase,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> SeatResponse:
    """
    Create or update seats for an organization.

    Admin only.
    """
    from datetime import datetime, timedelta

    # Check for existing seat of this type
    result = await db.execute(
        select(Seat).where(
            Seat.organization_id == org_id,
            Seat.seat_type == seat_data.seat_type,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing seats
        existing.total_seats += seat_data.quantity
        seat = existing
    else:
        # Create new seats
        now = datetime.now(UTC)
        period_end = now + timedelta(days=30)  # Monthly billing

        seat = Seat(
            organization_id=org_id,
            seat_type=seat_data.seat_type,
            total_seats=seat_data.quantity,
            used_seats=0,
            pending_seats=0,
            period_start=now,
            period_end=period_end,
        )
        db.add(seat)

    await db.commit()
    await db.refresh(seat)

    logger.info(
        "Seats created/updated",
        seat_id=str(seat.id),
        organization_id=str(org_id),
        seat_type=seat_data.seat_type,
        quantity=seat_data.quantity,
        admin_id=str(admin.id),
    )

    return SeatResponse(
        id=str(seat.id),
        organization_id=str(seat.organization_id),
        seat_type=seat.seat_type,
        total_seats=seat.total_seats,
        used_seats=seat.used_seats,
        pending_seats=seat.pending_seats,
        available_seats=seat.available_seats,
        period_start=seat.period_start.isoformat() if seat.period_start else "",
        period_end=seat.period_end.isoformat() if seat.period_end else "",
    )


@router.delete("/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seats(
    seat_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(),
) -> None:
    """
    Delete seat allocation.

    Admin only. Will fail if there are active users.
    """
    result = await db.execute(
        select(Seat).where(Seat.id == seat_id)
    )
    seat = result.scalar_one_or_none()

    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Seat not found"},
        )

    # Check for used seats
    if seat.used_seats > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot delete seats with active users",
                "used_seats": seat.used_seats,
            },
        )

    await db.delete(seat)
    await db.commit()

    logger.info(
        "Seats deleted",
        seat_id=str(seat_id),
        admin_id=str(admin.id),
    )
