<script lang="ts">
  import { invoke } from '@tauri-apps/api/tauri';
  import { currentFile, fileActions } from '$stores/fileStore';
  import Button from '../common/Button.svelte';
  import { formatFileSize } from '$utils/formatters';
  import { apiService } from '$services/api';

  let isDragging = false;
  let isUploading = false;
  let uploadError: string | null = null;
  let uploadSuccess: string | null = null;

  // 检查是否为大文件 (>100MB)
  $: isLargeFile = $currentFile && $currentFile.size > 100 * 1024 * 1024;

  async function handleUpload() {
    if (!$currentFile) return;

    isUploading = true;
    uploadError = null;
    uploadSuccess = null;

    try {
      const response = await apiService.uploadFile($currentFile.path);
      uploadSuccess = `文件上传成功,任务序号: ${response.task_id}`;
      console.log('上传成功:', response);
    } catch (error) {
      uploadError = `上传失败: ${error}`;
      console.error('上传失败:', error);
    } finally {
      isUploading = false;
    }
  }

  async function selectFile() {
    try {
      const filePath = await invoke<string>('select_file');
      fileActions.setFile({
        path: filePath,
        name: filePath.split('/').pop() || filePath.split('\\').pop() || '',
        size: 0, // 实际大小需要额外获取
      });
    } catch (error) {
      console.error('文件选择失败:', error);
    }
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    isDragging = false;

    const files = event.dataTransfer?.files;
    if (!files || files.length === 0) {
      return;
    }

    // 仅支持单个文件上传
    if (files.length > 1) {
      console.error('仅支持单个文件上传');
      // TODO: 添加用户可见的错误提示
      return;
    }

    const file = files[0];
    const fileName = file.name;

    // 验证文件类型 (仅支持 DWG 格式)
    if (!fileName.toLowerCase().endsWith('.dwg')) {
      console.error('仅支持 DWG 格式');
      // TODO: 添加用户可见的错误提示
      return;
    }

    // 设置文件信息到 store
    fileActions.setFile({
      path: fileName, // 注意: 浏览器拖拽无法获取完整路径,使用文件名
      name: fileName,
      size: file.size,
    });
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave() {
    isDragging = false;
  }
</script>

<div class="file-upload">
  <h2>上传 CAD 文件</h2>

  <div
    role="region"
    aria-label="File drop zone"
    class="drop-zone"
    class:dragging={isDragging}
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
  >
    {#if $currentFile}
      <div class="file-info">
        <div class="file-header">
          <span class="file-icon">📄</span>
          <p class="file-name">{$currentFile.name}</p>
        </div>
        <div class="file-details">
          <span class="file-size">💾 {formatFileSize($currentFile.size)}</span>
          <span class="file-format">DWG</span>
        </div>
        {#if isLargeFile}
          <div class="warning">
            <span class="warning-icon">⚠️</span>
            <span>文件较大,上传可能需要较长时间</span>
          </div>
        {/if}
        {#if uploadSuccess}
          <div class="success-message">
            <span>✅ {uploadSuccess}</span>
          </div>
        {/if}
        {#if uploadError}
          <div class="error-message">
            <span>❌ {uploadError}</span>
            <Button on:click={handleUpload}>重试</Button>
          </div>
        {/if}
        <div class="file-actions">
          <Button on:click={selectFile}>重新选择</Button>
          <Button on:click={() => fileActions.clearFile()}>清除</Button>
          <Button on:click={handleUpload} disabled={isUploading || !!uploadSuccess}>
            {isUploading ? '上传中...' : '开始处理'}
          </Button>
        </div>
      </div>
    {:else}
      <div class="upload-prompt">
        <p>拖拽 DWG 文件到此处</p>
        <p class="or">或</p>
        <Button on:click={selectFile} disabled={isUploading}>选择文件</Button>
      </div>
    {/if}
  </div>
</div>

<style>
  .file-upload {
    width: 100%;
  }

  h2 {
    margin-bottom: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .drop-zone {
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-lg);
    padding: 3rem 2rem;
    text-align: center;
    transition: all 0.2s ease;
    background: var(--bg-primary);
  }

  .drop-zone.dragging {
    border-color: var(--primary-color);
    background: var(--primary-light);
    opacity: 0.8;
  }

  .upload-prompt {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .or {
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .file-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    width: 100%;
  }

  .file-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .file-icon {
    font-size: 1.5rem;
  }

  .file-name {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1rem;
    margin: 0;
  }

  .file-details {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .file-size {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .file-format {
    padding: 0.25rem 0.75rem;
    background: var(--primary-color);
    color: white;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.75rem;
  }

  .warning {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: var(--warning-light);
    border: 1px solid var(--warning-color);
    border-radius: var(--radius-md);
    color: var(--warning-dark);
    font-size: 0.875rem;
  }

  .warning-icon {
    font-size: 1rem;
  }

  .success-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #d1fae5;
    border: 1px solid var(--success-color);
    border-radius: var(--radius-md);
    color: #065f46;
    font-size: 0.875rem;
  }

  .error-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #fee2e2;
    border: 1px solid var(--error-color);
    border-radius: var(--radius-md);
    color: #991b1b;
    font-size: 0.875rem;
  }

  .file-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
</style>
