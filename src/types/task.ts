export interface Task {
  taskId: string;
  fileName: string;
  fileSize: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  uploadTime: string;
  completionTime?: string;
  errorMessage?: string;
  pdfUrl?: string;
}

export interface FileInfo {
  path: string;
  name: string;
  size: number;
}
