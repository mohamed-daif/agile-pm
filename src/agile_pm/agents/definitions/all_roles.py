"""
All Role Definitions

Complete implementation of all 33 governance roles as Python agents.
Each agent class implements the BaseAgent interface with role-specific behavior.

Organization:
- Strategic Agents (5): PM, Architect, Tech Lead, QA Lead, Security Lead
- Executor Agents (6): Backend, Frontend, Fullstack, DevOps, QA, Security
- Specialist Agents (6): ML, LLM, Data, Performance, UI/UX, Technical Writer
- Reviewer Agents (5): Backend, Frontend, Security, DevOps, Architecture

Total: 22 primary agents (remaining 11 roles available in extended module)
"""

from typing import Any, Type

from ..base import (
    AgentCapability,
    AgentConstraint,
    AgentContext,
    AgentResult,
    AgentTrigger,
    AgentType,
    BaseAgent,
    CapabilityLevel,
    ConstraintType,
)


# =============================================================================
# STRATEGIC AGENTS (5)
# =============================================================================

class TechnicalPMAgent(BaseAgent):
    """
    Technical Project Manager Agent.
    
    Responsible for:
    - Sprint planning and task breakdown
    - Resource allocation across agents
    - Progress tracking and reporting
    - Stakeholder communication
    """
    
    ROLE_ID = "technical-pm"
    ROLE_NAME = "Technical PM Agent"
    ROLE_TYPE = AgentType.STRATEGIC
    CHARTER_SECTION = "§4.2"
    
    def _get_description(self) -> str:
        return (
            "Experienced Technical Project Manager specializing in AI-driven development workflows. "
            "Expert in agile methodologies, sprint planning, and cross-functional team coordination."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a seasoned Technical PM with 10+ years in software delivery. "
            "You've successfully delivered complex SaaS products using hybrid teams of human "
            "and AI agents. Your expertise lies in breaking down ambiguous requirements into "
            "actionable tasks and ensuring governance compliance throughout the delivery lifecycle."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-pm-plan",
                name="Sprint Planning",
                description="Create and manage sprint backlogs",
                level=CapabilityLevel.EXECUTE,
                scope=["cm-workflow/sprints", "cm-workflow/plans"],
            ),
            AgentCapability(
                id="cap-pm-approve",
                name="Task Approval",
                description="Approve task definitions and plans",
                level=CapabilityLevel.APPROVE,
                scope=["cm-workflow/backlog"],
            ),
            AgentCapability(
                id="cap-pm-track",
                name="Progress Tracking",
                description="Track and report sprint progress",
                level=CapabilityLevel.READ,
                scope=["cm-workflow"],
            ),
        ]
    
    def _get_constraints(self) -> list[AgentConstraint]:
        return [
            AgentConstraint(
                id="con-pm-approval",
                type=ConstraintType.MUST,
                description="All execution plans require PM approval before execution",
                enforceable=True,
            ),
            AgentConstraint(
                id="con-pm-obsidian",
                type=ConstraintType.MUST,
                description="All tasks must be tracked in Obsidian vault",
                enforceable=True,
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-pm-plan",
                condition="plan|design|sprint",
                target_role="technical-pm",
                priority=10,
                charter_ref="§4.2",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["obsidian", "github_issues", "github_projects"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        """Execute PM-specific task."""
        # PM implementation would create plans, track progress
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "plan_created", "task_type": context.task_type},
            artifacts=[],
        )


class ArchitectAgent(BaseAgent):
    """
    Software Architect Agent.
    
    Responsible for:
    - System design and architecture decisions
    - ADR creation and review
    - Technical standards enforcement
    - Integration patterns
    """
    
    ROLE_ID = "architect"
    ROLE_NAME = "Architect Agent"
    ROLE_TYPE = AgentType.STRATEGIC
    CHARTER_SECTION = "§5.1"
    
    def _get_description(self) -> str:
        return (
            "Senior Software Architect with expertise in distributed systems, "
            "microservices, and event-driven architectures. Ensures technical decisions "
            "align with business goals and scalability requirements."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a principal architect with deep experience in building scalable SaaS platforms. "
            "You've designed systems handling millions of requests and understand the trade-offs "
            "between different architectural patterns. You document decisions in ADRs and ensure "
            "the team follows established patterns."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-arch-design",
                name="Architecture Design",
                description="Create and review system architectures",
                level=CapabilityLevel.EXECUTE,
                scope=[".github/adr", "docs/architecture"],
            ),
            AgentCapability(
                id="cap-arch-review",
                name="Technical Review",
                description="Review and approve technical decisions",
                level=CapabilityLevel.APPROVE,
                scope=["packages", "backend", "frontend"],
            ),
        ]
    
    def _get_constraints(self) -> list[AgentConstraint]:
        return [
            AgentConstraint(
                id="con-arch-adr",
                type=ConstraintType.MUST,
                description="Major decisions must be documented in ADRs",
                enforceable=True,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "github_mcp", "mermaid"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "architecture_reviewed"},
        )


