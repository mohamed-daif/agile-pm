/**
 * Dashboard Event Handler
 * Routes and processes WebSocket events
 */

import { 
  DashboardEvent, 
  DashboardEventType,
  Agent,
  Task,
  Activity,
  SystemMetrics,
  AgentStatus,
  TaskStatus,
} from '@/types';

export interface AgentStatusPayload {
  agentId: string;
  status: AgentStatus;
  currentTask?: string;
}

export interface TaskProgressPayload {
  taskId: string;
  progress: number;
  status: TaskStatus;
}

export interface DashboardState {
  agents: Map<string, Agent>;
  tasks: Map<string, Task>;
  activities: Activity[];
  metrics: SystemMetrics | null;
}

export type StateUpdateCallback = (state: DashboardState) => void;

export class DashboardEventHandler {
  private state: DashboardState = {
    agents: new Map(),
    tasks: new Map(),
    activities: [],
    metrics: null,
  };

  private maxActivities = 100;
  private subscribers: Set<StateUpdateCallback> = new Set();

  subscribe(callback: StateUpdateCallback): () => void {
    this.subscribers.add(callback);
    // Immediately send current state
    callback(this.getState());
    return () => this.subscribers.delete(callback);
  }

  getState(): DashboardState {
    return {
      agents: new Map(this.state.agents),
      tasks: new Map(this.state.tasks),
      activities: [...this.state.activities],
      metrics: this.state.metrics ? { ...this.state.metrics } : null,
    };
  }

  handleEvent(event: DashboardEvent): void {
    switch (event.type) {
      case 'agent_status':
        this.handleAgentStatus(event.payload as AgentStatusPayload);
        break;
      case 'task_progress':
        this.handleTaskProgress(event.payload as TaskProgressPayload);
        break;
      case 'metrics':
        this.handleMetrics(event.payload as SystemMetrics);
        break;
      case 'activity':
        this.handleActivity(event.payload as Activity);
        break;
      default:
        console.warn('Unknown event type:', event.type);
    }
  }

  setInitialState(data: {
    agents?: Agent[];
    tasks?: Task[];
    activities?: Activity[];
    metrics?: SystemMetrics;
  }): void {
    if (data.agents) {
      this.state.agents = new Map(data.agents.map(a => [a.id, a]));
    }
    if (data.tasks) {
      this.state.tasks = new Map(data.tasks.map(t => [t.id, t]));
    }
    if (data.activities) {
      this.state.activities = data.activities.slice(0, this.maxActivities);
    }
    if (data.metrics) {
      this.state.metrics = data.metrics;
    }
    this.notifySubscribers();
  }

  private handleAgentStatus(payload: AgentStatusPayload): void {
    const agent = this.state.agents.get(payload.agentId);
    if (agent) {
      agent.status = payload.status;
      if (payload.currentTask !== undefined) {
        agent.currentTask = payload.currentTask;
      }
      agent.lastActivity = new Date().toISOString();
      this.notifySubscribers();
    }
  }

  private handleTaskProgress(payload: TaskProgressPayload): void {
    const task = this.state.tasks.get(payload.taskId);
    if (task) {
      task.progress = payload.progress;
      task.status = payload.status;
      task.updatedAt = new Date().toISOString();
      this.notifySubscribers();
    }
  }

  private handleMetrics(metrics: SystemMetrics): void {
    this.state.metrics = metrics;
    this.notifySubscribers();
  }

  private handleActivity(activity: Activity): void {
    this.state.activities.unshift(activity);
    if (this.state.activities.length > this.maxActivities) {
      this.state.activities.pop();
    }
    this.notifySubscribers();
  }

  private notifySubscribers(): void {
    const state = this.getState();
    this.subscribers.forEach(cb => cb(state));
  }
}
