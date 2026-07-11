# ATLAS Platform

**AI-Powered Business Intelligence Operating System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

ATLAS is a revolutionary AI-driven business opportunity intelligence platform designed to transform how businesses discover, evaluate, and capitalize on strategic opportunities.

## 🌟 Vision

ATLAS is not merely a search engine or a simple chatbot—it is an integrated AI Intelligence Operating System that transforms scattered global information streams into focused, actionable business intelligence.

## 🎯 Core Features

- **Intelligence Engine**: Multi-source data processing with causal reasoning
- **Opportunity Discovery**: AI-powered opportunity identification and scoring
- **Knowledge Graph**: Cross-domain relationship mapping
- **Explainable AI**: Full transparency in recommendations with confidence levels
- **Multi-Source Intelligence**: Integration with news, financial data, patents, and more
- **Subscription Management**: Multi-tier plans with usage limits and feature flags
- **Enterprise Security**: RBAC, SSO, and comprehensive audit logging

## 🏗️ Architecture

```
atlas_platform/
├── backend/              # FastAPI backend services
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration and security
│   ├── db/               # Database connections and migrations
│   ├── intelligence/     # Intelligence engine
│   ├── models/           # SQLAlchemy ORM models
│   ├── monetization/     # Payments and billing
│   ├── schemas/          # Pydantic validation schemas
│   └── services/         # Business logic services
├── frontend/             # Next.js React frontend
├── infrastructure/       # Docker, Kubernetes, Terraform
├── tests/                # Unit, integration, E2E tests
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/atlas-platform/atlas.git
cd atlas
```

2. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start infrastructure:
```bash
docker-compose up -d postgres redis
```

4. Install backend dependencies:
```bash
cd backend
pip install -e ".[dev]"
```

5. Run database migrations:
```bash
cd backend
alembic upgrade head
python -m backend.db.seeds.cli run
```

6. Install frontend dependencies:
```bash
cd frontend
npm install
```

7. Start development servers:
```bash
# Backend
cd backend
uvicorn backend.api.main:app --reload

# Frontend (in another terminal)
cd frontend
npm run dev
```

8. Access the application:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## 📚 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [Development Guide](./docs/DEVELOPMENT_GUIDE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [API Configuration](./API_CONFIGURATION.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=backend --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test -- --coverage
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

## 🔒 Security

- JWT-based authentication with access/refresh tokens
- Role-based access control (RBAC) with 6 roles
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for API security
- Environment variable secret management

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Migration**: Alembic
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript 5
- **UI Library**: React 18
- **State Management**: Zustand
- **API Client**: Axios/Fetch

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud Ready**: Terraform configurations

## 🤝 Contributing

Please read our [Contributing Guide](./CONTRIBUTING.md) for details on our development workflow.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/atlas-platform/atlas?style=social)
![GitHub forks](https://img.shields.io/github/forks/atlas-platform/atlas?style=social)
![GitHub issues](https://img.shields.io/github/issues/atlas-platform/atlas)

---

**Built with ❤️ by the ATLAS Team**