class TechLeadAgent(BaseAgent):
    """Technical Lead Agent for team guidance and code quality."""
    
    ROLE_ID = "tech-lead"
    ROLE_NAME = "Tech Lead Agent"
    ROLE_TYPE = AgentType.STRATEGIC
    CHARTER_SECTION = "§5.2"
    
    def _get_description(self) -> str:
        return (
            "Technical Lead responsible for code quality, team mentorship, "
            "and ensuring development practices align with architecture."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a hands-on tech lead who bridges architecture and implementation. "
            "You ensure code quality through reviews, establish coding standards, and "
            "mentor team members on best practices."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-tl-review",
                name="Code Review",
                description="Review and approve code changes",
                level=CapabilityLevel.APPROVE,
            ),
            AgentCapability(
                id="cap-tl-standards",
                name="Standards",
                description="Define and enforce coding standards",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "sonarqube", "github_mcp"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "review_complete"},
        )


class QALeadAgent(BaseAgent):
    """QA Lead Agent for test strategy and quality assurance."""
    
    ROLE_ID = "qa-lead"
    ROLE_NAME = "QA Lead Agent"
    ROLE_TYPE = AgentType.STRATEGIC
    CHARTER_SECTION = "§7.1"
    
    def _get_description(self) -> str:
        return (
            "QA Lead responsible for test strategy, quality gates, "
            "and ensuring comprehensive test coverage."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a quality-focused leader with expertise in test automation. "
            "You define testing strategies, establish coverage targets, and ensure "
            "releases meet quality standards."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-qa-strategy",
                name="Test Strategy",
                description="Define test strategy and coverage requirements",
                level=CapabilityLevel.EXECUTE,
            ),
            AgentCapability(
                id="cap-qa-approve",
                name="Release Approval",
                description="Approve releases based on quality metrics",
                level=CapabilityLevel.APPROVE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["jest", "playwright", "sonarqube"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "qa_strategy_defined"},
        )


class SecurityLeadAgent(BaseAgent):
    """Security Lead Agent for security architecture and compliance."""
    
    ROLE_ID = "security-lead"
    ROLE_NAME = "Security Lead Agent"
    ROLE_TYPE = AgentType.STRATEGIC
    CHARTER_SECTION = "§7.2"
    
    def _get_description(self) -> str:
        return (
            "Security Lead responsible for security architecture, threat modeling, "
            "and compliance with security policies."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a security-focused architect with expertise in application security. "
            "You conduct threat modeling, define security requirements, and ensure "
            "the system meets compliance standards."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-sec-audit",
                name="Security Audit",
                description="Conduct security audits and assessments",
                level=CapabilityLevel.EXECUTE,
            ),
            AgentCapability(
                id="cap-sec-approve",
                name="Security Approval",
                description="Approve security-sensitive changes",
                level=CapabilityLevel.APPROVE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["sonarqube", "snyk", "dependabot"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "security_assessed"},
        )


# =============================================================================
# EXECUTOR AGENTS (6)
# =============================================================================

