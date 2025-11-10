<script lang="ts">
  import { logStore, type LogLevel } from '$stores/logStore';
  import { slide } from 'svelte/transition';

  let isExpanded = false;
  let selectedLevel: LogLevel | 'all' = 'all';
  let searchTerm = '';

  // 记录每个日志条目的展开状态
  let expandedEntries: Set<string> = new Set();

  $: filteredLogs = $logStore.entries.filter((entry) => {
    // 过滤日志级别
    if (selectedLevel !== 'all' && entry.level !== selectedLevel) {
      return false;
    }

    // 搜索过滤
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        entry.message.toLowerCase().includes(searchLower) ||
        JSON.stringify(entry.data).toLowerCase().includes(searchLower)
      );
    }

    return true;
  });

  function toggleExpanded() {
    isExpanded = !isExpanded;
  }

  function clearLogs() {
    logStore.clear();
    expandedEntries.clear();
  }

  function toggleEntryData(entryId: string) {
    if (expandedEntries.has(entryId)) {
      expandedEntries.delete(entryId);
    } else {
      expandedEntries.add(entryId);
    }
    expandedEntries = expandedEntries; // 触发响应式更新
  }

  function formatTimestamp(timestamp: number): string {
    const date = new Date(timestamp);
    const timeStr = date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    const ms = date.getMilliseconds().toString().padStart(3, '0');
    return `${timeStr}.${ms}`;
  }

  function getLevelColor(level: LogLevel): string {
    const colors: Record<LogLevel, string> = {
      request: '#3b82f6', // blue
      response: '#10b981', // green
      error: '#ef4444', // red
      info: '#6b7280', // gray
      polling: '#8b5cf6', // purple
    };
    return colors[level];
  }

  function getLevelIcon(level: LogLevel): string {
    const icons: Record<LogLevel, string> = {
      request: '↗️',
      response: '↙️',
      error: '❌',
      info: 'ℹ️',
      polling: '🔄',
    };
    return icons[level];
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      alert('已复制到剪贴板');
    });
  }
</script>

