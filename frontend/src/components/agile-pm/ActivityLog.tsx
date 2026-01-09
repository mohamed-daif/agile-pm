import { Activity } from '@/types';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

interface ActivityLogProps {
  activities: Activity[];
  maxItems?: number;
}

const severityConfig = {
  info: { icon: Info, color: 'text-blue-500' },
  warning: { icon: AlertTriangle, color: 'text-warning' },
  error: { icon: AlertCircle, color: 'text-error' },
};

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export function ActivityLog({ activities, maxItems = 50 }: ActivityLogProps) {
  const displayActivities = activities.slice(0, maxItems);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Activity Log</h2>
        <span className="text-sm text-gray-500">{activities.length} events</span>
      </div>

      <div className="space-y-1 max-h-96 overflow-y-auto">
        {displayActivities.map(activity => {
          const config = severityConfig[activity.severity];
          const Icon = config.icon;

          return (
            <div
              key={activity.id}
              className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded"
            >
              <Icon className={cn('w-4 h-4 mt-0.5 flex-shrink-0', config.color)} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{activity.message}</p>
                <p className="text-xs text-gray-500">{formatTime(activity.timestamp)}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