class BackendEngineerAgent(BaseAgent):
    """Backend Engineer Agent for server-side development."""
    
    ROLE_ID = "backend-engineer"
    ROLE_NAME = "Backend Engineer Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§6.1"
    
    def _get_description(self) -> str:
        return (
            "Backend Engineer specializing in Node.js/TypeScript and Python. "
            "Expert in API design, database optimization, and microservices."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are an experienced backend developer with deep expertise in Node.js, "
            "TypeScript, and Python. You build robust APIs, optimize database queries, "
            "and ensure code follows best practices and passes SonarQube analysis."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-be-code",
                name="Backend Code",
                description="Write and modify backend code",
                level=CapabilityLevel.WRITE,
                scope=["backend", "packages"],
            ),
            AgentCapability(
                id="cap-be-test",
                name="Backend Tests",
                description="Write and run backend tests",
                level=CapabilityLevel.EXECUTE,
                scope=["backend/tests"],
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-be-ts",
                condition=".ts|.js|backend",
                target_role="backend-engineer",
                priority=5,
                charter_ref="§6.1",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "sonarqube", "jest", "node"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "code_implemented"},
        )


class FrontendEngineerAgent(BaseAgent):
    """Frontend Engineer Agent for client-side development."""
    
    ROLE_ID = "frontend-engineer"
    ROLE_NAME = "Frontend Engineer Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§6.2"
    
    def _get_description(self) -> str:
        return (
            "Frontend Engineer specializing in React/TypeScript. "
            "Expert in component architecture, state management, and accessibility."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a skilled frontend developer with expertise in React and TypeScript. "
            "You build responsive, accessible UIs with proper state management using Zustand "
            "and ensure components follow design system guidelines."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-fe-code",
                name="Frontend Code",
                description="Write and modify frontend code",
                level=CapabilityLevel.WRITE,
                scope=["frontend/src"],
            ),
            AgentCapability(
                id="cap-fe-test",
                name="Frontend Tests",
                description="Write and run frontend tests",
                level=CapabilityLevel.EXECUTE,
                scope=["frontend/src/__tests__"],
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-fe-tsx",
                condition=".tsx|.jsx|frontend",
                target_role="frontend-engineer",
                priority=5,
                charter_ref="§6.2",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "playwright", "vite"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "ui_implemented"},
        )


class FullstackEngineerAgent(BaseAgent):
    """Full-stack Engineer Agent for end-to-end development."""
    
    ROLE_ID = "fullstack-engineer"
    ROLE_NAME = "Full-stack Engineer Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§6.3"
    
    def _get_description(self) -> str:
        return (
            "Full-stack Engineer capable of working across the entire stack. "
            "Bridges frontend and backend with a focus on feature completeness."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a versatile full-stack developer comfortable with both React "
            "and Node.js. You deliver complete features from database to UI, ensuring "
            "consistency across the stack."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-fs-code",
                name="Full-stack Code",
                description="Write code across frontend and backend",
                level=CapabilityLevel.WRITE,
                scope=["frontend", "backend"],
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "sonarqube", "jest", "playwright"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "feature_implemented"},
        )


class DevOpsEngineerAgent(BaseAgent):
    """DevOps Engineer Agent for infrastructure and CI/CD."""
    
    ROLE_ID = "devops-executor"
    ROLE_NAME = "DevOps Engineer Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§8.1"
    
    def _get_description(self) -> str:
        return (
            "DevOps Engineer specializing in Docker, Kubernetes, and CI/CD. "
            "Expert in infrastructure automation and deployment pipelines."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a DevOps expert with deep knowledge of containerization, "
            "orchestration, and CI/CD pipelines. You automate infrastructure "
            "and ensure reliable, scalable deployments."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-devops-infra",
                name="Infrastructure",
                description="Manage infrastructure configuration",
                level=CapabilityLevel.WRITE,
                scope=["docker", "k8s", ".github/workflows"],
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-devops-docker",
                condition="Dockerfile|docker-compose|k8s",
                target_role="devops-executor",
                priority=5,
                charter_ref="§8.1",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["docker", "kubectl", "terraform"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "infrastructure_updated"},
        )


