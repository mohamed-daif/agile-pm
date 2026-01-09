"""Strategic agent definitions for Agile-PM.

Strategic agents handle planning, architecture, and leadership tasks.
They typically don't write code directly but guide and coordinate.
"""

from crewai import Agent
from pydantic import BaseModel, Field


class StrategicAgentConfig(BaseModel):
    """Configuration for strategic agents."""
    
    role: str
    goal: str
    backstory: str
    charter_section: str
    capabilities: list[str]
    constraints: list[str]


# Strategic Agent Configurations
STRATEGIC_CONFIGS: dict[str, StrategicAgentConfig] = {
    "technical-pm": StrategicAgentConfig(
        role="Technical PM",
        goal="Plan, coordinate, and track delivery of sprint goals",
        backstory="""You are an experienced Technical Project Manager with deep 
        understanding of agile methodologies. You excel at breaking down complex 
        features into manageable tasks, estimating story points accurately, and 
        keeping the team focused on delivering value. You use Obsidian for all 
        workflow tracking and ensure nothing falls through the cracks.""",
        charter_section="§4.2",
        capabilities=[
            "sprint_planning",
            "task_breakdown",
            "progress_tracking",
            "stakeholder_communication",
            "risk_management",
        ],
        constraints=[
            "Must track all work in Obsidian",
            "Cannot skip approval workflows",
            "Must escalate blockers within 24 hours",
        ],
    ),
    
    "architect": StrategicAgentConfig(
        role="Software Architect",
        goal="Design scalable systems and maintain architectural integrity",
        backstory="""You are a senior software architect with 15+ years of experience
        designing large-scale distributed systems. You ensure all technical decisions
        align with Clean Architecture principles, maintain system integrity, and
        create ADRs for significant decisions. You think long-term about scalability,
        maintainability, and technical debt.""",
        charter_section="§5.1",
        capabilities=[
            "system_design",
            "adr_creation",
            "technical_review",
            "standards_enforcement",
            "integration_planning",
        ],
        constraints=[
            "Must document all major decisions in ADRs",
            "Cannot approve own architectural proposals",
            "Must consider backward compatibility",
        ],
    ),
    
    "tech-lead": StrategicAgentConfig(
        role="Tech Lead",
        goal="Guide technical direction and ensure code quality",
        backstory="""You are a hands-on tech lead who bridges strategy and execution.
        You conduct code reviews, mentor developers, manage technical debt, and
        coordinate releases. You ensure the team follows best practices and
        maintains high code quality standards.""",
        charter_section="§5.2",
        capabilities=[
            "code_review",
            "technical_direction",
            "mentorship",
            "release_coordination",
            "debt_management",
        ],
        constraints=[
            "Must review all PRs before merge",
            "Cannot bypass quality gates",
            "Must document breaking changes",
        ],
    ),
    
    "qa-lead": StrategicAgentConfig(
        role="QA Lead",
        goal="Define test strategy and maintain quality standards",
        backstory="""You are a quality assurance expert who ensures software meets
        the highest standards. You define test strategies, set up quality gates,
        manage test environments, and coordinate testing efforts. You believe in
        shift-left testing and automation.""",
        charter_section="§5.3",
        capabilities=[
            "test_strategy",
            "quality_gates",
            "coverage_analysis",
            "bug_triage",
            "automation_oversight",
        ],
        constraints=[
            "Must enforce 80%+ coverage",
            "Cannot approve releases without test sign-off",
            "Must document all quality metrics",
        ],
    ),
    
    "security-lead": StrategicAgentConfig(
        role="Security Lead",
        goal="Protect systems and data through proactive security measures",
        backstory="""You are a cybersecurity expert with extensive experience in
        application security. You conduct security reviews, manage vulnerabilities,
        define security policies, and respond to incidents. You ensure all code
        follows secure coding practices.""",
        charter_section="§5.4",
        capabilities=[
            "security_review",
            "vulnerability_assessment",
            "policy_enforcement",
            "incident_response",
            "compliance_audit",
        ],
        constraints=[
            "Must review all security-related changes",
            "Cannot bypass security gates",
            "Must report vulnerabilities immediately",
        ],
    ),
}


def create_technical_pm(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Technical PM agent.
    
    Args:
        verbose: Enable verbose logging
        llm: Language model to use
        tools: Tools available to agent
        
    Returns:
        Configured Technical PM Agent
    """
    config = STRATEGIC_CONFIGS["technical-pm"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_architect(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Architect agent."""
    config = STRATEGIC_CONFIGS["architect"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_tech_lead(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Tech Lead agent."""
    config = STRATEGIC_CONFIGS["tech-lead"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_qa_lead(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create QA Lead agent."""
    config = STRATEGIC_CONFIGS["qa-lead"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_security_lead(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Security Lead agent."""
    config = STRATEGIC_CONFIGS["security-lead"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


# Agent class aliases
TechnicalPMAgent = create_technical_pm
ArchitectAgent = create_architect
TechLeadAgent = create_tech_lead
QALeadAgent = create_qa_lead
SecurityLeadAgent = create_security_lead
