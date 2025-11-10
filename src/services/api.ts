import { invoke } from '@tauri-apps/api/tauri';
import { appConfig } from '$stores/configStore';
import { get } from 'svelte/store';

// ========== 请求类型定义 ==========

export interface PrintTaskRequest {
  dwg_url: string; // DWG 文件下载地址（必填）
  config_name?: string; // 配置名称（可选，默认为"default"）
  callback_url?: string; // 完成后回调地址（可选）
  use_bplot?: boolean; // 是否使用bplot工作流（可选，默认为false）
}

// ========== 响应类型定义 ==========

// 标准 API 响应包装器
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 任务创建响应数据
export interface TaskCreateData {
  task_id: string;
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

// 上传响应(兼容旧版本,实际返回 ApiResponse<TaskCreateData>)
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

export interface TaskDetailResponse {
  task_id: string;
  dwg_url: string;
  dwg_filename?: string;
  local_path?: string;
  file_size?: number;
  config_name: string;
  use_bplot: boolean;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step?: string;
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  steps: TaskStep[];
}

export interface TaskStep {
  step_order: number;
  step_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  message?: string;
  error_message?: string;
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

  /**
   * 提交 DWG 文件打印任务
   * POST /api/v1/tasks/print
   */
  async uploadFile(filePath: string, useBplot = false): Promise<UploadResponse> {
    const apiUrl = this.getApiUrl();

    // 构建请求参数
    const requestData: PrintTaskRequest = {
      dwg_url: filePath, // 在实际使用中，这应该是一个可访问的 URL
      config_name: useBplot ? 'bplot' : 'default',
      use_bplot: useBplot,
    };

    const response = await invoke<UploadResponse>('upload_file', {
      apiUrl,
      requestData: JSON.stringify(requestData),
    });

    return response;
  }

  /**
   * 查询任务详情
   * GET /api/v1/tasks/{task_id}
   */
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const apiUrl = this.getApiUrl();
    const response = await invoke<TaskDetailResponse>('get_task_detail', {
      taskId,
      apiUrl,
    });

    // 将详细响应转换为状态响应
    return {
      task_id: response.task_id,
      status: response.status,
      progress: response.progress,
      message: response.error_message || this.getStatusMessage(response),
    };
  }

  /**
   * 查询任务详情（完整信息）
   * GET /api/v1/tasks/{task_id}
   */
  async getTaskDetail(taskId: string): Promise<TaskDetailResponse> {
    const apiUrl = this.getApiUrl();
    const response = await invoke<TaskDetailResponse>('get_task_detail', {
      taskId,
      apiUrl,
    });
    return response;
  }

  /**
   * 生成 PDF（保留接口，实际 PDF 由后端自动生成）
   */
  async generatePdf(taskId: string): Promise<GeneratePdfResponse> {
    // 在新的 API 中，PDF 由后端自动生成
    // 这里只是查询任务详情，从中提取 PDF 信息
    const detail = await this.getTaskDetail(taskId);

    if (detail.status !== 'completed') {
      throw new Error('任务尚未完成');
    }

    // 从任务步骤中查找 PDF 相关信息
    // 这里需要根据实际 API 返回的数据结构调整
    return {
      pdf_id: taskId,
      file_name: `output_${taskId}.pdf`,
      download_url: `${this.getApiUrl()}/api/v1/tasks/${taskId}/download`,
      file_size: 0, // 需要从实际响应中获取
    };
  }

  /**
   * 下载 PDF
   */
  async downloadPdf(pdfUrl: string, savePath: string): Promise<string> {
    const response = await invoke<string>('download_pdf', {
      pdfUrl,
      savePath,
    });
    return response;
  }

  /**
   * 根据任务详情生成状态消息
   */
  private getStatusMessage(detail: TaskDetailResponse): string {
    if (detail.status === 'completed') {
      return 'PDF 生成成功';
    }

    if (detail.status === 'failed') {
      return detail.error_message || '任务失败';
    }

    // 查找当前正在执行的步骤
    const currentStep = detail.steps.find((s) => s.status === 'running');
    if (currentStep) {
      return `正在执行: ${currentStep.step_name}`;
    }

    const completedSteps = detail.steps.filter((s) => s.status === 'completed').length;
    return `已完成 ${completedSteps}/${detail.steps.length} 步`;
  }
}

export const apiService = new ApiService();
