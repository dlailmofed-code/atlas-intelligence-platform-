# Contributing to ATLAS Platform

Thank you for your interest in contributing to the ATLAS Intelligence Platform!

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Release Process](#release-process)

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Run tests to ensure nothing is broken
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

```bash
# Clone the repository
git clone https://github.com/atlas-platform/atlas.git
cd atlas

# Copy environment file
cp .env.example .env

# Start infrastructure
docker-compose up -d postgres redis

# Install backend dependencies
cd backend
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend
npm install

# Run database migrations
alembic upgrade head

# Start development servers
# Backend: uvicorn backend.api.main:app --reload
# Frontend: npm run dev
```

## Development Workflow

### Branch Naming

- `feature/<issue-number>-description` - New features
- `fix/<issue-number>-description` - Bug fixes
- `hotfix/<issue-number>-description` - Urgent fixes
- `refactor/<description>` - Code refactoring
- `docs/<description>` - Documentation updates

### Example
```bash
git checkout -b feature/123-user-authentication
git checkout -b fix/456-subscription-billing
```

## Coding Standards

### Python

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all public modules and functions
- Maximum line length: 100 characters

### JavaScript/TypeScript

- Follow ESLint configuration
- Use TypeScript for all new code
- Maximum line length: 100 characters

### Formatting

We use automated formatting tools:
- **Python**: ruff format
- **JavaScript**: Prettier

```bash
# Format Python code
ruff format .

# Format JavaScript code
npm run format
```

### Linting

```bash
# Python linting
ruff check .

# JavaScript linting
npm run lint
```

## Testing

### Writing Tests

- All new features must include tests
- All bug fixes must include a regression test
- Test coverage must not decrease

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=backend

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database operations
- **E2E Tests**: Test complete user workflows

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
git commit -m "feat(auth): add OAuth2 authentication"
git commit -m "fix(billing): resolve subscription cancellation issue"
git commit -m "docs(api): update user endpoints documentation"
```

## Pull Requests

### Before Submitting

1. Ensure all tests pass
2. Update documentation if needed
3. Add entry to CHANGELOG.md
4. Rebase on latest main branch

### PR Description Template

```markdown
## Summary
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how changes were tested

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one approval required
3. All comments must be resolved
4. Branch must be up to date with main

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch: `release/v1.x.x`
4. Run full test suite
5. Create GitHub release
6. Merge to main
7. Tag release

## Questions?

If you have any questions, please open an issue or contact the maintainers.

Thank you for contributing to ATLAS Platform!
