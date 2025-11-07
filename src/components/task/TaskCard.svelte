<script lang="ts">
  import type { Task } from '$types/task';
  import ProgressBar from '../common/ProgressBar.svelte';
  import StatusBadge from '../common/StatusBadge.svelte';
  import { formatFileSize } from '$utils/formatters';

  export let task: Task;

  $: uploadDate = new Date(task.uploadTime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });

  $: hasMessage = task.message && task.message.length > 0;
  $: hasPdf = task.pdfDownloadUrl && task.pdfDownloadUrl.length > 0;
</script>

<div class="task-card" class:completed={task.status === 'completed'}>
  <div class="task-header">
    <div class="task-info">
      <span class="task-id">#{task.taskId.substring(0, 8)}</span>
      <span class="file-size">{formatFileSize(task.fileSize)}</span>
    </div>
    <StatusBadge status={task.status} />
  </div>

  <div class="task-body">
    <p class="file-name">{task.fileName}</p>
    <p class="upload-time">📤 {uploadDate}</p>

    {#if hasMessage}
      <p class="status-message">{task.message}</p>
    {/if}
  </div>

  {#if task.status === 'processing' || task.status === 'queued'}
    <ProgressBar progress={task.progress} />
  {/if}

  {#if task.status === 'completed' && hasPdf}
    <div class="pdf-section">
      <div class="pdf-info">
        <span class="pdf-icon">📄</span>
        <div class="pdf-details">
          <p class="pdf-name">{task.pdfFileName || 'output.pdf'}</p>
          {#if task.pdfFileSize}
            <p class="pdf-size">{formatFileSize(task.pdfFileSize)}</p>
          {/if}
        </div>
      </div>
      <a href={task.pdfDownloadUrl} class="download-btn" download>下载 PDF</a>
    </div>
  {/if}

  {#if task.errorMessage || task.status === 'failed'}
    <p class="error-message">{task.errorMessage || task.message || '处理失败'}</p>
  {/if}
</div>

<style>
  .task-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1rem;
    transition: all 0.2s ease;
    animation: fadeIn 0.3s ease-in;
  }

  .task-card.completed {
    border-color: var(--success-color);
    background: var(--success-light);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .task-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-sm);
  }

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .task-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .task-id {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
  }

  .file-size {
    font-size: 0.75rem;
    color: var(--text-secondary);
    padding: 0.125rem 0.5rem;
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
  }

  .task-body {
    margin-bottom: 0.75rem;
  }

  .file-name {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
    word-break: break-all;
  }

  .upload-time {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
  }

  .status-message {
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-style: italic;
    margin-top: 0.5rem;
  }

  .pdf-section {
    margin-top: 1rem;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pdf-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .pdf-icon {
    font-size: 1.5rem;
  }

  .pdf-details {
    display: flex;
    flex-direction: column;
  }

  .pdf-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .pdf-size {
    font-size: 0.75rem;
    color: var(--text-secondary);
  }

  .download-btn {
    padding: 0.5rem 1rem;
    background: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .download-btn:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .error-message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    background: #fee;
    color: var(--error-color);
    font-size: 0.875rem;
    border-radius: var(--radius-sm);
  }
</style>
