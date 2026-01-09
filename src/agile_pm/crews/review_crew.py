"""Review crew for code review and security audits.

Combines Reviewer, Security, and PM agents for comprehensive reviews.
"""

from typing import Any, Optional
from datetime import datetime
from enum import Enum

from crewai import Agent, Crew, Task, Process
from pydantic import BaseModel, Field

from ..crewai.crew import CrewConfig, CrewResult


class ReviewType(str, Enum):
    """Types of reviews."""
    
    CODE = "code"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPREHENSIVE = "comprehensive"


class ReviewCrewConfig(BaseModel):
    """Configuration for review crew."""

    name: str = Field(default="Review Crew")
    description: str = Field(
        default="Collaborative review for code quality and security"
    )
    process: str = Field(default="sequential")
    verbose: bool = Field(default=True)
    security_scan: bool = Field(default=True)
    performance_check: bool = Field(default=True)


class ReviewInput(BaseModel):
    """Input for code review."""

    pr_number: Optional[int] = None
    title: str
    description: str
    review_type: ReviewType = Field(default=ReviewType.CODE)
    files_changed: list[dict[str, Any]] = Field(default_factory=list)
    diff: Optional[str] = None
    author: Optional[str] = None


class ReviewFinding(BaseModel):
    """A single review finding."""

    severity: str = Field(description="critical, major, minor, suggestion")
    category: str = Field(description="security, performance, maintainability, etc.")
    file: Optional[str] = None
    line: Optional[int] = None
    message: str
    suggestion: Optional[str] = None