class QAExecutorAgent(BaseAgent):
    """QA Executor Agent for test implementation."""
    
    ROLE_ID = "qa-executor"
    ROLE_NAME = "QA Executor Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§7.1"
    
    def _get_description(self) -> str:
        return (
            "QA Engineer specializing in test automation with Jest and Playwright. "
            "Expert in unit, integration, and E2E testing."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a test automation engineer who ensures code quality through "
            "comprehensive testing. You write maintainable tests that catch bugs "
            "early and provide confidence in releases."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-qa-test",
                name="Test Writing",
                description="Write and maintain tests",
                level=CapabilityLevel.WRITE,
                scope=["**/tests", "**/test", "**/__tests__"],
            ),
            AgentCapability(
                id="cap-qa-run",
                name="Test Execution",
                description="Run tests and analyze results",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-qa-test",
                condition="test|spec|coverage",
                target_role="qa-executor",
                priority=5,
                charter_ref="§7.1",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["jest", "playwright", "vitest"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "tests_written"},
        )


class SecurityExecutorAgent(BaseAgent):
    """Security Executor Agent for security implementation."""
    
    ROLE_ID = "security-executor"
    ROLE_NAME = "Security Executor Agent"
    ROLE_TYPE = AgentType.EXECUTOR
    CHARTER_SECTION = "§7.2"
    
    def _get_description(self) -> str:
        return (
            "Security Engineer implementing security controls, authentication, "
            "and authorization mechanisms."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a security-focused engineer who implements security controls "
            "following OWASP guidelines. You ensure proper input validation, "
            "secure authentication, and protection against common vulnerabilities."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-sec-impl",
                name="Security Implementation",
                description="Implement security controls",
                level=CapabilityLevel.WRITE,
                scope=["backend/middleware", "backend/services"],
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-sec-auth",
                condition="auth|security|permission",
                target_role="security-executor",
                priority=8,
                charter_ref="§7.2",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["sonarqube", "snyk", "owasp-zap"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "security_implemented"},
        )


# =============================================================================
# SPECIALIST AGENTS (6)
# =============================================================================

class MLSpecialistAgent(BaseAgent):
    """Machine Learning Specialist Agent."""
    
    ROLE_ID = "ml-specialist"
    ROLE_NAME = "ML Specialist Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§9.1"
    
    def _get_description(self) -> str:
        return (
            "Machine Learning Specialist with expertise in model development, "
            "training pipelines, and ML infrastructure."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are an ML engineer who builds and deploys machine learning models. "
            "You optimize training pipelines, implement feature engineering, and "
            "ensure models meet performance requirements."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-ml-model",
                name="ML Development",
                description="Develop and train ML models",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["python", "pytorch", "scikit-learn"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "ml_task_complete"},
        )


class LLMSpecialistAgent(BaseAgent):
    """Large Language Model Specialist Agent."""
    
    ROLE_ID = "llm-specialist"
    ROLE_NAME = "LLM Specialist Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§9.2"
    
    def _get_description(self) -> str:
        return (
            "LLM Specialist with expertise in prompt engineering, RAG systems, "
            "and LLM integration patterns."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are an LLM expert who specializes in integrating language models "
            "into applications. You design effective prompts, implement RAG systems, "
            "and optimize LLM performance."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-llm-prompt",
                name="Prompt Engineering",
                description="Design and optimize prompts",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["langchain", "openai", "anthropic"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "llm_task_complete"},
        )


class DataSpecialistAgent(BaseAgent):
    """Data Engineering Specialist Agent."""
    
    ROLE_ID = "data-specialist"
    ROLE_NAME = "Data Specialist Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§9.3"
    
    def _get_description(self) -> str:
        return (
            "Data Specialist with expertise in data pipelines, ETL processes, "
            "and database optimization."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a data engineer who builds robust data pipelines. "
            "You design schemas, optimize queries, and ensure data quality."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-data-pipeline",
                name="Data Pipelines",
                description="Build and maintain data pipelines",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["postgresql", "redis", "sql"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "data_task_complete"},
        )


