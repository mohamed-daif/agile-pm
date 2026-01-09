# Hooks Reference

## Available Hooks

| Hook | Description | Parameters |
|------|-------------|------------|
| `ON_TASK_CREATED` | Task was created | `task` |
| `ON_TASK_STARTED` | Task execution started | `task` |
| `ON_TASK_COMPLETED` | Task completed successfully | `task`, `result` |
| `ON_TASK_FAILED` | Task failed | `task`, `error` |
| `ON_SPRINT_STARTED` | Sprint started | `sprint` |
| `ON_SPRINT_COMPLETED` | Sprint completed | `sprint`, `stats` |
| `ON_AGENT_STATUS_CHANGE` | Agent status changed | `agent`, `old_status`, `new_status` |
| `ON_MEMORY_WRITE` | Memory key written | `key`, `value` |
| `ON_ERROR` | System error occurred | `error`, `context` |

## Registering Hooks

```python
def register_hooks(self, hook_manager):
    hook_manager.register(
        Hook.ON_TASK_CREATED,
        self.handle_task,
        priority=10,  # Higher = earlier execution
        plugin_name=self.name
    )
```

## Hook Handler Signature

```python
async def handle_task(self, task=None, **kwargs):
    # Handle the event
    return result  # Optional return value
```

## Priority

Handlers execute in priority order (highest first). Default is 0.
