<script lang="ts">
  import type { Task } from '$types/task';
  import ProgressBar from '../common/ProgressBar.svelte';
  import StatusBadge from '../common/StatusBadge.svelte';

  export let task: Task;
</script>

<div class="task-card">
  <div class="task-header">
    <span class="task-id">#{task.taskId}</span>
    <StatusBadge status={task.status} />
  </div>

  <div class="task-body">
    <p class="file-name">{task.fileName}</p>
    <p class="upload-time">{new Date(task.uploadTime).toLocaleString('zh-CN')}</p>
  </div>

  {#if task.status === 'processing'}
    <ProgressBar progress={task.progress} />
  {/if}

  {#if task.errorMessage}
    <p class="error-message">{task.errorMessage}</p>
  {/if}
</div>

<style>
  .task-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1rem;
    transition: all 0.2s ease;
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

  .task-id {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .task-body {
    margin-bottom: 0.75rem;
  }

  .file-name {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
  }

  .upload-time {
    font-size: 0.875rem;
    color: var(--text-secondary);
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
