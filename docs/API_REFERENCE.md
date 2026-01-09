# Agile-PM API Reference

This document provides a complete API reference for the Agile-PM framework.

## Core Module

### `AgileConfig`

Main configuration class for Agile-PM.

```python
from agile_pm import AgileConfig

config = AgileConfig(
    project=ProjectInfo(name="my-project"),
    memory=MemoryConfig(enabled=True),
    features=FeaturesConfig(crews=True),
)
```

#### Class Methods

| Method | Description |
|--------|-------------|
| `from_file(path)` | Load configuration from YAML file |
| `to_file(path)` | Save configuration to YAML file |

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `version` | `str` | `"1.0"` | Configuration version |
| `project` | `ProjectInfo` | - | Project metadata |
| `providers` | `dict[str, ProviderConfig]` | - | AI provider configurations |
| `memory` | `MemoryConfig` | - | Memory persistence settings |
| `obsidian` | `ObsidianConfig` | - | Obsidian vault integration |
| `features` | `FeaturesConfig` | - | Feature flags |

---

### `AgileProject`

Main entry point for Agile-PM project integration.

```python
from agile_pm import AgileProject

# Initialize new project
project = AgileProject.init(root_path=Path.cwd())

# Load existing project
project = AgileProject.from_config(".agile-pm/config.yaml")
```

#### Class Methods

| Method | Description |
|--------|-------------|
| `init(root_path, **kwargs)` | Initialize new Agile-PM project |
| `from_config(config_path)` | Load project from existing config |

#### Instance Methods

| Method | Description |
|--------|-------------|
| `link_provider(name)` | Link to an AI provider |
| `sync()` | Sync all provider configurations |
| `uninstall(keep_overrides)` | Remove Agile-PM from project |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `config` | `AgileConfig` | Project configuration |
| `root_path` | `Path` | Project root directory |
| `memory` | `MemoryManager` | Memory manager (lazy) |
| `crews` | `CrewManager` | Crew manager (lazy) |
| `dashboard` | `DashboardServer` | Dashboard server (lazy) |

---

## Memory Module

### `MemoryManager`

Manages persistent memory for Agile-PM agents.

```python
from agile_pm.memory import MemoryManager
from agile_pm.core.config import MemoryConfig

config = MemoryConfig(backend="sqlite", path=".agile-pm/cache/memory.db")
manager = MemoryManager(config)

# Store memory
manager.store("project:context", {"key": "value"})

# Recall memory
memory = manager.recall("project:context")

# List memories
keys = manager.list_memories(prefix="project:")

# Forget memory
manager.forget("project:context")
```

#### Methods

| Method | Description |
|--------|-------------|
| `store(key, value, metadata)` | Store a memory |
| `recall(key)` | Recall a memory by key |
| `forget(key)` | Forget (delete) a memory |
| `list_memories(prefix)` | List all memory keys |

---

## Crews Module

### `CrewManager`

Manages CrewAI crews for Agile-PM.

```python
from agile_pm.crews import CrewManager

manager = CrewManager(config)

# Create crews
planning_crew = manager.create_planning_crew()
review_crew = manager.create_review_crew()
execution_crew = manager.create_execution_crew()

# Run crew
result = manager.run_crew("planning", {"task": "Plan Sprint 5"})
```

#### Methods

| Method | Description |
|--------|-------------|
| `create_planning_crew()` | Create sprint/task planning crew |
| `create_review_crew()` | Create code/architecture review crew |
| `create_execution_crew()` | Create task implementation crew |
| `get_crew(name)` | Get crew by name |
| `get_agent(name)` | Get agent by name |
| `run_crew(name, inputs)` | Run crew with inputs |

---

## Observability Module

### `Tracer`

Tracing for Agile-PM operations.

```python
from agile_pm.observability import Tracer

tracer = Tracer(enabled=True)

with tracer.span("operation", attribute="value") as span:
    tracer.add_event("step_completed", status="success")
    # Do work...

spans = tracer.get_spans()
```

#### Methods

| Method | Description |
|--------|-------------|
| `span(name, **attributes)` | Context manager for creating spans |
| `add_event(name, **attributes)` | Add event to current span |
| `get_spans()` | Get all recorded spans |
| `clear()` | Clear all spans |
| `export_json()` | Export spans as JSON |

---

## Dashboard Module

### `DashboardServer`

Web dashboard for Agile-PM monitoring.

```python
from agile_pm.dashboard import DashboardServer

server = DashboardServer(config)
server.start(host="127.0.0.1", port=8080)
```

#### Methods

| Method | Description |
|--------|-------------|
| `create_app()` | Create FastAPI application |
| `start(host, port)` | Start dashboard server |
| `stop()` | Stop dashboard server |

---

## CLI Module

### Commands

| Command | Description |
|---------|-------------|
| `agile-pm init [path]` | Initialize Agile-PM in project |
| `agile-pm link <provider>` | Link to AI provider |
| `agile-pm sync` | Sync provider configurations |
| `agile-pm uninstall` | Remove Agile-PM |
| `agile-pm dashboard` | Start dashboard server |
| `agile-pm version` | Show version |

---

## Providers Module

### `BaseProvider`

Abstract base class for AI provider adapters.

```python
from agile_pm.providers import get_provider

provider = get_provider("github_copilot")
provider.link(project)
```

### Supported Providers

| Provider | Status | Description |
|----------|--------|-------------|
| `github_copilot` | ✅ Full | GitHub Copilot integration |
| `cursor` | ✅ Full | Cursor IDE integration |
| `qodo` | 🚧 Planned | Qodo integration |
| `codex` | 🚧 Planned | OpenAI Codex integration |
