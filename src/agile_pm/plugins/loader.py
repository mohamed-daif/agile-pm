"""Plugin discovery and loading."""
import importlib
import importlib.util
import os
from typing import Optional, Type
from agile_pm.plugins.base import Plugin

class PluginLoader:
    def __init__(self, plugin_dirs: list = None):
        self.plugin_dirs = plugin_dirs or []
        self._discovered: dict = {}
    
    def discover(self) -> dict:
        for plugin_dir in self.plugin_dirs:
            if os.path.isdir(plugin_dir):
                self._scan_directory(plugin_dir)
        return self._discovered
    
    def _scan_directory(self, directory: str) -> None:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                plugin_file = os.path.join(item_path, "plugin.py")
                if os.path.exists(plugin_file):
                    self._load_plugin_module(item, plugin_file)
    
    def _load_plugin_module(self, name: str, path: str) -> None:
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                        self._discovered[name] = attr
        except Exception as e:
            print(f"Failed to load plugin {name}: {e}")
    
    def load(self, name: str) -> Optional[Plugin]:
        if name in self._discovered:
            return self._discovered[name]()
        return None
    
    def load_from_package(self, package_name: str) -> Optional[Plugin]:
        try:
            module = importlib.import_module(package_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                    return attr()
        except ImportError:
            return None
        return None
