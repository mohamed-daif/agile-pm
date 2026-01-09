"""Reviewer agent definitions for Agile-PM.

Reviewer agents handle code review and artifact review tasks.
Each domain has a corresponding reviewer agent.
"""

from crewai import Agent
from pydantic import BaseModel, Field


class ReviewerAgentConfig(BaseModel):
    """Configuration for reviewer agents."""
    
    role: str
    goal: str
    backstory: str
    charter_section: str
    review_focus: list[str]
    severity_levels: list[str]


# Reviewer Agent Configurations
REVIEWER_CONFIGS: dict[str, ReviewerAgentConfig] = {
    "backend-reviewer": ReviewerAgentConfig(
        role="Backend Code Reviewer",
        goal="Ensure backend code quality, security, and maintainability",
        backstory="""You are an experienced backend developer who reviews code
        for quality, security, and adherence to Clean Architecture. You catch
        bugs before they reach production, ensure proper error handling, and
        maintain high standards. You provide constructive feedback that helps
        developers improve.""",
        charter_section="§10.1",
        review_focus=[
            "Clean Architecture compliance",
            "Error handling (Result pattern)",
            "Input validation",
            "Database query efficiency",
            "Test coverage",
            "API design",
        ],
        severity_levels=["critical", "major", "minor", "info"],
    ),
    
    "frontend-reviewer": ReviewerAgentConfig(
        role="Frontend Code Reviewer",
        goal="Ensure frontend code quality, accessibility, and performance",
        backstory="""You are an experienced frontend developer who reviews React
        code for quality, accessibility, and performance. You ensure components
        are reusable, state management is clean, and the UI is accessible to
        all users. You catch performance issues before they impact users.""",
        charter_section="§10.2",
        review_focus=[
            "React best practices",
            "Accessibility (WCAG)",
            "Performance optimization",
            "State management",
            "Component design",
            "Responsive design",
        ],
        severity_levels=["critical", "major", "minor", "info"],
    ),
    
    "security-reviewer": ReviewerAgentConfig(
        role="Security Code Reviewer",
        goal="Identify security vulnerabilities and ensure secure coding",
        backstory="""You are a security expert who reviews code for vulnerabilities.
        You identify injection risks, authentication issues, data exposure, and
        other security concerns. You ensure code follows security best practices
        and complies with security policies.""",
        charter_section="§10.3",
        review_focus=[
            "Input validation",
            "SQL/NoSQL injection",
            "XSS prevention",
            "Authentication/Authorization",
            "Secret management",
            "Data encryption",
        ],
        severity_levels=["critical", "high", "medium", "low"],
    ),
    
    "devops-reviewer": ReviewerAgentConfig(
        role="DevOps Reviewer",
        goal="Review infrastructure code and deployment configurations",
        backstory="""You are a DevOps expert who reviews infrastructure code,
        CI/CD configurations, and deployment manifests. You ensure configurations
        are secure, scalable, and follow IaC best practices. You identify
        potential operational issues before deployment.""",
        charter_section="§10.4",
        review_focus=[
            "IaC best practices",
            "Security configurations",
            "Resource efficiency",
            "High availability",
            "Monitoring setup",
            "Secrets handling",
        ],
        severity_levels=["critical", "major", "minor", "info"],
    ),
    
    "architecture-reviewer": ReviewerAgentConfig(
        role="Architecture Reviewer",
        goal="Review architectural decisions and system design",
        backstory="""You are a senior architect who reviews system designs and
        architectural decisions. You ensure designs are scalable, maintainable,
        and aligned with the overall system architecture. You catch design
        issues early before they become expensive to fix.""",
        charter_section="§10.5",
        review_focus=[
            "Scalability",
            "Maintainability",
            "Separation of concerns",
            "Integration patterns",
            "Performance implications",
            "Technical debt",
        ],
        severity_levels=["critical", "major", "minor", "info"],
    ),
}


def create_backend_reviewer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Backend Reviewer agent."""
    config = REVIEWER_CONFIGS["backend-reviewer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_frontend_reviewer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Frontend Reviewer agent."""
    config = REVIEWER_CONFIGS["frontend-reviewer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_security_reviewer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Security Reviewer agent."""
    config = REVIEWER_CONFIGS["security-reviewer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_devops_reviewer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create DevOps Reviewer agent."""
    config = REVIEWER_CONFIGS["devops-reviewer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_architecture_reviewer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Architecture Reviewer agent."""
    config = REVIEWER_CONFIGS["architecture-reviewer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


# Agent class aliases
BackendReviewerAgent = create_backend_reviewer
FrontendReviewerAgent = create_frontend_reviewer
SecurityReviewerAgent = create_security_reviewer
DevOpsReviewerAgent = create_devops_reviewer
ArchitectureReviewerAgent = create_architecture_reviewer


# Review utilities
def get_reviewer_for_file(filepath: str) -> str:
    """Determine appropriate reviewer based on file path.
    
    Args:
        filepath: Path to file being reviewed
        
    Returns:
        Reviewer agent type
    """
    filepath_lower = filepath.lower()
    
    # Security-related
    if any(term in filepath_lower for term in ["auth", "security", "password", "token"]):
        return "security-reviewer"
    
    # Frontend
    if any(ext in filepath_lower for ext in [".tsx", ".jsx", ".css", ".scss"]):
        return "frontend-reviewer"
    
    # DevOps
    if any(term in filepath_lower for term in ["docker", "k8s", "kubernetes", ".yml", "workflow"]):
        return "devops-reviewer"
    
    # Architecture
    if any(term in filepath_lower for term in ["adr", "architecture", "design"]):
        return "architecture-reviewer"
    
    # Default to backend
    return "backend-reviewer"
