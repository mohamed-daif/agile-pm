# Agile-PM

[![CI](https://github.com/mohamed-daif/agile-pm/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamed-daif/agile-pm/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> AI-powered Agile project management agent framework

## Overview

Agile-PM is a framework that provides AI agent instructions, memory management, and multi-agent collaboration for software development projects. It integrates with popular AI coding assistants (GitHub Copilot, Cursor, Qodo) to enforce governance, role-based workflows, and Agile best practices.

## Features

- 🤖 **Agent Instructions** — Role-based prompts for AI coding assistants
- 🧠 **Memory Management** — Persistent context across sessions
- 👥 **Crew Collaboration** — Multi-agent orchestration with consensus
- 📊 **Dashboard** — Real-time metrics and monitoring
- 🔍 **Observability** — OpenTelemetry tracing and Prometheus metrics
- 📋 **Governance** — Approval workflows and authority boundaries

## Quick Start

### Installation

```bash
# Install from PyPI (when available)
pip install agile-pm

# Or install from source
pip install git+https://github.com/mohamed-daif/agile-pm.git
```

### Initialize in Your Project

```bash
# Create .agile-pm/ folder with default configuration
agile-pm init

# Link to GitHub Copilot
agile-pm link github-copilot
```

### Project Structure

After initialization:

```
your-project/
├── .agile-pm/
│   ├── config.yaml          # Main configuration
│   ├── instructions/        # Project-specific context
│   └── overrides/           # Role customizations
└── .github/
    └── copilot-instructions.md  # Auto-updated
```

## Documentation

- [Integration Guide](docs/INTEGRATION_GUIDE.md) — How to integrate Agile-PM
- [API Reference](docs/API_REFERENCE.md) — Python API documentation
- [Provider Adapters](docs/PROVIDER_ADAPTERS.md) — Supported AI assistants

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agile-PM Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Providers        │  Core           │  Infrastructure       │
│  ─────────────    │  ─────────────  │  ─────────────────    │
│  GitHub Copilot   │  Memory         │  PostgreSQL           │
│  Cursor           │  Crews          │  Redis                │
│  Qodo             │  Dashboard      │  Vector DB            │
│  Codex            │  Observability  │  File System          │
└─────────────────────────────────────────────────────────────┘
```

## Development

### Prerequisites

- Python 3.11+
- Poetry or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/mohamed-daif/agile-pm.git
cd agile-pm

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src tests
```

### Project Structure

```
agile-pm/
├── src/agile_pm/
│   ├── core/           # Core configuration and project management
│   ├── memory/         # Memory persistence (Buffer, Summary, Entity, Vector)
│   ├── crews/          # Multi-agent collaboration
│   ├── dashboard/      # Metrics and monitoring
│   ├── observability/  # Tracing and logging
│   ├── cli/            # Command-line interface
│   └── providers/      # AI assistant adapters
├── tests/
├── docs/
├── templates/          # Obsidian templates
├── governance/         # Role definitions
└── config/             # Default configurations
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License — see [LICENSE](LICENSE) for details.

## Related

- [Campaign System](https://github.com/mohamed-daif/campaign-system) — Original project where Agile-PM was developed
- [ADR-016](https://github.com/mohamed-daif/campaign-system/blob/main/.github/adr/ADR-016-agile-pm-separation.md) — Architecture decision for separation
