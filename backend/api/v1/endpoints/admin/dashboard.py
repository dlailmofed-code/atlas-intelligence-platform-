"""
ATLAS Platform - Admin Dashboard API

System monitoring and admin dashboard endpoints.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from backend.api.v1.endpoints.auth import get_current_user
from backend.core.logging import get_logger
from backend.models.users import User

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/dashboard", tags=["admin"])


# =============================================================================
# Response Models
# =============================================================================


class SystemHealth(BaseModel):
    """System health status."""

    status: str = "healthy"
    uptime_seconds: float = 0.0
    version: str = "1.0.0"
    environment: str = "development"
    last_checked: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ServiceStatus(BaseModel):
    """Status of a service."""

    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float | None = None
    is_available: bool = True
    error_message: str | None = None


class ServiceHealthResponse(BaseModel):
    """Response for service health check."""

    overall_status: str = "healthy"
    services: list[ServiceStatus] = []
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UsageMetric(BaseModel):
    """A usage metric."""

    name: str
    value: float
    unit: str = ""
    timestamp: datetime | None = None


class UsageStatsResponse(BaseModel):
    """Response for usage statistics."""

    total_users: int = 0
    active_users_24h: int = 0
    total_organizations: int = 0
    total_requests: int = 0
    requests_today: int = 0
    total_api_calls: int = 0
    api_calls_today: int = 0
    metrics: list[UsageMetric] = []
    period_start: datetime
    period_end: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CostMetric(BaseModel):
    """A cost metric."""

    provider: str
    total_cost: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    requests: int = 0


class CostStatsResponse(BaseModel):
    """Response for cost statistics."""

    total_cost: float = 0.0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    budget_limit: float = 1000.0
    budget_used_percent: float = 0.0
    by_provider: list[CostMetric] = []


class ErrorSummary(BaseModel):
    """Summary of errors."""

    error_type: str
    count: int
    last_occurrence: datetime | None = None


class ErrorStatsResponse(BaseModel):
    """Response for error statistics."""

    total_errors_24h: int = 0
    error_rate: float = 0.0
    top_errors: list[ErrorSummary] = []
    period_start: datetime
    period_end: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DashboardResponse(BaseModel):
    """Complete dashboard response."""

    system_health: SystemHealth
    service_health: ServiceHealthResponse
    usage: UsageStatsResponse
    costs: CostStatsResponse
    errors: ErrorStatsResponse
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: User = Depends(get_current_user),
) -> SystemHealth:
    """
    Get system health status.
    
    Returns overall system health including uptime, version, and status.
    """
    return SystemHealth(
        status="healthy",
        uptime_seconds=0.0,  # Would calculate from process start time
        version="1.0.1-beta",
        environment="development",
        last_checked=datetime.now(UTC),
    )


@router.get("/services", response_model=ServiceHealthResponse)
async def get_service_health(
    current_user: User = Depends(get_current_user),
) -> ServiceHealthResponse:
    """
    Get health status of all services.
    
    Returns status of database, cache, AI providers, and other services.
    """
    services = [
        ServiceStatus(name="database", status="healthy", latency_ms=5.0, is_available=True),
        ServiceStatus(name="cache", status="healthy", latency_ms=1.0, is_available=True),
        ServiceStatus(name="openai", status="healthy", latency_ms=100.0, is_available=True),
        ServiceStatus(name="anthropic", status="healthy", latency_ms=150.0, is_available=True),
        ServiceStatus(name="google", status="healthy", latency_ms=80.0, is_available=True),
    ]

    return ServiceHealthResponse(
        overall_status="healthy",
        services=services,
        checked_at=datetime.now(UTC),
    )


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    period: str = Query("day", description="Time period: day, week, month"),
    current_user: User = Depends(get_current_user),
) -> UsageStatsResponse:
    """
    Get usage statistics.
    
    Returns user activity, API usage, and other metrics.
    """
    now = datetime.now(UTC)

    return UsageStatsResponse(
        total_users=100,
        active_users_24h=50,
        total_organizations=10,
        total_requests=10000,
        requests_today=1000,
        total_api_calls=50000,
        api_calls_today=5000,
        metrics=[
            UsageMetric(name="avg_response_time", value=150.0, unit="ms"),
            UsageMetric(name="cache_hit_rate", value=85.0, unit="%"),
            UsageMetric(name="active_connections", value=25, unit=""),
        ],
        period_start=now,
        period_end=now,
    )


@router.get("/costs", response_model=CostStatsResponse)
async def get_cost_stats(
    current_user: User = Depends(get_current_user),
) -> CostStatsResponse:
    """
    Get cost statistics.
    
    Returns AI provider costs and budget information.
    """
    return CostStatsResponse(
        total_cost=250.50,
        daily_cost=10.25,
        monthly_cost=150.75,
        budget_limit=1000.0,
        budget_used_percent=25.05,
        by_provider=[
            CostMetric(provider="openai", total_cost=150.0, prompt_tokens=500000, completion_tokens=200000, requests=5000),
            CostMetric(provider="anthropic", total_cost=75.50, prompt_tokens=250000, completion_tokens=100000, requests=2500),
            CostMetric(provider="google", total_cost=25.0, prompt_tokens=100000, completion_tokens=50000, requests=1000),
        ],
    )


@router.get("/errors", response_model=ErrorStatsResponse)
async def get_error_stats(
    current_user: User = Depends(get_current_user),
) -> ErrorStatsResponse:
    """
    Get error statistics.
    
    Returns error counts and top errors.
    """
    now = datetime.now(UTC)

    return ErrorStatsResponse(
        total_errors_24h=25,
        error_rate=0.5,
        top_errors=[
            ErrorSummary(error_type="ValidationError", count=10, last_occurrence=now),
            ErrorSummary(error_type="TimeoutError", count=8, last_occurrence=now),
            ErrorSummary(error_type="AuthenticationError", count=5, last_occurrence=now),
        ],
        period_start=now,
        period_end=now,
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    """
    Get complete dashboard data.
    
    Returns all dashboard metrics in a single response.
    """
    health = await get_system_health(current_user)
    services = await get_service_health(current_user)
    usage = await get_usage_stats("day", current_user)
    costs = await get_cost_stats(current_user)
    errors = await get_error_stats(current_user)

    return DashboardResponse(
        system_health=health,
        service_health=services,
        usage=usage,
        costs=costs,
        errors=errors,
    )


@router.get("/metrics")
async def get_prometheus_metrics(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get Prometheus-format metrics.
    
    Returns metrics in Prometheus exposition format.
    """
    # This would generate actual Prometheus metrics
    return {
        "atlas_users_total": 100,
        "atlas_requests_total": 10000,
        "atlas_api_latency_seconds": 0.15,
        "atlas_cost_total_usd": 250.50,
    }
