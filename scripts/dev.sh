#!/bin/bash
# ATLAS Platform - Development Setup Script

set -e

echo "========================================"
echo "ATLAS Platform - Development Setup"
echo "========================================"

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting."; exit 1; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and configure your settings."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v uv >/dev/null 2>&1; then
    echo "Using uv for package management..."
    uv sync --dev
else
    echo "Using pip for package management..."
    pip install -e ".[dev]"
fi

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create initial data
echo "Creating initial data..."
python -c "
from backend.db import init_db
from backend.core.logging import setup_logging
setup_logging()
import asyncio
asyncio.run(init_db())
"

echo "========================================"
echo "Development setup complete!"
echo "========================================"
echo ""
echo "To start the development server:"
echo "  uvicorn backend.api.main:app --reload"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up"
