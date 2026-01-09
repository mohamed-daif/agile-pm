# Notification Plugin Example

Sends notifications to a webhook when tasks are completed or fail.

## Configuration

```yaml
plugins:
  notification:
    enabled: true
    settings:
      webhook_url: https://hooks.slack.com/services/xxx
```

## Events

- `ON_TASK_COMPLETED` - Sends success message
- `ON_TASK_FAILED` - Sends failure message

## Usage

```python
from agile_pm.plugins.registry import PluginRegistry
from notification_plugin import NotificationPlugin

registry = PluginRegistry()
await registry.register(
    NotificationPlugin(),
    {"webhook_url": "https://..."}
)
```
