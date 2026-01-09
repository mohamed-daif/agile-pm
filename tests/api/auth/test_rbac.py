"""Test RBAC authorization."""
import pytest


class TestRBACManager:
    """Test Role-Based Access Control."""

    def test_admin_has_all_permissions(self):
        """Test admin role has all permissions."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        assert manager.has_permission(["admin"], Permission.READ_AGENTS)
        assert manager.has_permission(["admin"], Permission.WRITE_AGENTS)
        assert manager.has_permission(["admin"], Permission.DELETE_AGENTS)
        assert manager.has_permission(["admin"], Permission.EXECUTE_AGENTS)

    def test_viewer_has_read_only(self):
        """Test viewer role has read-only access."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        assert manager.has_permission(["viewer"], Permission.READ_AGENTS)
        assert not manager.has_permission(["viewer"], Permission.WRITE_AGENTS)
        assert not manager.has_permission(["viewer"], Permission.DELETE_AGENTS)

    def test_operator_permissions(self):
        """Test operator role permissions."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        assert manager.has_permission(["operator"], Permission.READ_AGENTS)
        assert manager.has_permission(["operator"], Permission.WRITE_AGENTS)
        assert manager.has_permission(["operator"], Permission.EXECUTE_AGENTS)

    def test_get_permissions(self):
        """Test getting all permissions for roles."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        permissions = manager.get_permissions(["viewer"])
        assert Permission.READ_AGENTS in permissions
        assert Permission.WRITE_AGENTS not in permissions

    def test_check_permission_raises(self):
        """Test permission check raises on failure."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        with pytest.raises(PermissionError):
            manager.check_permission(["viewer"], Permission.DELETE_AGENTS)

    def test_multiple_roles(self):
        """Test combining multiple roles."""
        from agile_pm.api.auth.rbac import RBACManager, Permission
        manager = RBACManager()
        permissions = manager.get_permissions(["viewer", "service"])
        # Should have union of both roles
        assert Permission.READ_AGENTS in permissions
        assert Permission.EXECUTE_AGENTS in permissions
