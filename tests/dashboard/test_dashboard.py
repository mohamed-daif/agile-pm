"""Tests for dashboard events and metrics."""

import pytest
from datetime import datetime, timedelta

from agile_pm.dashboard.events import (
    DashboardEvent,
    EventType,
    AgentStatusEvent,
    TaskProgressEvent,
    MetricsEvent,
    ConnectionEvent,
    ErrorEvent,
)
from agile_pm.dashboard.metrics import (
    AgentMetrics,
    TaskMetrics,
    CrewMetrics,
    SystemMetrics,
    MetricsCollector,
)


class TestDashboardEvents:
    """Tests for dashboard event types."""

    def test_base_event(self):
        """Test creating a base event."""
        event = DashboardEvent(
            type=EventType.AGENT_STARTED,
            source="test-agent",
            data={"key": "value"},
        )
        
        assert event.type == EventType.AGENT_STARTED
        assert event.source == "test-agent"
        assert event.data == {"key": "value"}
        assert event.id is not None
        assert event.timestamp is not None
    
    def test_agent_status_event(self):
        """Test agent status event."""
        event = AgentStatusEvent(
            source="system",
            agent_id="agent-1",
            agent_role="Backend Engineer",
            status="started",
            message="Starting task",
            task_id="task-123",
        )
        
        assert event.type == EventType.AGENT_STARTED
        assert event.agent_id == "agent-1"
        assert event.agent_role == "Backend Engineer"
        assert event.status == "started"
    
    def test_task_progress_event(self):
        """Test task progress event."""
        event = TaskProgressEvent(
            source="executor",
            task_id="task-123",
            title="Implement feature",
            progress=0.5,
            status="in_progress",
            assigned_agent="agent-1",
        )
        
        assert event.type == EventType.TASK_PROGRESS
        assert event.task_id == "task-123"
        assert event.progress == 0.5
        assert event.status == "in_progress"
    
    def test_metrics_event(self):
        """Test metrics event."""
        event = MetricsEvent(
            source="collector",
            metrics={"cpu": 50, "memory": 1024},
            period="5m",
        )
        
        assert event.type == EventType.METRICS_UPDATE
        assert event.metrics["cpu"] == 50
        assert event.period == "5m"
    
    def test_connection_event(self):
        """Test connection event."""
        event = ConnectionEvent(
            source="server",
            client_id="client-123",
            action="connected",
            ip_address="192.168.1.1",
        )
        
        assert event.type == EventType.CONNECTION
        assert event.client_id == "client-123"
        assert event.action == "connected"
    
    def test_error_event(self):
        """Test error event."""
        event = ErrorEvent(
            source="agent",
            error_type="RuntimeError",
            error_message="Something went wrong",
            stack_trace="...",
            context={"task_id": "123"},
        )
        
        assert event.type == EventType.ERROR
        assert event.error_type == "RuntimeError"
        assert event.error_message == "Something went wrong"


class TestAgentMetrics:
    """Tests for AgentMetrics."""

    def test_create_agent_metrics(self):
        """Test creating agent metrics."""
        metrics = AgentMetrics(
            agent_id="agent-1",
            role="Backend Engineer",
        )
        
        assert metrics.agent_id == "agent-1"
        assert metrics.role == "Backend Engineer"
        assert metrics.tasks_executed == 0
        assert metrics.success_rate == 0.0
    
    def test_record_execution(self):
        """Test recording execution."""
        metrics = AgentMetrics(agent_id="agent-1", role="Test")
        
        metrics.record_execution(
            execution_time=10.5,
            success=True,
            tokens_used=100,
        )
        
        assert metrics.tasks_executed == 1
        assert metrics.tasks_successful == 1
        assert metrics.tasks_failed == 0
        assert metrics.total_execution_time == 10.5
        assert metrics.avg_execution_time == 10.5
        assert metrics.total_tokens_used == 100
        assert metrics.success_rate == 1.0
    
    def test_record_multiple_executions(self):
        """Test recording multiple executions."""
        metrics = AgentMetrics(agent_id="agent-1", role="Test")
        
        metrics.record_execution(10.0, True, 100)
        metrics.record_execution(20.0, True, 200)
        metrics.record_execution(15.0, False, 50)
        
        assert metrics.tasks_executed == 3
        assert metrics.tasks_successful == 2
        assert metrics.tasks_failed == 1
        assert metrics.total_execution_time == 45.0
        assert metrics.avg_execution_time == 15.0
        assert metrics.min_execution_time == 10.0
        assert metrics.max_execution_time == 20.0
        assert metrics.total_tokens_used == 350
        assert metrics.success_rate == pytest.approx(0.666, rel=0.01)


