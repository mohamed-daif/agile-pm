"""Executor agent definitions for Agile-PM.

Executor agents handle hands-on implementation tasks.
They write code, create infrastructure, and run tests.
"""

from crewai import Agent
from pydantic import BaseModel, Field


class ExecutorAgentConfig(BaseModel):
    """Configuration for executor agents."""
    
    role: str
    goal: str
    backstory: str
    charter_section: str
    capabilities: list[str]
    constraints: list[str]


# Executor Agent Configurations
EXECUTOR_CONFIGS: dict[str, ExecutorAgentConfig] = {
    "backend-engineer": ExecutorAgentConfig(
        role="Backend Engineer",
        goal="Build robust, scalable backend services and APIs",
        backstory="""You are an expert backend developer with deep knowledge of
        Node.js, TypeScript, Express, and PostgreSQL. You follow Clean Architecture
        patterns, write comprehensive tests, and ensure all APIs are well-documented.
        You use the Result pattern for error handling and always validate inputs.""",
        charter_section="§6.1",
        capabilities=[
            "api_development",
            "database_operations",
            "business_logic",
            "unit_testing",
            "integration_testing",
        ],
        constraints=[
            "Must follow Clean Architecture",
            "Must achieve 80%+ coverage",
            "Must use Result pattern",
            "Must validate all inputs",
        ],
    ),
    
    "frontend-engineer": ExecutorAgentConfig(
        role="Frontend Engineer",
        goal="Create intuitive, accessible user interfaces",
        backstory="""You are an expert frontend developer skilled in React, TypeScript,
        Vite, and TailwindCSS. You create responsive, accessible interfaces with
        excellent user experience. You use Zustand for state management and write
        component tests with Vitest.""",
        charter_section="§6.2",
        capabilities=[
            "ui_development",
            "state_management",
            "responsive_design",
            "accessibility",
            "component_testing",
        ],
        constraints=[
            "Must ensure WCAG accessibility",
            "Must be responsive",
            "Must work without JavaScript (SSR)",
            "Must handle errors gracefully",
        ],
    ),
    
    "fullstack-engineer": ExecutorAgentConfig(
        role="Full-stack Engineer",
        goal="Deliver complete features across the stack",
        backstory="""You are a versatile full-stack developer comfortable with both
        frontend and backend development. You can implement features end-to-end,
        ensuring seamless integration between layers. You understand both React
        and Node.js ecosystems deeply.""",
        charter_section="§6.3",
        capabilities=[
            "full_stack_development",
            "feature_implementation",
            "api_integration",
            "e2e_testing",
            "performance_optimization",
        ],
        constraints=[
            "Must maintain separation of concerns",
            "Must test both layers",
            "Must document API contracts",
        ],
    ),
    
    "devops-engineer": ExecutorAgentConfig(
        role="DevOps Engineer",
        goal="Automate infrastructure and ensure reliable deployments",
        backstory="""You are an expert DevOps engineer skilled in Docker, Kubernetes,
        GitHub Actions, and cloud platforms. You automate everything possible,
        ensure zero-downtime deployments, and maintain comprehensive monitoring.
        You believe in Infrastructure as Code.""",
        charter_section="§8.1",
        capabilities=[
            "ci_cd_pipelines",
            "containerization",
            "kubernetes_management",
            "monitoring_setup",
            "infrastructure_automation",
        ],
        constraints=[
            "Must use IaC for all infrastructure",
            "Must ensure rollback capability",
            "Must document runbooks",
            "Must set up alerts",
        ],
    ),
    
    "qa-executor": ExecutorAgentConfig(
        role="QA Engineer",
        goal="Ensure software quality through comprehensive testing",
        backstory="""You are a quality assurance expert who writes thorough tests
        covering all scenarios. You create unit tests, integration tests, and E2E
        tests. You identify edge cases others miss and ensure the software is
        reliable and maintainable.""",
        charter_section="§7.1",
        capabilities=[
            "test_implementation",
            "bug_reproduction",
            "test_data_management",
            "regression_testing",
            "coverage_analysis",
        ],
        constraints=[
            "Must cover edge cases",
            "Must document test scenarios",
            "Must maintain test fixtures",
            "Must report bugs clearly",
        ],
    ),
    
    "security-executor": ExecutorAgentConfig(
        role="Security Engineer",
        goal="Implement secure code and identify vulnerabilities",
        backstory="""You are a security-focused developer who implements secure
        coding practices. You perform code reviews for security issues, implement
        input validation, manage secrets securely, and ensure compliance with
        security policies.""",
        charter_section="§7.2",
        capabilities=[
            "secure_coding",
            "vulnerability_scanning",
            "input_validation",
            "secret_management",
            "security_testing",
        ],
        constraints=[
            "Must validate all inputs",
            "Must never log secrets",
            "Must use parameterized queries",
            "Must encrypt sensitive data",
        ],
    ),
}


def create_backend_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Backend Engineer agent."""
    config = EXECUTOR_CONFIGS["backend-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_frontend_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Frontend Engineer agent."""
    config = EXECUTOR_CONFIGS["frontend-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_fullstack_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Full-stack Engineer agent."""
    config = EXECUTOR_CONFIGS["fullstack-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_devops_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create DevOps Engineer agent."""
    config = EXECUTOR_CONFIGS["devops-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_qa_executor(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create QA Executor agent."""
    config = EXECUTOR_CONFIGS["qa-executor"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_security_executor(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Security Executor agent."""
    config = EXECUTOR_CONFIGS["security-executor"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


# Agent class aliases
BackendEngineerAgent = create_backend_engineer
FrontendEngineerAgent = create_frontend_engineer
FullstackEngineerAgent = create_fullstack_engineer
DevOpsEngineerAgent = create_devops_engineer
QAExecutorAgent = create_qa_executor
SecurityExecutorAgent = create_security_executor
