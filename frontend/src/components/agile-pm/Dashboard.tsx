import { useState, useEffect } from 'react';
import { Agent, Task, Activity, SystemMetrics, Crew } from '@/types';
import { AgentList } from './AgentList';
import { TaskProgress } from './TaskProgress';
import { ActivityLog } from './ActivityLog';
import { SystemHealth } from './SystemHealth';
import { CrewStatus } from './CrewStatus';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Wifi, WifiOff } from 'lucide-react';

// Mock data for development
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Technical PM Agent',
    role: 'strategic',
    status: 'active',
    currentTask: 'Sprint 05 Planning',
    lastActivity: new Date().toISOString(),
    metrics: { tasksCompleted: 45, successRate: 98, avgResponseTime: 2.3 },
  },
  {
    id: '2',
    name: 'Backend Engineer Agent',
    role: 'executor',
    status: 'active',
    currentTask: 'API Implementation',
    lastActivity: new Date().toISOString(),
    metrics: { tasksCompleted: 120, successRate: 95, avgResponseTime: 3.1 },
  },
  {
    id: '3',
    name: 'QA Executor Agent',
    role: 'reviewer',
    status: 'idle',
    lastActivity: new Date().toISOString(),
    metrics: { tasksCompleted: 80, successRate: 99, avgResponseTime: 1.8 },
  },
];

const mockTasks: Task[] = [
  { id: '1', title: 'S05-001: React Dashboard', status: 'in_progress', priority: 'P0', progress: 60, estimatedPoints: 8, createdAt: '', updatedAt: '', assignee: 'Frontend Agent' },
  { id: '2', title: 'S05-002: WebSocket Integration', status: 'pending', priority: 'P0', progress: 0, estimatedPoints: 6, createdAt: '', updatedAt: '' },
  { id: '3', title: 'S05-003: E2E Testing', status: 'pending', priority: 'P1', progress: 0, estimatedPoints: 6, createdAt: '', updatedAt: '' },
];

const mockMetrics: SystemMetrics = {
  cpu: 45.2,
  memory: 62.8,
  activeAgents: 2,
  totalAgents: 3,
  tasksInProgress: 1,
  tasksCompleted: 245,
  tasksFailed: 3,
  uptime: 86400,
  llmCalls: 523,
  llmLatency: 850,
};

const mockActivities: Activity[] = [
  { id: '1', type: 'task_started', message: 'Backend Agent started API Implementation', timestamp: new Date().toISOString(), severity: 'info' },
  { id: '2', type: 'task_completed', message: 'QA Agent completed test suite', timestamp: new Date(Date.now() - 60000).toISOString(), severity: 'info' },
];

export function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [activities, setActivities] = useState<Activity[]>(mockActivities);
  const [metrics, setMetrics] = useState<SystemMetrics>(mockMetrics);
  
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8001/ws/dashboard');

  useEffect(() => {
    if (lastMessage) {
      // Handle WebSocket messages
      switch (lastMessage.type) {
        case 'metrics':
          setMetrics(lastMessage.payload as SystemMetrics);
          break;
        case 'activity':
          setActivities(prev => [lastMessage.payload as Activity, ...prev].slice(0, 100));
          break;
        // Add more handlers as needed
      }
    }
  }, [lastMessage]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Agile-PM Dashboard</h1>
            <p className="text-sm text-gray-500">AI Agent Monitoring & Control</p>
          </div>
          <div className="flex items-center gap-2">
            {isConnected ? (
              <div className="flex items-center gap-1 text-success">
                <Wifi className="w-4 h-4" />
                <span className="text-sm">Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-error">
                <WifiOff className="w-4 h-4" />
                <span className="text-sm">Disconnected</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* System Health */}
        <section>
          <SystemHealth metrics={metrics} />
        </section>

        {/* Agents and Tasks */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section>
            <AgentList agents={agents} />
          </section>
          <section>
            <TaskProgress tasks={tasks} />
          </section>
        </div>

        {/* Activity Log */}
        <section>
          <ActivityLog activities={activities} />
        </section>
      </main>
    </div>
  );
}
