# =============================================================================
# ATLAS Platform - Multi-stage Dockerfile
# =============================================================================
# This Dockerfile supports multiple build targets:
# - api: Main FastAPI application
# - worker: Background task worker
# - migrate: Database migration runner

# -----------------------------------------------------------------------------
# Base Stage - Common dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# Builder Stage - Install dependencies
# -----------------------------------------------------------------------------
FROM base as builder

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-ansi --no-interaction

# -----------------------------------------------------------------------------
# API Stage - FastAPI Application
# -----------------------------------------------------------------------------
FROM base as api

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Worker Stage - Background Task Worker
# -----------------------------------------------------------------------------
FROM base as worker

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

# Default command
CMD ["python", "-m", "backend.worker"]

# -----------------------------------------------------------------------------
# Migrate Stage - Database Migration Runner
# -----------------------------------------------------------------------------
FROM base as migrate

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Default command
CMD ["alembic", "upgrade", "head"]

# -----------------------------------------------------------------------------
# Development Stage - Development Environment
# -----------------------------------------------------------------------------
FROM base as development

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY pyproject.toml ./

# Install development dependencies
RUN poetry install --no-root --only dev --no-ansi --no-interaction

# Set hot reload
ENV WATCHFILES_FORCE_POLLING=true

# Default command with hot reload
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
