# ATLAS Platform - Agent Instructions

## Project Overview

ATLAS is an AI-powered business opportunity intelligence platform. It transforms global information streams into actionable business intelligence using multi-source data processing, causal reasoning, and explainable AI.

## Architecture Principles

1. **Clean Architecture**: Separation of concerns with distinct layers
2. **API First**: All functionality exposed through well-defined APIs
3. **Microservices-Ready**: Components designed for independent deployment
4. **Cloud Native**: Built for cloud deployment with containerization
5. **AI First**: Intelligence layer at the core of all operations
6. **Observability First**: Comprehensive logging, metrics, and tracing

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic
- **Cache**: Redis
- **Database**: PostgreSQL 15+
- **Authentication**: OAuth2 + JWT

### Frontend
- **Framework**: Next.js (React 18+)
- **Styling**: Tailwind CSS
- **State**: React Query + Zustand
- **UI**: shadcn/ui components

### Infrastructure
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes (future)
- **IaC**: Terraform (future)
- **CI/CD**: GitHub Actions

## Development Guidelines

### Python Code Standards
- Use type hints on all functions
- Follow PEP 8 style guide
- Use async/await for I/O operations
- Implement dependency injection
- Write docstrings for all public modules

### API Design
- RESTful endpoints with versioned URLs (/api/v1/)
- Use Pydantic schemas for validation
- Return consistent response format
- Implement proper error handling
- Document with OpenAPI/Swagger

### Database
- Use migrations for all schema changes
- Never modify migrations after merging
- Include indexes for query optimization
- Use soft deletes where appropriate

### Testing
- Write tests before implementing features (TDD)
- Maintain >80% code coverage
- Use fixtures for reusable test data
- Mock external dependencies
- Run tests in CI/CD pipeline

## Environment Variables

See `.env.example` for all required variables. Key categories:

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### AI Providers
- `OPENAI_API_KEY`: OpenAI GPT models
- `GOOGLE_GEMINI_KEY`: Google Gemini models
- `ANTHROPIC_API_KEY`: Anthropic Claude models

### External Services
- `STRIPE_SECRET_KEY`: Payment processing
- `SENDGRID_API_KEY`: Email service

### Application
- `SECRET_KEY`: JWT signing key
- `ALGORITHM`: JWT algorithm (HS256/RS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration

## Project Structure

```
backend/
├── api/              # API route handlers
│   └── v1/
│       ├── endpoints/   # Route modules
│       └── router.py    # Main router
├── core/             # Core functionality
│   ├── config.py     # Configuration management
│   ├── security.py   # Security utilities
│   └── logging.py    # Logging setup
├── db/               # Database layer
│   ├── base.py       # Base declarative class
│   ├── session.py    # Session management
│   └── init_db.py    # Database initialization
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── services/         # Business logic services
└── utils/            # Utility functions
```

## Git Workflow

1. Create feature branch from `main`
2. Write tests first
3. Implement feature
4. Ensure all tests pass
5. Create pull request with description
6. Get code review approval
7. Squash and merge

## Important Notes

- Never commit secrets to version control
- Use `.env` files for local development
- Keep branch names descriptive (`feature/...`, `bugfix/...`)
- Write meaningful commit messages
- Update CHANGELOG.md for each release
