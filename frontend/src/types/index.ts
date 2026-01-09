// Agent Types
export type AgentStatus = 'active' | 'idle' | 'error' | 'offline';
export type AgentRole = 'strategic' | 'executor' | 'reviewer' | 'specialist';

export interface Agent {
  id: string;
  name: string;
  role: AgentRole;
  status: AgentStatus;
  currentTask?: string;
  lastActivity: string;
  metrics: {
    tasksCompleted: number;
    successRate: number;
    avgResponseTime: number;
  };
}

// Task Types
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked';
export type TaskPriority = 'P0' | 'P1' | 'P2' | 'P3';

export interface Task {
  id: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: string;
  progress: number;
  estimatedPoints: number;
  createdAt: string;
  updatedAt: string;
}

// Activity Types
export type ActivityType = 'task_started' | 'task_completed' | 'agent_status' | 'error' | 'system';

export interface Activity {
  id: string;
  type: ActivityType;
  message: string;
  agentId?: string;
  taskId?: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error';
}

// System Metrics
export interface SystemMetrics {
  cpu: number;
  memory: number;
  activeAgents: number;
  totalAgents: number;
  tasksInProgress: number;
  tasksCompleted: number;
  tasksFailed: number;
  uptime: number;
  llmCalls: number;
  llmLatency: number;
}

// Crew Types
export type CrewStatus = 'idle' | 'planning' | 'executing' | 'reviewing' | 'completed';

export interface Crew {
  id: string;
  name: string;
  status: CrewStatus;
  agents: string[];
  currentSprint?: string;
  progress: number;
}

// WebSocket Event Types
export type DashboardEventType = 'agent_status' | 'task_progress' | 'metrics' | 'activity' | 'connection';

export interface DashboardEvent<T = unknown> {
  type: DashboardEventType;
  payload: T;
  timestamp: string;
}
