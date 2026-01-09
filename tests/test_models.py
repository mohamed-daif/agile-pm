"""Test configuration for agile-pm-agents."""

import pytest
from datetime import datetime
from agile_pm.models import (
    RoleDefinition,
    AgentConfig,
    TaskAssignment,
    GovernanceCheck,
    RoleType,
    AgentProvider,
    AgentStatus,
    TaskStatus,
    TaskPriority,
    GovernanceCheckType,
    GovernanceCheckStatus,
)


class TestRoleDefinition:
    """Tests for RoleDefinition model."""

    def test_create_role_definition(self):
        """Test creating a valid role definition."""
        role = RoleDefinition(
            id="backend-engineer",
            name="Backend Engineer",
            type=RoleType.AI_AGENT,
            charter_section="§6.1",
            capabilities=["Write TypeScript code", "Design APIs"],
            constraints=["Must follow coding standards"],
        )

        assert role.id == "backend-engineer"
        assert role.name == "Backend Engineer"
        assert role.type == RoleType.AI_AGENT
        assert role.charter_section == "§6.1"
        assert len(role.capabilities) == 2

    def test_role_definition_validation(self):
        """Test validation of role definition."""
        with pytest.raises(ValueError):
            RoleDefinition(
                id="",  # Invalid: empty ID
                name="Test",
                type=RoleType.HUMAN,
                charter_section="invalid",  # Invalid pattern
            )

    def test_role_definition_timestamps(self):
        """Test automatic timestamp generation."""
        role = RoleDefinition(
            id="test-role",
            name="Test Role",
            type=RoleType.SPECIALIST,
            charter_section="§9.1",
        )

        assert isinstance(role.created_at, datetime)
        assert isinstance(role.updated_at, datetime)


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_create_agent_config(self):
        """Test creating a valid agent configuration."""
        agent = AgentConfig(
            id="agent-001",
            name="Backend Engineer Agent",
            role_id="backend-engineer",
            provider=AgentProvider.ANTHROPIC,
            status=AgentStatus.ACTIVE,
            capabilities=["code-generation", "api-design"],
        )

        assert agent.id == "agent-001"
        assert agent.provider == AgentProvider.ANTHROPIC
        assert agent.status == AgentStatus.ACTIVE

    def test_agent_config_defaults(self):
        """Test default values for agent config."""
        agent = AgentConfig(
            id="agent-002",
            name="Test Agent",
            role_id="qa-engineer",
            provider=AgentProvider.OPENAI,
        )

        assert agent.status == AgentStatus.PENDING
        assert agent.capabilities == []
        assert agent.config == {}


class TestTaskAssignment:
    """Tests for TaskAssignment model."""

    def test_create_task_assignment(self):
        """Test creating a valid task assignment."""
        task = TaskAssignment(
            id="task-001",
            title="Implement user authentication",
            description="Add JWT-based auth to API",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.P0,
            assignee_id="agent-001",
            story_points=5,
            tags=["security", "backend"],
        )

        assert task.id == "task-001"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.P0
        assert task.story_points == 5

    def test_task_story_points_validation(self):
        """Test story points validation."""
        with pytest.raises(ValueError):
            TaskAssignment(
                id="task-002",
                title="Test task",
                story_points=25,  # Invalid: > 21
            )

    def test_task_defaults(self):
        """Test default values for task."""
        task = TaskAssignment(
            id="task-003",
            title="Simple task",
        )

        assert task.status == TaskStatus.NOT_STARTED
        assert task.priority == TaskPriority.P2
        assert task.tags == []
        assert task.completed_at is None


class TestGovernanceCheck:
    """Tests for GovernanceCheck model."""

    def test_create_governance_check(self):
        """Test creating a governance check."""
        check = GovernanceCheck(
            id="check-001",
            type=GovernanceCheckType.APPROVAL_REQUIRED,
            target_id="adr-001",
            target_type="adr",
            status=GovernanceCheckStatus.PENDING,
        )

        assert check.id == "check-001"
        assert check.type == GovernanceCheckType.APPROVAL_REQUIRED
        assert check.status == GovernanceCheckStatus.PENDING

    def test_governance_check_bypass(self):
        """Test governance check bypass scenario."""
        check = GovernanceCheck(
            id="check-002",
            type=GovernanceCheckType.SECURITY_REVIEW,
            target_id="pr-123",
            target_type="deployment",
            status=GovernanceCheckStatus.BYPASSED,
            bypass_reason="Emergency security fix",
        )

        assert check.status == GovernanceCheckStatus.BYPASSED
        assert check.bypass_reason is not None


class TestEnums:
    """Tests for enum values."""

    def test_role_type_values(self):
        """Test role type enum values."""
        assert RoleType.HUMAN == "human"
        assert RoleType.AI_AGENT == "ai-agent"
        assert RoleType.SPECIALIST == "specialist"

    def test_agent_provider_values(self):
        """Test agent provider enum values."""
        assert AgentProvider.OPENAI == "openai"
        assert AgentProvider.ANTHROPIC == "anthropic"
        assert AgentProvider.AZURE == "azure"
        assert AgentProvider.LOCAL == "local"

    def test_task_priority_values(self):
        """Test task priority enum values."""
        assert TaskPriority.P0 == "P0"
        assert TaskPriority.P1 == "P1"
        assert TaskPriority.P2 == "P2"
        assert TaskPriority.P3 == "P3"
