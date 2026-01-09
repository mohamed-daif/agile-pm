"""Base plugin class."""
from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel

class PluginMetadata(BaseModel):
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: list = []
    
class Plugin(ABC):
    def __init__(self):
        self._initialized = False
        self._config: dict = {}
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def version(self) -> str:
        return self.metadata.version
    
    @abstractmethod
    async def initialize(self, config: dict) -> None:
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        pass
    
    def register_hooks(self, hook_manager: Any) -> None:
        pass
    
    async def health_check(self) -> dict:
        return {"status": "healthy", "plugin": self.name}
