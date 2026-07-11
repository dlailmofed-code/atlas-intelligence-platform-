#!/bin/bash
# ATLAS Platform - Test Runner Script

set -e

echo "========================================"
echo "ATLAS Platform - Running Tests"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Parse arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-false}"

# Set options
OPTIONS="-v"

if [ "$COVERAGE" = "true" ]; then
    OPTIONS="$OPTIONS --cov=backend --cov-report=html --cov-report=xml"
fi

# Run tests based on type
case $TEST_TYPE in
    unit)
        echo "Running unit tests..."
        pytest tests/unit $OPTIONS
        ;;
    integration)
        echo "Running integration tests..."
        pytest tests/integration $OPTIONS
        ;;
    e2e)
        echo "Running E2E tests..."
        pytest tests/e2e $OPTIONS
        ;;
    all)
        echo "Running all tests..."
        pytest tests/ $OPTIONS
        ;;
    *)
        echo "Unknown test type: $TEST_TYPE"
        echo "Usage: $0 [unit|integration|e2e|all] [coverage]"
        exit 1
        ;;
esac

echo "========================================"
echo "Tests complete!"
echo "========================================"
