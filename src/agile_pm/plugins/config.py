"""Plugin configuration loading and management."""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel, Field, validator
import re


class PluginConfig(BaseModel):
    """Individual plugin configuration."""
    enabled: bool = True
    priority: int = 100
    settings: Dict[str, Any] = Field(default_factory=dict)


class PluginsConfig(BaseModel):
    """Global plugins configuration."""
    plugins_dir: str = "plugins"
    auto_discover: bool = True
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)


class AgilePMConfig(BaseModel):
    """Main .agile-pm.yml configuration."""
    version: str = "1.0"
    project_name: str = "agile-pm"
    
    # Core settings
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Plugin settings
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    
    # Feature flags
    features: Dict[str, bool] = Field(default_factory=dict)
    
    @validator("database_url", "redis_url", pre=True)
    def expand_env_vars(cls, v):
        """Expand environment variables in values."""
        if v and isinstance(v, str):
            return _expand_env_vars(v)
        return v


def _expand_env_vars(value: str) -> str:
    """Expand ${VAR} and $VAR patterns with environment variables."""
    pattern = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')
    
    def replacer(match):
        var_name = match.group(1) or match.group(2)
        default = None
        if ":-" in var_name:
            var_name, default = var_name.split(":-", 1)
        return os.environ.get(var_name, default or "")
    
    return pattern.sub(replacer, value)


class ConfigLoader:
    """Load and manage configuration."""
    
    CONFIG_FILES = [
        ".agile-pm.yml",
        ".agile-pm.yaml",
        "agile-pm.yml",
        "agile-pm.yaml",
    ]
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd()
        self._config: Optional[AgilePMConfig] = None
    
    def load(self) -> AgilePMConfig:
        """Load configuration from file."""
        if self._config:
            return self._config
        
        config_file = self._find_config_file()
        if config_file:
            self._config = self._load_from_file(config_file)
        else:
            self._config = AgilePMConfig()
        
        return self._config
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file."""
        for filename in self.CONFIG_FILES:
            path = self.config_dir / filename
            if path.exists():
                return path
        return None
    
    def _load_from_file(self, path: Path) -> AgilePMConfig:
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        
        # Expand environment variables in all string values
        data = self._expand_all_env_vars(data)
        
        return AgilePMConfig(**data)
    
    def _expand_all_env_vars(self, data: Any) -> Any:
        """Recursively expand environment variables."""
        if isinstance(data, str):
            return _expand_env_vars(data)
        elif isinstance(data, dict):
            return {k: self._expand_all_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_all_env_vars(item) for item in data]
        return data
    
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        config = self.load()
        return [
            name for name, plugin in config.plugins.plugins.items()
            if plugin.enabled
        ]
    
    def get_plugin_config(self, plugin_name: str) -> Optional[PluginConfig]:
        """Get configuration for a specific plugin."""
        config = self.load()
        return config.plugins.plugins.get(plugin_name)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        config = self.load()
        
        if config.database_url and not config.database_url.startswith(("postgresql", "sqlite")):
            errors.append(f"Invalid database_url scheme: {config.database_url}")
        
        if config.redis_url and not config.redis_url.startswith("redis"):
            errors.append(f"Invalid redis_url scheme: {config.redis_url}")
        
        return errors


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config() -> AgilePMConfig:
    """Get the global configuration."""
    global _config_loader
    if not _config_loader:
        _config_loader = ConfigLoader()
    return _config_loader.load()


def reload_config() -> AgilePMConfig:
    """Reload configuration from disk."""
    global _config_loader
    _config_loader = ConfigLoader()
    return _config_loader.load()