<div class="debug-logger" class:expanded={isExpanded}>
  <!-- Toggle Button -->
  <button class="toggle-btn" on:click={toggleExpanded}>
    <span class="icon">{isExpanded ? '▼' : '▲'}</span>
    <span class="label">调试日志</span>
    {#if $logStore.entries.length > 0}
      <span class="badge">{$logStore.entries.length}</span>
    {/if}
  </button>

  <!-- Logger Panel -->
  {#if isExpanded}
    <div class="logger-panel" transition:slide={{ duration: 300 }}>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="filters">
          <select bind:value={selectedLevel}>
            <option value="all">全部日志</option>
            <option value="request">请求</option>
            <option value="response">响应</option>
            <option value="polling">轮询</option>
            <option value="info">信息</option>
            <option value="error">错误</option>
          </select>

          <input
            type="text"
            placeholder="搜索日志..."
            bind:value={searchTerm}
            class="search-input"
          />
        </div>

        <button class="clear-btn" on:click={clearLogs}>🗑️ 清空</button>
      </div>

      <!-- Log Entries -->
      <div class="log-entries">
        {#if filteredLogs.length === 0}
          <div class="empty-state">
            <p>暂无日志</p>
          </div>
        {:else}
          {#each filteredLogs as entry (entry.id)}
            <div class="log-entry" data-level={entry.level}>
              <div class="log-header">
                <span class="log-icon">{getLevelIcon(entry.level)}</span>
                <span class="log-level" style="color: {getLevelColor(entry.level)}">
                  {entry.level.toUpperCase()}
                </span>
                <span class="log-timestamp">{formatTimestamp(entry.timestamp)}</span>
                {#if entry.metadata?.duration}
                  <span class="log-duration">{entry.metadata.duration}ms</span>
                {/if}
              </div>

              <div class="log-message">{entry.message}</div>

              {#if entry.metadata}
                <div class="log-metadata">
                  {#if entry.metadata.endpoint}
                    <span class="metadata-item">
                      <strong>{entry.metadata.method || 'GET'}</strong>
                      {entry.metadata.endpoint}
                    </span>
                  {/if}
                  {#if entry.metadata.taskId}
                    <span class="metadata-item">Task: {entry.metadata.taskId}</span>
                  {/if}
                </div>
              {/if}

              {#if entry.data}
                <div class="log-data">
                  <button
                    class="data-toggle"
                    on:click={() => toggleEntryData(entry.id)}
                  >
                    <span class="toggle-icon">{expandedEntries.has(entry.id) ? '▼' : '▶'}</span>
                    查看数据 ({typeof entry.data === 'object' && entry.data !== null ? Object.keys(entry.data).length + ' 个字段' : '数据'})
                  </button>

                  {#if expandedEntries.has(entry.id)}
                    <div class="data-wrapper" transition:slide={{ duration: 200 }}>
                      <pre class="data-content">{JSON.stringify(entry.data, null, 2)}</pre>
                      <button
                        class="copy-btn"
                        on:click|stopPropagation={() => copyToClipboard(JSON.stringify(entry.data, null, 2))}
                      >
                        📋 复制
                      </button>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .debug-logger {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-color);
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  }

  .toggle-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-secondary);
    border: none;
    cursor: pointer;
    font-weight: 600;
    color: var(--text-primary);
    transition: background 0.2s;
  }

  .toggle-btn:hover {
    background: var(--bg-tertiary);
  }

  .toggle-btn .icon {
    font-size: 0.875rem;
  }

  .toggle-btn .badge {
    margin-left: auto;
    padding: 0.25rem 0.5rem;
    background: var(--primary-color);
    color: white;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .logger-panel {
    max-height: 400px;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
  }

  .filters {
    display: flex;
    gap: 0.5rem;
    flex: 1;
  }

  .filters select,
  .search-input {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.875rem;
  }

  .search-input {
    flex: 1;
    max-width: 300px;
  }

  .clear-btn {
    padding: 0.5rem 1rem;
    background: var(--error-color);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 600;
    transition: opacity 0.2s;
  }

  .clear-btn:hover {
    opacity: 0.9;
  }

  .log-entries {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    color: var(--text-secondary);
  }

  .log-entry {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: var(--bg-secondary);
    border-left: 3px solid var(--border-color);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
  }

  .log-entry[data-level='request'] {
    border-left-color: #3b82f6;
  }

  .log-entry[data-level='response'] {
    border-left-color: #10b981;
  }

  .log-entry[data-level='error'] {
    border-left-color: #ef4444;
    background: #fef2f2;
  }

  .log-entry[data-level='polling'] {
    border-left-color: #8b5cf6;
  }

  .log-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.75rem;
  }

  .log-icon {
    font-size: 1rem;
  }

  .log-level {
    font-weight: 700;
    font-family: 'Courier New', monospace;
  }

  .log-timestamp {
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
  }

  .log-duration {
    margin-left: auto;
    padding: 0.125rem 0.375rem;
    background: var(--bg-tertiary);
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    color: var(--text-secondary);
  }

  .log-message {
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }

  .log-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .metadata-item {
    padding: 0.25rem 0.5rem;
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
  }

  .log-data {
    margin-top: 0.5rem;
  }

  .data-toggle {
    width: 100%;
    text-align: left;
    cursor: pointer;
    color: var(--primary-color);
    font-weight: 600;
    padding: 0.5rem;
    background: var(--bg-tertiary);
    border: none;
    border-radius: var(--radius-sm);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .data-toggle:hover {
    background: var(--bg-primary);
    text-decoration: underline;
  }

  .data-toggle:active {
    transform: scale(0.98);
  }

  .toggle-icon {
    font-size: 0.75rem;
    transition: transform 0.2s ease;
  }

  .data-wrapper {
    padding-top: 0.5rem;
  }

  .data-content {
    margin-top: 0.5rem;
    padding: 0.75rem;
    background: #1e1e1e;
    color: #d4d4d4;
    border-radius: var(--radius-sm);
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    line-height: 1.4;
  }

  .copy-btn {
    margin-top: 0.5rem;
    padding: 0.375rem 0.75rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .copy-btn:hover {
    opacity: 0.9;
  }
</style>
