"""Tests for Agile-PM project management."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from agile_pm.core.project import AgileProject
from agile_pm.core.config import AgileConfig, ProjectInfo


class TestAgileProject:
    """Tests for AgileProject."""

    def test_project_init(self):
        """Test project initialization."""
        with TemporaryDirectory() as tmpdir:
            root_path = Path(tmpdir)
            
            project = AgileProject.init(
                root_path=root_path,
                project=ProjectInfo(name="test-init"),
            )
            
            assert project.root_path == root_path
            assert project.config.project.name == "test-init"
            
            # Check .agile-pm structure
            agile_pm_path = root_path / ".agile-pm"
            assert agile_pm_path.exists()
            assert (agile_pm_path / "config.yaml").exists()
            assert (agile_pm_path / "instructions").exists()
            assert (agile_pm_path / "overrides").exists()
            assert (agile_pm_path / "cache").exists()
            assert (agile_pm_path / "cache" / ".gitignore").exists()

    def test_project_from_config(self):
        """Test loading project from config."""
        with TemporaryDirectory() as tmpdir:
            root_path = Path(tmpdir)
            
            # First initialize
            AgileProject.init(root_path=root_path, project=ProjectInfo(name="test-load"))
            
            # Then load
            project = AgileProject.from_config(root_path / ".agile-pm" / "config.yaml")
            assert project.config.project.name == "test-load"

    def test_project_uninstall(self):
        """Test project uninstallation."""
        with TemporaryDirectory() as tmpdir:
            root_path = Path(tmpdir)
            
            project = AgileProject.init(root_path=root_path)
            assert (root_path / ".agile-pm").exists()
            
            project.uninstall()
            assert not (root_path / ".agile-pm").exists()

    def test_project_uninstall_keep_overrides(self):
        """Test project uninstallation with keeping overrides."""
        with TemporaryDirectory() as tmpdir:
            root_path = Path(tmpdir)
            
            project = AgileProject.init(root_path=root_path)
            
            # Create a custom override
            override_path = root_path / ".agile-pm" / "overrides" / "test.yaml"
            override_path.write_text("test: true")
            
            project.uninstall(keep_overrides=True)
            
            assert not (root_path / ".agile-pm").exists()
            assert (root_path / ".agile-pm-overrides-backup").exists()
