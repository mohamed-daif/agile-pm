import { Crew, CrewStatus as CrewStatusType } from '@/types';
import { cn } from '@/lib/utils';
import { Users, Play, Pause, CheckCircle, Clock } from 'lucide-react';

interface CrewStatusProps {
  crews: Crew[];
}

const statusConfig: Record<CrewStatusType, { icon: typeof Users; color: string; label: string }> = {
  idle: { icon: Clock, color: 'text-gray-400', label: 'Idle' },
  planning: { icon: Users, color: 'text-purple-500', label: 'Planning' },
  executing: { icon: Play, color: 'text-blue-500', label: 'Executing' },
  reviewing: { icon: Pause, color: 'text-orange-500', label: 'Reviewing' },
  completed: { icon: CheckCircle, color: 'text-success', label: 'Completed' },
};

export function CrewStatus({ crews }: CrewStatusProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Crew Status</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {crews.map(crew => {
          const config = statusConfig[crew.status];
          const Icon = config.icon;

          return (
            <div
              key={crew.id}
              className="p-4 bg-white rounded-lg border border-gray-200"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">{crew.name}</h3>
                <div className={cn('flex items-center gap-1', config.color)}>
                  <Icon className="w-4 h-4" />
                  <span className="text-sm">{config.label}</span>
                </div>
              </div>

              {crew.currentSprint && (
                <p className="text-sm text-gray-600 mb-2">
                  Sprint: {crew.currentSprint}
                </p>
              )}

              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Users className="w-4 h-4" />
                <span>{crew.agents.length} agents</span>
              </div>

              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span>
                  <span>{crew.progress}%</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 transition-all duration-500"
                    style={{ width: `${crew.progress}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
