import { apiService, type TaskStatusResponse } from './api';
import { taskActions } from '$stores/taskStore';
import { logActions } from '$stores/logStore';

interface PollingInstance {
  taskId: string;
  intervalId: number;
  retryCount: number;
}

class TaskPollingService {
  private pollingInstances: Map<string, PollingInstance> = new Map();
  private readonly POLL_INTERVAL = 3000; // 3秒轮询间隔
  private readonly MAX_RETRIES = 3; // 最大重试次数
  private readonly RETRY_DELAYS = [5000, 10000, 15000]; // 重试延迟（指数退避）

  /**
   * 开始轮询任务状态
   */
  startPolling(taskId: string): void {
    // 如果已经在轮询中，直接返回
    if (this.pollingInstances.has(taskId)) {
      console.log(`Task ${taskId} is already being polled`);
      return;
    }

    console.log(`Starting polling for task ${taskId}`);
    logActions.polling(`开始轮询任务: ${taskId}`, null, { taskId });

    // 创建轮询实例
    const instance: PollingInstance = {
      taskId,
      intervalId: 0,
      retryCount: 0,
    };

    // 立即执行第一次轮询
    this.pollTaskStatus(taskId);

    // 设置定时轮询
    const intervalId = window.setInterval(() => {
      this.pollTaskStatus(taskId);
    }, this.POLL_INTERVAL);

    instance.intervalId = intervalId;
    this.pollingInstances.set(taskId, instance);
  }

  /**
   * 停止轮询任务状态
   */
  stopPolling(taskId: string): void {
    const instance = this.pollingInstances.get(taskId);
    if (!instance) return;

    console.log(`Stopping polling for task ${taskId}`);
    logActions.polling(`停止轮询任务: ${taskId}`, null, { taskId });

    clearInterval(instance.intervalId);
    this.pollingInstances.delete(taskId);
  }

  /**
   * 停止所有轮询
   */
  stopAllPolling(): void {
    console.log('Stopping all polling instances');
    this.pollingInstances.forEach((_instance, taskId) => {
      this.stopPolling(taskId);
    });
  }

  /**
   * 执行任务状态轮询
   */
  private async pollTaskStatus(taskId: string): Promise<void> {
    const instance = this.pollingInstances.get(taskId);
    if (!instance) {
      console.warn(`Polling instance not found for task ${taskId}`);
      return;
    }

    try {
      // 调用 API 获取任务状态
      const status: TaskStatusResponse = await apiService.getTaskStatus(taskId);

      console.log(`Task ${taskId} status update:`, {
        status: status.status,
        progress: status.progress,
        current_step: status.current_step,
        message: status.message,
        file_size: status.file_size,
        dwg_filename: status.dwg_filename,
      });

      logActions.polling(`任务状态: ${status.status} (${status.progress}%)`, {
        status: status.status,
        progress: status.progress,
        current_step: status.current_step,
        message: status.message,
        file_size: status.file_size,
        dwg_filename: status.dwg_filename,
      }, { taskId });

      // 重置重试计数
      instance.retryCount = 0;

      // 确定要显示的消息(优先级: message > current_step > 状态)
      const displayMessage = status.message || status.current_step || `${status.status}`;

      // 更新任务状态到 Store (包含所有可用字段)
      taskActions.updateTask(taskId, {
        status: status.status,
        progress: status.progress,
        message: displayMessage,
        updatedAt: Date.now(),
        // 更新文件信息(如果API返回了这些字段)
        ...(status.file_size && { fileSize: status.file_size }),
        ...(status.dwg_filename && { fileName: status.dwg_filename }),
        ...(status.created_at && { uploadTime: status.created_at }),
      });

      console.log(`Task ${taskId} store updated:`, {
        status: status.status,
        progress: status.progress,
        message: displayMessage,
        fileSize: status.file_size,
        fileName: status.dwg_filename,
        updatedAt: Date.now(),
      });

      // 检查是否需要停止轮询
      if (status.status === 'completed' || status.status === 'failed') {
        console.log(`Task ${taskId} reached terminal state: ${status.status}`);
        logActions.info(`任务到达最终状态: ${status.status}`, null, { taskId });
        this.stopPolling(taskId);

        // 如果任务完成，触发 PDF 生成
        if (status.status === 'completed') {
          this.handleTaskCompleted(taskId);
        }
      }
    } catch (error) {
      console.error(`Failed to poll task ${taskId}:`, error);
      this.handlePollingError(taskId, error);
    }
  }

