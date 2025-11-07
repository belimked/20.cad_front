import { writable } from 'svelte/store';

// 应用配置 Store
export interface AppConfig {
  apiBaseUrl: string;
  pollingInterval: number; // 毫秒
  maxHistoryRecords: number;
  enableNotifications: boolean;
}

const defaultConfig: AppConfig = {
  apiBaseUrl: 'https://api.example.com',
  pollingInterval: 3000,
  maxHistoryRecords: 1000,
  enableNotifications: true,
};

export const appConfig = writable<AppConfig>(defaultConfig);

// 配置操作方法
export const configActions = {
  updateConfig: (updates: Partial<AppConfig>) => {
    appConfig.update((config) => ({ ...config, ...updates }));
  },

  resetConfig: () => {
    appConfig.set(defaultConfig);
  },
};
