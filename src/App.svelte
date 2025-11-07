<script lang="ts">
  import { onMount } from 'svelte';
  import FileUpload from './components/upload/FileUpload.svelte';
  import TaskMonitor from './components/task/TaskMonitor.svelte';
  import DwgTestPanel from './components/test/DwgTestPanel.svelte';

  let appReady = false;
  let activeTab: 'upload' | 'test' = 'upload';

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

      <!-- Tab 切换 -->
      <div class="tab-nav">
        <button
          class="tab-btn"
          class:active={activeTab === 'upload'}
          on:click={() => (activeTab = 'upload')}
        >
          📁 文件上传
        </button>
        <button
          class="tab-btn"
          class:active={activeTab === 'test'}
          on:click={() => (activeTab = 'test')}
        >
          🧪 URL 测试
        </button>
      </div>
    </header>

    <div class="app-content">
      {#if activeTab === 'upload'}
        <!-- 文件上传模块 -->
        <section class="upload-section">
          <FileUpload />
        </section>
      {:else if activeTab === 'test'}
        <!-- URL 测试模块 -->
        <section class="test-section">
          <DwgTestPanel />
        </section>
      {/if}

      <!-- 任务监控模块 (两个 Tab 共享) -->
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

  .tab-nav {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .tab-btn {
    padding: 0.5rem 1.5rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: white;
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .tab-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.5);
  }

  .tab-btn.active {
    background: white;
    color: var(--primary-color);
    border-color: white;
    font-weight: 600;
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
  .test-section,
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