class ReviewOutput(BaseModel):
    """Output from review."""

    pr_number: Optional[int] = None
    status: str = Field(default="reviewed", description="approved, changes_requested, reviewed")
    findings: list[ReviewFinding] = Field(default_factory=list)
    summary: str = ""
    security_passed: bool = True
    performance_passed: bool = True
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewCrew:
    """Crew for code review and audits.
    
    Combines:
    - Code Reviewer: Reviews code quality and best practices
    - Security Engineer: Checks for security vulnerabilities
    - Performance Engineer: Analyzes performance implications
    """

    def __init__(self, config: Optional[ReviewCrewConfig] = None):
        """Initialize review crew.
        
        Args:
            config: Crew configuration
        """
        self.config = config or ReviewCrewConfig()
        self._crew: Optional[Crew] = None
        self._agents: dict[str, Agent] = {}
        self._setup_agents()
    
    def _setup_agents(self) -> None:
        """Set up crew agents."""
        # Code Reviewer
        self._agents["reviewer"] = Agent(
            role="Senior Code Reviewer",
            goal="Ensure code quality, maintainability, and adherence to best practices",
            backstory="""You are a senior engineer with 10+ years of experience
            conducting code reviews. You focus on code clarity, maintainability,
            and following SOLID principles. You provide constructive feedback
            with specific suggestions for improvement. You catch logical errors
            and ensure proper error handling.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # Security Engineer
        self._agents["security"] = Agent(
            role="Security Engineer",
            goal="Identify and prevent security vulnerabilities",
            backstory="""You are a security expert who reviews code for potential
            vulnerabilities. You check for OWASP Top 10 issues, injection attacks,
            authentication flaws, and data exposure risks. You ensure secure
            coding practices and proper input validation.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
        
        # Performance Engineer
        self._agents["performance"] = Agent(
            role="Performance Engineer",
            goal="Identify performance issues and optimization opportunities",
            backstory="""You are a performance specialist who identifies bottlenecks
            and optimization opportunities. You check for N+1 queries, memory leaks,
            inefficient algorithms, and caching opportunities. You balance
            performance with code readability.""",
            verbose=self.config.verbose,
            allow_delegation=True,
        )
    
    def create_review_tasks(
        self,
        input_data: ReviewInput,
    ) -> list[Task]:
        """Create tasks for review.
        
        Args:
            input_data: Review input
            
        Returns:
            List of review tasks
        """
        tasks = []
        
        files_info = self._format_files(input_data.files_changed)
        
        # Task 1: Code quality review
        code_review_task = Task(
            description=f"""Review the following code changes:
            
            PR: {input_data.title}
            Description: {input_data.description}
            Author: {input_data.author or 'Unknown'}
            
            Files Changed:
            {files_info}
            
            {f'Diff:{chr(10)}{input_data.diff}' if input_data.diff else ''}
            
            Review for:
            1. Code quality and readability
            2. Logical correctness
            3. Error handling
            4. Test coverage
            5. Documentation
            6. Adherence to project patterns
            
            For each issue found, provide:
            - Severity: critical/major/minor/suggestion
            - File and line (if applicable)
            - Clear description
            - Suggested fix
            
            Output findings in markdown format.""",
            agent=self._agents["reviewer"],
            expected_output="Code review findings with suggestions",
        )
        tasks.append(code_review_task)
        
        # Task 2: Security review
        if self.config.security_scan:
            security_task = Task(
                description=f"""Security review of code changes:
                
                PR: {input_data.title}
                
                Check for OWASP Top 10:
                1. Injection vulnerabilities (SQL, NoSQL, OS command)
                2. Broken authentication
                3. Sensitive data exposure
                4. XXE vulnerabilities
                5. Broken access control
                6. Security misconfiguration
                7. XSS vulnerabilities
                8. Insecure deserialization
                9. Using components with known vulnerabilities
                10. Insufficient logging/monitoring
                
                Additional checks:
                - Input validation
                - Output encoding
                - Authentication/authorization
                - Cryptographic issues
                - Information disclosure
                
                Files:
                {files_info}
                
                Output security findings with severity and remediation.""",
                agent=self._agents["security"],
                expected_output="Security review findings",
                context=[code_review_task],
            )
            tasks.append(security_task)
        
        # Task 3: Performance review
        if self.config.performance_check:
            perf_context = [code_review_task]
            if self.config.security_scan:
                perf_context.append(security_task)
            
            performance_task = Task(
                description=f"""Performance review of code changes:
                
                PR: {input_data.title}
                
                Check for:
                1. N+1 query problems
                2. Missing indexes
                3. Inefficient algorithms (O(n²) when O(n) possible)
                4. Memory leaks
                5. Missing caching opportunities
                6. Large payload sizes
                7. Blocking operations in async code
                8. Resource cleanup
                
                Files:
                {files_info}
                
                Output performance findings with:
                - Issue description
                - Performance impact (estimated)
                - Recommended fix
                - Priority (high/medium/low)""",
                agent=self._agents["performance"],
                expected_output="Performance review findings",
                context=perf_context,
            )
            tasks.append(performance_task)
        
        return tasks
    
    def build(self, input_data: ReviewInput) -> Crew:
        """Build the crew with tasks.
        
        Args:
            input_data: Review input
            
        Returns:
            Configured Crew
        """
        tasks = self.create_review_tasks(input_data)
        
        active_agents = [self._agents["reviewer"]]
        if self.config.security_scan:
            active_agents.append(self._agents["security"])
        if self.config.performance_check:
            active_agents.append(self._agents["performance"])
        
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
    
    def kickoff(self, input_data: ReviewInput) -> CrewResult:
        """Execute the review.
        
        Args:
            input_data: Review input
            
        Returns:
            CrewResult with review output
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
            )
        except Exception as e:
            return CrewResult(
                success=False,
                output=str(e),
                tasks_completed=0,
                agents_used=[],
            )
    
    async def kickoff_async(self, input_data: ReviewInput) -> CrewResult:
        """Execute the review asynchronously.
        
        Args:
            input_data: Review input
            
        Returns:
            CrewResult with review output
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
    
    def _format_files(self, files: list[dict[str, Any]]) -> str:
        """Format files info for prompt.
        
        Args:
            files: List of file changes
            
        Returns:
            Formatted string
        """
        if not files:
            return "No specific files provided"
        
        formatted = []
        for f in files:
            path = f.get("path", "unknown")
            status = f.get("status", "modified")
            additions = f.get("additions", 0)
            deletions = f.get("deletions", 0)
            formatted.append(f"- {path} ({status}: +{additions}/-{deletions})")
        
        return "\n".join(formatted)
