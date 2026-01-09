"""Test plugin loader."""
import pytest
import tempfile
import os


class TestPluginLoader:
    """Test plugin discovery and loading."""

    def test_discover_empty_dir(self):
        """Test discovery with empty directory."""
        from agile_pm.plugins.loader import PluginLoader
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PluginLoader(plugin_dirs=[tmpdir])
            discovered = loader.discover()
            assert discovered == {}

    def test_load_nonexistent_plugin(self):
        """Test loading nonexistent plugin."""
        from agile_pm.plugins.loader import PluginLoader
        loader = PluginLoader()
        plugin = loader.load("nonexistent")
        assert plugin is None