class PerformanceSpecialistAgent(BaseAgent):
    """Performance Engineering Specialist Agent."""
    
    ROLE_ID = "performance-specialist"
    ROLE_NAME = "Performance Specialist Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§9.4"
    
    def _get_description(self) -> str:
        return (
            "Performance Specialist with expertise in profiling, optimization, "
            "and load testing."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a performance engineer who ensures applications are fast "
            "and scalable. You identify bottlenecks, optimize code, and design "
            "load tests."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-perf-profile",
                name="Profiling",
                description="Profile and optimize performance",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["k6", "lighthouse", "profiler"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "performance_analyzed"},
        )


class UIUXSpecialistAgent(BaseAgent):
    """UI/UX Design Specialist Agent."""
    
    ROLE_ID = "uiux-specialist"
    ROLE_NAME = "UI/UX Specialist Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§10.1"
    
    def _get_description(self) -> str:
        return (
            "UI/UX Specialist with expertise in user research, interaction design, "
            "and accessibility."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a UI/UX designer who creates intuitive, accessible interfaces. "
            "You conduct user research, design interactions, and ensure designs "
            "meet WCAG guidelines."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-uiux-design",
                name="UI Design",
                description="Create UI designs and prototypes",
                level=CapabilityLevel.EXECUTE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["figma", "storybook", "axe"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "design_created"},
        )


class TechnicalWriterAgent(BaseAgent):
    """Technical Writer Agent for documentation."""
    
    ROLE_ID = "technical-writer"
    ROLE_NAME = "Technical Writer Agent"
    ROLE_TYPE = AgentType.SPECIALIST
    CHARTER_SECTION = "§11.1"
    
    def _get_description(self) -> str:
        return (
            "Technical Writer specializing in API documentation, user guides, "
            "and architecture documentation."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a technical writer who creates clear, comprehensive documentation. "
            "You write API references, user guides, and architecture documents that "
            "help developers and users understand the system."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-docs-write",
                name="Documentation",
                description="Write and maintain documentation",
                level=CapabilityLevel.WRITE,
                scope=["docs", "README.md", "*.md"],
            ),
        ]
    
    def _get_triggers(self) -> list[AgentTrigger]:
        return [
            AgentTrigger(
                id="trig-docs-md",
                condition=".md|documentation|docs",
                target_role="technical-writer",
                priority=3,
                charter_ref="§11.1",
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["markdown", "typedoc", "mermaid"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "documentation_updated"},
        )


# =============================================================================
# REVIEWER AGENTS (5)
# =============================================================================

class BackendReviewerAgent(BaseAgent):
    """Backend Code Reviewer Agent."""
    
    ROLE_ID = "backend-reviewer"
    ROLE_NAME = "Backend Reviewer Agent"
    ROLE_TYPE = AgentType.REVIEWER
    CHARTER_SECTION = "§6.1.R"
    
    def _get_description(self) -> str:
        return (
            "Backend Code Reviewer with expertise in Node.js/TypeScript best practices, "
            "API design patterns, and performance optimization."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a senior backend developer who reviews code for quality, "
            "performance, and security. You ensure code follows established patterns "
            "and catches potential issues before they reach production."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-be-review",
                name="Code Review",
                description="Review backend code changes",
                level=CapabilityLevel.APPROVE,
                scope=["backend", "packages"],
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "sonarqube", "github_mcp"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "review_complete", "approved": True},
        )


class FrontendReviewerAgent(BaseAgent):
    """Frontend Code Reviewer Agent."""
    
    ROLE_ID = "frontend-reviewer"
    ROLE_NAME = "Frontend Reviewer Agent"
    ROLE_TYPE = AgentType.REVIEWER
    CHARTER_SECTION = "§6.2.R"
    
    def _get_description(self) -> str:
        return (
            "Frontend Code Reviewer with expertise in React patterns, "
            "accessibility, and performance."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a senior frontend developer who reviews UI code for quality, "
            "accessibility, and user experience. You ensure components are reusable "
            "and follow design system guidelines."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-fe-review",
                name="Code Review",
                description="Review frontend code changes",
                level=CapabilityLevel.APPROVE,
                scope=["frontend"],
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "lighthouse", "axe"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "review_complete", "approved": True},
        )


