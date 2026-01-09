"""Plugin configuration."""
from typing import Any, Optional
from pydantic import BaseModel

class PluginConfig(BaseModel):
    enabled: bool = True
    settings: dict = {}
    
class PluginsConfig(BaseModel):
    plugins: dict = {}
    
    def get_plugin_config(self, name: str) -> Optional[PluginConfig]:
        if name in self.plugins:
            return PluginConfig(**self.plugins[name])
        return None
    
    def is_enabled(self, name: str) -> bool:
        config = self.get_plugin_config(name)
        return config.enabled if config else False
