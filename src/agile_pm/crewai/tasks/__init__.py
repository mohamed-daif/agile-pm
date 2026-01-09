"""Task definitions for CrewAI crews.

This module provides task templates for common Agile-PM workflows.
"""

from typing import Any, Optional

from crewai import Agent, Task
from pydantic import BaseModel, Field


class TaskTemplate(BaseModel):
    """Template for creating tasks."""
    
    name: str
    description_template: str
    expected_output: str
    requires_context: bool = False


# Task Templates
TASK_TEMPLATES: dict[str, TaskTemplate] = {
    "planning": TaskTemplate(
        name="Planning Task",
        description_template="""Create an implementation plan for: {feature}

Requirements:
{requirements}

Constraints:
{constraints}

Create a detailed plan including:
1. Executive summary
2. Task breakdown with story points
3. Dependencies
4. Risk assessment
5. Timeline
""",
        expected_output="Implementation plan in Markdown format with approval section",
        requires_context=False,
    ),
    
    "implementation": TaskTemplate(
        name="Implementation Task",
        description_template="""Implement: {task_title}

Description:
{description}

Acceptance Criteria:
{acceptance_criteria}

Guidelines:
- Follow existing code patterns
- Add comprehensive tests
- Update documentation
- Ensure no secrets in code
""",
        expected_output="Implementation with code, tests, and documentation updates",
        requires_context=True,
    ),
    
    "review": TaskTemplate(
        name="Review Task",
        description_template="""Review the following {artifact_type}:

{content}

Review criteria:
{criteria}

Provide:
1. Summary assessment
2. Findings by severity (Critical, Major, Minor, Info)
3. Recommendations
4. Approval decision
""",
        expected_output="Structured review with findings and recommendation",
        requires_context=True,
    ),
    
    "testing": TaskTemplate(
        name="Testing Task",
        description_template="""Create tests for: {subject}

Test requirements:
{requirements}

Ensure coverage of:
- Happy path scenarios
- Edge cases
- Error handling
- Input validation

Target coverage: {coverage_target}%
""",
        expected_output="Test suite with coverage report",
        requires_context=True,
    ),
    
    "deployment": TaskTemplate(
        name="Deployment Task",
        description_template="""Deploy {service} to {environment}

Pre-deployment checklist:
{checklist}

Deployment steps:
1. Verify tests passing
2. Build artifacts
3. Deploy to environment
4. Run smoke tests
5. Verify monitoring
""",
        expected_output="Deployment report with status and any issues",
        requires_context=False,
    ),
}


def create_task(
    template_name: str,
    agent: Agent,
    variables: dict[str, Any],
    context: Optional[list[Task]] = None,
) -> Task:
    """Create a task from template.
    
    Args:
        template_name: Name of template to use
        agent: Agent to assign task to
        variables: Variables to fill template
        context: Optional list of context tasks
        
    Returns:
        Configured Task
        
    Raises:
        ValueError: If template not found
    """
    if template_name not in TASK_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Valid: {list(TASK_TEMPLATES.keys())}")
    
    template = TASK_TEMPLATES[template_name]
    description = template.description_template.format(**variables)
    
    task_kwargs = {
        "description": description,
        "agent": agent,
        "expected_output": template.expected_output,
    }
    
    if context and template.requires_context:
        task_kwargs["context"] = context
    
    return Task(**task_kwargs)


# Convenience classes for common task types
class PlanningTask:
    """Factory for planning tasks."""
    
    @staticmethod
    def create(
        agent: Agent,
        feature: str,
        requirements: str,
        constraints: str = "Standard governance rules apply",
    ) -> Task:
        """Create a planning task."""
        return create_task(
            "planning",
            agent,
            {
                "feature": feature,
                "requirements": requirements,
                "constraints": constraints,
            },
        )


class ImplementationTask:
    """Factory for implementation tasks."""
    
    @staticmethod
    def create(
        agent: Agent,
        task_title: str,
        description: str,
        acceptance_criteria: str,
        context: Optional[list[Task]] = None,
    ) -> Task:
        """Create an implementation task."""
        return create_task(
            "implementation",
            agent,
            {
                "task_title": task_title,
                "description": description,
                "acceptance_criteria": acceptance_criteria,
            },
            context,
        )


class ReviewTask:
    """Factory for review tasks."""
    
    @staticmethod
    def create(
        agent: Agent,
        artifact_type: str,
        content: str,
        criteria: str,
        context: Optional[list[Task]] = None,
    ) -> Task:
        """Create a review task."""
        return create_task(
            "review",
            agent,
            {
                "artifact_type": artifact_type,
                "content": content,
                "criteria": criteria,
            },
            context,
        )


class TestingTask:
    """Factory for testing tasks."""
    
    @staticmethod
    def create(
        agent: Agent,
        subject: str,
        requirements: str,
        coverage_target: int = 80,
        context: Optional[list[Task]] = None,
    ) -> Task:
        """Create a testing task."""
        return create_task(
            "testing",
            agent,
            {
                "subject": subject,
                "requirements": requirements,
                "coverage_target": coverage_target,
            },
            context,
        )


class DeploymentTask:
    """Factory for deployment tasks."""
    
    @staticmethod
    def create(
        agent: Agent,
        service: str,
        environment: str,
        checklist: str,
    ) -> Task:
        """Create a deployment task."""
        return create_task(
            "deployment",
            agent,
            {
                "service": service,
                "environment": environment,
                "checklist": checklist,
            },
        )
