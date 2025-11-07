import { writable, derived } from 'svelte/store';
import type { Task } from '$types/task';

// 任务列表 Store
export const tasks = writable<Task[]>([]);

// 派生 Store - 当前处理中的任务
export const activeTasks = derived(tasks, ($tasks) =>
  $tasks.filter((t) => t.status === 'processing' || t.status === 'queued')
);

// 派生 Store - 已完成的任务
export const completedTasks = derived(tasks, ($tasks) =>
  $tasks.filter((t) => t.status === 'completed')
);

// Store 操作方法
export const taskActions = {
  addTask: (task: Task) => {
    tasks.update((list) => [...list, task]);
  },

  updateTask: (taskId: string, updates: Partial<Task>) => {
    tasks.update((list) => list.map((t) => (t.taskId === taskId ? { ...t, ...updates } : t)));
  },

  removeTask: (taskId: string) => {
    tasks.update((list) => list.filter((t) => t.taskId !== taskId));
  },

  clearCompleted: () => {
    tasks.update((list) => list.filter((t) => t.status !== 'completed' && t.status !== 'failed'));
  },

  clearAll: () => {
    tasks.set([]);
  },
};
