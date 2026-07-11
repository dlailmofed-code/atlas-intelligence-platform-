"""
ATLAS Platform - AI Provider Base Interface

Base interface for all AI providers.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from backend.ai_providers.core.types import (
    ChatRequest,
    ChatResponse,
    FunctionDefinition,
    ModelInfo,
    ProviderMetrics,
    ProviderType,
    StreamChunk,
    UsageStats,
)


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    
    All provider implementations must inherit from this class
    and implement the required methods.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._metrics = ProviderMetrics(provider_name=self.provider_name)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type enum."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model identifier."""
        pass

    @abstractmethod
    def get_available_models(self) -> list[ModelInfo]:
        """Return list of available models."""
        pass

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Execute a chat completion request.
        
        Args:
            request: ChatRequest with messages and options
            
        Returns:
            ChatResponse with content and metadata
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:
        """
        Execute a streaming chat completion request.
        
        Args:
            request: ChatRequest with messages and options
            
        Yields:
            StreamChunk for each response delta
        """
        pass

    async def chat_with_retry(
        self,
        request: ChatRequest,
        retry_count: int = 0,
    ) -> ChatResponse:
        """
        Execute chat with automatic retry.
        
        Args:
            request: ChatRequest with messages and options
            retry_count: Current retry attempt (for internal use)
            
        Returns:
            ChatResponse with content and metadata
        """
        try:
            return await self.chat(request)
        except Exception as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.chat_with_retry(request, retry_count + 1)
            return ChatResponse(
                content="",
                model=request.model,
                provider=self.provider_type,
                error=str(e),
            )

    async def health_check(self) -> bool:
        """
        Check if the provider is healthy.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            test_request = ChatRequest(
                messages=[{"role": "user", "content": "test"}],
                model=self.default_model,
                max_tokens=5,
            )
            response = await asyncio.wait_for(
                self.chat(test_request),
                timeout=self.timeout,
            )
            return response.error is None
        except Exception:
            return False

    def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics."""
        return self._metrics

    def reset_metrics(self) -> None:
        """Reset provider metrics."""
        self._metrics = ProviderMetrics(provider_name=self.provider_name)

    def _update_metrics(
        self,
        latency_ms: float,
        usage: UsageStats | None = None,
        error: str | None = None,
        is_rate_limit: bool = False,
    ) -> None:
        """Update internal metrics."""
        self._metrics.total_requests += 1
        self._metrics.total_latency_ms += latency_ms
        self._metrics.min_latency_ms = min(self._metrics.min_latency_ms, latency_ms)
        self._metrics.max_latency_ms = max(self._metrics.max_latency_ms, latency_ms)

        if error:
            self._metrics.failed_requests += 1
            self._metrics.consecutive_failures += 1
        else:
            self._metrics.successful_requests += 1
            self._metrics.consecutive_failures = 0

        if is_rate_limit:
            self._metrics.rate_limit_hits += 1

        if usage:
            self._metrics.total_prompt_tokens += usage.prompt_tokens
            self._metrics.total_completion_tokens += usage.completion_tokens
            self._metrics.total_cost += usage.estimated_cost

    @abstractmethod
    def _format_messages(self, messages: list[dict]) -> list[dict]:
        """Format messages for provider-specific API."""
        pass

    @abstractmethod
    def _parse_response(self, raw_response: Any) -> ChatResponse:
        """Parse raw API response to ChatResponse."""
        pass

    @abstractmethod
    def _calculate_cost(self, usage: UsageStats, model: str) -> float:
        """Calculate estimated cost based on token usage."""
        pass


class StreamingProviderMixin:
    """Mixin for providers that support streaming."""

    async def chat_stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:
        """
        Default streaming implementation that wraps non-streaming.
        Override for true streaming support.
        """
        response = await self.chat(request)
        yield StreamChunk(
            content=response.content,
            delta=response.content,
            index=0,
            is_final=True,
            finish_reason=response.finish_reason,
        )


class FunctionCallingProviderMixin:
    """Mixin for providers that support function calling."""

    def supports_function_calling(self) -> bool:
        """Check if provider supports function calling."""
        return True

    @abstractmethod
    async def chat_with_functions(
        self,
        request: ChatRequest,
        functions: list[FunctionDefinition],
    ) -> ChatResponse:
        """Execute chat with function calling support."""
        pass
