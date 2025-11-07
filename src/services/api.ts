import { invoke } from '@tauri-apps/api/tauri';
import { appConfig } from '$stores/configStore';
import { get } from 'svelte/store';

export interface UploadResponse {
  task_id: string;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
}

export interface GeneratePdfResponse {
  pdf_id: string;
  file_name: string;
  download_url: string;
  file_size?: number;
}

class ApiService {
  private getApiUrl(): string {
    const config = get(appConfig);
    return config.apiBaseUrl;
  }

  async uploadFile(filePath: string): Promise<UploadResponse> {
    const apiUrl = this.getApiUrl();
    const response = await invoke<UploadResponse>('upload_file', {
      filePath,
      apiUrl,
    });
    return response;
  }

  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const apiUrl = this.getApiUrl();
    const response = await invoke<TaskStatusResponse>('poll_task_status', {
      taskId,
      apiUrl,
    });
    return response;
  }

  async generatePdf(taskId: string): Promise<GeneratePdfResponse> {
    const apiUrl = this.getApiUrl();
    const response = await invoke<GeneratePdfResponse>('generate_pdf', {
      taskId,
      apiUrl,
    });
    return response;
  }

  async downloadPdf(pdfUrl: string, savePath: string): Promise<string> {
    const response = await invoke<string>('download_pdf', {
      pdfUrl,
      savePath,
    });
    return response;
  }
}

export const apiService = new ApiService();
