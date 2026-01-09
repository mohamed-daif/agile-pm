"""Core configuration for Agile-PM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""

    enabled: bool = False
    instructions_path: str | None = None
    config_path: str | None = None
    inject: dict[str, bool] = Field(default_factory=lambda: {
        "roles": True,
        "governance": True,
        "project_context": True,
    })


class MemoryConfig(BaseModel):
    """Configuration for memory persistence."""

    enabled: bool = True
    backend: str = "sqlite"  # sqlite, postgresql, redis
    path: str = ".agile-pm/cache/memory.db"


class ObsidianConfig(BaseModel):
    """Configuration for Obsidian integration."""

    enabled: bool = False
    vault_path: str = "docs/workflow/"


class FeaturesConfig(BaseModel):
    """Feature flags for Agile-PM."""

    crews: bool = True
    dashboard: bool = False
    tracing: bool = True
    approval_enforcement: bool = True


class ProjectInfo(BaseModel):
    """Project metadata."""

    name: str = "my-project"
    description: str = ""
    type: str = "python"  # python, typescript-nodejs, java, go, rust


class AgileConfig(BaseModel):
    """Main Agile-PM configuration."""

    version: str = "1.0"
    project: ProjectInfo = Field(default_factory=ProjectInfo)
    providers: dict[str, ProviderConfig] = Field(default_factory=lambda: {
        "github_copilot": ProviderConfig(enabled=True, instructions_path=".github/copilot-instructions.md"),
        "qodo": ProviderConfig(enabled=False),
        "cursor": ProviderConfig(enabled=False),
        "codex": ProviderConfig(enabled=False),
    })
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    obsidian: ObsidianConfig = Field(default_factory=ObsidianConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)

    @classmethod
    def from_file(cls, path: str | Path) -> AgileConfig:
        """Load configuration from a YAML file."""
        path = Path(path)
        if not path.exists():
            return cls()
        
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        
        return cls(**data)

    def to_file(self, path: str | Path) -> None:
        """Save configuration to a YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)


class AgileSettings(BaseSettings):
    """Environment-based settings for Agile-PM."""

    agile_pm_config_path: str = ".agile-pm/config.yaml"
    agile_pm_log_level: str = "INFO"
    agile_pm_trace_enabled: bool = True

    class Config:
        env_prefix = ""
        case_sensitive = False
