"""Tests for CrewAI crew implementation.

These tests verify the CrewAI orchestration components
without requiring actual LLM API calls (using mocks).
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from agile_pm.crewai.crew import (
    AgilePMCrew,
    CrewConfig,
    CrewResult,
)
from agile_pm.models import TaskPriority, TaskStatus


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def crew_config():
    """Create a test crew config."""
    return CrewConfig(
        name="Test Sprint Crew",
        description="Test crew for unit testing",
        process="sequential",
        verbose=False,
        governance_mode=True,
        obsidian_path="cm-workflow",
    )


@pytest.fixture
def mock_agent():
    """Create a mock CrewAI agent."""
    agent = MagicMock()
    agent.role = "Backend Engineer"
    agent.goal = "Implement features"
    agent.backstory = "Expert backend developer"
    return agent


@pytest.fixture
def mock_task():
    """Create a mock CrewAI task."""
    task = MagicMock()
    task.description = "Implement user authentication"
    task.expected_output = "Working auth module"
    return task


# ============================================================================
# CrewConfig Tests
# ============================================================================


class TestCrewConfig:
    """Tests for CrewConfig model."""

    def test_create_crew_config(self, crew_config):
        """Test creating a crew config."""
        assert crew_config.name == "Test Sprint Crew"
        assert crew_config.process == "sequential"
        assert crew_config.governance_mode is True

    def test_config_defaults(self):
        """Test crew config default values."""
        config = CrewConfig(
            name="Default Crew",
            description="Test",
        )
        assert config.process == "sequential"
        assert config.verbose is True
        assert config.governance_mode is True
        assert config.obsidian_path == "cm-workflow"

    def test_hierarchical_process(self):
        """Test hierarchical process type."""
        config = CrewConfig(
            name="Hierarchical Crew",
            description="Uses hierarchical process",
            process="hierarchical",
        )
        assert config.process == "hierarchical"


# ============================================================================
# CrewResult Tests
# ============================================================================


class TestCrewResult:
    """Tests for CrewResult model."""

    def test_create_success_result(self):
        """Test creating a successful crew result."""
        result = CrewResult(
            success=True,
            output="Task completed",
            tasks_completed=3,
            agents_used=["PM", "Engineer", "QA"],
            artifacts=["cm-workflow/tasks/TASK-001.md"],
        )
        assert result.success is True
        assert result.tasks_completed == 3
        assert len(result.agents_used) == 3

    def test_create_failure_result(self):
        """Test creating a failed crew result."""
        result = CrewResult(
            success=False,
            output="Error: LLM API unavailable",
            tasks_completed=0,
            agents_used=["PM"],
        )
        assert result.success is False
        assert result.tasks_completed == 0

    def test_result_with_governance_checks(self):
        """Test result with governance checks."""
        result = CrewResult(
            success=True,
            output="Done",
            tasks_completed=2,
            agents_used=["Engineer"],
            governance_checks=[
                {"type": "approval", "passed": True},
            ],
        )
        assert len(result.governance_checks) == 1

    def test_result_defaults(self):
        """Test result default values."""
        result = CrewResult(
            success=True,
            output="Done",
            tasks_completed=1,
            agents_used=["Agent"],
        )
        assert result.artifacts == []
        assert result.governance_checks == []


# ============================================================================
# AgilePMCrew Tests
# ============================================================================


class TestAgilePMCrew:
    """Tests for AgilePMCrew class."""

    def test_crew_instantiation(self, crew_config, mock_agent, mock_task):
        """Test creating an AgilePMCrew."""
        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )
        assert crew.config.name == "Test Sprint Crew"
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1

    def test_crew_with_multiple_agents(self, crew_config, mock_agent, mock_task):
        """Test crew with multiple agents."""
        agent2 = MagicMock()
        agent2.role = "QA Engineer"

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent, agent2],
            tasks=[mock_task],
        )
        assert len(crew.agents) == 2

    @patch("agile_pm.crewai.crew.Crew")
    def test_crew_build(self, mock_crew_class, crew_config, mock_agent, mock_task):
        """Test building the crew."""
        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )

        result = crew.build()

        mock_crew_class.assert_called_once()
        assert crew._crew is not None

    @patch("agile_pm.crewai.crew.Crew")
    def test_crew_kickoff_success(self, mock_crew_class, crew_config, mock_agent, mock_task):
        """Test successful crew kickoff."""
        # Setup mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Task completed successfully"
        mock_crew_class.return_value = mock_crew_instance

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )

        result = crew.kickoff({"input": "test"})

        assert result.success is True
        assert result.tasks_completed == 1
        mock_crew_instance.kickoff.assert_called_once_with({"input": "test"})

    @patch("agile_pm.crewai.crew.Crew")
    def test_crew_kickoff_failure(self, mock_crew_class, crew_config, mock_agent, mock_task):
        """Test crew kickoff with failure."""
        # Setup mock to raise exception
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.side_effect = Exception("API Error")
        mock_crew_class.return_value = mock_crew_instance

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )

        result = crew.kickoff()

        assert result.success is False
        assert "API Error" in result.output
        assert result.tasks_completed == 0

    @patch("agile_pm.crewai.crew.Crew")
    def test_crew_kickoff_without_inputs(self, mock_crew_class, crew_config, mock_agent, mock_task):
        """Test crew kickoff without inputs."""
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Done"
        mock_crew_class.return_value = mock_crew_instance

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )

        result = crew.kickoff()

        # Should be called with empty dict
        mock_crew_instance.kickoff.assert_called_once_with({})


# ============================================================================
# Process Type Tests
# ============================================================================


class TestCrewProcessTypes:
    """Tests for different crew process types."""

    @patch("agile_pm.crewai.crew.Crew")
    @patch("agile_pm.crewai.crew.Process")
    def test_sequential_process(self, mock_process, mock_crew, mock_agent, mock_task):
        """Test sequential process type."""
        config = CrewConfig(
            name="Sequential",
            description="Sequential test",
            process="sequential",
        )
        mock_process.sequential = "seq"

        crew = AgilePMCrew(config=config, agents=[mock_agent], tasks=[mock_task])
        crew.build()

        mock_crew.assert_called_once()
        call_kwargs = mock_crew.call_args.kwargs
        assert call_kwargs["process"] == "seq"

    @patch("agile_pm.crewai.crew.Crew")
    @patch("agile_pm.crewai.crew.Process")
    def test_hierarchical_process(self, mock_process, mock_crew, mock_agent, mock_task):
        """Test hierarchical process type."""
        config = CrewConfig(
            name="Hierarchical",
            description="Hierarchical test",
            process="hierarchical",
        )
        mock_process.sequential = "seq"
        mock_process.hierarchical = "hier"

        crew = AgilePMCrew(config=config, agents=[mock_agent], tasks=[mock_task])
        crew.build()

        mock_crew.assert_called_once()
        call_kwargs = mock_crew.call_args.kwargs
        assert call_kwargs["process"] == "hier"


# ============================================================================
# Integration Tests (Mocked)
# ============================================================================


class TestCrewIntegration:
    """Integration tests with mocked CrewAI."""

    @patch("agile_pm.crewai.crew.Crew")
    def test_full_sprint_workflow(self, mock_crew_class, crew_config):
        """Test a full sprint workflow with multiple agents and tasks."""
        # Create agents
        pm_agent = MagicMock()
        pm_agent.role = "Technical PM"

        engineer_agent = MagicMock()
        engineer_agent.role = "Backend Engineer"

        qa_agent = MagicMock()
        qa_agent.role = "QA Executor"

        # Create tasks
        plan_task = MagicMock()
        plan_task.description = "Create sprint plan"

        implement_task = MagicMock()
        implement_task.description = "Implement features"

        test_task = MagicMock()
        test_task.description = "Run tests"

        # Setup mock
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Sprint completed"
        mock_crew_class.return_value = mock_crew_instance

        # Execute
        crew = AgilePMCrew(
            config=crew_config,
            agents=[pm_agent, engineer_agent, qa_agent],
            tasks=[plan_task, implement_task, test_task],
        )

        result = crew.kickoff({"sprint": "Sprint 20"})

        assert result.success is True
        assert result.tasks_completed == 3
        assert len(result.agents_used) == 3

    def test_crew_governance_mode(self, crew_config, mock_agent, mock_task):
        """Test that governance mode is configured."""
        assert crew_config.governance_mode is True

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )
        assert crew.config.governance_mode is True

    def test_crew_obsidian_path(self, crew_config, mock_agent, mock_task):
        """Test that Obsidian path is configured."""
        assert crew_config.obsidian_path == "cm-workflow"

        crew = AgilePMCrew(
            config=crew_config,
            agents=[mock_agent],
            tasks=[mock_task],
        )
        assert crew.config.obsidian_path == "cm-workflow"
