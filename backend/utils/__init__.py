"""
ATLAS Platform - Utilities Package

This package contains utility functions and helpers.
"""

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def is_valid_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
    return bool(re.match(pattern, url))


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def parse_json_safe(json_str: str) -> Any:
    """
    Safely parse JSON string.

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed JSON or None if parsing fails
    """
    import json

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime to format
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def dict_to_model(model_class: type, data: dict) -> Any:
    """
    Convert dictionary to model instance.

    Args:
        model_class: Model class
        data: Dictionary data

    Returns:
        Model instance
    """
    return model_class(**data)