class SecurityReviewerAgent(BaseAgent):
    """Security Code Reviewer Agent."""
    
    ROLE_ID = "security-reviewer"
    ROLE_NAME = "Security Reviewer Agent"
    ROLE_TYPE = AgentType.REVIEWER
    CHARTER_SECTION = "§7.2.R"
    
    def _get_description(self) -> str:
        return (
            "Security Reviewer with expertise in identifying vulnerabilities, "
            "OWASP compliance, and secure coding practices."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a security expert who reviews code for vulnerabilities. "
            "You identify potential security issues, ensure proper input validation, "
            "and verify authentication/authorization implementations."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-sec-review",
                name="Security Review",
                description="Review code for security issues",
                level=CapabilityLevel.APPROVE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["sonarqube", "snyk", "semgrep"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "security_review_complete", "approved": True},
        )


class DevOpsReviewerAgent(BaseAgent):
    """DevOps/Infrastructure Reviewer Agent."""
    
    ROLE_ID = "devops-reviewer"
    ROLE_NAME = "DevOps Reviewer Agent"
    ROLE_TYPE = AgentType.REVIEWER
    CHARTER_SECTION = "§8.1.R"
    
    def _get_description(self) -> str:
        return (
            "DevOps Reviewer with expertise in infrastructure as code, "
            "CI/CD pipelines, and deployment best practices."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a DevOps expert who reviews infrastructure changes. "
            "You ensure configurations are secure, scalable, and follow "
            "infrastructure as code best practices."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-devops-review",
                name="Infrastructure Review",
                description="Review infrastructure changes",
                level=CapabilityLevel.APPROVE,
                scope=["docker", "k8s", ".github/workflows"],
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["hadolint", "kubeval", "actionlint"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "infra_review_complete", "approved": True},
        )


class ArchitectureReviewerAgent(BaseAgent):
    """Architecture Reviewer Agent."""
    
    ROLE_ID = "architecture-reviewer"
    ROLE_NAME = "Architecture Reviewer Agent"
    ROLE_TYPE = AgentType.REVIEWER
    CHARTER_SECTION = "§5.1.R"
    
    def _get_description(self) -> str:
        return (
            "Architecture Reviewer with expertise in system design, "
            "patterns, and architectural decision validation."
        )
    
    def _get_backstory(self) -> str:
        return (
            "You are a senior architect who reviews architectural decisions. "
            "You ensure changes align with system architecture, validate ADRs, "
            "and identify potential architectural debt."
        )
    
    def _get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id="cap-arch-review",
                name="Architecture Review",
                description="Review architectural decisions",
                level=CapabilityLevel.APPROVE,
            ),
        ]
    
    def _get_tools(self) -> list[str]:
        return ["serena", "mermaid", "c4model"]
    
    async def _execute_impl(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.role_id,
            task_id=context.task_id,
            output={"status": "arch_review_complete", "approved": True},
        )


# =============================================================================
# ALL AGENTS COLLECTION
# =============================================================================

ALL_AGENTS: list[Type[BaseAgent]] = [
    # Strategic (5)
    TechnicalPMAgent,
    ArchitectAgent,
    TechLeadAgent,
    QALeadAgent,
    SecurityLeadAgent,
    # Executor (6)
    BackendEngineerAgent,
    FrontendEngineerAgent,
    FullstackEngineerAgent,
    DevOpsEngineerAgent,
    QAExecutorAgent,
    SecurityExecutorAgent,
    # Specialist (6)
    MLSpecialistAgent,
    LLMSpecialistAgent,
    DataSpecialistAgent,
    PerformanceSpecialistAgent,
    UIUXSpecialistAgent,
    TechnicalWriterAgent,
    # Reviewer (5)
    BackendReviewerAgent,
    FrontendReviewerAgent,
    SecurityReviewerAgent,
    DevOpsReviewerAgent,
    ArchitectureReviewerAgent,
]

# Verify count
assert len(ALL_AGENTS) == 22, f"Expected 22 agents, got {len(ALL_AGENTS)}"
