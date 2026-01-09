# Provider Adapters

This document describes how to implement and use AI provider adapters in Agile-PM.

## Overview

Provider adapters allow Agile-PM to integrate with different AI coding assistants. Each adapter implements the `BaseProvider` interface to:

1. **Link** - Connect Agile-PM to the provider
2. **Unlink** - Disconnect Agile-PM from the provider
3. **Generate Instructions** - Create provider-specific instruction content

## Supported Providers

### GitHub Copilot

**Status:** ✅ Full Support

GitHub Copilot integration works by:
1. Creating/updating `.github/copilot-instructions.md`
2. Injecting Agile-PM governance rules
3. Providing project context to Copilot

```yaml
# .agile-pm/config.yaml
providers:
  github_copilot:
    enabled: true
    instructions_path: .github/copilot-instructions.md
    inject:
      roles: true
      governance: true
      project_context: true
```

### Cursor

**Status:** ✅ Full Support

Cursor integration works by:
1. Creating `.cursor/rules/agile-pm.mdc`
2. Using Cursor's MDC format for rules
3. Auto-updating on configuration changes

```yaml
# .agile-pm/config.yaml
providers:
  cursor:
    enabled: true
    config_path: .cursor/rules/agile-pm.mdc
    inject:
      roles: true
      governance: true
```

### Qodo

**Status:** 🚧 Planned

Qodo integration will support:
- Custom instruction injection
- Test generation hints
- Code review rules

### OpenAI Codex

**Status:** 🚧 Planned

Codex integration will support:
- System prompt injection
- Context management
- Tool definitions

## Implementing a Custom Provider

To create a custom provider adapter:

```python
from agile_pm.providers.base import BaseProvider
from agile_pm.core.project import AgileProject

class MyCustomProvider(BaseProvider):
    """Custom provider adapter."""
    
    name = "my_custom"
    
    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to the provider."""
        instructions = self.generate_instructions(project)
        
        # Write instructions to provider-specific location
        instructions_path = project.root_path / ".my-custom" / "config.json"
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        instructions_path.write_text(instructions)
    
    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from the provider."""
        instructions_path = project.root_path / ".my-custom" / "config.json"
        if instructions_path.exists():
            instructions_path.unlink()
    
    def generate_instructions(self, project: AgileProject) -> str:
        """Generate provider-specific instructions."""
        return json.dumps({
            "project": project.config.project.name,
            "rules": "Follow Agile-PM governance",
        })
```

### Registering the Provider

Add your provider to the registry:

```python
from agile_pm.providers.base import _PROVIDERS

_PROVIDERS["my_custom"] = MyCustomProvider
```

## Configuration Options

### `inject` Settings

Control what Agile-PM injects into provider instructions:

| Option | Default | Description |
|--------|---------|-------------|
| `roles` | `true` | Inject role definitions from governance |
| `governance` | `true` | Inject governance rules |
| `project_context` | `true` | Inject project metadata |

### `instructions_path`

Path where provider instructions are written. Supports:
- Absolute paths
- Relative paths (from project root)
- Template variables: `{project_name}`, `{project_type}`

### `config_path`

Alternative configuration file path for providers that use config files instead of markdown.

## Best Practices

1. **Minimal Changes** - Only modify provider config files, don't overwrite user content
2. **Markers** - Use clear start/end markers for Agile-PM sections
3. **Backup** - Keep backup of original config before modification
4. **Idempotent** - Link/unlink operations should be safe to run multiple times

## Provider API Reference

### `BaseProvider.link(project: AgileProject) -> None`

Connect Agile-PM to the provider. Should:
- Create/update provider configuration files
- Inject Agile-PM governance content
- Handle existing content gracefully

### `BaseProvider.unlink(project: AgileProject) -> None`

Disconnect Agile-PM from the provider. Should:
- Remove Agile-PM sections from config files
- Preserve user content
- Handle missing files gracefully

### `BaseProvider.generate_instructions(project: AgileProject) -> str`

Generate provider-specific instruction content. Should:
- Use project configuration
- Format appropriately for the provider
- Include governance and context as configured
