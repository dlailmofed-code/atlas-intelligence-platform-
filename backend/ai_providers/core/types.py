"""
ATLAS Platform - AI Providers Core Types

Type definitions for the AI provider layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """AI provider types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    OPENROUTER = "openrouter"


class ModelCapability(str, Enum):
    """Model capabilities."""

    CHAT = "chat"
    COMPLETION = "completion"
    STREAMING = "streaming"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    CONTEXT_WINDOW = "context_window"
    TOOL_USE = "tool_use"


class ProviderStatus(str, Enum):
    """Provider health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


@dataclass
class ModelInfo:
    """Information about an AI model."""

    name: str
    provider: ProviderType
    display_name: str
    description: str = ""
    capabilities: list[ModelCapability] = field(default_factory=list)
    context_window: int = 0
    max_output_tokens: int = 0
    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False


@dataclass
class PromptTemplate:
    """A prompt template."""

    id: str
    name: str
    version: str
    system_template: str
    user_template: str
    description: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """A chat message."""

    role: str  # "system", "user", "assistant", "function"
    content: str
    name: str | None = None
    function_call: dict[str, Any] | None = None


@dataclass
class FunctionDefinition:
    """Definition of a callable function."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    required: list[str] = field(default_factory=list)


@dataclass
class ChatRequest:
    """Request for chat completion."""

    messages: list[Message]
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: list[str] | None = None
    stream: bool = False
    functions: list[FunctionDefinition] | None = None
    function_call: str | dict | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0


@dataclass
class ProviderMetrics:
    """Metrics for a provider."""

    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0
    rate_limit_hits: int = 0
    timeout_hits: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    consecutive_failures: int = 0
    last_request_at: datetime | None = None
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def average_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def average_cost(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests


@dataclass
class ChatResponse:
    """Response from chat completion."""

    content: str
    model: str
    provider: ProviderType
    finish_reason: str | None = None
    usage: UsageStats | None = None
    function_call: dict[str, Any] | None = None
    safety_scores: dict[str, float] | None = None
    citations: list[dict[str, Any]] | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""

    content: str
    delta: str
    index: int
    is_final: bool = False
    finish_reason: str | None = None
    function_call: dict[str, Any] | None = None


@dataclass
class CircuitBreakerState:
    """State of a circuit breaker."""

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    state: str = "closed"  # closed, open, half_open
    next_attempt_time: datetime | None = None


@dataclass
class RoutingConfig:
    """Configuration for request routing."""

    priority_providers: list[ProviderType] = field(default_factory=list)
    weights: dict[ProviderType, float] = field(default_factory=dict)
    fallback_enabled: bool = True
    circuit_breaker_enabled: bool = True
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0


@dataclass
class ProviderHealth:
    """Health status of a provider."""

    provider: ProviderType
    status: ProviderStatus
    latency_ms: float | None = None
    success_rate: float | None = None
    consecutive_failures: int = 0
    is_available: bool = True
    error_message: str | None = None
    last_checked: datetime = field(default_factory=datetime.utcnow)
