# Plugin Architecture

## Components

```
┌─────────────────────────────────────────────────┐
│                Plugin Registry                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Plugin  │  │  Plugin  │  │  Plugin  │      │
│  │ (GitHub) │  │  (Jira)  │  │ (Custom) │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │             │
│       └─────────────┼─────────────┘             │
│                     │                           │
│              ┌──────▼──────┐                    │
│              │ Hook Manager │                    │
│              └──────────────┘                    │
└─────────────────────────────────────────────────┘
```

## Plugin Lifecycle

1. **Discovery** - Plugin loader scans directories
2. **Loading** - Plugin class is imported
3. **Initialization** - `initialize(config)` called
4. **Registration** - Plugin added to registry
5. **Hook Registration** - Plugin registers for events
6. **Operation** - Plugin responds to hooks
7. **Shutdown** - `shutdown()` called on exit

## Key Classes

- `Plugin` - Base class for all plugins
- `PluginLoader` - Discovers and loads plugins
- `PluginRegistry` - Manages plugin lifecycle
- `HookManager` - Event dispatch system
