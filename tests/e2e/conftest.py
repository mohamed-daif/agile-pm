"""E2E Test Configuration and Fixtures."""

import os
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Environment configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agilepm:testpass@localhost:5433/agilepm_test")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380/0")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def api_client() -> Generator[httpx.Client, None, None]:
    """Create HTTP client for API tests."""
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
async def async_api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async HTTP client for API tests."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine."""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create database session with automatic rollback."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def clean_db(db_session: Session) -> None:
    """Clean database before each test."""
    # Truncate all tables (implement based on your schema)
    # db_session.execute("TRUNCATE TABLE agents, tasks, activities CASCADE")
    pass


@pytest.fixture
def mock_sprint():
    """Mock sprint data for testing."""
    return {
        "id": "sprint-001",
        "name": "Sprint 05",
        "goal": "Frontend Dashboard & Production Hardening",
        "status": "active",
        "start_date": "2026-01-20",
        "end_date": "2026-01-27",
        "tasks": [
            {
                "id": "task-001",
                "title": "S05-001: React Dashboard Components",
                "priority": "P0",
                "status": "in_progress",
                "estimated_points": 8,
            },
            {
                "id": "task-002",
                "title": "S05-002: WebSocket Integration",
                "priority": "P0",
                "status": "pending",
                "estimated_points": 6,
            },
        ],
    }


@pytest.fixture
def mock_agents():
    """Mock agent data for testing."""
    return [
        {
            "id": "agent-001",
            "name": "Technical PM Agent",
            "role": "strategic",
            "status": "active",
            "metrics": {"tasks_completed": 45, "success_rate": 0.98},
        },
        {
            "id": "agent-002",
            "name": "Backend Engineer Agent",
            "role": "executor",
            "status": "active",
            "metrics": {"tasks_completed": 120, "success_rate": 0.95},
        },
        {
            "id": "agent-003",
            "name": "QA Executor Agent",
            "role": "reviewer",
            "status": "idle",
            "metrics": {"tasks_completed": 80, "success_rate": 0.99},
        },
    ]
