"""Metrics collection for dashboard."""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict
import time

from pydantic import BaseModel, Field


class AgentMetrics(BaseModel):
    """Metrics for a single agent."""

    agent_id: str
    role: str
    
    # Execution metrics
    tasks_executed: int = 0
    tasks_successful: int = 0
    tasks_failed: int = 0
    
    # Timing metrics
    total_execution_time: float = 0.0  # seconds
    avg_execution_time: float = 0.0
    min_execution_time: Optional[float] = None
    max_execution_time: Optional[float] = None
    
    # Token metrics (if LLM)
    total_tokens_used: int = 0
    avg_tokens_per_task: float = 0.0
    
    # Status
    current_status: str = "idle"
    last_active: Optional[datetime] = None
    
    def record_execution(
        self,
        execution_time: float,
        success: bool,
        tokens_used: int = 0,
    ) -> None:
        """Record a task execution.
        
        Args:
            execution_time: Time in seconds
            success: Whether task succeeded
            tokens_used: Tokens consumed
        """
        self.tasks_executed += 1
        if success:
            self.tasks_successful += 1
        else:
            self.tasks_failed += 1
        
        self.total_execution_time += execution_time
        self.avg_execution_time = self.total_execution_time / self.tasks_executed
        
        if self.min_execution_time is None or execution_time < self.min_execution_time:
            self.min_execution_time = execution_time
        if self.max_execution_time is None or execution_time > self.max_execution_time:
            self.max_execution_time = execution_time
        
        self.total_tokens_used += tokens_used
        self.avg_tokens_per_task = self.total_tokens_used / self.tasks_executed
        
        self.last_active = datetime.utcnow()
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.tasks_executed == 0:
            return 0.0
        return self.tasks_successful / self.tasks_executed


class TaskMetrics(BaseModel):
    """Metrics for task execution."""

    task_id: str
    title: str
    
    # Status
    status: str = "pending"
    assigned_agent: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Progress
    progress: float = 0.0
    steps_total: int = 1
    steps_completed: int = 0
    
    # Output
    output_size: int = 0
    tokens_used: int = 0
    
    def start(self, agent_id: str) -> None:
        """Mark task as started.
        
        Args:
            agent_id: Assigned agent
        """
        self.status = "in_progress"
        self.assigned_agent = agent_id
        self.started_at = datetime.utcnow()
    
    def update_progress(self, step: int) -> None:
        """Update progress.
        
        Args:
            step: Current step number
        """
        self.steps_completed = step
        self.progress = step / self.steps_total if self.steps_total > 0 else 0.0
    
    def complete(self, success: bool, output_size: int = 0, tokens: int = 0) -> None:
        """Mark task as completed.
        
        Args:
            success: Whether task succeeded
            output_size: Size of output
            tokens: Tokens used
        """
        self.status = "completed" if success else "failed"
        self.completed_at = datetime.utcnow()
        self.progress = 1.0 if success else self.progress
        self.output_size = output_size
        self.tokens_used = tokens
        
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()


class CrewMetrics(BaseModel):
    """Metrics for crew execution."""

    crew_id: str
    crew_name: str
    
    # Agents
    agents_count: int = 0
    agent_ids: list[str] = Field(default_factory=list)
    
    # Tasks
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Status
    status: str = "pending"
    
    @property
    def progress(self) -> float:
        """Calculate overall progress."""
        if self.tasks_total == 0:
            return 0.0
        return (self.tasks_completed + self.tasks_failed) / self.tasks_total


