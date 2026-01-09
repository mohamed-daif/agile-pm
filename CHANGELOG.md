# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- React dashboard with real-time WebSocket updates (S05-001)
- WebSocket manager with auto-reconnect and heartbeat (S05-002)
- E2E testing infrastructure with Docker (S05-003)
- Performance benchmarking suite (S05-004)
- Security hardening: input validation, rate limiting (S05-005)
- Resilience patterns: circuit breaker, retry, health checks (S05-006)
- CI/CD pipeline with GitHub Actions (S05-007)
- User documentation (S05-008)

### Changed
- Improved agent orchestration performance
- Enhanced error handling and recovery

### Fixed
- Memory leak in WebSocket connections
- Race condition in agent pool

## [0.1.0] - 2026-01-05

### Added
- Initial release
- CLI tool with `init`, `plan`, `execute` commands
- Multi-agent orchestration
- Basic sprint and task management
- Memory persistence with Redis/PostgreSQL
- OpenAI integration

[Unreleased]: https://github.com/mohamed-daif/agile-pm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mohamed-daif/agile-pm/releases/tag/v0.1.0
