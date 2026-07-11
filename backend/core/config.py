"""
ATLAS Platform - Core Configuration Module

This module handles all configuration management using Pydantic Settings.
Configuration is loaded from environment variables with validation.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="atlas", description="Database name")
    user: str = Field(default="atlas", description="Database user")
    password: str = Field(default="", description="Database password")

    url: str | None = Field(default=None, description="Full database URL")
    url_sync: str | None = Field(default=None, description="Synchronous database URL")

    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max pool overflow")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        case_sensitive=False,
        extra="ignore"
    )

    def get_url(self) -> str:
        """Get the async database URL."""
        if self.url:
            return self.url
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def get_url_sync(self) -> str:
        """Get the sync database URL."""
        if self.url_sync:
            return self.url_sync
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis cache configuration settings."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")

    url: str | None = Field(default=None, description="Full Redis URL")

    ssl: bool = Field(default=False, description="Use SSL connection")
    decode_responses: bool = Field(default=True, description="Decode responses")

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        case_sensitive=False,
        extra="ignore"
    )

    def get_url(self) -> str:
        """Get the Redis URL."""
        if self.url:
            return self.url
        auth = f":{self.password}@" if self.password else ""
        ssl = "ssl=" if self.ssl else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}?{ssl}ssl_cert_reqs=none"


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""

    secret_key: str = Field(default="", description="JWT signing secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration")

    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase")
    password_require_digit: bool = Field(default=True, description="Require digit")
    password_require_special: bool = Field(default=False, description="Require special character")

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore"
    )


class AIProviderSettings(BaseSettings):
    """AI provider configuration settings."""

    # OpenAI
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_organization: str | None = Field(default=None, description="OpenAI organization")
    openai_project: str | None = Field(default=None, description="OpenAI project")
    openai_max_retries: int = Field(default=3, description="Max retries for OpenAI")

    # Google Gemini
    google_gemini_key: str | None = Field(default=None, description="Google Gemini API key")
    google_gemini_model: str = Field(default="gemini-pro", description="Gemini model")

    # Anthropic
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-opus-20240229", description="Anthropic model")

    # DeepSeek
    deepseek_api_key: str | None = Field(default=None, description="DeepSeek API key")

    # Mistral
    mistral_api_key: str | None = Field(default=None, description="Mistral API key")

    # OpenRouter
    openrouter_api_key: str | None = Field(default=None, description="OpenRouter API key")

    # Groq
    groq_api_key: str | None = Field(default=None, description="Groq API key")

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )


class AppSettings(BaseSettings):
    """Main application settings."""

    name: str = Field(default="ATLAS Platform", description="Application name")
    version: str = Field(default="1.0.1", description="Application version")
    description: str = Field(default="AI-Powered Business Intelligence Operating System")

    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")

    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], description="CORS origins")

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


class ExternalServiceSettings(BaseSettings):
    """External service API keys configuration."""

    # Search Services
    search_engine_api_key: str | None = Field(default=None)
    search_trends_api_key: str | None = Field(default=None)
    keyword_intelligence_api_key: str | None = Field(default=None)

    # News Services
    global_news_api_key: str | None = Field(default=None)
    financial_news_api_key: str | None = Field(default=None)
    technology_news_api_key: str | None = Field(default=None)
    business_news_api_key: str | None = Field(default=None)
    regional_news_api_key: str | None = Field(default=None)
    open_news_api_key: str | None = Field(default=None)

    # Financial Data
    stock_markets_api_key: str | None = Field(default=None)
    crypto_markets_api_key: str | None = Field(default=None)
    economic_indicators_api_key: str | None = Field(default=None)

    # Government & Legal
    government_contracts_api_key: str | None = Field(default=None)
    patents_api_key: str | None = Field(default=None)
    legal_cases_api_key: str | None = Field(default=None)

    # Academic & Research
    academic_search_api_key: str | None = Field(default=None)
    research_papers_api_key: str | None = Field(default=None)

    # Social Media
    twitter_api_key: str | None = Field(default=None)
    twitter_api_secret: str | None = Field(default=None)
    linkedin_api_key: str | None = Field(default=None)
    reddit_api_key: str | None = Field(default=None)

    # Company Data
    company_data_api_key: str | None = Field(default=None)
    business_registrations_api_key: str | None = Field(default=None)
    reviews_api_key: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )


class PaymentSettings(BaseSettings):
    """Payment service configuration."""

    # Provider settings
    default_provider: str = Field(default="stripe", description="Default payment provider")

    # Stripe
    stripe_secret_key: str | None = Field(default=None)
    stripe_publishable_key: str | None = Field(default=None)
    stripe_webhook_secret: str | None = Field(default=None)

    stripe_price_id_free: str | None = Field(default=None)
    stripe_price_id_starter: str | None = Field(default=None)
    stripe_price_id_pro: str | None = Field(default=None)
    stripe_price_id_enterprise: str | None = Field(default=None)

    # PayPal (for future)
    paypal_client_id: str | None = Field(default=None)
    paypal_client_secret: str | None = Field(default=None)
    paypal_webhook_id: str | None = Field(default=None)

    # Paddle (for future)
    paddle_vendor_id: str | None = Field(default=None)
    paddle_vendor_auth_code: str | None = Field(default=None)
    paddle_webhook_secret: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="STRIPE_",
        case_sensitive=False,
        extra="ignore"
    )


class EmailSettings(BaseSettings):
    """Email service configuration."""

    sendgrid_api_key: str | None = Field(default=None)
    sendgrid_from_email: str = Field(default="noreply@atlas-platform.ai")
    sendgrid_from_name: str = Field(default="ATLAS Platform")

    model_config = SettingsConfigDict(
        env_prefix="SENDGRID_",
        case_sensitive=False,
        extra="ignore"
    )


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json/text)")
    log_output: str = Field(default="stdout", description="Log output (stdout/file)")

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore"
    )


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""

    sentry_dsn: str | None = Field(default=None, description="Sentry DSN")
    sentry_environment: str = Field(default="development")
    sentry_traces_sample_rate: float = Field(default=1.0)

    datadog_api_key: str | None = Field(default=None)
    datadog_app_key: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )


class CacheSettings(BaseSettings):
    """Cache TTL configuration."""

    ttl_short: int = Field(default=300, description="Short cache TTL (5 min)")
    ttl_medium: int = Field(default=3600, description="Medium cache TTL (1 hour)")
    ttl_long: int = Field(default=86400, description="Long cache TTL (24 hours)")
    ttl_intelligence: int = Field(default=7200, description="Intelligence cache TTL (2 hours)")

    model_config = SettingsConfigDict(
        env_prefix="CACHE_TTL_",
        case_sensitive=False,
        extra="ignore"
    )


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""

    per_minute: int = Field(default=60, description="Requests per minute")
    per_hour: int = Field(default=1000, description="Requests per hour")

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT_",
        case_sensitive=False,
        extra="ignore"
    )


class Settings(BaseSettings):
    """Main settings class that aggregates all configuration."""

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ai_provider: AIProviderSettings = Field(default_factory=AIProviderSettings)
    external_services: ExternalServiceSettings = Field(default_factory=ExternalServiceSettings)
    payment: PaymentSettings = Field(default_factory=PaymentSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function is cached to ensure settings are only loaded once.
    Use dependency injection to get settings in route handlers.
    """
    return Settings()
