"""Plugin hook system."""
from typing import Callable, Any
from enum import Enum
from dataclasses import dataclass, field

class Hook(str, Enum):
    ON_TASK_CREATED = "on_task_created"
    ON_TASK_STARTED = "on_task_started"
    ON_TASK_COMPLETED = "on_task_completed"
    ON_TASK_FAILED = "on_task_failed"
    ON_SPRINT_STARTED = "on_sprint_started"
    ON_SPRINT_COMPLETED = "on_sprint_completed"
    ON_AGENT_STATUS_CHANGE = "on_agent_status_change"
    ON_MEMORY_WRITE = "on_memory_write"
    ON_ERROR = "on_error"

@dataclass
class HookHandler:
    callback: Callable
    priority: int = 0
    plugin_name: str = ""

class HookManager:
    def __init__(self):
        self._handlers: dict = {hook: [] for hook in Hook}
    
    def register(self, hook: Hook, callback: Callable, priority: int = 0, plugin_name: str = "") -> None:
        handler = HookHandler(callback=callback, priority=priority, plugin_name=plugin_name)
        self._handlers[hook].append(handler)
        self._handlers[hook].sort(key=lambda h: h.priority, reverse=True)
    
    def unregister(self, hook: Hook, callback: Callable) -> None:
        self._handlers[hook] = [h for h in self._handlers[hook] if h.callback != callback]
    
    def unregister_plugin(self, plugin_name: str) -> None:
        for hook in Hook:
            self._handlers[hook] = [h for h in self._handlers[hook] if h.plugin_name != plugin_name]
    
    async def trigger(self, hook: Hook, **kwargs) -> list:
        results = []
        for handler in self._handlers[hook]:
            try:
                result = handler.callback(**kwargs)
                if hasattr(result, "__await__"):
                    result = await result
                results.append(result)
            except Exception as e:
                print(f"Hook handler error: {e}")
        return results
