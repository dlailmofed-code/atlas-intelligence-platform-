"""
ATLAS Platform - Logging Configuration Module

This module configures structured logging for the application using loguru and structlog.
Logs are output in JSON format for production and pretty-printed for development.
"""

import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any

import structlog
from loguru import logger as loguru_logger

from .config import LoggingSettings, get_settings

# Context variables for request-scoped data
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def add_contextvars_processor(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add context variables to log entries."""
    request_id = request_id_ctx.get()
    user_id = user_id_ctx.get()
    correlation_id = correlation_id_ctx.get()

    if request_id:
        event_dict["request_id"] = request_id
    if user_id:
        event_dict["user_id"] = user_id
    if correlation_id:
        event_dict["correlation_id"] = correlation_id

    return event_dict


def add_timestamp_processor(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add ISO format timestamp to log entries."""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def rename_event_key_processor(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Rename 'event' key to 'message' for standard logging."""
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict


def add_service_info_processor(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add service information to log entries."""
    try:
        settings = get_settings()
        event_dict["service"] = settings.app.name
        event_dict["version"] = settings.app.version
        event_dict["environment"] = settings.app.environment
    except Exception:
        pass
    return event_dict


def configure_logging(settings: LoggingSettings | None = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        settings: Logging settings. If None, loads from environment.
    """
    if settings is None:
        try:
            settings = get_settings().logging
        except Exception:
            # Fallback if settings not configured yet
            settings = LoggingSettings()

    # Remove default loguru handler
    loguru_logger.remove()

    # Configure loguru based on environment
    if settings.log_format == "json":
        log_format = (
            "{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        )
        colorize = False
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        colorize = True

    # Configure loguru logger
    loguru_logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.log_level.upper(),
                "format": log_format,
                "colorize": colorize,
                "backtrace": True,
                "diagnose": True,
            }
        ]
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_timestamp_processor,
        add_service_info_processor,
        add_contextvars_processor,
        rename_event_key_processor,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
        stream=sys.stdout,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary context to logs."""

    def __init__(
        self,
        request_id: str | None = None,
        user_id: str | None = None,
        correlation_id: str | None = None,
        **kwargs: Any,
    ):
        self.tokens = []
        self.context = kwargs

        if request_id is not None:
            self.tokens.append(request_id_ctx.set(request_id))
        if user_id is not None:
            self.tokens.append(user_id_ctx.set(user_id))
        if correlation_id is not None:
            self.tokens.append(correlation_id_ctx.set(correlation_id))

    def __enter__(self) -> "LogContext":
        return self

    def __exit__(self, *args: Any) -> None:
        for token in self.tokens:
            request_id_ctx.reset(token)
            user_id_ctx.reset(token)
            correlation_id_ctx.reset(token)


def setup_logging() -> None:
    """Initialize logging on application startup."""
    configure_logging()
