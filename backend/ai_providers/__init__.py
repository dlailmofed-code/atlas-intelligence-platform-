"""
ATLAS Platform - AI Providers Module

Production AI provider layer with automatic failover, cost tracking, and observability.
"""

from backend.ai_providers.core.base import BaseProvider
from backend.ai_providers.core.registry import (
    CircuitBreaker,
    ProviderConfig,
    ProviderFactory,
    ProviderRegistry,
    get_provider_factory,
    get_provider_registry,
)
from backend.ai_providers.core.types import (
    ChatRequest,
    ChatResponse,
    FunctionDefinition,
    Message,
    ModelInfo,
    ProviderHealth,
    ProviderMetrics,
    ProviderStatus,
    ProviderType,
    PromptTemplate,
    RoutingConfig,
    StreamChunk,
    UsageStats,
)
from backend.ai_providers.observability.metrics import (
    AIObserver,
    HealthMonitor,
    MetricsCollector,
    TraceCollector,
    get_ai_observer,
)
from backend.ai_providers.providers.providers import (
    PROVIDER_CLASSES,
    create_provider,
    get_provider_class,
)
from backend.ai_providers.prompting.framework import (
    ConversationManager,
    PromptContext,
    PromptManager,
    PromptVersion,
    get_conversation_manager,
    get_prompt_manager,
)
from backend.ai_providers.response.processor import (
    ProcessedResponse,
    ResponseNormalizer,
    ResponseProcessor,
    SafetyFilter,
    get_response_processor,
)

__all__ = [
    # Core
    "BaseProvider",
    "ProviderRegistry",
    "ProviderFactory",
    "CircuitBreaker",
    "ProviderConfig",
    "get_provider_registry",
    "get_provider_factory",
    # Types
    "ProviderType",
    "ProviderStatus",
    "ModelInfo",
    "ChatRequest",
    "ChatResponse",
    "Message",
    "FunctionDefinition",
    "StreamChunk",
    "UsageStats",
    "ProviderMetrics",
    "ProviderHealth",
    "PromptTemplate",
    "PromptVersion",
    "PromptContext",
    "RoutingConfig",
    # Providers
    "PROVIDER_CLASSES",
    "create_provider",
    "get_provider_class",
    # Prompting
    "PromptManager",
    "PromptVersion",
    "ConversationManager",
    "get_prompt_manager",
    "get_conversation_manager",
    # Response
    "ResponseProcessor",
    "ProcessedResponse",
    "ResponseNormalizer",
    "SafetyFilter",
    "get_response_processor",
    # Observability
    "AIObserver",
    "MetricsCollector",
    "TraceCollector",
    "HealthMonitor",
    "get_ai_observer",
]
