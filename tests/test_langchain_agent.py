"""Tests for LangChain agent implementation.

These tests verify the LangChain agent components without
requiring actual LLM API calls (using mocks).
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from agile_pm.langchain.agent import (
    BaseAgilePMAgent,
    AgentContext,
    AgentResult,
)
from agile_pm.langchain.tools import (
    ObsidianTool,
    GitHubMCPTool,
    SerenaTool,
    get_tool_registry,
)
from agile_pm.models import (
    RoleDefinition,
    RoleType,
    AgentConfig,
    AgentStatus,
    AgentProvider,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = MagicMock()
    mock.invoke = MagicMock(return_value="Mock response")
    mock.ainvoke = AsyncMock(return_value="Async mock response")
    return mock


@pytest.fixture
def role_definition():
    """Create a test role definition."""
    return RoleDefinition(
        id="test-role-001",
        name="Test Backend Engineer",
        type=RoleType.AI_AGENT,
        charter_section="§6.1",
        capabilities=["code_generation", "testing"],
        constraints=["Must follow governance"],
    )


@pytest.fixture
def agent_config(role_definition):
    """Create a test agent config."""
    return AgentConfig(
        id="agent-test-001",
        name="Test Agent",
        role_id=role_definition.id,
        provider=AgentProvider.OPENAI,
        status=AgentStatus.ACTIVE,
        capabilities=["code_generation", "testing"],
    )


@pytest.fixture
def agent_context(role_definition):
    """Create a test agent context."""
    return AgentContext(
        session_id="session-test-001",
        role=role_definition,
        task=None,
        governance_mode=True,
        obsidian_path="cm-workflow",
        governance_path=".github/governance",
    )


# ============================================================================
# Agent Context Tests
# ============================================================================


class TestAgentContext:
    """Tests for AgentContext model."""

    def test_create_context(self, role_definition):
        """Test creating an agent context."""
        context = AgentContext(
            session_id="test-session",
            role=role_definition,
        )
        assert context.session_id == "test-session"
        assert context.role.name == "Test Backend Engineer"
        assert context.governance_mode is True

    def test_context_defaults(self, role_definition):
        """Test context default values."""
        context = AgentContext(
            session_id="test",
            role=role_definition,
        )
        assert context.obsidian_path == "cm-workflow"
        assert context.governance_path == ".github/governance"
        assert context.chat_history == []
        assert context.task is None

    def test_context_with_custom_paths(self, role_definition):
        """Test context with custom paths."""
        context = AgentContext(
            session_id="test",
            role=role_definition,
            obsidian_path="custom/vault",
            governance_path="custom/governance",
        )
        assert context.obsidian_path == "custom/vault"
        assert context.governance_path == "custom/governance"

    def test_context_timestamps(self, role_definition):
        """Test context timestamp generation."""
        before = datetime.utcnow()
        context = AgentContext(
            session_id="test",
            role=role_definition,
        )
        after = datetime.utcnow()
        assert before <= context.started_at <= after


# ============================================================================
# Agent Result Tests
# ============================================================================


class TestAgentResult:
    """Tests for AgentResult model."""

    def test_create_success_result(self):
        """Test creating a success result."""
        result = AgentResult(
            success=True,
            output="Task completed successfully",
            artifacts=["cm-workflow/tasks/TEST-001.md"],
            duration_ms=1500,
        )
        assert result.success is True
        assert result.output == "Task completed successfully"
        assert len(result.artifacts) == 1
        assert result.error is None

    def test_create_error_result(self):
        """Test creating an error result."""
        result = AgentResult(
            success=False,
            output="",
            error="Governance check failed",
            duration_ms=100,
        )
        assert result.success is False
        assert result.error == "Governance check failed"

    def test_result_with_governance_checks(self):
        """Test result with governance checks."""
        result = AgentResult(
            success=True,
            output="Done",
            governance_checks=[
                {"type": "approval", "passed": True},
                {"type": "role_switch", "passed": True},
            ],
        )
        assert len(result.governance_checks) == 2

    def test_result_defaults(self):
        """Test result default values."""
        result = AgentResult(
            success=True,
            output="Done",
        )
        assert result.artifacts == []
        assert result.governance_checks == []
        assert result.duration_ms == 0
        assert result.metadata == {}


# ============================================================================
# Tool Registry Tests
# ============================================================================


class TestToolRegistry:
    """Tests for tool registration."""

    def test_get_tool_registry(self):
        """Test getting the tool registry."""
        registry = get_tool_registry()
        assert isinstance(registry, dict)
        assert len(registry) > 0

    def test_obsidian_tool_registered(self):
        """Test that ObsidianTool is registered."""
        registry = get_tool_registry()
        assert "obsidiantool" in registry

    def test_github_tool_registered(self):
        """Test that GitHubMCPTool is registered."""
        registry = get_tool_registry()
        assert "githubmcptool" in registry

    def test_serena_tool_registered(self):
        """Test that SerenaTool is registered."""
        registry = get_tool_registry()
        assert "serenatool" in registry


# ============================================================================
# Obsidian Tool Tests
# ============================================================================


class TestObsidianTool:
    """Tests for ObsidianTool."""

    def test_tool_instantiation(self):
        """Test creating an ObsidianTool."""
        tool = ObsidianTool(vault_path="cm-workflow")
        assert tool.name == "obsidian"
        assert tool.vault_path == "cm-workflow"

    def test_tool_description(self):
        """Test tool description is set."""
        tool = ObsidianTool()
        assert "Obsidian" in tool.description
        assert "workflow" in tool.description.lower()

    @patch("builtins.open", create=True)
    @patch("os.path.exists")
    def test_read_file(self, mock_exists, mock_open):
        """Test reading a file from vault."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "---\ntitle: Test\n---\n\n# Test File"
        )

        tool = ObsidianTool(vault_path="cm-workflow")
        result = tool._run("sprints/current.md")

        assert "Test File" in result
        mock_exists.assert_called_once()

    @patch("os.path.exists")
    def test_read_nonexistent_file(self, mock_exists):
        """Test reading a non-existent file raises error."""
        mock_exists.return_value = False

        tool = ObsidianTool(vault_path="cm-workflow")

        from langchain_core.tools import ToolException

        with pytest.raises(ToolException, match="not found"):
            tool._run("nonexistent.md")


