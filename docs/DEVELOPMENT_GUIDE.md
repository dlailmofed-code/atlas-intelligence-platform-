# ATLAS Platform Development Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Database](#database)
- [Testing](#testing)
- [Debugging](#debugging)
- [Code Style](#code-style)
- [Common Tasks](#common-tasks)

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Git

## Project Structure

```
atlas_platform/
├── backend/                  # FastAPI backend
│   ├── api/                 # API routes and endpoints
│   ├── core/                # Core configuration
│   ├── db/                  # Database connections
│   ├── intelligence/         # Intelligence engine
│   ├── models/              # SQLAlchemy models
│   ├── monetization/         # Payment & billing
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── tests/               # Backend tests
├── frontend/                # React/Next.js frontend
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   └── tests/               # Frontend tests
├── docs/                    # Documentation
├── infrastructure/          # Docker, K8s, Terraform
├── tests/                   # Shared tests
└── pyproject.toml           # Python project config
```

## Local Development Setup

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/atlas-platform/atlas.git
cd atlas

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Seed database
python -m backend.db.seeds.cli run

# Start development server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access Services

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Backend Development

### Project Layout

```
backend/
├── api/
│   ├── main.py              # FastAPI app entry
│   └── v1/
│       ├── router.py        # API router
│       └── endpoints/       # Endpoint modules
├── core/
│   ├── config.py            # Configuration
│   ├── security.py          # Auth utilities
│   └── logging.py           # Logging config
├── db/
│   ├── session.py           # Database session
│   └── seeds/               # Database seeds
├── intelligence/
│   ├── base.py              # Base models
│   ├── engine.py            # Main engine
│   └── components/          # Engine components
├── models/
│   └── [domain]/            # Domain models
├── monetization/
│   ├── adapters/            # Payment adapters
│   └── services/            # Billing services
├── schemas/
│   └── [domain]/            # API schemas
└── services/
    └── [domain]/            # Business logic
```

### Creating New Models

1. Create model file in `backend/models/<domain>/`
2. Inherit from `Base` and mixins
3. Add to `backend/models/__init__.py`
4. Create migration: `alembic revision --autogenerate -m "Add <model>"`
5. Run migration: `alembic upgrade head`

### Creating New Endpoints

1. Create schema in `backend/schemas/<domain>/`
2. Create service in `backend/services/<domain>/`
3. Create endpoint in `backend/api/v1/endpoints/<domain>.py`
4. Register in router
5. Add tests

### API Patterns

```python
# Standard CRUD endpoint pattern
@router.get("/", response_model=list[SchemaOut])
async def list_items(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
):
    items = await service.list_items(session, skip=skip, limit=limit)
    return items

@router.post("/", response_model=SchemaOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: SchemaIn,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_permission("item:create")),
):
    return await service.create_item(session, item)
```

## Frontend Development

### Project Layout

```
frontend/
├── src/
│   ├── app/                 # Next.js app router
│   ├── components/          # React components
│   ├── hooks/               # Custom hooks
│   ├── lib/                 # Utilities
│   ├── services/            # API clients
│   └── styles/               # Global styles
├── public/                  # Static assets
└── tests/                   # Test files
```

### Creating New Components

1. Create component in `src/components/`
2. Add TypeScript types
3. Write unit tests
4. Export from `src/components/index.ts`

### API Integration

```typescript
// services/api.ts
import { apiClient } from '@/lib/api-client';

export const getItems = (params: QueryParams) =>
  apiClient.get<Item[]>('/v1/items', { params });

export const createItem = (data: CreateItem) =>
  apiClient.post<Item>('/v1/items', data);
```

## Database

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Run migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>

# Show current revision
alembic current

# Show migration history
alembic history
```

### Seeds

```bash
# Run all seeds
python -m backend.db.seeds.cli run

# Run specific seed
python -m backend.db.seeds.cli run --seed plans

# Rollback all seeds
python -m backend.db.seeds.cli rollback
```

### Database Tools

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Reset database
alembic downgrade base && alembic upgrade head

# Check migrations status
alembic current && alembic check
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py -v

# Run tests matching pattern
pytest -k "test_create"

# Run with verbose output
pytest -vv -s
```

### Frontend Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run specific test
npm run test -- src/components/Button.test.tsx

# Update snapshots
npm run test -- -u
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration -v

# Run with database
pytest tests/integration --create-db
```

## Debugging

### Backend Debugging

1. **VS Code**: Use the provided `.vscode/launch.json`
2. **PyCharm**: Create run configuration with debugger
3. **CLI**: 
   ```bash
   python -m debugpy --listen localhost:5678 -m uvicorn backend.api.main:app --reload
   ```

### Frontend Debugging

1. **Browser DevTools**: React DevTools, Redux DevTools
2. **VS Code**: Use Chrome debugger
3. **CLI**: Add `debugger` statements

### Database Debugging

1. **Enable SQL logging**:
   ```python
   # In config
   DATABASE_ECHO=true
   ```

2. **pgcli for interactive**:
   ```bash
   pgcli $DATABASE_URL
   ```

## Code Style

### Python

We use `ruff` for linting and formatting:

```bash
# Check code
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

### TypeScript/JavaScript

We use ESLint and Prettier:

```bash
# Check code
npm run lint

# Format code
npm run format

# Fix auto-fixable issues
npm run lint -- --fix
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Common Tasks

### Add New Environment Variable

1. Add to `.env.example`
2. Add to `backend/core/config.py`
3. Add to `docker-compose.yml`
4. Add to documentation

### Add New Dependency

**Backend:**
```bash
# Add to pyproject.toml [project.dependencies]
pip install <package>
pip install -e ".[dev]"  # If dev dependency
```

**Frontend:**
```bash
npm install <package>
npm install -D <package>  # If dev dependency
```

### Update Documentation

1. Update relevant `.md` files
2. Update API documentation
3. Update inline code comments
4. Update CHANGELOG.md

### Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Merge to main

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL
```

### Node Modules Issues

```bash
# Clear cache
npm cache clean --force

# Remove and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Python Package Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -e ".[dev]" --force-reinstall
```

## Additional Resources

- [API Documentation](./API_DOCUMENTATION.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
