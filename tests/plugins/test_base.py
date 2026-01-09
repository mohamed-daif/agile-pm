"""Test plugin base class."""
import pytest


class TestPluginBase:
    """Test Plugin base class."""

    def test_plugin_metadata(self):
        """Test plugin metadata structure."""
        from agile_pm.plugins.base import PluginMetadata
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author"
        )
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"

    def test_plugin_abstract_methods(self):
        """Test that Plugin requires abstract methods."""
        from agile_pm.plugins.base import Plugin
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            Plugin()
