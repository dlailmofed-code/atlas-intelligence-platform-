# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within ATLAS Platform, please create a private security advisory through GitHub.

**Please do not report security vulnerabilities through public GitHub issues.**

### When reporting, please include:

1. Description of the vulnerability
2. Steps to reproduce the issue
3. Potential impact of the vulnerability
4. If possible, suggested fix

## Security Best Practices

When deploying ATLAS Platform:

1. **Never commit `.env` files** to version control
2. **Use strong SECRET_KEYs** in production (minimum 32 characters)
3. **Enable HTTPS** in production environments
4. **Configure CORS properly** for your domain
5. **Use PostgreSQL with SSL** for production database connections
6. **Enable Redis AUTH** and use TLS in production
7. **Regularly update dependencies** to patch security vulnerabilities

## Security Features

ATLAS Platform includes:

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Argon2 algorithm for secure password storage
- **RBAC**: Role-based access control
- **Input Validation**: Pydantic schema validation on all endpoints
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Protection**: Configurable cross-origin request handling
