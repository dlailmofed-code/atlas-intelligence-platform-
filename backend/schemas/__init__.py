"""
ATLAS Platform - Pydantic Schemas

This package contains Pydantic schemas for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# =============================================================================
# Base Schemas
# =============================================================================

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Base paginated response."""

    items: list
    total: int
    page: int
    page_size: int
    has_next: bool


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(max_length=100)
    company: str | None = Field(default=None, max_length=200)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: str | None = Field(default=None, max_length=100)
    company: str | None = Field(default=None, max_length=200)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    timezone: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, max_length=10)


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    bio: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"
    is_active: bool = True
    is_verified: bool = False


class UserPreferences(BaseModel):
    """User preferences schema."""

    email_notifications: bool = True
    push_notifications: bool = True
    weekly_digest: bool = True
    opportunity_alerts: bool = True
    market_updates: bool = False
    dark_mode: bool = False
    language: str = "en"


# =============================================================================
# Auth Schemas
# =============================================================================

class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    """Schema for registration request."""
    pass


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


# =============================================================================
# Opportunity Schemas
# =============================================================================

class OpportunityScore(BaseModel):
    """Opportunity scoring metrics."""

    overall: float = Field(description="Overall opportunity score (0-100)")
    demand: float = Field(description="Market demand score")
    growth: float = Field(description="Growth potential score")
    competition: float = Field(description="Competition intensity score")
    risk: float = Field(description="Risk level score")
    confidence: float = Field(description="Confidence in the analysis")


class GeographicFocus(BaseModel):
    """Geographic focus area."""

    region: str | None = None
    country: str | None = None
    city: str | None = None


class EvidenceSource(BaseModel):
    """Evidence supporting an opportunity."""

    source: str
    type: str
    date: str
    relevance: float
    summary: str


class OpportunityBase(BaseModel):
    """Base opportunity schema."""

    title: str = Field(max_length=500)
    description: str
    category: str = Field(max_length=100)
    industry: str = Field(max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)


class OpportunityCreate(OpportunityBase):
    """Schema for creating an opportunity."""

    project_id: str | None = None
    score_overall: float = 0.0
    score_demand: float = 0.0
    score_growth: float = 0.0
    score_competition: float = 0.0
    score_risk: float = 0.0
    confidence: float = 0.0


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""

    title: str | None = Field(default=None, max_length=500)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    is_bookmarked: bool | None = None


class OpportunityResponse(OpportunityBase, TimestampMixin):
    """Schema for opportunity response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None = None
    score: OpportunityScore | None = None
    evidence: list[EvidenceSource] = []
    signals: list[str] = []
    insights: list[str] = []
    key_players: list[str] = []
    estimated_market_size: str | None = None
    growth_rate: str | None = None
    is_bookmarked: bool = False
    is_analyzed: bool = False


class OpportunityListResponse(PaginatedResponse):
    """Schema for paginated opportunity list."""

    items: list[OpportunityResponse]


# =============================================================================
# Signal Schemas
# =============================================================================

class SignalSource(BaseModel):
    """Signal data source."""

    source_id: str
    source_name: str
    source_type: str
    reliability: float
    last_updated: str


class IntelligenceSignalBase(BaseModel):
    """Base intelligence signal schema."""

    type: str
    name: str
    description: str
    category: str
    intensity: float = 0.0
    trend: str = "stable"
    confidence: float = 0.0
    region: str | None = None
    industry: str | None = None


class IntelligenceSignalResponse(IntelligenceSignalBase):
    """Schema for signal response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    sources: list[SignalSource] = []
    entities: list[str] = []
    detected_at: datetime
    updated_at: datetime


# =============================================================================
# Project Schemas
# =============================================================================

class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(max_length=200)
    description: str | None = None
    is_public: bool = False


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_public: bool | None = None


class ProjectResponse(ProjectBase, TimestampMixin):
    """Schema for project response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    organization_id: str | None = None
    opportunity_count: int = 0


# =============================================================================
# API Key Schemas
# =============================================================================

class ApiKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(max_length=100)
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    key_preview: str  # Last 4 characters
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool
    created_at: datetime


# =============================================================================
# Health Schemas
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: datetime
    dependencies: dict[str, str] = {}


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str
    code: str | None = None
    errors: list[dict] | None = None
