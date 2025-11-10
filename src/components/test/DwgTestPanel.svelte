<script lang="ts">
  import { DWG_FILE_OPTIONS, type DwgFileOption } from '$config/dwgFiles';
  import { apiService } from '$services/api';
  import { taskActions } from '$stores/taskStore';
  import type { Task } from '$types/task';

  let selectedFileId = DWG_FILE_OPTIONS[0]?.id || '';
  let useBplot = false;
  let isSubmitting = false;
  let lastError = '';
  let lastSuccess = '';

  $: selectedFile = DWG_FILE_OPTIONS.find((f: DwgFileOption) => f.id === selectedFileId);

  async function submitTask() {
    if (!selectedFile) {
      lastError = '请选择一个文件';
      return;
    }

    isSubmitting = true;
    lastError = '';
    lastSuccess = '';

    try {
      console.log('提交打印任务:', {
        dwg_url: selectedFile.url,
        use_bplot: useBplot,
      });

      const response = await apiService.uploadFile(selectedFile.url, useBplot);

      console.log('任务创建成功:', response);

      // 创建任务对象并添加到 Store
      const task: Task = {
        taskId: response.task_id,
        fileName: selectedFile.name,
        fileSize: 0, // URL 方式无法获取文件大小
        status: 'queued',
        progress: 0,
        uploadTime: String(Date.now()),
        message: response.message,
      };

      taskActions.addTask(task);

      lastSuccess = `任务已创建: ${response.task_id.substring(0, 8)}...`;

      // 2秒后清除成功消息
      setTimeout(() => {
        lastSuccess = '';
      }, 2000);
    } catch (error) {
      console.error('任务提交失败:', error);
      lastError = error instanceof Error ? error.message : String(error);
    } finally {
      isSubmitting = false;
    }
  }

  function clearMessages() {
    lastError = '';
    lastSuccess = '';
  }
</script>

<div class="test-panel">
  <h2>🧪 DWG 打印任务测试</h2>

  <div class="form-group">
    <label for="file-select">选择 DWG 文件:</label>
    <select id="file-select" bind:value={selectedFileId} on:change={clearMessages}>
      {#each DWG_FILE_OPTIONS as file}
        <option value={file.id}>
          {file.displayName}
          {#if file.description}
            - {file.description}
          {/if}
        </option>
      {/each}
    </select>
  </div>

  {#if selectedFile}
    <div class="file-info">
      <p class="info-label">文件名:</p>
      <p class="info-value">{selectedFile.name}</p>

      <p class="info-label">URL:</p>
      <p class="info-value url">{selectedFile.url}</p>
    </div>
  {/if}

  <div class="form-group">
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={useBplot} on:change={clearMessages} />
      <span>使用 bplot 工作流</span>
    </label>
  </div>

  <button class="submit-btn" on:click={submitTask} disabled={isSubmitting || !selectedFile}>
    {#if isSubmitting}
      ⏳ 提交中...
    {:else}
      🚀 提交打印任务
    {/if}
  </button>

  {#if lastSuccess}
    <div class="message success">
      ✅ {lastSuccess}
    </div>
  {/if}

  {#if lastError}
    <div class="message error">
      ❌ {lastError}
    </div>
  {/if}

  <div class="info-box">
    <h3>📋 API 配置</h3>
    <p><strong>服务器:</strong> http://10.3.19.63:8000</p>
    <p><strong>接口:</strong> POST /api/v1/tasks/print</p>
    <p><strong>文件服务器:</strong> http://10.3.19.199/cad/</p>
  </div>
</div>

<style>
  .test-panel {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
  }

  h2 {
    margin-top: 0;
    color: var(--text-primary);
    font-size: 1.5rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  select {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .file-info {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 1rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    margin-bottom: 1.5rem;
  }

  .info-label {
    font-weight: 600;
    color: var(--text-secondary);
    margin: 0;
  }

  .info-value {
    color: var(--text-primary);
    margin: 0;
    word-break: break-all;
  }

  .info-value.url {
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-weight: normal;
  }

  .checkbox-label input {
    margin-right: 0.5rem;
    width: 1.25rem;
    height: 1.25rem;
    cursor: pointer;
  }

  .submit-btn {
    width: 100%;
    padding: 0.875rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: white;
    background: var(--primary-color);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .submit-btn:hover:not(:disabled) {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }

  .submit-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .message {
    margin-top: 1rem;
    padding: 0.875rem;
    border-radius: var(--radius-md);
    font-weight: 500;
  }

  .message.success {
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #34d399;
  }

  .message.error {
    background: #fee;
    color: var(--error-color);
    border: 1px solid #f87171;
  }

  .info-box {
    margin-top: 2rem;
    padding: 1rem;
    background: var(--bg-tertiary);
    border-left: 4px solid var(--primary-color);
    border-radius: var(--radius-sm);
  }

  .info-box h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
    font-size: 1rem;
    color: var(--text-primary);
  }

  .info-box p {
    margin: 0.25rem 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .info-box strong {
    color: var(--text-primary);
  }
</style>
