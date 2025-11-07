<script lang="ts">
  import { onMount } from 'svelte';
  import FileUpload from './components/upload/FileUpload.svelte';
  import TaskMonitor from './components/task/TaskMonitor.svelte';

  let appReady = false;

  onMount(async () => {
    console.log('CAD PDF Converter 应用启动');
    appReady = true;
  });
</script>

<main class="app-container">
  {#if appReady}
    <header class="app-header">
      <h1>CAD 文件处理工具</h1>
      <p class="subtitle">轻松将 DWG 文件转换为 PDF</p>
    </header>

    <div class="app-content">
      <!-- 文件上传模块 -->
      <section class="upload-section">
        <FileUpload />
      </section>

      <!-- 任务监控模块 -->
      <section class="monitor-section">
        <TaskMonitor />
      </section>
    </div>
  {:else}
    <div class="loading">
      <p>加载中...</p>
    </div>
  {/if}
</main>

<style>
  .app-container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-primary);
  }

  .app-header {
    padding: 2rem;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
    color: white;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .app-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
  }

  .subtitle {
    margin: 0.5rem 0 0 0;
    font-size: 1rem;
    opacity: 0.9;
  }

  .app-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    padding: 2rem;
    overflow-y: auto;
  }

  .upload-section,
  .monitor-section {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 1.2rem;
    color: var(--text-secondary);
  }
</style>
