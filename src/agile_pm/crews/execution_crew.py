"""Execution crew for task implementation.

Combines Backend, Frontend, and QA agents for collaborative execution.
"""

from typing import Any, Optional
from datetime import datetime
from enum import Enum

from crewai import Agent, Crew, Task, Process
from pydantic import BaseModel, Field

from ..crewai.crew import CrewConfig, CrewResult


class TaskType(str, Enum):
    """Types of tasks for execution crew."""
    
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"


class ExecutionCrewConfig(BaseModel):
    """Configuration for execution crew."""

    name: str = Field(default="Execution Crew")
    description: str = Field(
        default="Collaborative task execution with code generation and testing"
    )
    process: str = Field(default="sequential")
    verbose: bool = Field(default=True)
    obsidian_path: str = Field(default="cm-workflow")
    code_review_required: bool = Field(default=True)
    test_required: bool = Field(default=True)


class TaskInput(BaseModel):
    """Input for task execution."""

    task_id: str
    title: str
    description: str
    task_type: TaskType = Field(default=TaskType.FULLSTACK)
    acceptance_criteria: list[str] = Field(default_factory=list)
    technical_notes: Optional[str] = None
    files_to_modify: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class TaskOutput(BaseModel):
    """Output from task execution."""

    task_id: str
    status: str = Field(default="completed")
    code_changes: list[dict[str, Any]] = Field(default_factory=list)
    tests_added: list[str] = Field(default_factory=list)
    review_notes: str = ""
    artifacts: list[str] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionCrew:
    """Crew for task execution and code generation.
    
    Combines:
    - Backend Engineer: Implements server-side logic
    - Frontend Engineer: Implements UI components
    - QA Engineer: Writes tests and validates
    """

    def __init__(self, config: Optional[ExecutionCrewConfig] = None):
        """Initialize execution crew.
        
        Args:
            config: Crew configuration
        """
        self.config = config or ExecutionCrewConfig()
        self._crew: Optional[Crew] = None
        self._agents: dict[str, Agent] = {}
        self._setup_agents()
    
    def _setup_agents(self) -> None:
        """Set up crew agents."""
        # Backend Engineer
        self._agents["backend"] = Agent(
            role="Backend Engineer",
            goal="Implement robust, efficient server-side solutions",
            backstory="""You are a senior Backend Engineer specializing in TypeScript
            and Node.js. You write clean, maintainable code following SOLID principles.
            You have expertise in REST APIs, database design, and system architecture.
            You always consider security, performance, and scalability.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # Frontend Engineer
        self._agents["frontend"] = Agent(
            role="Frontend Engineer",
            goal="Create intuitive, responsive user interfaces",
            backstory="""You are a skilled Frontend Engineer with expertise in React,
            TypeScript, and modern CSS. You focus on user experience, accessibility,
            and performance. You write clean, reusable components following best
            practices and design system guidelines.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # QA Engineer
        self._agents["qa"] = Agent(
            role="QA Engineer",
            goal="Ensure code quality through comprehensive testing",
            backstory="""You are a meticulous QA Engineer who writes comprehensive
            tests covering unit, integration, and edge cases. You identify potential
            bugs before they reach production. You use Jest for testing and follow
            the Arrange-Act-Assert pattern.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
    
    def create_execution_tasks(
        self,
        input_data: TaskInput,
    ) -> list[Task]:
        """Create tasks for execution.
        
        Args:
            input_data: Task execution input
            
        Returns:
            List of execution tasks
        """
        tasks = []
        
        # Determine which agents to use based on task type
        if input_data.task_type in [TaskType.BACKEND, TaskType.INFRASTRUCTURE]:
            primary_agent = self._agents["backend"]
        elif input_data.task_type == TaskType.FRONTEND:
            primary_agent = self._agents["frontend"]
        else:
            primary_agent = self._agents["backend"]
        
        # Task 1: Implementation
        implementation_task = Task(
            description=f"""Implement the following task:
            
            Task ID: {input_data.task_id}
            Title: {input_data.title}
            Description: {input_data.description}
            
            Technical Notes: {input_data.technical_notes or 'None provided'}
            
            Files to Modify: {', '.join(input_data.files_to_modify) or 'Determine from task'}
            Dependencies: {', '.join(input_data.dependencies) or 'None'}
            
            Acceptance Criteria:
            {self._format_criteria(input_data.acceptance_criteria)}
            
            Requirements:
            1. Write clean, well-documented code
            2. Follow existing project patterns
            3. Handle errors appropriately
            4. Consider edge cases
            5. Add JSDoc comments
            
            Output the implementation code in markdown code blocks with file paths.""",
            agent=primary_agent,
            expected_output="Implementation code with file paths",
        )
        tasks.append(implementation_task)
        
        # Task 2: Frontend (if fullstack)
        if input_data.task_type == TaskType.FULLSTACK:
            frontend_task = Task(
                description=f"""Implement the frontend for task: {input_data.title}
                
                Based on the backend implementation, create:
                1. React components for the feature
                2. API integration hooks
                3. UI state management
                4. Error handling and loading states
                5. Responsive design
                
                Follow the existing design system and component patterns.
                Output the component code in markdown code blocks.""",
                agent=self._agents["frontend"],
                expected_output="Frontend component code",
                context=[implementation_task],
            )
            tasks.append(frontend_task)
        
        # Task 3: Testing
        if self.config.test_required:
            test_context = [implementation_task]
            if input_data.task_type == TaskType.FULLSTACK:
                test_context.append(frontend_task)
            
            test_task = Task(
                description=f"""Write comprehensive tests for task: {input_data.title}
                
                Based on the implementation, create:
                1. Unit tests for all functions/methods
                2. Integration tests for API endpoints
                3. Edge case tests
                4. Error handling tests
                
                Acceptance Criteria to Verify:
                {self._format_criteria(input_data.acceptance_criteria)}
                
                Use Jest and follow:
                - Arrange-Act-Assert pattern
                - Descriptive test names
                - Mock external dependencies
                - Aim for >80% coverage
                
                Output test code in markdown code blocks.""",
                agent=self._agents["qa"],
                expected_output="Test code with coverage",
                context=test_context,
            )
            tasks.append(test_task)
        
        return tasks
    
    def build(self, input_data: TaskInput) -> Crew:
        """Build the crew with tasks.
        
        Args:
            input_data: Task execution input
            
        Returns:
            Configured Crew
        """
        tasks = self.create_execution_tasks(input_data)
        
        # Select active agents based on task type
        active_agents = [self._agents["backend"]]
        if input_data.task_type in [TaskType.FRONTEND, TaskType.FULLSTACK]:
            active_agents.append(self._agents["frontend"])
        if self.config.test_required:
            active_agents.append(self._agents["qa"])
        
        process = Process.sequential
        if self.config.process == "hierarchical":
            process = Process.hierarchical
        
        self._crew = Crew(
            agents=active_agents,
            tasks=tasks,
            process=process,
            verbose=self.config.verbose,
            max_rpm=10,
        )
        
        return self._crew
    
    def kickoff(self, input_data: TaskInput) -> CrewResult:
        """Execute the task.
        
        Args:
            input_data: Task execution input
            
        Returns:
            CrewResult with execution output
        """
        if self._crew is None:
            self.build(input_data)
        
        try:
            result = self._crew.kickoff()
            
            return CrewResult(
                success=True,
                output=result,
                tasks_completed=len(self._crew.tasks),
                agents_used=[a.role for a in self._crew.agents],
                artifacts=[],
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=[],
            )
    
    async def kickoff_async(self, input_data: TaskInput) -> CrewResult:
        """Execute the task asynchronously.
        
        Args:
            input_data: Task execution input
            
        Returns:
            CrewResult with execution output
        """
        if self._crew is None:
            self.build(input_data)
        
        try:
            result = await self._crew.kickoff_async()
            
            return CrewResult(
                success=True,
                output=result,
                tasks_completed=len(self._crew.tasks),
                agents_used=[a.role for a in self._crew.agents],
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=[],
            )
    
    def _format_criteria(self, criteria: list[str]) -> str:
        """Format acceptance criteria.
        
        Args:
            criteria: List of criteria
            
        Returns:
            Formatted string
        """
        if not criteria:
            return "- No specific criteria provided"
        return "\n".join(f"- {c}" for c in criteria)
