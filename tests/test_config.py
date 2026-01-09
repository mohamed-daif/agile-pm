"""Tests for Agile-PM core configuration."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from agile_pm.core.config import AgileConfig, ProjectInfo, MemoryConfig


class TestAgileConfig:
    """Tests for AgileConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AgileConfig()
        
        assert config.version == "1.0"
        assert config.project.name == "my-project"
        assert config.project.type == "python"
        assert config.memory.enabled is True
        assert config.memory.backend == "sqlite"
        assert config.features.crews is True
        assert config.features.approval_enforcement is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = AgileConfig(
            project=ProjectInfo(name="test-project", type="typescript-nodejs"),
            memory=MemoryConfig(enabled=False),
        )
        
        assert config.project.name == "test-project"
        assert config.project.type == "typescript-nodejs"
        assert config.memory.enabled is False

    def test_config_from_file(self):
        """Test loading configuration from file."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create a config file
            config_content = """
version: "1.0"
project:
  name: test-project
  type: python
memory:
  enabled: true
  backend: sqlite
"""
            config_path.write_text(config_content)
            
            config = AgileConfig.from_file(config_path)
            assert config.project.name == "test-project"

    def test_config_to_file(self):
        """Test saving configuration to file."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            config = AgileConfig(
                project=ProjectInfo(name="save-test"),
            )
            config.to_file(config_path)
            
            assert config_path.exists()
            content = config_path.read_text()
            assert "save-test" in content

    def test_config_from_nonexistent_file(self):
        """Test loading from nonexistent file returns default config."""
        config = AgileConfig.from_file("/nonexistent/path/config.yaml")
        assert config.project.name == "my-project"


class TestProviderConfig:
    """Tests for provider configuration."""

    def test_default_providers(self):
        """Test default provider configuration."""
        config = AgileConfig()
        
        assert "github_copilot" in config.providers
        assert config.providers["github_copilot"].enabled is True
        assert "qodo" in config.providers
        assert config.providers["qodo"].enabled is False
