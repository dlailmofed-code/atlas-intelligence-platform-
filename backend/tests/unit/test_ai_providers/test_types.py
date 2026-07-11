"""
Tests for AI provider types.
"""

import pytest

from backend.ai_providers.core.types import (
    ChatRequest,
    ChatResponse,
    FunctionDefinition,
    Message,
    ModelCapability,
    ModelInfo,
    ProviderMetrics,
    ProviderStatus,
    ProviderType,
    UsageStats,
)


class TestProviderType:
    """Tests for ProviderType enum."""
    
    def test_all_types(self):
        """Test all provider type values."""
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.GOOGLE.value == "google"
        assert ProviderType.GROQ.value == "groq"
        assert ProviderType.DEEPSEEK.value == "deepseek"
        assert ProviderType.MISTRAL.value == "mistral"
        assert ProviderType.OPENROUTER.value == "openrouter"


class TestProviderStatus:
    """Tests for ProviderStatus enum."""
    
    def test_all_statuses(self):
        """Test all status values."""
        assert ProviderStatus.HEALTHY.value == "healthy"
        assert ProviderStatus.DEGRADED.value == "degraded"
        assert ProviderStatus.UNHEALTHY.value == "unhealthy"
        assert ProviderStatus.UNKNOWN.value == "unknown"
        assert ProviderStatus.DISABLED.value == "disabled"


class TestMessage:
    """Tests for Message dataclass."""
    
    def test_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
        assert msg.function_call is None
    
    def test_with_function(self):
        """Test message with function call."""
        msg = Message(
            role="assistant",
            content="",
            function_call={"name": "test", "arguments": "{}"},
        )
        
        assert msg.function_call is not None
        assert msg.function_call["name"] == "test"


class TestChatRequest:
    """Tests for ChatRequest dataclass."""
    
    def test_creation(self):
        """Test request creation."""
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")],
            model="gpt-4",
        )
        
        assert len(request.messages) == 1
        assert request.model == "gpt-4"
        assert request.temperature == 0.7
        assert request.stream is False
    
    def test_with_functions(self):
        """Test request with functions."""
        func = FunctionDefinition(
            name="get_weather",
            description="Get weather",
            parameters={"type": "object", "properties": {}},
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Weather?")],
            model="gpt-4",
            functions=[func],
        )
        
        assert len(request.functions) == 1
        assert request.functions[0].name == "get_weather"


class TestChatResponse:
    """Tests for ChatResponse dataclass."""
    
    def test_creation(self):
        """Test response creation."""
        response = ChatResponse(
            content="Hello!",
            model="gpt-4",
            provider=ProviderType.OPENAI,
        )
        
        assert response.content == "Hello!"
        assert response.model == "gpt-4"
        assert response.provider == ProviderType.OPENAI
        assert response.error is None
    
    def test_with_error(self):
        """Test error response."""
        response = ChatResponse(
            content="",
            model="gpt-4",
            provider=ProviderType.OPENAI,
            error="Rate limit exceeded",
        )
        
        assert response.error == "Rate limit exceeded"


class TestUsageStats:
    """Tests for UsageStats dataclass."""
    
    def test_creation(self):
        """Test usage stats creation."""
        usage = UsageStats(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.01,
        )
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150


class TestModelInfo:
    """Tests for ModelInfo dataclass."""
    
    def test_creation(self):
        """Test model info creation."""
        model = ModelInfo(
            name="gpt-4",
            provider=ProviderType.OPENAI,
            display_name="GPT-4",
            description="Most capable model",
            capabilities=[ModelCapability.CHAT, ModelCapability.STREAMING],
            context_window=8192,
        )
        
        assert model.name == "gpt-4"
        assert model.provider == ProviderType.OPENAI
        assert model.context_window == 8192
        assert ModelCapability.CHAT in model.capabilities


class TestProviderMetrics:
    """Tests for ProviderMetrics dataclass."""
    
    def test_creation(self):
        """Test metrics creation."""
        metrics = ProviderMetrics(provider_name="openai")
        
        assert metrics.provider_name == "openai"
        assert metrics.total_requests == 0
        assert metrics.success_rate == 0.0
    
    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = ProviderMetrics(provider_name="test")
        metrics.total_requests = 10
        metrics.successful_requests = 8
        metrics.failed_requests = 2
        
        assert metrics.success_rate == 0.8
    
    def test_average_latency(self):
        """Test average latency calculation."""
        metrics = ProviderMetrics(provider_name="test")
        metrics.successful_requests = 5
        metrics.total_latency_ms = 500.0
        
        assert metrics.average_latency_ms == 100.0


class TestFunctionDefinition:
    """Tests for FunctionDefinition dataclass."""
    
    def test_creation(self):
        """Test function definition creation."""
        func = FunctionDefinition(
            name="get_weather",
            description="Get weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"],
            },
            required=["location"],
        )
        
        assert func.name == "get_weather"
        assert func.description == "Get weather for a location"
        assert "location" in func.required
