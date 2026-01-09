# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-09

### Added

- Initial release of Agile-PM as standalone package
- Extracted from campaign-system/packages/agile-pm-agents

#### Core Modules
- `AgileConfig`: Configuration management with YAML persistence
- `AgileProject`: Project lifecycle (init, link, sync, uninstall)
- Models: `AgentConfig`, `RoleDefinition`, `TaskAssignment`, and enums

#### Memory System
- `MemoryManager`: Unified memory orchestration
- `BufferMemory`: Short-term conversation buffer
- `SummaryMemory`: Long-term summarization
- `EntityMemory`: Entity extraction and tracking
- `VectorStoreMemory`: Semantic retrieval
- `PostgresMemoryStore`: PostgreSQL persistence backend

#### Multi-Agent Crews
- `PlanningCrew`: Sprint planning and backlog management
- `ExecutionCrew`: Task implementation
- `ReviewCrew`: Code and architecture review
- `CollaborationHub`: Inter-agent communication
- Consensus strategies: Voting and Leader-based

#### Dashboard
- `DashboardServer`: WebSocket server for real-time updates
- Event streaming with subscriptions
- Metrics collection and broadcasting

#### Observability
- OpenTelemetry tracing integration
- Prometheus metrics
- Structured logging

#### CLI
- `agile-pm init`: Initialize Agile-PM in a project
- `agile-pm link`: Link to AI providers
- `agile-pm sync`: Sync provider configurations
- `agile-pm dashboard`: Start monitoring dashboard

#### Provider Adapters
- GitHub Copilot (full support)
- Cursor IDE (full support)
- Qodo (planned)
- OpenAI Codex (planned)

#### Templates
- Sprint planning template
- Task template
- Review template

#### Governance
- 33 role definitions for AI agents
- Authority matrix
- Approval enforcement

### Migration Notes

This package was extracted from `campaign-system/packages/agile-pm-agents` as part of ADR-016. The package has been renamed from `agile_pm_agents` to `agile_pm`.

Import changes:
```python
# Old
from agile_pm_agents import AgentConfig
from agile_pm_agents.memory import MemoryManager

# New
from agile_pm import AgentConfig
from agile_pm.memory import MemoryManager
```

[Unreleased]: https://github.com/mohamed-daif/agile-pm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mohamed-daif/agile-pm/releases/tag/v0.1.0
