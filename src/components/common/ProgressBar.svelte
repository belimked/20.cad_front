<script lang="ts">
  export let progress: number; // 0-100

  $: clampedProgress = Math.min(100, Math.max(0, progress));
</script>

<div class="progress-bar">
  <div class="progress-track">
    <div class="progress-fill" style="width: {clampedProgress}%"></div>
  </div>
  <span class="progress-text">{clampedProgress}%</span>
</div>

<style>
  .progress-bar {
    width: 100%;
  }

  .progress-track {
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 0.25rem;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
    border-radius: 9999px;
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 600;
  }
</style>
