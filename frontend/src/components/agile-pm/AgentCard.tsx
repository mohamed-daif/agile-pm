import { Agent, AgentStatus } from '@/types';
import { Activity, AlertCircle, CheckCircle, Clock, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AgentCardProps {
  agent: Agent;
  onClick?: (agent: Agent) => void;
}

const statusConfig: Record<AgentStatus, { icon: typeof Activity; color: string; label: string }> = {
  active: { icon: Activity, color: 'text-success', label: 'Active' },
  idle: { icon: Clock, color: 'text-gray-400', label: 'Idle' },
  error: { icon: AlertCircle, color: 'text-error', label: 'Error' },
  offline: { icon: Loader2, color: 'text-gray-300', label: 'Offline' },
};

const roleColors: Record<string, string> = {
  strategic: 'bg-purple-100 text-purple-800',
  executor: 'bg-blue-100 text-blue-800',
  reviewer: 'bg-green-100 text-green-800',
  specialist: 'bg-orange-100 text-orange-800',
};

export function AgentCard({ agent, onClick }: AgentCardProps) {
  const status = statusConfig[agent.status];
  const StatusIcon = status.icon;

  return (
    <div
      onClick={() => onClick?.(agent)}
      className={cn(
        'p-4 bg-white rounded-lg border border-gray-200 shadow-sm',
        'hover:shadow-md transition-shadow cursor-pointer',
        agent.status === 'error' && 'border-error/50'
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
          <span className={cn('text-xs px-2 py-0.5 rounded-full', roleColors[agent.role])}>
            {agent.role}
          </span>
        </div>
        <div className={cn('flex items-center gap-1', status.color)}>
          <StatusIcon className="w-4 h-4" />
          <span className="text-xs">{status.label}</span>
        </div>
      </div>

      {agent.currentTask && (
        <p className="mt-2 text-sm text-gray-600 truncate">
          Working on: {agent.currentTask}
        </p>
      )}

      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div>
          <div className="font-semibold text-gray-900">{agent.metrics.tasksCompleted}</div>
          <div className="text-gray-500">Completed</div>
        </div>
        <div>
          <div className="font-semibold text-gray-900">{agent.metrics.successRate}%</div>
          <div className="text-gray-500">Success</div>
        </div>
        <div>
          <div className="font-semibold text-gray-900">{agent.metrics.avgResponseTime}s</div>
          <div className="text-gray-500">Avg Time</div>
        </div>
      </div>
    </div>
  );
}
