# Changelog

All notable changes to Agile-PM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-10

### Added

#### Core Features
- Multi-agent orchestration system with role-based agents
- RESTful API with FastAPI
- Plugin system for extensibility
- Webhook integration with delivery guarantees
- Memory persistence with PostgreSQL and Redis cache

#### API & Authentication
- JWT and API key authentication
- Role-based access control (RBAC)
- Standardized API response format
- Cursor and page-based pagination

#### Infrastructure
- PostgreSQL storage with SQLAlchemy ORM
- Redis caching and session storage
- Celery task queue for async operations
- Alembic database migrations

#### Observability
- OpenTelemetry tracing integration
- Prometheus metrics endpoint
- Grafana dashboards
- Structured JSON logging
- Deep health checks

#### Deployment
- Docker and docker-compose support
- Kubernetes manifests
- Helm chart for deployment
- GitHub Actions CI/CD pipeline

### Security
- Input validation on all endpoints
- Tenant isolation
- Secret management with External Secrets Operator
- Security headers and CORS configuration

## [0.1.0] - 2025-12-01

### Added
- Initial project structure
- Basic agent implementation
- CLI interface
- Configuration management
