import { writable } from 'svelte/store';
import type { FileInfo } from '$types/task';

// 当前选中的文件 Store
export const currentFile = writable<FileInfo | null>(null);

// Store 操作方法
export const fileActions = {
  setFile: (file: FileInfo) => {
    currentFile.set(file);
  },

  clearFile: () => {
    currentFile.set(null);
  },
};
