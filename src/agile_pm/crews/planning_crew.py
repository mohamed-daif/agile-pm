"""Planning crew for sprint planning and backlog management.

Combines Research, Architect, and PM agents for collaborative planning.
"""

from typing import Any, Optional
from datetime import datetime

from crewai import Agent, Crew, Task, Process
from pydantic import BaseModel, Field

from ..crewai.crew import CrewConfig, CrewResult


class PlanningCrewConfig(BaseModel):
    """Configuration for planning crew."""

    name: str = Field(default="Planning Crew")
    description: str = Field(
        default="Collaborative planning for sprint and backlog management"
    )
    process: str = Field(default="sequential")
    verbose: bool = Field(default=True)
    obsidian_path: str = Field(default="cm-workflow")
    max_iterations: int = Field(default=3, description="Max planning iterations")


class SprintPlanInput(BaseModel):
    """Input for sprint planning."""

    sprint_goal: str
    backlog_items: list[dict[str, Any]]
    team_capacity: int = Field(default=50)
    sprint_duration: str = Field(default="2 weeks")
    constraints: list[str] = Field(default_factory=list)


class SprintPlanOutput(BaseModel):
    """Output from sprint planning."""

    sprint_number: int
    goal: str
    selected_items: list[dict[str, Any]]
    total_points: int
    risk_assessment: list[dict[str, str]]
    dependencies: list[str]
    definition_of_done: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PlanningCrew:
    """Crew for sprint planning and backlog management.
    
    Combines:
    - Research Agent: Analyzes requirements and gathers context
    - Architect Agent: Ensures technical feasibility
    - PM Agent: Coordinates planning and prioritization
    """

    def __init__(self, config: Optional[PlanningCrewConfig] = None):
        """Initialize planning crew.
        
        Args:
            config: Crew configuration
        """
        self.config = config or PlanningCrewConfig()
        self._crew: Optional[Crew] = None
        self._agents: dict[str, Agent] = {}
        self._setup_agents()
    
    def _setup_agents(self) -> None:
        """Set up crew agents."""
        # Research Agent
        self._agents["research"] = Agent(
            role="Research Analyst",
            goal="Analyze requirements, gather context, and identify dependencies",
            backstory="""You are a meticulous Research Analyst who excels at 
            understanding complex requirements and gathering relevant context.
            You identify dependencies, constraints, and risks that others might miss.
            Your research forms the foundation for sound technical decisions.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # Architect Agent
        self._agents["architect"] = Agent(
            role="Solution Architect",
            goal="Ensure technical feasibility and architectural alignment",
            backstory="""You are an experienced Solution Architect who ensures all
            technical decisions align with the system architecture. You evaluate
            technical complexity, identify potential blockers, and suggest optimal
            implementation approaches. You prioritize maintainability and scalability.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # PM Agent
        self._agents["pm"] = Agent(
            role="Technical Project Manager",
            goal="Coordinate planning, prioritize work, and ensure sprint success",
            backstory="""You are a skilled Technical PM who excels at breaking down
            features into manageable tasks, estimating story points, and balancing
            team capacity with business priorities. You ensure the team delivers
            value every sprint while maintaining sustainable pace.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
    
    def create_sprint_planning_tasks(
        self,
        input_data: SprintPlanInput,
    ) -> list[Task]:
        """Create tasks for sprint planning.
        
        Args:
            input_data: Sprint planning input
            
        Returns:
            List of planning tasks
        """
        tasks = []
        
        # Task 1: Research and context gathering
        research_task = Task(
            description=f"""Analyze the sprint planning context:
            
            Sprint Goal: {input_data.sprint_goal}
            Team Capacity: {input_data.team_capacity} story points
            Duration: {input_data.sprint_duration}
            Constraints: {', '.join(input_data.constraints) or 'None specified'}
            
            Backlog Items to Analyze:
            {self._format_backlog_items(input_data.backlog_items)}
            
            Research and provide:
            1. Dependencies between backlog items
            2. External dependencies (APIs, services, etc.)
            3. Knowledge gaps that need addressing
            4. Risks that could impact sprint success
            5. Recommended priority order based on dependencies
            
            Output a structured analysis in markdown format.""",
            agent=self._agents["research"],
            expected_output="Structured analysis of dependencies, risks, and priorities",
        )
        tasks.append(research_task)
        
        # Task 2: Technical feasibility assessment
        architecture_task = Task(
            description=f"""Review the technical feasibility based on research findings.
            
            Sprint Goal: {input_data.sprint_goal}
            
            For each backlog item, assess:
            1. Technical complexity (Low/Medium/High)
            2. Architectural alignment
            3. Required technical spikes
            4. Potential technical debt
            5. Recommended implementation approach
            
            Consider the research analysis and provide:
            - Story point estimates for each item
            - Technical risk assessment
            - Recommended sprint capacity allocation
            
            Output in markdown format with clear estimates.""",
            agent=self._agents["architect"],
            expected_output="Technical assessment with story point estimates",
            context=[research_task],
        )
        tasks.append(architecture_task)
        
        # Task 3: Sprint plan creation
        planning_task = Task(
            description=f"""Create the final sprint plan.
            
            Sprint Goal: {input_data.sprint_goal}
            Available Capacity: {input_data.team_capacity} story points
            
            Using the research and technical assessments:
            
            1. Select items for the sprint (P0 first, then P1)
            2. Ensure total points <= capacity with 20% buffer
            3. Create task breakdown for selected items
            4. Define acceptance criteria
            5. Identify sprint risks and mitigations
            6. Create sprint definition of done
            
            Output the complete sprint plan in markdown format:
            - Sprint summary
            - Selected items with points
            - Task breakdown
            - Risk register
            - Definition of done""",
            agent=self._agents["pm"],
            expected_output="Complete sprint plan in markdown",
            context=[research_task, architecture_task],
        )
        tasks.append(planning_task)
        
        return tasks
    
    def build(self, input_data: SprintPlanInput) -> Crew:
        """Build the crew with tasks.
        
        Args:
            input_data: Sprint planning input
            
        Returns:
            Configured Crew
        """
        tasks = self.create_sprint_planning_tasks(input_data)
        
        process = Process.sequential
        if self.config.process == "hierarchical":
            process = Process.hierarchical
        
        self._crew = Crew(
            agents=list(self._agents.values()),
            tasks=tasks,
            process=process,
            verbose=self.config.verbose,
            max_rpm=10,  # Rate limit
        )
        
        return self._crew
    
    def kickoff(self, input_data: SprintPlanInput) -> CrewResult:
        """Execute sprint planning.
        
        Args:
            input_data: Sprint planning input
            
        Returns:
            CrewResult with planning output
        """
        if self._crew is None:
            self.build(input_data)
        
        try:
            result = self._crew.kickoff()
            
            return CrewResult(
                success=True,
                output=result,
                tasks_completed=len(self._crew.tasks),
                agents_used=list(self._agents.keys()),
                artifacts=[],
                governance_checks=[],
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=list(self._agents.keys()),
            )
    
    async def kickoff_async(self, input_data: SprintPlanInput) -> CrewResult:
        """Execute sprint planning asynchronously.
        
        Args:
            input_data: Sprint planning input
            
        Returns:
            CrewResult with planning output
        """
        if self._crew is None:
            self.build(input_data)
        
        try:
            result = await self._crew.kickoff_async()
            
            return CrewResult(
                success=True,
                output=result,
                tasks_completed=len(self._crew.tasks),
                agents_used=list(self._agents.keys()),
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=list(self._agents.keys()),
            )
    
    def _format_backlog_items(self, items: list[dict[str, Any]]) -> str:
        """Format backlog items for prompt.
        
        Args:
            items: List of backlog items
            
        Returns:
            Formatted string
        """
        formatted = []
        for i, item in enumerate(items, 1):
            title = item.get("title", "Untitled")
            priority = item.get("priority", "P2")
            points = item.get("points", "TBD")
            desc = item.get("description", "No description")
            formatted.append(f"{i}. [{priority}] {title} ({points} pts)\n   {desc}")
        return "\n".join(formatted)
