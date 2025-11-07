<script lang="ts">
  export let status: 'queued' | 'processing' | 'completed' | 'failed';

  const statusConfig = {
    queued: { label: '排队中', color: 'var(--text-tertiary)' },
    processing: { label: '处理中', color: 'var(--primary-color)' },
    completed: { label: '已完成', color: 'var(--success-color)' },
    failed: { label: '失败', color: 'var(--error-color)' },
  };

  $: config = statusConfig[status];
</script>

<span class="status-badge" style="background: {config.color}">
  {config.label}
</span>

<style>
  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
  }
</style>
