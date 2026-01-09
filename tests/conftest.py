"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime


@pytest.fixture
def sample_role_data():
    """Sample role data for testing."""
    return {
        "id": "backend-engineer",
        "name": "Backend Engineer",
        "type": "ai-agent",
        "charter_section": "§6.1",
        "capabilities": ["Write TypeScript code", "Design APIs", "Database design"],
        "constraints": ["Must follow coding standards", "Must not commit secrets"],
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent configuration data."""
    return {
        "id": "agent-test-001",
        "name": "Test Backend Engineer",
        "role_id": "backend-engineer",
        "provider": "anthropic",
        "status": "pending",
        "capabilities": ["code-generation", "code-review"],
        "config": {"temperature": 0.7, "max_tokens": 4096},
    }


@pytest.fixture
def sample_task_data():
    """Sample task assignment data."""
    return {
        "id": "task-test-001",
        "title": "Implement user authentication",
        "description": "Add JWT-based authentication to the API endpoints",
        "status": "not-started",
        "priority": "P0",
        "story_points": 5,
        "tags": ["security", "backend", "auth"],
    }


@pytest.fixture
def mock_governance_context():
    """Mock governance context for testing."""
    return {
        "session_id": "session-001",
        "role": "backend-engineer",
        "mode": "executor",
        "governance_loaded": True,
        "mcp_active": ["Serena", "GitHub"],
        "obsidian_task": "TASK-028",
        "tracking_issue": "#53",
    }
