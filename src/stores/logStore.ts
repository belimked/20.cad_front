import { writable } from 'svelte/store';

export type LogLevel = 'request' | 'response' | 'error' | 'info' | 'polling';

export interface LogEntry {
  id: string;
  timestamp: number;
  level: LogLevel;
  message: string;
  data?: unknown;
  metadata?: {
    taskId?: string;
    endpoint?: string;
    method?: string;
    duration?: number;
  };
}

interface LogStore {
  entries: LogEntry[];
  maxEntries: number;
}

const MAX_LOG_ENTRIES = 500;

function createLogStore() {
  const { subscribe, update } = writable<LogStore>({
    entries: [],
    maxEntries: MAX_LOG_ENTRIES,
  });

  return {
    subscribe,
    /**
     * 添加日志条目
     */
    addLog: (
      level: LogLevel,
      message: string,
      data?: unknown,
      metadata?: LogEntry['metadata']
    ) => {
      update((store) => {
        const entry: LogEntry = {
          id: `${Date.now()}_${Math.random().toString(36).substring(7)}`,
          timestamp: Date.now(),
          level,
          message,
          data,
          metadata,
        };

        // 添加新日志并限制最大条目数
        const newEntries = [entry, ...store.entries].slice(0, store.maxEntries);

        return {
          ...store,
          entries: newEntries,
        };
      });
    },

    /**
     * 清除所有日志
     */
    clear: () => {
      update((store) => ({
        ...store,
        entries: [],
      }));
    },

    /**
     * 删除指定日志
     */
    removeLog: (id: string) => {
      update((store) => ({
        ...store,
        entries: store.entries.filter((entry) => entry.id !== id),
      }));
    },
  };
}

export const logStore = createLogStore();

// 便捷方法
export const logActions = {
  request: (message: string, data?: unknown, metadata?: LogEntry['metadata']) => {
    logStore.addLog('request', message, data, metadata);
  },
  response: (message: string, data?: unknown, metadata?: LogEntry['metadata']) => {
    logStore.addLog('response', message, data, metadata);
  },
  error: (message: string, data?: unknown, metadata?: LogEntry['metadata']) => {
    logStore.addLog('error', message, data, metadata);
  },
  info: (message: string, data?: unknown, metadata?: LogEntry['metadata']) => {
    logStore.addLog('info', message, data, metadata);
  },
  polling: (message: string, data?: unknown, metadata?: LogEntry['metadata']) => {
    logStore.addLog('polling', message, data, metadata);
  },
  clear: () => {
    logStore.clear();
  },
};