  /**
   * 处理轮询错误（自动重试机制）
   */
  private handlePollingError(taskId: string, _error: unknown): void {
    const instance = this.pollingInstances.get(taskId);
    if (!instance) return;

    instance.retryCount++;

    if (instance.retryCount <= this.MAX_RETRIES) {
      const retryDelay = this.RETRY_DELAYS[instance.retryCount - 1];
      console.log(
        `Retry ${instance.retryCount}/${this.MAX_RETRIES} for task ${taskId} in ${retryDelay}ms`
      );

      logActions.error(
        `轮询失败，将在 ${retryDelay}ms 后重试 (${instance.retryCount}/${this.MAX_RETRIES})`,
        _error,
        { taskId }
      );

      // 更新任务状态为"连接中"
      taskActions.updateTask(taskId, {
        status: 'queued',
        message: `连接中... (重试 ${instance.retryCount}/${this.MAX_RETRIES})`,
      });

      // 停止当前的定时器
      clearInterval(instance.intervalId);

      // 延迟后重新启动轮询（创建新的interval）
      setTimeout(() => {
        // 检查实例是否仍然存在（防止在延迟期间被手动停止）
        if (!this.pollingInstances.has(taskId)) {
          console.log(`Task ${taskId} was stopped during retry delay, skipping restart`);
          return;
        }

        console.log(`Restarting polling for task ${taskId} after retry delay`);

        // 重新创建定时器
        const newIntervalId = window.setInterval(() => {
          this.pollTaskStatus(taskId);
        }, this.POLL_INTERVAL);

        // 更新实例的 intervalId
        const currentInstance = this.pollingInstances.get(taskId);
        if (currentInstance) {
          currentInstance.intervalId = newIntervalId;
        }
      }, retryDelay);
    } else {
      // 重试次数耗尽，标记为连接失败
      console.error(`Max retries reached for task ${taskId}`);

      logActions.error(`轮询重试次数已用尽，任务失败`, _error, { taskId });

      taskActions.updateTask(taskId, {
        status: 'failed',
        message: '无法连接到服务器，请检查网络连接',
      });
      this.stopPolling(taskId);
    }
  }

  /**
   * 处理任务完成（自动调用 PDF 生成）
   */
  private async handleTaskCompleted(taskId: string): Promise<void> {
    try {
      console.log(`Generating PDF for completed task ${taskId}`);
      logActions.info(`开始生成PDF: ${taskId}`, null, { taskId });

      const pdfResponse = await apiService.generatePdf(taskId);

      // 更新任务信息，添加 PDF 下载链接
      taskActions.updateTask(taskId, {
        pdfId: pdfResponse.pdf_id,
        pdfFileName: pdfResponse.file_name,
        pdfDownloadUrl: pdfResponse.download_url,
        pdfFileSize: pdfResponse.file_size,
        message: 'PDF 生成成功',
      });

      console.log(`PDF generated successfully for task ${taskId}:`, pdfResponse);
      logActions.info(`PDF生成成功`, pdfResponse, { taskId });
    } catch (error) {
      console.error(`Failed to generate PDF for task ${taskId}:`, error);

      logActions.error(`PDF生成失败`, error, { taskId });

      taskActions.updateTask(taskId, {
        message: `PDF 生成失败: ${error}`,
      });
    }
  }

  /**
   * 获取当前轮询的任务数量
   */
  getPollingCount(): number {
    return this.pollingInstances.size;
  }

  /**
   * 检查任务是否正在轮询
   */
  isTaskPolling(taskId: string): boolean {
    return this.pollingInstances.has(taskId);
  }
}

// 导出单例
export const taskPollingService = new TaskPollingService();

// 确保应用关闭时停止所有轮询
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    taskPollingService.stopAllPolling();
  });
}