# ============================================================================
# GitHub MCP Tool Tests
# ============================================================================


class TestGitHubMCPTool:
    """Tests for GitHubMCPTool."""

    def test_tool_instantiation(self):
        """Test creating a GitHubMCPTool."""
        tool = GitHubMCPTool()
        assert tool.name == "github_mcp"

    def test_tool_description(self):
        """Test tool description is set."""
        tool = GitHubMCPTool()
        assert "GitHub" in tool.description

    def test_tool_actions(self):
        """Test tool supports required actions."""
        tool = GitHubMCPTool()
        # Verify description mentions key actions
        assert "issue" in tool.description.lower() or "pr" in tool.description.lower()


# ============================================================================
# Serena Tool Tests
# ============================================================================


class TestSerenaTool:
    """Tests for SerenaTool."""

    def test_tool_instantiation(self):
        """Test creating a SerenaTool."""
        tool = SerenaTool()
        assert tool.name == "serena"

    def test_tool_description(self):
        """Test tool description is set."""
        tool = SerenaTool()
        assert "code" in tool.description.lower() or "symbol" in tool.description.lower()


# ============================================================================
# Agent Config Tests
# ============================================================================


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_active_agent(self, agent_config):
        """Test agent status is active."""
        assert agent_config.status == AgentStatus.ACTIVE

    def test_provider_setting(self, agent_config):
        """Test provider is set."""
        assert agent_config.provider == AgentProvider.OPENAI

    def test_capabilities_list(self, agent_config):
        """Test capabilities are set."""
        assert "code_generation" in agent_config.capabilities
        assert "testing" in agent_config.capabilities


# ============================================================================
# Integration Tests (Mocked)
# ============================================================================


class TestAgentIntegration:
    """Integration tests with mocked LLM."""

    def test_tool_chain(self, mock_llm):
        """Test tools can be chained in an agent."""
        tools = [
            ObsidianTool(vault_path="cm-workflow"),
            GitHubMCPTool(),
            SerenaTool(),
        ]

        # Verify all tools have required attributes
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "_run")

    @pytest.mark.asyncio
    async def test_async_tool_execution(self):
        """Test async tool execution."""
        tool = ObsidianTool(vault_path="cm-workflow")

        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(
                            return_value=MagicMock(read=MagicMock(return_value="test"))
                        ),
                        __exit__=MagicMock(return_value=False),
                    )
                ),
            ):
                result = await tool._arun("test.md")
                assert result == "test"
