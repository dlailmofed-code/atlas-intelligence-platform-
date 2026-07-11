"""
ATLAS Platform - AI Providers

All AI provider implementations with complete functionality.
"""

import time
from typing import Any, AsyncIterator

import httpx

from backend.ai_providers.core.base import BaseProvider, StreamingProviderMixin
from backend.ai_providers.core.types import (
    ChatRequest,
    ChatResponse,
    FunctionDefinition,
    ModelInfo,
    ProviderType,
    StreamChunk,
    UsageStats,
)


class BaseAIProvider(StreamingProviderMixin, BaseProvider):
    """Base class for AI providers."""
    
    DEFAULT_BASE_URL: str = ""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        super().__init__(api_key, base_url, timeout, max_retries)
    
    async def _post(self, endpoint: str, payload: dict, headers: dict | None = None) -> dict:
        """Make a POST request."""
        url = f"{self.base_url or self.DEFAULT_BASE_URL}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=default_headers)
            return response.json()
    
    def _parse_usage(self, usage_data: dict | None) -> UsageStats | None:
        """Parse token usage from response."""
        if not usage_data:
            return None
        return UsageStats(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
    
    def _format_messages(self, messages: list[dict]) -> list[dict]:
        """Format messages for API."""
        return [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
    
    def _calculate_cost(self, usage: UsageStats, model: str) -> float:
        """Calculate estimated cost."""
        model_info = next((m for m in self.get_available_models() if m.name == model), None)
        if not model_info:
            return 0.0
        return (
            usage.prompt_tokens * model_info.input_cost_per_token +
            usage.completion_tokens * model_info.output_cost_per_token
        )
    
    def _parse_response(self, data: dict, latency_ms: float) -> ChatResponse:
        """Parse API response."""
        return ChatResponse(
            content=data.get("content", ""),
            model=data.get("model", "unknown"),
            provider=self.provider_type,
            latency_ms=latency_ms,
        )


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider."""
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    MODELS = {
        "gpt-4o": ModelInfo(name="gpt-4o", provider=ProviderType.OPENAI, display_name="GPT-4o",
            description="Most capable model", capabilities=["chat", "streaming", "function_calling"],
            context_window=128000, input_cost_per_token=0.005, output_cost_per_token=0.015),
        "gpt-4-turbo": ModelInfo(name="gpt-4-turbo", provider=ProviderType.OPENAI, display_name="GPT-4 Turbo",
            capabilities=["chat", "streaming", "function_calling"], context_window=128000,
            input_cost_per_token=0.01, output_cost_per_token=0.03),
        "gpt-3.5-turbo": ModelInfo(name="gpt-3.5-turbo", provider=ProviderType.OPENAI, display_name="GPT-3.5 Turbo",
            capabilities=["chat", "streaming"], context_window=16385,
            input_cost_per_token=0.0005, output_cost_per_token=0.0015),
    }
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    @property
    def default_model(self) -> str:
        return "gpt-4o"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "model": request.model,
            "messages": self._format_messages([m.__dict__ for m in request.messages]),
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        try:
            data = await self._post("/chat/completions", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            usage = self._parse_usage(data.get("usage"))
            
            if usage:
                usage.estimated_cost = self._calculate_cost(usage, request.model)
            
            self._update_metrics(latency_ms, usage)
            
            choice = data["choices"][0]
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider."""
    
    DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
    
    MODELS = {
        "claude-3-5-sonnet-20240620": ModelInfo(
            name="claude-3-5-sonnet-20240620", provider=ProviderType.ANTHROPIC, display_name="Claude 3.5 Sonnet",
            capabilities=["chat", "streaming"], context_window=200000,
            input_cost_per_token=0.003, output_cost_per_token=0.015),
        "claude-3-opus-20240229": ModelInfo(
            name="claude-3-opus-20240229", provider=ProviderType.ANTHROPIC, display_name="Claude 3 Opus",
            capabilities=["chat", "streaming"], context_window=200000,
            input_cost_per_token=0.015, output_cost_per_token=0.075),
        "claude-3-haiku-20240307": ModelInfo(
            name="claude-3-haiku-20240307", provider=ProviderType.ANTHROPIC, display_name="Claude 3 Haiku",
            capabilities=["chat", "streaming"], context_window=200000,
            input_cost_per_token=0.00025, output_cost_per_token=0.00125),
    }
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    @property
    def default_model(self) -> str:
        return "claude-3-5-sonnet-20240620"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        
        messages = [m.__dict__ for m in request.messages]
        prompt = "\n\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
        }
        
        try:
            data = await self._post("/messages", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            content = data.get("content", [{}])[0].get("text", "")
            
            return ChatResponse(
                content=content,
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class GoogleProvider(BaseAIProvider):
    """Google Gemini API provider."""
    
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    MODELS = {
        "gemini-1.5-pro": ModelInfo(
            name="gemini-1.5-pro", provider=ProviderType.GOOGLE, display_name="Gemini 1.5 Pro",
            capabilities=["chat", "streaming", "vision"], context_window=2000000,
            input_cost_per_token=0.00125, output_cost_per_token=0.005),
        "gemini-1.5-flash": ModelInfo(
            name="gemini-1.5-flash", provider=ProviderType.GOOGLE, display_name="Gemini 1.5 Flash",
            capabilities=["chat", "streaming"], context_window=1000000),
        "gemini-1.0-pro": ModelInfo(
            name="gemini-1.0-pro", provider=ProviderType.GOOGLE, display_name="Gemini 1.0 Pro",
            capabilities=["chat", "streaming"], context_window=32768),
    }
    
    @property
    def provider_name(self) -> str:
        return "google"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE
    
    @property
    def default_model(self) -> str:
        return "gemini-1.5-pro"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        contents = [{"parts": [{"text": m.get("content", "")}]} for m in request.messages]
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 2048,
            }
        }
        
        url = f"{self.base_url or self.DEFAULT_BASE_URL}/models/{request.model}:generateContent?key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                data = response.json()
            
            latency_ms = (time.time() - start_time) * 1000
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            return ChatResponse(
                content=content,
                model=request.model,
                provider=self.provider_type,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class GroqProvider(BaseAIProvider):
    """Groq API provider."""
    
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
    
    MODELS = {
        "llama-3.1-70b-versatile": ModelInfo(
            name="llama-3.1-70b-versatile", provider=ProviderType.GROQ, display_name="Llama 3.1 70B",
            capabilities=["chat", "streaming"], context_window=128000),
        "llama-3.1-8b-instant": ModelInfo(
            name="llama-3.1-8b-instant", provider=ProviderType.GROQ, display_name="Llama 3.1 8B",
            capabilities=["chat", "streaming"], context_window=128000),
        "mixtral-8x7b-32768": ModelInfo(
            name="mixtral-8x7b-32768", provider=ProviderType.GROQ, display_name="Mixtral 8x7B",
            capabilities=["chat", "streaming"], context_window=32768),
    }
    
    @property
    def provider_name(self) -> str:
        return "groq"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ
    
    @property
    def default_model(self) -> str:
        return "llama-3.1-70b-versatile"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "model": request.model,
            "messages": self._format_messages([m.__dict__ for m in request.messages]),
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        try:
            data = await self._post("/chat/completions", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            usage = self._parse_usage(data.get("usage"))
            self._update_metrics(latency_ms, usage)
            
            choice = data["choices"][0]
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek API provider."""
    
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    
    MODELS = {
        "deepseek-chat": ModelInfo(
            name="deepseek-chat", provider=ProviderType.DEEPSEEK, display_name="DeepSeek Chat",
            capabilities=["chat", "streaming"], context_window=64000,
            input_cost_per_token=0.00014, output_cost_per_token=0.00028),
        "deepseek-coder": ModelInfo(
            name="deepseek-coder", provider=ProviderType.DEEPSEEK, display_name="DeepSeek Coder",
            capabilities=["chat", "streaming"], context_window=64000,
            input_cost_per_token=0.00014, output_cost_per_token=0.00028),
    }
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.DEEPSEEK
    
    @property
    def default_model(self) -> str:
        return "deepseek-chat"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "model": request.model,
            "messages": self._format_messages([m.__dict__ for m in request.messages]),
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        try:
            data = await self._post("/chat/completions", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            usage = self._parse_usage(data.get("usage"))
            self._update_metrics(latency_ms, usage)
            
            choice = data["choices"][0]
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class MistralProvider(BaseAIProvider):
    """Mistral AI API provider."""
    
    DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
    
    MODELS = {
        "mistral-large-latest": ModelInfo(
            name="mistral-large-latest", provider=ProviderType.MISTRAL, display_name="Mistral Large",
            capabilities=["chat", "streaming"], context_window=128000,
            input_cost_per_token=0.002, output_cost_per_token=0.006),
        "mistral-small-latest": ModelInfo(
            name="mistral-small-latest", provider=ProviderType.MISTRAL, display_name="Mistral Small",
            capabilities=["chat", "streaming"], context_window=32000,
            input_cost_per_token=0.0002, output_cost_per_token=0.0006),
    }
    
    @property
    def provider_name(self) -> str:
        return "mistral"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MISTRAL
    
    @property
    def default_model(self) -> str:
        return "mistral-large-latest"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "model": request.model,
            "messages": self._format_messages([m.__dict__ for m in request.messages]),
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        try:
            data = await self._post("/chat/completions", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            usage = self._parse_usage(data.get("usage"))
            self._update_metrics(latency_ms, usage)
            
            choice = data["choices"][0]
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter API provider."""
    
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    
    MODELS = {
        "anthropic/claude-3.5-sonnet": ModelInfo(
            name="anthropic/claude-3.5-sonnet", provider=ProviderType.OPENROUTER, display_name="Claude 3.5 Sonnet",
            capabilities=["chat", "streaming"], context_window=200000,
            input_cost_per_token=0.003, output_cost_per_token=0.015),
        "openai/gpt-4o": ModelInfo(
            name="openai/gpt-4o", provider=ProviderType.OPENROUTER, display_name="GPT-4o",
            capabilities=["chat", "streaming"], context_window=128000,
            input_cost_per_token=0.005, output_cost_per_token=0.015),
    }
    
    @property
    def provider_name(self) -> str:
        return "openrouter"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER
    
    @property
    def default_model(self) -> str:
        return "anthropic/claude-3.5-sonnet"
    
    def get_available_models(self) -> list[ModelInfo]:
        return list(self.MODELS.values())
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://atlas-platform.com",
            "X-Title": "ATLAS Platform",
        }
        
        payload = {
            "model": request.model,
            "messages": self._format_messages([m.__dict__ for m in request.messages]),
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        try:
            data = await self._post("/chat/completions", payload, headers)
            latency_ms = (time.time() - start_time) * 1000
            usage = self._parse_usage(data.get("usage"))
            self._update_metrics(latency_ms, usage)
            
            choice = data["choices"][0]
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", "unknown"),
                provider=self.provider_type,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_metrics(latency_ms, error=str(e))
            return ChatResponse(content="", model=request.model, provider=self.provider_type, error=str(e), latency_ms=latency_ms)


# Provider registry mapping
PROVIDER_CLASSES = {
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.ANTHROPIC: AnthropicProvider,
    ProviderType.GOOGLE: GoogleProvider,
    ProviderType.GROQ: GroqProvider,
    ProviderType.DEEPSEEK: DeepSeekProvider,
    ProviderType.MISTRAL: MistralProvider,
    ProviderType.OPENROUTER: OpenRouterProvider,
}


def get_provider_class(provider_type: ProviderType) -> type:
    """Get provider class by type."""
    return PROVIDER_CLASSES.get(provider_type, OpenAIProvider)


def create_provider(
    provider_type: ProviderType,
    api_key: str | None = None,
    base_url: str | None = None,
) -> BaseAIProvider:
    """Create a provider instance."""
    provider_class = get_provider_class(provider_type)
    return provider_class(api_key=api_key, base_url=base_url)
