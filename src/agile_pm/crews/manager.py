"""Crew manager implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agile_pm.core.config import AgileConfig

if TYPE_CHECKING:
    from crewai import Crew, Agent, Task


class CrewManager:
    """Manages CrewAI crews for Agile-PM."""

    def __init__(self, config: AgileConfig) -> None:
        """Initialize crew manager.
        
        Args:
            config: Agile-PM configuration
        """
        self.config = config
        self._crews: dict[str, Crew] = {}
        self._agents: dict[str, Agent] = {}

    def create_planning_crew(self) -> Crew:
        """Create a planning crew for sprint/task planning.
        
        Returns:
            A CrewAI crew for planning
        """
        from crewai import Crew, Agent, Task
        
        tech_lead = Agent(
            role="Technical Lead",
            goal="Create actionable technical plans from requirements",
            backstory="Expert in translating business requirements into technical tasks",
            verbose=True,
        )
        
        architect = Agent(
            role="Solution Architect",
            goal="Design scalable and maintainable solutions",
            backstory="Expert in system design and architecture patterns",
            verbose=True,
        )
        
        self._agents["tech_lead"] = tech_lead
        self._agents["architect"] = architect
        
        crew = Crew(
            agents=[tech_lead, architect],
            tasks=[],  # Tasks added dynamically
            verbose=True,
        )
        
        self._crews["planning"] = crew
        return crew

    def create_review_crew(self) -> Crew:
        """Create a review crew for code/architecture review.
        
        Returns:
            A CrewAI crew for review
        """
        from crewai import Crew, Agent, Task
        
        reviewer = Agent(
            role="Code Reviewer",
            goal="Ensure code quality and adherence to standards",
            backstory="Expert in code review and quality assurance",
            verbose=True,
        )
        
        security_analyst = Agent(
            role="Security Analyst",
            goal="Identify security vulnerabilities and risks",
            backstory="Expert in application security and threat modeling",
            verbose=True,
        )
        
        self._agents["reviewer"] = reviewer
        self._agents["security_analyst"] = security_analyst
        
        crew = Crew(
            agents=[reviewer, security_analyst],
            tasks=[],
            verbose=True,
        )
        
        self._crews["review"] = crew
        return crew

    def create_execution_crew(self) -> Crew:
        """Create an execution crew for task implementation.
        
        Returns:
            A CrewAI crew for execution
        """
        from crewai import Crew, Agent, Task
        
        backend_engineer = Agent(
            role="Backend Engineer",
            goal="Implement backend features following best practices",
            backstory="Expert in backend development and API design",
            verbose=True,
        )
        
        frontend_engineer = Agent(
            role="Frontend Engineer",
            goal="Implement frontend features with great UX",
            backstory="Expert in frontend development and user experience",
            verbose=True,
        )
        
        qa_engineer = Agent(
            role="QA Engineer",
            goal="Ensure comprehensive test coverage",
            backstory="Expert in testing strategies and automation",
            verbose=True,
        )
        
        self._agents["backend_engineer"] = backend_engineer
        self._agents["frontend_engineer"] = frontend_engineer
        self._agents["qa_engineer"] = qa_engineer
        
        crew = Crew(
            agents=[backend_engineer, frontend_engineer, qa_engineer],
            tasks=[],
            verbose=True,
        )
        
        self._crews["execution"] = crew
        return crew

    def get_crew(self, name: str) -> Crew | None:
        """Get a crew by name.
        
        Args:
            name: Crew name (planning, review, execution)
            
        Returns:
            The crew if found, None otherwise
        """
        return self._crews.get(name)

    def get_agent(self, name: str) -> Agent | None:
        """Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            The agent if found, None otherwise
        """
        return self._agents.get(name)

    def run_crew(self, crew_name: str, inputs: dict[str, Any]) -> Any:
        """Run a crew with the given inputs.
        
        Args:
            crew_name: Name of the crew to run
            inputs: Inputs for the crew
            
        Returns:
            Crew execution result
        """
        crew = self._crews.get(crew_name)
        if crew is None:
            raise ValueError(f"Crew not found: {crew_name}")
        
        return crew.kickoff(inputs=inputs)
