"""CrewAI crew orchestration for Agile-PM.

This module provides crew definitions for orchestrating
multiple agents to complete complex tasks.
"""

from typing import Any, Optional

from crewai import Agent, Crew, Task, Process
from pydantic import BaseModel, Field

from agile_pm.models import TaskPriority, TaskStatus


class CrewConfig(BaseModel):
    """Configuration for a crew."""
    
    name: str = Field(..., description="Crew name")
    description: str = Field(..., description="Crew purpose")
    process: str = Field("sequential", description="Execution process type")
    verbose: bool = Field(True, description="Enable verbose logging")
    governance_mode: bool = Field(True, description="Enable governance checks")
    obsidian_path: str = Field("cm-workflow", description="Path to Obsidian vault")


class CrewResult(BaseModel):
    """Result from crew execution."""
    
    success: bool
    output: Any
    tasks_completed: int
    agents_used: list[str]
    artifacts: list[str] = Field(default_factory=list)
    governance_checks: list[dict[str, Any]] = Field(default_factory=list)


class AgilePMCrew:
    """Base class for Agile-PM crews."""
    
    def __init__(
        self,
        config: CrewConfig,
        agents: list[Agent],
        tasks: list[Task],
    ):
        """Initialize crew.
        
        Args:
            config: Crew configuration
            agents: List of agents
            tasks: List of tasks
        """
        self.config = config
        self.agents = agents
        self.tasks = tasks
        self._crew: Optional[Crew] = None
    
    def build(self) -> Crew:
        """Build the CrewAI crew."""
        process = Process.sequential
        if self.config.process == "hierarchical":
            process = Process.hierarchical
        
        self._crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=process,
            verbose=self.config.verbose,
        )
        return self._crew
    
    def kickoff(self, inputs: Optional[dict[str, Any]] = None) -> CrewResult:
        """Execute the crew.
        
        Args:
            inputs: Optional input variables
            
        Returns:
            CrewResult with execution outcome
        """
        if self._crew is None:
            self.build()
        
        try:
            result = self._crew.kickoff(inputs or {})
            
            return CrewResult(
                success=True,
                output=result,
                tasks_completed=len(self.tasks),
                agents_used=[a.role for a in self.agents],
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=[a.role for a in self.agents],
            )


class SprintCrew(AgilePMCrew):
    """Crew for sprint planning and execution."""
    
    @classmethod
    def create(
        cls,
        sprint_goal: str,
        backlog_items: list[dict[str, Any]],
        team_capacity: int = 50,
    ) -> "SprintCrew":
        """Create a sprint crew.
        
        Args:
            sprint_goal: Sprint objective
            backlog_items: Items to consider for sprint
            team_capacity: Story points capacity
            
        Returns:
            Configured SprintCrew
        """
        # Define agents
        pm_agent = Agent(
            role="Technical PM",
            goal="Plan and coordinate the sprint to achieve the sprint goal",
            backstory="""You are an experienced Technical PM who excels at 
            breaking down features into manageable tasks, estimating story points,
            and ensuring the team delivers value each sprint.""",
            verbose=True,
        )
        
        architect_agent = Agent(
            role="Architect",
            goal="Ensure technical feasibility and architectural alignment",
            backstory="""You are a seasoned software architect who ensures all
            technical decisions align with the system architecture and follow
            best practices.""",
            verbose=True,
        )
        
        # Define tasks
        planning_task = Task(
            description=f"""Plan the sprint with goal: {sprint_goal}
            
            Available backlog items: {backlog_items}
            Team capacity: {team_capacity} story points
            
            Create a sprint backlog with:
            1. Selected items (P0 first, then P1)
            2. Task breakdown
            3. Story point assignments
            4. Dependencies identified
            """,
            agent=pm_agent,
            expected_output="Sprint backlog in Markdown format",
        )
        
        review_task = Task(
            description="""Review the sprint plan for technical feasibility.
            
            Check:
            1. Architectural alignment
            2. Technical dependencies
            3. Risk assessment
            4. Resource requirements
            """,
            agent=architect_agent,
            expected_output="Technical review with approval status",
        )
        
        config = CrewConfig(
            name="Sprint Planning Crew",
            description=f"Plan sprint: {sprint_goal}",
            process="sequential",
        )
        
        return cls(
            config=config,
            agents=[pm_agent, architect_agent],
            tasks=[planning_task, review_task],
        )