class TestTaskMetrics:
    """Tests for TaskMetrics."""

    def test_create_task_metrics(self):
        """Test creating task metrics."""
        metrics = TaskMetrics(
            task_id="task-1",
            title="Implement feature",
        )
        
        assert metrics.task_id == "task-1"
        assert metrics.status == "pending"
        assert metrics.progress == 0.0
    
    def test_start_task(self):
        """Test starting a task."""
        metrics = TaskMetrics(task_id="task-1", title="Test")
        metrics.start("agent-1")
        
        assert metrics.status == "in_progress"
        assert metrics.assigned_agent == "agent-1"
        assert metrics.started_at is not None
    
    def test_update_progress(self):
        """Test updating progress."""
        metrics = TaskMetrics(
            task_id="task-1",
            title="Test",
            steps_total=4,
        )
        
        metrics.update_progress(2)
        
        assert metrics.steps_completed == 2
        assert metrics.progress == 0.5
    
    def test_complete_task(self):
        """Test completing a task."""
        metrics = TaskMetrics(task_id="task-1", title="Test")
        metrics.start("agent-1")
        metrics.complete(success=True, output_size=500, tokens=150)
        
        assert metrics.status == "completed"
        assert metrics.progress == 1.0
        assert metrics.output_size == 500
        assert metrics.tokens_used == 150
        assert metrics.completed_at is not None
        assert metrics.duration is not None


class TestCrewMetrics:
    """Tests for CrewMetrics."""

    def test_create_crew_metrics(self):
        """Test creating crew metrics."""
        metrics = CrewMetrics(
            crew_id="crew-1",
            crew_name="Planning Crew",
            agents_count=3,
            tasks_total=5,
        )
        
        assert metrics.crew_id == "crew-1"
        assert metrics.crew_name == "Planning Crew"
        assert metrics.progress == 0.0
    
    def test_crew_progress(self):
        """Test crew progress calculation."""
        metrics = CrewMetrics(
            crew_id="crew-1",
            crew_name="Test",
            tasks_total=4,
            tasks_completed=2,
        )
        
        assert metrics.progress == 0.5


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    @pytest.fixture
    def collector(self):
        """Create collector fixture."""
        return MetricsCollector()
    
    def test_register_agent(self, collector):
        """Test registering an agent."""
        metrics = collector.register_agent("agent-1", "Backend Engineer")
        
        assert metrics.agent_id == "agent-1"
        assert metrics.role == "Backend Engineer"
        assert collector.get_agent_metrics("agent-1") is not None
    
    def test_register_task(self, collector):
        """Test registering a task."""
        metrics = collector.register_task("task-1", "Test Task", steps=3)
        
        assert metrics.task_id == "task-1"
        assert metrics.title == "Test Task"
        assert metrics.steps_total == 3
    
    def test_register_crew(self, collector):
        """Test registering a crew."""
        metrics = collector.register_crew(
            crew_id="crew-1",
            crew_name="Planning Crew",
            agent_ids=["a1", "a2"],
            tasks_count=4,
        )
        
        assert metrics.crew_id == "crew-1"
        assert metrics.agents_count == 2
        assert metrics.tasks_total == 4
    
    def test_get_system_metrics(self, collector):
        """Test getting system metrics."""
        # Register some components
        collector.register_agent("a1", "Backend")
        collector.register_agent("a2", "Frontend")
        collector.register_task("t1", "Task 1")
        
        metrics = collector.get_system_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.idle_agents == 2
        assert metrics.tasks_queued == 1
    
    def test_get_all_metrics(self, collector):
        """Test getting all metrics."""
        collector.register_agent("a1", "Test")
        collector.register_task("t1", "Test")
        
        all_metrics = collector.get_all_metrics()
        
        assert "system" in all_metrics
        assert "agents" in all_metrics
        assert "tasks" in all_metrics
        assert "crews" in all_metrics
        assert "uptime_seconds" in all_metrics
        assert "a1" in all_metrics["agents"]
    
    def test_snapshot(self, collector):
        """Test taking snapshots."""
        collector.register_agent("a1", "Test")
        
        collector.snapshot()
        collector.snapshot()
        
        history = collector.get_history(minutes=60)
        assert len(history) == 2
    
    def test_reset(self, collector):
        """Test resetting metrics."""
        collector.register_agent("a1", "Test")
        collector.snapshot()
        
        collector.reset()
        
        assert collector.get_agent_metrics("a1") is None
        assert len(collector.get_history()) == 0
