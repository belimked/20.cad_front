<script lang="ts">
  import { tasks } from '$stores/taskStore';
  import TaskCard from './TaskCard.svelte';
</script>

<div class="task-monitor">
  <h2>任务监控</h2>

  {#if $tasks.length === 0}
    <div class="empty-state">
      <p>暂无任务</p>
    </div>
  {:else}
    <div class="task-list">
      {#each $tasks as task (task.taskId)}
        <TaskCard {task} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .task-monitor {
    width: 100%;
  }

  h2 {
    margin-bottom: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .empty-state {
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
  }

  .task-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
</style>
