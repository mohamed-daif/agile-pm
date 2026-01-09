import { Agent } from '@/types';
import { AgentCard } from './AgentCard';

interface AgentListProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
}

export function AgentList({ agents, onAgentClick }: AgentListProps) {
  const activeAgents = agents.filter(a => a.status === 'active');
  const idleAgents = agents.filter(a => a.status === 'idle');
  const errorAgents = agents.filter(a => a.status === 'error');

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Agents</h2>
        <div className="flex gap-2 text-sm">
          <span className="text-success">{activeAgents.length} active</span>
          <span className="text-gray-400">•</span>
          <span className="text-gray-500">{idleAgents.length} idle</span>
          {errorAgents.length > 0 && (
            <>
              <span className="text-gray-400">•</span>
              <span className="text-error">{errorAgents.length} error</span>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map(agent => (
          <AgentCard key={agent.id} agent={agent} onClick={onAgentClick} />
        ))}
      </div>
    </div>
  );
}
