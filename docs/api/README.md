# API Reference

## Core Classes

### AgentOrchestrator

Main class for orchestrating multi-agent workflows.

```python
from agile_pm import AgentOrchestrator

orchestrator = AgentOrchestrator(config=None)
```

#### Methods

| Method | Description |
|--------|-------------|
| `register_agent(agent)` | Register an agent with the orchestrator |
| `execute(task)` | Execute a single task |
| `execute_batch(tasks)` | Execute multiple tasks |
| `get_status()` | Get orchestrator status |

### Agent

Represents an AI agent.

```python
from agile_pm import Agent

agent = Agent(
    name="Backend Engineer",
    role="executor",
    capabilities=["python", "api"],
    config={}
)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Agent display name |
| `role` | str | Agent role (strategic, executor, reviewer) |
| `capabilities` | List[str] | Agent capabilities |
| `status` | AgentStatus | Current status |

### Task

Represents a task to be executed.

```python
from agile_pm import Task

task = Task(
    id="task-001",
    title="Implement feature",
    description="...",
    priority="P0",
    estimated_points=5
)
```

### Sprint

Represents a sprint.

```python
from agile_pm import Sprint

sprint = Sprint(
    name="Sprint 05",
    goal="Production hardening",
    start_date=date(2026, 1, 20),
    end_date=date(2026, 1, 27)
)
```

## Security Module

### InputValidator

Input validation utilities.

```python
from agile_pm.security import InputValidator

result = InputValidator.validate_string(user_input)
if result.is_valid:
    safe_input = result.sanitized
```

### RateLimiter

Rate limiting implementation.

```python
from agile_pm.security import get_rate_limiter

limiter = get_rate_limiter()
result = await limiter.check("user-123")
if result.allowed:
    # Process request
```

## Resilience Module

### CircuitBreaker

Circuit breaker pattern implementation.

```python
from agile_pm.resilience import CircuitBreaker

cb = CircuitBreaker("external-api")
result = await cb.call(external_api_call, arg1, arg2)
```

### Retry

Retry with exponential backoff.

```python
from agile_pm.resilience import retry, RetryConfig

@retry(RetryConfig(max_attempts=3))
async def flaky_operation():
    ...
```

### HealthChecker

Health check management.

```python
from agile_pm.resilience import get_health_checker

checker = get_health_checker()
checker.register("database", check_db_connection)
result = await checker.check()
```

## CLI Reference

See `agile-pm --help` for full CLI documentation.

```bash
# Project management
agile-pm init <project-name>
agile-pm status

# Sprint management
agile-pm sprint create --name "Sprint 01"
agile-pm sprint list
agile-pm sprint show <sprint-id>

# Task management
agile-pm task create --title "Task" --priority P0
agile-pm task list
agile-pm task show <task-id>

# Execution
agile-pm execute task <task-id>
agile-pm execute sprint

# Dashboard
agile-pm dashboard
```