class SystemMetrics(BaseModel):
    """System-wide metrics."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Agents
    active_agents: int = 0
    idle_agents: int = 0
    
    # Tasks
    tasks_queued: int = 0
    tasks_in_progress: int = 0
    tasks_completed_last_hour: int = 0
    
    # Performance
    avg_task_duration: float = 0.0
    success_rate: float = 0.0
    
    # Resources
    memory_sessions_active: int = 0
    websocket_connections: int = 0
    
    # Tokens
    tokens_used_last_hour: int = 0


class MetricsCollector:
    """Collects and aggregates metrics from agents and tasks."""

    def __init__(self):
        """Initialize metrics collector."""
        self._agent_metrics: dict[str, AgentMetrics] = {}
        self._task_metrics: dict[str, TaskMetrics] = {}
        self._crew_metrics: dict[str, CrewMetrics] = {}
        self._history: list[SystemMetrics] = []
        self._start_time = time.time()
    
    def register_agent(self, agent_id: str, role: str) -> AgentMetrics:
        """Register an agent for metrics collection.
        
        Args:
            agent_id: Agent identifier
            role: Agent role
            
        Returns:
            Agent metrics object
        """
        if agent_id not in self._agent_metrics:
            self._agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                role=role,
            )
        return self._agent_metrics[agent_id]
    
    def register_task(self, task_id: str, title: str, steps: int = 1) -> TaskMetrics:
        """Register a task for metrics collection.
        
        Args:
            task_id: Task identifier
            title: Task title
            steps: Number of steps
            
        Returns:
            Task metrics object
        """
        if task_id not in self._task_metrics:
            self._task_metrics[task_id] = TaskMetrics(
                task_id=task_id,
                title=title,
                steps_total=steps,
            )
        return self._task_metrics[task_id]
    
    def register_crew(
        self,
        crew_id: str,
        crew_name: str,
        agent_ids: list[str],
        tasks_count: int,
    ) -> CrewMetrics:
        """Register a crew for metrics collection.
        
        Args:
            crew_id: Crew identifier
            crew_name: Crew name
            agent_ids: List of agent IDs
            tasks_count: Number of tasks
            
        Returns:
            Crew metrics object
        """
        if crew_id not in self._crew_metrics:
            self._crew_metrics[crew_id] = CrewMetrics(
                crew_id=crew_id,
                crew_name=crew_name,
                agents_count=len(agent_ids),
                agent_ids=agent_ids,
                tasks_total=tasks_count,
            )
        return self._crew_metrics[crew_id]
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent metrics if found
        """
        return self._agent_metrics.get(agent_id)
    
    def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """Get metrics for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task metrics if found
        """
        return self._task_metrics.get(task_id)
    
    def get_crew_metrics(self, crew_id: str) -> Optional[CrewMetrics]:
        """Get metrics for a crew.
        
        Args:
            crew_id: Crew identifier
            
        Returns:
            Crew metrics if found
        """
        return self._crew_metrics.get(crew_id)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics.
        
        Returns:
            System metrics snapshot
        """
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Count agent states
        active = sum(
            1 for m in self._agent_metrics.values()
            if m.current_status != "idle"
        )
        idle = len(self._agent_metrics) - active
        
        # Count task states
        queued = sum(
            1 for m in self._task_metrics.values()
            if m.status == "pending"
        )
        in_progress = sum(
            1 for m in self._task_metrics.values()
            if m.status == "in_progress"
        )
        completed_hour = sum(
            1 for m in self._task_metrics.values()
            if m.completed_at and m.completed_at > one_hour_ago
        )
        
        # Calculate averages
        completed_tasks = [
            m for m in self._task_metrics.values()
            if m.duration is not None
        ]
        avg_duration = (
            sum(m.duration for m in completed_tasks) / len(completed_tasks)
            if completed_tasks else 0.0
        )
        
        successful = sum(
            1 for m in self._task_metrics.values()
            if m.status == "completed"
        )
        total_finished = sum(
            1 for m in self._task_metrics.values()
            if m.status in ["completed", "failed"]
        )
        success_rate = successful / total_finished if total_finished > 0 else 0.0
        
        # Token usage
        tokens_hour = sum(
            m.tokens_used for m in self._task_metrics.values()
            if m.completed_at and m.completed_at > one_hour_ago
        )
        
        return SystemMetrics(
            timestamp=now,
            active_agents=active,
            idle_agents=idle,
            tasks_queued=queued,
            tasks_in_progress=in_progress,
            tasks_completed_last_hour=completed_hour,
            avg_task_duration=avg_duration,
            success_rate=success_rate,
            tokens_used_last_hour=tokens_hour,
        )
    
    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics as a dictionary.
        
        Returns:
            Dict with all metrics
        """
        return {
            "system": self.get_system_metrics().model_dump(),
            "agents": {
                k: v.model_dump() for k, v in self._agent_metrics.items()
            },
            "tasks": {
                k: v.model_dump() for k, v in self._task_metrics.items()
            },
            "crews": {
                k: v.model_dump() for k, v in self._crew_metrics.items()
            },
            "uptime_seconds": time.time() - self._start_time,
        }
    
    def snapshot(self) -> None:
        """Take a snapshot of system metrics for history."""
        metrics = self.get_system_metrics()
        self._history.append(metrics)
        
        # Keep last 1000 snapshots
        if len(self._history) > 1000:
            self._history = self._history[-1000:]
    
    def get_history(
        self,
        minutes: int = 60,
    ) -> list[SystemMetrics]:
        """Get historical metrics.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of historical metrics
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self._history if m.timestamp > cutoff]
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._agent_metrics.clear()
        self._task_metrics.clear()
        self._crew_metrics.clear()
        self._history.clear()
        self._start_time = time.time()
