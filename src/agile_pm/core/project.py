"""Project management for Agile-PM."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from agile_pm.core.config import AgileConfig

if TYPE_CHECKING:
    from agile_pm.memory import MemoryManager
    from agile_pm.crews import CrewManager
    from agile_pm.dashboard import DashboardServer


class AgileProject:
    """Main entry point for Agile-PM project integration."""

    def __init__(self, config: AgileConfig, root_path: Path | None = None) -> None:
        """Initialize an Agile-PM project.
        
        Args:
            config: Agile-PM configuration
            root_path: Project root path (defaults to current directory)
        """
        self.config = config
        self.root_path = root_path or Path.cwd()
        self._memory: MemoryManager | None = None
        self._crews: CrewManager | None = None
        self._dashboard: DashboardServer | None = None

    @classmethod
    def from_config(cls, config_path: str | Path = ".agile-pm/config.yaml") -> AgileProject:
        """Load project from configuration file.
        
        Args:
            config_path: Path to config.yaml
            
        Returns:
            Initialized AgileProject instance
        """
        config_path = Path(config_path)
        config = AgileConfig.from_file(config_path)
        root_path = config_path.parent.parent if config_path.parent.name == ".agile-pm" else config_path.parent
        return cls(config, root_path)

    @classmethod
    def init(cls, root_path: Path | None = None, **kwargs) -> AgileProject:
        """Initialize a new Agile-PM project.
        
        Args:
            root_path: Project root path
            **kwargs: Configuration overrides
            
        Returns:
            Initialized AgileProject instance
        """
        root_path = root_path or Path.cwd()
        agile_pm_path = root_path / ".agile-pm"
        agile_pm_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (agile_pm_path / "instructions").mkdir(exist_ok=True)
        (agile_pm_path / "overrides").mkdir(exist_ok=True)
        (agile_pm_path / "cache").mkdir(exist_ok=True)
        
        # Create .gitignore for cache
        gitignore = agile_pm_path / "cache" / ".gitignore"
        gitignore.write_text("*\n!.gitignore\n")
        
        # Create config
        config = AgileConfig(**kwargs)
        config.to_file(agile_pm_path / "config.yaml")
        
        return cls(config, root_path)

    @property
    def memory(self) -> MemoryManager:
        """Get the memory manager (lazy initialization)."""
        if self._memory is None:
            from agile_pm.memory import MemoryManager
            self._memory = MemoryManager(self.config.memory)
        return self._memory

    @property
    def crews(self) -> CrewManager:
        """Get the crew manager (lazy initialization)."""
        if self._crews is None:
            from agile_pm.crews import CrewManager
            self._crews = CrewManager(self.config)
        return self._crews

    @property
    def dashboard(self) -> DashboardServer:
        """Get the dashboard server (lazy initialization)."""
        if self._dashboard is None:
            from agile_pm.dashboard import DashboardServer
            self._dashboard = DashboardServer(self.config)
        return self._dashboard

    def link_provider(self, provider_name: str) -> None:
        """Link Agile-PM to an AI provider.
        
        Args:
            provider_name: Name of provider (github_copilot, qodo, cursor, codex)
        """
        from agile_pm.providers import get_provider
        
        provider = get_provider(provider_name)
        provider.link(self)

    def sync(self) -> None:
        """Sync all provider configurations."""
        for provider_name, provider_config in self.config.providers.items():
            if provider_config.enabled:
                self.link_provider(provider_name)

    def uninstall(self, keep_overrides: bool = False) -> None:
        """Remove Agile-PM from the project.
        
        Args:
            keep_overrides: If True, preserve custom overrides
        """
        import shutil
        
        agile_pm_path = self.root_path / ".agile-pm"
        
        if keep_overrides:
            # Move overrides to a backup location
            overrides_path = agile_pm_path / "overrides"
            if overrides_path.exists():
                backup_path = self.root_path / ".agile-pm-overrides-backup"
                shutil.move(str(overrides_path), str(backup_path))
        
        # Remove .agile-pm folder
        if agile_pm_path.exists():
            shutil.rmtree(agile_pm_path)
        
        # Clean up provider configs
        for provider_name, provider_config in self.config.providers.items():
            if provider_config.enabled:
                from agile_pm.providers import get_provider
                provider = get_provider(provider_name)
                provider.unlink(self)
