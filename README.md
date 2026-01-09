# Agile-PM

[![CI](https://github.com/mohamed-daif/agile-pm/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamed-daif/agile-pm/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mohamed-daif/agile-pm/branch/main/graph/badge.svg)](https://codecov.io/gh/mohamed-daif/agile-pm)
[![PyPI version](https://badge.fury.io/py/agile-pm.svg)](https://badge.fury.io/py/agile-pm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-Powered Agile Project Management with Multi-Agent Orchestration**

Agile-PM is a standalone Python package that provides AI-powered project management capabilities using multi-agent collaboration. It enables autonomous sprint planning, task execution, and workflow management.

## 🚀 Quick Start

### Installation

```bash
# From PyPI
pip install agile-pm

# From source
git clone https://github.com/mohamed-daif/agile-pm.git
cd agile-pm
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Check version
agile-pm version

# Initialize a new project
agile-pm init my-project

# Plan a sprint
agile-pm plan sprint --goal "Implement user authentication"

# Execute tasks
agile-pm execute task S01-001
```

### Python API

```python
from agile_pm import AgentOrchestrator, Task

# Create orchestrator
orchestrator = AgentOrchestrator()

# Create and execute a task
task = Task(
    id="task-001",
    title="Implement login feature",
    priority="P0"
)

result = await orchestrator.execute(task)
print(f"Task completed: {result.status}")
```

## 📚 Documentation

- [Getting Started Guide](docs/guides/getting-started.md)
- [API Reference](docs/api/README.md)
- [Configuration Guide](docs/guides/configuration.md)
- [Multi-Agent Architecture](docs/architecture.md)

## ✨ Features

- **🤖 Multi-Agent Orchestration**: Coordinate multiple AI agents for complex tasks
- **📋 Sprint Planning**: AI-powered sprint planning and task breakdown
- **🔄 Real-Time Updates**: WebSocket-based dashboard for monitoring
- **🛡️ Production Ready**: Rate limiting, circuit breakers, and security hardening
- **📊 Performance Benchmarks**: Built-in benchmarking and SLA monitoring
- **🧪 Comprehensive Testing**: E2E tests with Docker integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Dashboard                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Agent Status │  │ Task Progress│  │ Activity Log │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                      WebSocket (Real-time)
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Agile-PM Core                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Orchestrator │  │  Agent Pool  │  │   Memory     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Security   │  │  Resilience  │  │   CLI        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
        ┌─────┴─────┐                 ┌───────┴───────┐
        │ PostgreSQL│                 │     Redis     │
        │ (Persist) │                 │   (Cache)     │
        └───────────┘                 └───────────────┘
```

## 🔧 Configuration

Create `.agile-pm.yml` in your project root:

```yaml
# Agile-PM Configuration
version: "1.0"

agents:
  max_concurrent: 5
  default_timeout: 300

llm:
  provider: openai
  model: gpt-4
  temperature: 0.7

memory:
  backend: redis
  ttl: 86400

security:
  rate_limit_rpm: 60
  rate_limit_burst: 10
```

## 🧪 Development

### Setup

```bash
# Clone repository
git clone https://github.com/mohamed-daif/agile-pm.git
cd agile-pm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev,test]"
```

### Testing

```bash
# Run unit tests
pytest tests/

# Run E2E tests (requires Docker)
docker-compose -f docker-compose.test.yml up --build

# Run benchmarks
python benchmarks/run_benchmarks.py
```

### Code Quality

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/
```

## 📈 Benchmarks

| Operation | P50 | P95 | P99 | SLA |
|-----------|-----|-----|-----|-----|
| Agent Startup | 4ms | 8ms | 12ms | <2s |
| Task Planning | 200ms | 400ms | 600ms | <30s |
| Memory Read | 2ms | 5ms | 8ms | <100ms |
| Memory Write | 10ms | 15ms | 20ms | <200ms |

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent inspiration
- [LangChain](https://github.com/langchain-ai/langchain) for LLM tooling
- The open-source community

---

**Made with ❤️ by the Agile-PM Team**
