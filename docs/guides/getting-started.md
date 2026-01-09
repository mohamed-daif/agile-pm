# Getting Started with Agile-PM

This guide will help you get started with Agile-PM for AI-powered project management.

## Prerequisites

- Python 3.11 or higher
- Node.js 20+ (for frontend)
- Docker (optional, for E2E tests)
- OpenAI API key (or compatible LLM provider)

## Installation

### From PyPI (Recommended)

```bash
pip install agile-pm
```

### From Source

```bash
git clone https://github.com/mohamed-daif/agile-pm.git
cd agile-pm
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev,test]"
```

## Initial Setup

### 1. Configure Environment

Create a `.env` file in your project root:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/agilepm

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 2. Initialize Project

```bash
agile-pm init my-project
```

This creates:
- `.agile-pm.yml` - Configuration file
- `sprints/` - Sprint planning directory
- `backlog/` - Product backlog

### 3. Verify Installation

```bash
agile-pm version
agile-pm --help
```

## Basic Workflow

### 1. Create a Sprint

```bash
agile-pm sprint create --name "Sprint 01" --goal "MVP features"
```

### 2. Add Tasks to Backlog

```bash
agile-pm task create --title "User authentication" --priority P0 --points 5
agile-pm task create --title "Dashboard UI" --priority P1 --points 8
```

### 3. Plan Sprint

```bash
agile-pm plan sprint --auto
```

This uses AI to:
- Analyze task dependencies
- Estimate complexity
- Suggest task ordering
- Assign to agents

### 4. Execute Tasks

```bash
# Execute single task
agile-pm execute task TASK-001

# Execute all sprint tasks
agile-pm execute sprint --parallel
```

### 5. Monitor Progress

```bash
# Start dashboard
agile-pm dashboard

# View status
agile-pm status
```

## Python API Usage

### Basic Agent Orchestration

```python
import asyncio
from agile_pm import AgentOrchestrator, Task, Agent

async def main():
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register agents
    orchestrator.register_agent(Agent(
        name="Backend Engineer",
        role="executor",
        capabilities=["python", "api", "database"]
    ))
    
    # Create task
    task = Task(
        id="task-001",
        title="Create REST API endpoint",
        description="Implement /api/users endpoint with CRUD operations",
        priority="P0",
        estimated_points=5
    )
    
    # Execute
    result = await orchestrator.execute(task)
    print(f"Status: {result.status}")
    print(f"Output: {result.output}")

asyncio.run(main())
```

### Sprint Planning

```python
from agile_pm import SprintPlanner, Sprint, Task

async def plan_sprint():
    planner = SprintPlanner()
    
    # Create sprint
    sprint = Sprint(
        name="Sprint 05",
        goal="Production hardening",
        duration_days=7
    )
    
    # Add tasks
    tasks = [
        Task(id="S05-001", title="Security audit", priority="P0", points=5),
        Task(id="S05-002", title="Performance optimization", priority="P1", points=8),
        Task(id="S05-003", title="Documentation", priority="P2", points=3),
    ]
    
    # AI-powered planning
    plan = await planner.plan(sprint, tasks)
    
    print(f"Planned {len(plan.tasks)} tasks")
    print(f"Total points: {plan.total_points}")
    print(f"Estimated completion: {plan.estimated_completion}")
```

### Real-time Updates

```python
from agile_pm import WebSocketClient

async def monitor():
    client = WebSocketClient("ws://localhost:8001/ws")
    
    async for event in client.events():
        if event.type == "task_progress":
            print(f"Task {event.task_id}: {event.progress}%")
        elif event.type == "agent_status":
            print(f"Agent {event.agent_id}: {event.status}")
```

## Next Steps

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Agent Guide](agents.md) - Working with AI agents
- [API Reference](../api/README.md) - Full API documentation
- [Examples](../examples/) - Example projects and use cases

## Troubleshooting

### Common Issues

**API Key Error**
```
Error: OpenAI API key not configured
```
Solution: Set `OPENAI_API_KEY` environment variable

**Connection Error**
```
Error: Cannot connect to database
```
Solution: Check `DATABASE_URL` or use SQLite for local development

**Rate Limit**
```
Error: Rate limit exceeded
```
Solution: Configure rate limits in `.agile-pm.yml` or wait and retry

### Getting Help

- [GitHub Issues](https://github.com/mohamed-daif/agile-pm/issues)
- [Discussions](https://github.com/mohamed-daif/agile-pm/discussions)
- [Documentation](https://agile-pm.readthedocs.io/)
