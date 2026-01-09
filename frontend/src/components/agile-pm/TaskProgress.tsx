import { Task, TaskStatus, TaskPriority } from '@/types';
import { cn } from '@/lib/utils';

interface TaskProgressProps {
  tasks: Task[];
}

const statusColors: Record<TaskStatus, string> = {
  pending: 'bg-gray-200',
  in_progress: 'bg-blue-500',
  completed: 'bg-success',
  failed: 'bg-error',
  blocked: 'bg-warning',
};

const priorityColors: Record<TaskPriority, string> = {
  P0: 'text-red-600 bg-red-50',
  P1: 'text-orange-600 bg-orange-50',
  P2: 'text-yellow-600 bg-yellow-50',
  P3: 'text-gray-600 bg-gray-50',
};

export function TaskProgress({ tasks }: TaskProgressProps) {
  const completed = tasks.filter(t => t.status === 'completed').length;
  const total = tasks.length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Task Progress</h2>
        <span className="text-sm text-gray-500">{completed}/{total} completed ({percentage}%)</span>
      </div>

      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-success transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {tasks.map(task => (
          <div
            key={task.id}
            className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200"
          >
            <div className={cn('w-2 h-2 rounded-full', statusColors[task.status])} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{task.title}</p>
              {task.assignee && (
                <p className="text-xs text-gray-500">Assigned to: {task.assignee}</p>
              )}
            </div>
            <span className={cn('text-xs px-2 py-0.5 rounded', priorityColors[task.priority])}>
              {task.priority}
            </span>
            <div className="w-16 text-right">
              <span className="text-sm font-medium">{task.progress}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
