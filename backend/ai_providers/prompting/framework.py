"""
ATLAS Platform - Prompt Framework

Prompt templates, versioning, and context injection.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from backend.ai_providers.core.types import Message, PromptTemplate


@dataclass
class PromptContext:
    """Context for prompt injection."""

    user_id: str | None = None
    organization_id: str | None = None
    session_id: str | None = None
    conversation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptVersion:
    """Versioned prompt."""

    id: str
    template_id: str
    version: str
    system_prompt: str
    user_prompt_template: str
    variables: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptManager:
    """Manages prompt templates and versioning."""

    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}
        self._versions: dict[str, list[PromptVersion]] = {}
        self._history: list[dict[str, Any]] = []

    def register_template(
        self,
        template: PromptTemplate,
    ) -> None:
        """Register a prompt template."""
        self._templates[template.id] = template
        self._versions[template.id] = []

    def register_version(
        self,
        template_id: str,
        version: PromptVersion,
    ) -> None:
        """Register a new version of a template."""
        if template_id not in self._versions:
            self._versions[template_id] = []
        self._versions[template_id].append(version)

    def get_template(self, template_id: str) -> PromptTemplate | None:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def get_latest_version(self, template_id: str) -> PromptVersion | None:
        """Get the latest version of a template."""
        versions = self._versions.get(template_id, [])
        if not versions:
            return None
        return versions[-1]

    def get_version(self, template_id: str, version: str) -> PromptVersion | None:
        """Get a specific version of a template."""
        versions = self._versions.get(template_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None

    def render_prompt(
        self,
        template_id: str,
        variables: dict[str, Any],
        context: PromptContext | None = None,
    ) -> list[Message]:
        """Render a prompt template with variables and context."""
        version = self.get_latest_version(template_id)
        if not version:
            raise ValueError(f"Template not found: {template_id}")

        # Validate variables
        for var in version.variables:
            if var not in variables:
                raise ValueError(f"Missing required variable: {var}")

        # Substitute variables in prompts
        system_prompt = version.system_prompt
        user_prompt = version.user_prompt_template

        for var, value in variables.items():
            placeholder = f"{{{var}}}"
            system_prompt = system_prompt.replace(placeholder, str(value))
            user_prompt = user_prompt.replace(placeholder, str(value))

        # Inject context if provided
        if context:
            system_prompt = self._inject_context(system_prompt, context)

        messages = []

        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))

        if user_prompt:
            messages.append(Message(role="user", content=user_prompt))

        # Record usage
        self._history.append({
            "template_id": template_id,
            "version": version.version,
            "variables": variables,
            "timestamp": str(uuid4()),
        })

        return messages

    def _inject_context(self, prompt: str, context: PromptContext) -> str:
        """Inject context into a prompt."""
        context_parts = []

        if context.user_id:
            context_parts.append(f"User ID: {context.user_id}")
        if context.organization_id:
            context_parts.append(f"Organization ID: {context.organization_id}")
        if context.session_id:
            context_parts.append(f"Session ID: {context.session_id}")
        if context.metadata:
            context_parts.append(f"Metadata: {context.metadata}")

        if context_parts:
            context_str = "\n".join(context_parts)
            return f"{prompt}\n\n[Context]\n{context_str}"

        return prompt

    def validate_prompt(self, prompt: str) -> tuple[bool, list[str]]:
        """Validate a prompt for safety and quality."""
        issues = []

        # Check for empty prompt
        if not prompt or not prompt.strip():
            issues.append("Prompt is empty")

        # Check for excessive length
        if len(prompt) > 100000:
            issues.append("Prompt exceeds maximum length")

        # Check for potentially harmful patterns
        harmful_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard your",
        ]

        prompt_lower = prompt.lower()
        for pattern in harmful_patterns:
            if pattern in prompt_lower:
                issues.append(f"Potentially harmful pattern detected: {pattern}")

        return len(issues) == 0, issues


class ConversationManager:
    """Manages conversation history."""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._conversations: dict[str, list[Message]] = {}

    def create_conversation(self, conversation_id: str) -> None:
        """Create a new conversation."""
        self._conversations[conversation_id] = []

    def add_message(
        self,
        conversation_id: str,
        message: Message,
    ) -> None:
        """Add a message to a conversation."""
        if conversation_id not in self._conversations:
            self.create_conversation(conversation_id)

        self._conversations[conversation_id].append(message)

        # Trim history if needed
        if len(self._conversations[conversation_id]) > self.max_history:
            self._conversations[conversation_id] = self._conversations[conversation_id][-self.max_history:]

    def get_history(
        self,
        conversation_id: str,
        max_messages: int | None = None,
    ) -> list[Message]:
        """Get conversation history."""
        messages = self._conversations.get(conversation_id, [])

        if max_messages:
            return messages[-max_messages:]

        return messages

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear a conversation."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]

    def get_or_create(
        self,
        conversation_id: str | None = None,
    ) -> tuple[str, list[Message]]:
        """Get or create a conversation."""
        if conversation_id and conversation_id in self._conversations:
            return conversation_id, self._conversations[conversation_id]

        new_id = conversation_id or str(uuid4())
        self.create_conversation(new_id)
        return new_id, []


# Global instances
_prompt_manager: PromptManager | None = None
_conversation_manager: ConversationManager | None = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def get_conversation_manager() -> ConversationManager:
    """Get the global conversation manager."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