class ReviewCrew(AgilePMCrew):
    """Crew for code and artifact review."""
    
    @classmethod
    def create(
        cls,
        artifact_type: str,
        content: str,
        context: Optional[str] = None,
    ) -> "ReviewCrew":
        """Create a review crew.
        
        Args:
            artifact_type: Type of artifact (code, plan, adr)
            content: Content to review
            context: Optional context
            
        Returns:
            Configured ReviewCrew
        """
        # Domain-specific reviewer
        reviewer_agent = Agent(
            role=f"{artifact_type.title()} Reviewer",
            goal=f"Thoroughly review the {artifact_type} for quality and compliance",
            backstory=f"""You are an expert {artifact_type} reviewer who ensures
            all submissions meet quality standards, follow best practices, and
            comply with governance requirements.""",
            verbose=True,
        )
        
        # Security reviewer
        security_agent = Agent(
            role="Security Reviewer",
            goal="Identify security vulnerabilities and compliance issues",
            backstory="""You are a security expert who identifies potential
            vulnerabilities, ensures input validation, and verifies no secrets
            are exposed.""",
            verbose=True,
        )
        
        # Review tasks
        quality_task = Task(
            description=f"""Review this {artifact_type} for quality:
            
            {content}
            
            Context: {context or 'None provided'}
            
            Check:
            1. Code quality / Structure
            2. Best practices adherence
            3. Documentation
            4. Test coverage (if applicable)
            """,
            agent=reviewer_agent,
            expected_output="Quality review findings",
        )
        
        security_task = Task(
            description=f"""Security review for {artifact_type}:
            
            {content}
            
            Check:
            1. Input validation
            2. Authentication/Authorization
            3. Data exposure risks
            4. Dependency vulnerabilities
            """,
            agent=security_agent,
            expected_output="Security review findings",
        )
        
        config = CrewConfig(
            name="Review Crew",
            description=f"Review {artifact_type}",
            process="sequential",
        )
        
        return cls(
            config=config,
            agents=[reviewer_agent, security_agent],
            tasks=[quality_task, security_task],
        )


class ExecutionCrew(AgilePMCrew):
    """Crew for task execution."""
    
    @classmethod
    def create(
        cls,
        task_id: str,
        task_description: str,
        acceptance_criteria: list[str],
        role_type: str = "backend",
    ) -> "ExecutionCrew":
        """Create an execution crew.
        
        Args:
            task_id: Task identifier
            task_description: What to implement
            acceptance_criteria: Acceptance criteria
            role_type: Type of work (backend, frontend, devops)
            
        Returns:
            Configured ExecutionCrew
        """
        # Executor agent based on role type
        role_configs = {
            "backend": {
                "role": "Backend Engineer",
                "goal": "Implement robust backend functionality",
                "backstory": """Expert backend developer skilled in Node.js,
                TypeScript, and Clean Architecture patterns.""",
            },
            "frontend": {
                "role": "Frontend Engineer",
                "goal": "Create excellent user interfaces",
                "backstory": """Expert frontend developer skilled in React,
                TypeScript, and responsive design.""",
            },
            "devops": {
                "role": "DevOps Engineer",
                "goal": "Build reliable infrastructure and pipelines",
                "backstory": """Expert DevOps engineer skilled in Docker,
                Kubernetes, and CI/CD automation.""",
            },
        }
        
        config = role_configs.get(role_type, role_configs["backend"])
        
        executor_agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=True,
        )
        
        # QA agent
        qa_agent = Agent(
            role="QA Engineer",
            goal="Ensure code quality through comprehensive testing",
            backstory="""Expert QA engineer who writes thorough tests
            and ensures all edge cases are covered.""",
            verbose=True,
        )
        
        # Implementation task
        impl_task = Task(
            description=f"""Implement task {task_id}:
            
            {task_description}
            
            Acceptance Criteria:
            {chr(10).join(f'- {ac}' for ac in acceptance_criteria)}
            
            Requirements:
            1. Follow existing patterns
            2. Add appropriate tests
            3. Update documentation
            4. No secrets in code
            """,
            agent=executor_agent,
            expected_output="Implementation with code and documentation",
        )
        
        # Testing task
        test_task = Task(
            description=f"""Create tests for task {task_id}:
            
            Ensure:
            1. Unit tests for all logic
            2. Edge case coverage
            3. Error handling tests
            4. 80%+ coverage
            """,
            agent=qa_agent,
            expected_output="Test suite with coverage report",
        )
        
        crew_config = CrewConfig(
            name="Execution Crew",
            description=f"Execute {task_id}",
            process="sequential",
        )
        
        return cls(
            config=crew_config,
            agents=[executor_agent, qa_agent],
            tasks=[impl_task, test_task],
        )


def create_crew(
    crew_type: str,
    **kwargs,
) -> AgilePMCrew:
    """Factory function to create crews.
    
    Args:
        crew_type: Type of crew (sprint, review, execution)
        **kwargs: Arguments for specific crew type
        
    Returns:
        Configured crew
        
    Raises:
        ValueError: If crew_type not recognized
    """
    crews = {
        "sprint": SprintCrew.create,
        "review": ReviewCrew.create,
        "execution": ExecutionCrew.create,
    }
    
    if crew_type not in crews:
        raise ValueError(f"Unknown crew type: {crew_type}. Valid: {list(crews.keys())}")
    
    return crews[crew_type](**kwargs)
