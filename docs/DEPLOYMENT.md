# ATLAS Platform - Deployment Guide

This guide covers deploying the ATLAS Platform in various environments.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database
DATABASE_NAME=atlas
DATABASE_USER=atlas
DATABASE_PASSWORD=your_secure_password
DATABASE_URL=postgresql://atlas:your_secure_password@postgres:5432/atlas

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-super-secret-key-min-32-chars

# Environment
ENVIRONMENT=production
DEBUG=false

# Ports
PORT=8000
FRONTEND_PORT=3000
POSTGRES_PORT=5432
REDIS_PORT=6379
```

## Quick Start (Development)

1. Clone the repository:
```bash
git clone https://github.com/your-org/atlas-platform.git
cd atlas-platform
```

2. Create the `.env` file:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Start all services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

5. Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

### Using Docker Compose

1. Create production `.env`:
```bash
cp .env.example .env.production
# Edit with secure values
```

2. Build and start:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --build
```

3. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

### Using Kubernetes

Helm charts are available in `infrastructure/helm/`:

```bash
helm install atlas ./infrastructure/helm/atlas-platform \
    --set database.password=your_password \
    --set secretKey=your_secret_key
```

## Monitoring

Enable monitoring profiles:

```bash
# Start with monitoring (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Access Grafana at http://localhost:3001
# Default credentials: admin / admin_password
```

## Management Tools

Enable management tools:

```bash
# Start with tools (pgAdmin + Redis Commander)
docker-compose --profile tools up -d

# pgAdmin: http://localhost:5050
# Redis Commander: http://localhost:8081
```

## Database Backups

Create a backup:
```bash
docker-compose exec postgres pg_dump -U atlas atlas > backup_$(date +%Y%m%d).sql
```

Restore a backup:
```bash
cat backup_file.sql | docker-compose exec -T postgres psql -U atlas atlas
```

## Health Checks

Check service health:
```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# PostgreSQL
docker-compose exec postgres pg_isready -U atlas

# Redis
docker-compose exec redis redis-cli ping
```

## Troubleshooting

### API container not starting
```bash
docker-compose logs api
docker-compose exec api alembic check
```

### Database connection issues
```bash
docker-compose exec postgres psql -U atlas -c "SELECT 1"
```

### Frontend not loading
```bash
docker-compose logs frontend
```

## CI/CD

GitHub Actions workflows are available in `.github/workflows/`:

- `ci.yml`: Continuous Integration
- `deploy.yml`: Deployment to staging/production

See [GitHub Actions Documentation](.github/workflows/README.md) for setup.
