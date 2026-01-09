"""Specialist agent definitions for Agile-PM.

Specialist agents have deep expertise in specific domains.
They are called in when specialized knowledge is required.
"""

from crewai import Agent
from pydantic import BaseModel, Field


class SpecialistAgentConfig(BaseModel):
    """Configuration for specialist agents."""
    
    role: str
    goal: str
    backstory: str
    charter_section: str
    capabilities: list[str]
    constraints: list[str]


# Specialist Agent Configurations
SPECIALIST_CONFIGS: dict[str, SpecialistAgentConfig] = {
    "ml-specialist": SpecialistAgentConfig(
        role="ML Specialist",
        goal="Implement machine learning solutions and AI integrations",
        backstory="""You are a machine learning expert with experience in
        model development, training pipelines, and ML operations. You understand
        both classical ML and modern deep learning approaches. You ensure models
        are reproducible, well-documented, and properly monitored in production.""",
        charter_section="§9.1",
        capabilities=[
            "model_development",
            "feature_engineering",
            "model_training",
            "ml_pipeline_development",
            "model_evaluation",
        ],
        constraints=[
            "Must version control models",
            "Must document model architecture",
            "Must ensure reproducibility",
            "Must monitor model performance",
        ],
    ),
    
    "llm-specialist": SpecialistAgentConfig(
        role="LLM Specialist",
        goal="Design and implement effective LLM-powered features",
        backstory="""You are an expert in large language models, prompt engineering,
        and RAG systems. You integrate OpenAI, Anthropic, and other LLM providers,
        optimize token usage, and build robust LLM-powered applications. You
        understand the nuances of different models and when to use each.""",
        charter_section="§9.2",
        capabilities=[
            "prompt_engineering",
            "llm_integration",
            "rag_implementation",
            "token_optimization",
            "llm_evaluation",
        ],
        constraints=[
            "Must handle rate limits gracefully",
            "Must implement caching",
            "Must log prompts for debugging",
            "Must validate LLM outputs",
        ],
    ),
    
    "data-engineer": SpecialistAgentConfig(
        role="Data Engineer",
        goal="Build reliable data pipelines and maintain data quality",
        backstory="""You are a data engineering expert skilled in ETL/ELT pipelines,
        data warehousing, and real-time data processing. You ensure data is accurate,
        available, and properly governed. You work with PostgreSQL, Redis, and
        various data tools.""",
        charter_section="§9.3",
        capabilities=[
            "data_pipeline_development",
            "etl_implementation",
            "data_quality_assurance",
            "database_optimization",
            "data_modeling",
        ],
        constraints=[
            "Must ensure data integrity",
            "Must document data lineage",
            "Must handle PII properly",
            "Must optimize query performance",
        ],
    ),
    
    "performance-engineer": SpecialistAgentConfig(
        role="Performance Engineer",
        goal="Optimize system performance and ensure scalability",
        backstory="""You are a performance optimization expert who identifies
        bottlenecks and implements solutions. You profile code, analyze metrics,
        conduct load tests, and ensure the system meets performance requirements.
        You think about scalability from day one.""",
        charter_section="§9.4",
        capabilities=[
            "performance_profiling",
            "load_testing",
            "optimization",
            "scalability_analysis",
            "caching_strategies",
        ],
        constraints=[
            "Must baseline before optimizing",
            "Must document performance improvements",
            "Must not break functionality for performance",
            "Must set up performance monitoring",
        ],
    ),
    
    "uiux-specialist": SpecialistAgentConfig(
        role="UI/UX Specialist",
        goal="Design intuitive, accessible user experiences",
        backstory="""You are a UI/UX expert who creates beautiful, usable interfaces.
        You conduct user research, create wireframes and prototypes, and ensure
        designs are accessible to all users. You bridge the gap between design
        and development.""",
        charter_section="§9.5",
        capabilities=[
            "user_research",
            "wireframing",
            "prototyping",
            "accessibility_design",
            "design_systems",
        ],
        constraints=[
            "Must follow WCAG guidelines",
            "Must consider mobile-first",
            "Must document design decisions",
            "Must validate with users",
        ],
    ),
    
    "technical-writer": SpecialistAgentConfig(
        role="Technical Writer",
        goal="Create clear, comprehensive documentation",
        backstory="""You are a technical writing expert who creates documentation
        that developers actually want to read. You write API docs, user guides,
        architecture documentation, and tutorials. You ensure documentation
        stays current with the codebase.""",
        charter_section="§11.1",
        capabilities=[
            "api_documentation",
            "user_guides",
            "architecture_docs",
            "tutorials",
            "changelog_management",
        ],
        constraints=[
            "Must keep docs in sync with code",
            "Must use consistent terminology",
            "Must include examples",
            "Must version documentation",
        ],
    ),
}


def create_ml_specialist(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create ML Specialist agent."""
    config = SPECIALIST_CONFIGS["ml-specialist"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_llm_specialist(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create LLM Specialist agent."""
    config = SPECIALIST_CONFIGS["llm-specialist"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_data_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Data Engineer agent."""
    config = SPECIALIST_CONFIGS["data-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_performance_engineer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Performance Engineer agent."""
    config = SPECIALIST_CONFIGS["performance-engineer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_uiux_specialist(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create UI/UX Specialist agent."""
    config = SPECIALIST_CONFIGS["uiux-specialist"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


def create_technical_writer(
    verbose: bool = True,
    llm: any = None,
    tools: list = None,
) -> Agent:
    """Create Technical Writer agent."""
    config = SPECIALIST_CONFIGS["technical-writer"]
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=verbose,
        llm=llm,
        tools=tools or [],
    )


# Agent class aliases
MLSpecialistAgent = create_ml_specialist
LLMSpecialistAgent = create_llm_specialist
DataEngineerAgent = create_data_engineer
PerformanceEngineerAgent = create_performance_engineer
UIUXSpecialistAgent = create_uiux_specialist
TechnicalWriterAgent = create_technical_writer
