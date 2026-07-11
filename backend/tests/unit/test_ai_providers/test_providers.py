"""
Tests for AI providers.
"""


from backend.ai_providers.core.types import ProviderType
from backend.ai_providers.providers import create_provider, get_provider_class


class TestProviderFactory:
    """Tests for provider factory functions."""

    def test_get_openai_class(self):
        """Test getting OpenAI provider class."""
        provider_class = get_provider_class(ProviderType.OPENAI)
        assert provider_class is not None
        assert provider_class.__name__ == "OpenAIProvider"

    def test_get_anthropic_class(self):
        """Test getting Anthropic provider class."""
        provider_class = get_provider_class(ProviderType.ANTHROPIC)
        assert provider_class is not None
        assert provider_class.__name__ == "AnthropicProvider"

    def test_get_google_class(self):
        """Test getting Google provider class."""
        provider_class = get_provider_class(ProviderType.GOOGLE)
        assert provider_class is not None
        assert provider_class.__name__ == "GoogleProvider"

    def test_get_groq_class(self):
        """Test getting Groq provider class."""
        provider_class = get_provider_class(ProviderType.GROQ)
        assert provider_class is not None
        assert provider_class.__name__ == "GroqProvider"

    def test_get_deepseek_class(self):
        """Test getting DeepSeek provider class."""
        provider_class = get_provider_class(ProviderType.DEEPSEEK)
        assert provider_class is not None
        assert provider_class.__name__ == "DeepSeekProvider"

    def test_get_mistral_class(self):
        """Test getting Mistral provider class."""
        provider_class = get_provider_class(ProviderType.MISTRAL)
        assert provider_class is not None
        assert provider_class.__name__ == "MistralProvider"

    def test_get_openrouter_class(self):
        """Test getting OpenRouter provider class."""
        provider_class = get_provider_class(ProviderType.OPENROUTER)
        assert provider_class is not None
        assert provider_class.__name__ == "OpenRouterProvider"


class TestProviderCreation:
    """Tests for provider creation."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = create_provider(ProviderType.OPENAI, api_key="test-key")
        assert provider is not None
        assert provider.provider_name == "openai"
        assert provider.api_key == "test-key"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        provider = create_provider(ProviderType.ANTHROPIC, api_key="test-key")
        assert provider is not None
        assert provider.provider_name == "anthropic"

    def test_create_with_custom_base_url(self):
        """Test creating provider with custom base URL."""
        provider = create_provider(
            ProviderType.OPENAI,
            api_key="test-key",
            base_url="https://custom.api.com",
        )
        assert provider.base_url == "https://custom.api.com"

    def test_default_model(self):
        """Test default models."""
        openai = create_provider(ProviderType.OPENAI)
        assert openai.default_model == "gpt-4o"

        anthropic = create_provider(ProviderType.ANTHROPIC)
        assert anthropic.default_model == "claude-3-5-sonnet-20240620"

        google = create_provider(ProviderType.GOOGLE)
        assert google.default_model == "gemini-1.5-pro"

        groq = create_provider(ProviderType.GROQ)
        assert groq.default_model == "llama-3.1-70b-versatile"


class TestProviderModels:
    """Tests for provider model lists."""

    def test_openai_models(self):
        """Test OpenAI available models."""
        provider = create_provider(ProviderType.OPENAI)
        models = provider.get_available_models()

        assert len(models) > 0
        model_names = [m.name for m in models]
        assert "gpt-4o" in model_names
        assert "gpt-3.5-turbo" in model_names

    def test_anthropic_models(self):
        """Test Anthropic available models."""
        provider = create_provider(ProviderType.ANTHROPIC)
        models = provider.get_available_models()

        assert len(models) > 0
        model_names = [m.name for m in models]
        assert any("claude" in name.lower() for name in model_names)

    def test_google_models(self):
        """Test Google available models."""
        provider = create_provider(ProviderType.GOOGLE)
        models = provider.get_available_models()

        assert len(models) > 0
        model_names = [m.name for m in models]
        assert any("gemini" in name.lower() for name in model_names)


class TestProviderTypes:
    """Tests for provider type properties."""

    def test_openai_type(self):
        """Test OpenAI provider type."""
        provider = create_provider(ProviderType.OPENAI)
        assert provider.provider_type == ProviderType.OPENAI

    def test_anthropic_type(self):
        """Test Anthropic provider type."""
        provider = create_provider(ProviderType.ANTHROPIC)
        assert provider.provider_type == ProviderType.ANTHROPIC

    def test_all_provider_types(self):
        """Test all provider types."""
        for pt in ProviderType:
            provider = create_provider(pt)
            assert provider.provider_type == pt
