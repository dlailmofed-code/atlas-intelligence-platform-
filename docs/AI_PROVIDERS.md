# ATLAS Platform - AI Provider Layer

## Overview

The ATLAS Platform AI Provider Layer provides a unified interface for interacting with multiple AI providers, featuring automatic failover, cost tracking, observability, and production-grade reliability.

## Architecture

```
backend/ai_providers/
├── __init__.py                    # Module exports
├── core/                          # Core interfaces
│   ├── __init__.py
│   ├── base.py                   # BaseProvider interface
│   ├── registry.py               # Provider registry & factory
│   └── types.py                 # Type definitions
├── providers/                     # Provider implementations
│   ├── __init__.py
│   └── providers.py              # All provider implementations
├── prompting/                     # Prompt framework
│   ├── __init__.py
│   └── framework.py              # Prompt management
├── response/                      # Response processing
│   ├── __init__.py
│   └── processor.py              # Response normalization
└── observability/                 # Observability
    ├── __init__.py
    └── metrics.py                # Metrics & tracing
```

## Supported Providers

| Provider | Models | Capabilities |
|----------|--------|--------------|
| **OpenAI** | GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo | Chat, Streaming, Function Calling |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | Chat, Streaming |
| **Google** | Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 1.0 Pro | Chat, Streaming, Vision |
| **Groq** | Llama 3.1 70B, Llama 3.1 8B, Mixtral 8x7B | Chat, Streaming |
| **DeepSeek** | DeepSeek Chat, DeepSeek Coder | Chat, Streaming |
| **Mistral** | Mistral Large, Mistral Small | Chat, Streaming |
| **OpenRouter** | Various models via unified API | Chat, Streaming |

## Usage

### Basic Usage

```python
from backend.ai_providers import create_provider, ProviderType, ChatRequest, Message

# Create a provider
provider = create_provider(ProviderType.OPENAI, api_key="your-api-key")

# Create a chat request
request = ChatRequest(
    messages=[Message(role="user", content="Hello, how are you?")],
    model="gpt-4o",
    temperature=0.7,
)

# Make a request
response = await provider.chat(request)
print(response.content)
```

### Automatic Failover

```python
from backend.ai_providers import ProviderFactory, ProviderRegistry, ProviderConfig, ProviderType

# Set up registry with multiple providers
registry = ProviderRegistry()

# Register providers
registry.register(ProviderType.OPENAI, openai_provider, ProviderConfig(
    provider_type=ProviderType.OPENAI,
    api_key="your-openai-key",
    priority=1,
))
registry.register(ProviderType.ANTHROPIC, anthropic_provider, ProviderConfig(
    provider_type=ProviderType.ANTHROPIC,
    api_key="your-anthropic-key",
    priority=2,
))

# Create factory
factory = ProviderFactory(registry)

# Get best available provider (with automatic failover)
provider, provider_type = await factory.get_provider()
```

### Prompt Management

```python
from backend.ai_providers import get_prompt_manager, PromptContext

manager = get_prompt_manager()

# Register a template
manager.register_template(PromptTemplate(
    id="analysis",
    name="Analysis Prompt",
    version="1.0",
    system_template="You are an AI assistant specializing in {domain}.",
    user_template="Analyze the following: {content}",
    variables=["domain", "content"],
))

# Render with variables
messages = manager.render_prompt(
    "analysis",
    {"domain": "finance", "content": "Q4 earnings report"},
)

# Use in request
request = ChatRequest(messages=messages, model="gpt-4o")
```

### Response Processing

```python
from backend.ai_providers import get_response_processor

processor = get_response_processor()

# Process response
processed = processor.process(response)

print(f"Content: {processed.content}")
print(f"Confidence: {processed.confidence}")
print(f"Safety Score: {processed.safety_scores}")
print(f"Warnings: {processed.warnings}")
```

### Observability

```python
from backend.ai_providers import get_ai_observer

observer = get_ai_observer()

# Record a request
observer.record(
    provider=ProviderType.OPENAI,
    model="gpt-4o",
    latency_ms=1000,
    success=True,
    prompt_tokens=100,
    completion_tokens=50,
    cost=0.01,
)

# Get dashboard data
dashboard = observer.get_dashboard_data()
print(f"Total Requests: {dashboard['summary']['total_requests']}")
print(f"Success Rate: {dashboard['summary']['success_rate']}")
```

## Configuration

### Environment Variables

```bash
# Provider API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_GEMINI_API_KEY=your-google-gemini-key
GROQ_API_KEY=your-groq-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
MISTRAL_API_KEY=your-mistral-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# Default Settings
AI_DEFAULT_PROVIDER=openai
AI_DEFAULT_MODEL=gpt-4o

# Failover Settings
AI_ENABLE_AUTO_FAILOVER=true
AI_ENABLE_CIRCUIT_BREAKER=true
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=3
AI_CIRCUIT_BREAKER_THRESHOLD=5

# Cost Tracking
AI_ENABLE_COST_TRACKING=true
AI_COST_BUDGET_MONTHLY=100.0

# Routing
AI_PRIORITY_PROVIDERS=["openai","anthropic","google"]
```

## Circuit Breaker

The circuit breaker prevents cascading failures by temporarily disabling unhealthy providers:

- **Closed State**: Normal operation, requests pass through
- **Open State**: Provider is unhealthy, requests fail immediately
- **Half-Open State**: Testing if provider has recovered

Configuration:
```python
CircuitBreaker(
    failure_threshold=5,  # Failures before opening
    recovery_timeout=60,  # Seconds before trying again
    half_open_max_calls=3,  # Test calls in half-open state
)
```

## Cost Tracking

Track and control AI spending:

```python
# Record costs
metrics = collector.get_provider_metrics(provider_type)
print(f"Total Cost: ${metrics.total_cost}")
print(f"Prompt Tokens: {metrics.total_prompt_tokens}")
print(f"Completion Tokens: {metrics.total_completion_tokens}")

# Aggregate costs
aggregated = collector.get_aggregated_metrics()
print(f"Monthly Cost: ${aggregated.total_cost}")
```

## Testing

Run AI provider tests:

```bash
cd backend
pytest tests/unit/test_ai_providers/ -v
```

## Error Handling

The provider layer handles various error types:

- **Rate Limiting**: Automatic retry with backoff
- **Timeout**: Configurable timeout with fallback
- **Provider Errors**: Automatic failover to next provider
- **Validation Errors**: Clear error messages with context

Example error response:
```python
ChatResponse(
    content="",
    model="gpt-4o",
    provider=ProviderType.OPENAI,
    error="Rate limit exceeded",
    latency_ms=1000,
)
```

## Best Practices

1. **Use Automatic Failover**: Always configure fallback providers
2. **Set Timeouts**: Prevent hanging requests
3. **Monitor Costs**: Use cost tracking to avoid surprises
4. **Implement Retries**: Handle transient failures gracefully
5. **Use Circuit Breakers**: Prevent cascading failures
6. **Log Everything**: Use observability for debugging

## Extending Providers

To add a new provider:

1. Create a new provider class in `providers/providers.py`
2. Inherit from `BaseAIProvider`
3. Implement required methods:
   - `provider_name` - Provider identifier
   - `provider_type` - ProviderType enum
   - `default_model` - Default model name
   - `get_available_models()` - List of available models
   - `chat()` - Chat completion method

4. Register in `PROVIDER_CLASSES` dict
5. Add tests
6. Update documentation
