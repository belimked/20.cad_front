export interface Task {
  taskId: string;
  fileName: string;
  fileSize: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  uploadTime: string;
  updatedAt?: number; // 最后更新时间（时间戳）
  completionTime?: string;
  message?: string; // 状态消息
  errorMessage?: string;
  // PDF 相关字段
  pdfId?: string;
  pdfFileName?: string;
  pdfDownloadUrl?: string;
  pdfFileSize?: number;
  pdfUrl?: string; // 保留向后兼容
}

export interface FileInfo {
  path: string;
  name: string;
  size: number;
}
