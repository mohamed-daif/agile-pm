import { SystemMetrics } from '@/types';
import { cn } from '@/lib/utils';
import { Cpu, HardDrive, Users, Clock, Zap, Activity } from 'lucide-react';

interface SystemHealthProps {
  metrics: SystemMetrics;
}

interface GaugeProps {
  value: number;
  max: number;
  label: string;
  icon: React.ElementType;
  unit?: string;
  thresholds?: { warning: number; critical: number };
}

function Gauge({ value, max, label, icon: Icon, unit = '%', thresholds }: GaugeProps) {
  const percentage = Math.min((value / max) * 100, 100);
  const color = thresholds
    ? percentage >= thresholds.critical
      ? 'text-error'
      : percentage >= thresholds.warning
        ? 'text-warning'
        : 'text-success'
    : 'text-primary-500';

  return (
    <div className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200">
      <Icon className={cn('w-6 h-6 mb-2', color)} />
      <div className={cn('text-2xl font-bold', color)}>
        {value.toFixed(1)}{unit}
      </div>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="w-full h-1 mt-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all', 
            percentage >= (thresholds?.critical || 90) ? 'bg-error' :
            percentage >= (thresholds?.warning || 70) ? 'bg-warning' : 'bg-success'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function SystemHealth({ metrics }: SystemHealthProps) {
  const uptimeHours = Math.floor(metrics.uptime / 3600);
  const uptimeMinutes = Math.floor((metrics.uptime % 3600) / 60);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">System Health</h2>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Gauge
          value={metrics.cpu}
          max={100}
          label="CPU Usage"
          icon={Cpu}
          thresholds={{ warning: 70, critical: 90 }}
        />
        <Gauge
          value={metrics.memory}
          max={100}
          label="Memory"
          icon={HardDrive}
          thresholds={{ warning: 70, critical: 90 }}
        />
        <Gauge
          value={metrics.activeAgents}
          max={metrics.totalAgents}
          label="Active Agents"
          icon={Users}
          unit={`/${metrics.totalAgents}`}
        />
        <div className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200">
          <Clock className="w-6 h-6 mb-2 text-primary-500" />
          <div className="text-2xl font-bold text-primary-500">
            {uptimeHours}h {uptimeMinutes}m
          </div>
          <div className="text-xs text-gray-500">Uptime</div>
        </div>
        <Gauge
          value={metrics.llmCalls}
          max={1000}
          label="LLM Calls"
          icon={Zap}
          unit=""
        />
        <Gauge
          value={metrics.llmLatency}
          max={5000}
          label="LLM Latency"
          icon={Activity}
          unit="ms"
          thresholds={{ warning: 2000, critical: 4000 }}
        />
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-primary-500">{metrics.tasksInProgress}</div>
          <div className="text-xs text-gray-500">Tasks In Progress</div>
        </div>
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-success">{metrics.tasksCompleted}</div>
          <div className="text-xs text-gray-500">Tasks Completed</div>
        </div>
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-error">{metrics.tasksFailed}</div>
          <div className="text-xs text-gray-500">Tasks Failed</div>
        </div>
      </div>
    </div>
  );
}
