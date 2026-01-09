"""Base provider interface for Agile-PM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agile_pm.core.project import AgileProject


class BaseProvider(ABC):
    """Base class for AI provider adapters."""

    name: str = "base"
    
    @abstractmethod
    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to the provider.
        
        Args:
            project: The AgileProject instance
        """
        pass

    @abstractmethod
    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from the provider.
        
        Args:
            project: The AgileProject instance
        """
        pass

    @abstractmethod
    def generate_instructions(self, project: AgileProject) -> str:
        """Generate provider-specific instructions.
        
        Args:
            project: The AgileProject instance
            
        Returns:
            Generated instructions content
        """
        pass


class GitHubCopilotProvider(BaseProvider):
    """GitHub Copilot provider adapter."""

    name = "github_copilot"

    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to GitHub Copilot."""
        instructions_path = project.root_path / ".github" / "copilot-instructions.md"
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = self.generate_instructions(project)
        
        # Append to existing or create new
        if instructions_path.exists():
            existing = instructions_path.read_text()
            if "# Agile-PM Integration" not in existing:
                content = existing + "\n\n" + content
            else:
                # Already linked
                return
        
        instructions_path.write_text(content)

    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from GitHub Copilot."""
        instructions_path = project.root_path / ".github" / "copilot-instructions.md"
        
        if not instructions_path.exists():
            return
        
        content = instructions_path.read_text()
        
        # Remove Agile-PM section
        start_marker = "# Agile-PM Integration"
        end_marker = "# End Agile-PM Integration"
        
        if start_marker in content:
            start = content.find(start_marker)
            end = content.find(end_marker)
            if end != -1:
                end = end + len(end_marker)
            else:
                end = len(content)
            
            content = content[:start] + content[end:]
            content = content.strip()
            instructions_path.write_text(content)

    def generate_instructions(self, project: AgileProject) -> str:
        """Generate GitHub Copilot instructions."""
        return f"""# Agile-PM Integration

This project uses Agile-PM for AI-powered Agile project management.

## Configuration

- Config: `.agile-pm/config.yaml`
- Project: {project.config.project.name}
- Type: {project.config.project.type}

## Enabled Features

- Memory: {project.config.memory.enabled}
- Crews: {project.config.features.crews}
- Tracing: {project.config.features.tracing}
- Approval Enforcement: {project.config.features.approval_enforcement}

## Instructions

When working on this project:
1. Follow the governance rules defined in the project
2. Use the role definitions for task-appropriate behavior
3. Track all work in the configured project management system

# End Agile-PM Integration
"""


class QodoProvider(BaseProvider):
    """Qodo provider adapter."""

    name = "qodo"

    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to Qodo."""
        # TODO: Implement Qodo-specific linking
        pass

    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from Qodo."""
        # TODO: Implement Qodo-specific unlinking
        pass

    def generate_instructions(self, project: AgileProject) -> str:
        """Generate Qodo instructions."""
        return ""


class CursorProvider(BaseProvider):
    """Cursor provider adapter."""

    name = "cursor"

    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to Cursor."""
        rules_path = project.root_path / ".cursor" / "rules"
        rules_path.mkdir(parents=True, exist_ok=True)
        
        agile_pm_rules = rules_path / "agile-pm.mdc"
        content = self.generate_instructions(project)
        agile_pm_rules.write_text(content)

    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from Cursor."""
        agile_pm_rules = project.root_path / ".cursor" / "rules" / "agile-pm.mdc"
        if agile_pm_rules.exists():
            agile_pm_rules.unlink()

    def generate_instructions(self, project: AgileProject) -> str:
        """Generate Cursor rules."""
        return f"""---
description: Agile-PM Integration
globs: ["**/*"]
---

# Agile-PM Integration

Project: {project.config.project.name}
Type: {project.config.project.type}

Follow the Agile-PM governance rules defined in `.agile-pm/config.yaml`.
"""


class CodexProvider(BaseProvider):
    """OpenAI Codex provider adapter."""

    name = "codex"

    def link(self, project: AgileProject) -> None:
        """Link Agile-PM to Codex."""
        # TODO: Implement Codex-specific linking
        pass

    def unlink(self, project: AgileProject) -> None:
        """Unlink Agile-PM from Codex."""
        # TODO: Implement Codex-specific unlinking
        pass

    def generate_instructions(self, project: AgileProject) -> str:
        """Generate Codex instructions."""
        return ""


# Provider registry
_PROVIDERS: dict[str, type[BaseProvider]] = {
    "github_copilot": GitHubCopilotProvider,
    "qodo": QodoProvider,
    "cursor": CursorProvider,
    "codex": CodexProvider,
}


def get_provider(name: str) -> BaseProvider:
    """Get a provider by name.
    
    Args:
        name: Provider name
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If provider not found
    """
    provider_class = _PROVIDERS.get(name)
    if provider_class is None:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {name}. Available: {available}")
    
    return provider_class()
