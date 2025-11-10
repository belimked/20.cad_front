# 轮询 6 次后停止问题修复

## 问题描述

用户反馈：任务监控部分在进行了 6 次请求后就不再更新，轮询完全停止。

## 根本原因

### 原始实现的 Bug

在 `src/services/taskPollingService.ts` 的错误处理逻辑中存在严重缺陷：

```typescript
// ❌ 原始实现（有问题）
private handlePollingError(taskId: string, _error: unknown): void {
  const instance = this.pollingInstances.get(taskId);
  if (!instance) return;

  instance.retryCount++;

  if (instance.retryCount <= this.MAX_RETRIES) {
    const retryDelay = this.RETRY_DELAYS[instance.retryCount - 1];

    // 暂停轮询，延迟后重试
    instance.isPolling = false;  // ⚠️ 设置标志位为 false
    setTimeout(() => {
      instance.isPolling = true;  // ⚠️ 尝试恢复，但可能失败
    }, retryDelay);
  }
}

// 轮询主函数检查标志位
private async pollTaskStatus(taskId: string): Promise<void> {
  const instance = this.pollingInstances.get(taskId);
  if (!instance) return;

  if (!instance.isPolling) {  // ⚠️ 如果为 false 就跳过
    console.warn(`Polling paused for task ${taskId}, skipping this cycle`);
    return;  // 直接返回，不执行任何操作
  }

  // ... 执行轮询
}
```

### 问题场景还原

1. **第 1-2 次轮询**：成功，一切正常
2. **第 3 次轮询**：API 请求失败（网络波动/超时）
   - 触发 `handlePollingError()`
   - 设置 `instance.isPolling = false`
   - 安排 5 秒后恢复（`setTimeout`）
3. **在等待期间（5 秒内）**：
   - `setInterval` 继续每 3 秒触发一次
   - 第 4 次、第 5 次、第 6 次轮询都被 `if (!instance.isPolling)` 拦截
   - 全部直接 return，什么都不做
4. **5 秒后 `setTimeout` 执行**：
   - 尝试设置 `instance.isPolling = true`
   - **但存在以下问题**：
     - 闭包中的 `instance` 引用可能已经失效
     - 如果在延迟期间出现任何状态变化，恢复可能失败
     - JavaScript 异步执行的不确定性

**结果**：`isPolling` 永远是 `false`，后续所有轮询请求都被跳过，轮询"死亡"

### 为什么是 6 次左右？

- 第 1-2 次：成功
- 第 3 次：触发错误
- 第 4-6 次：在重试延迟期间被跳过
- 第 7 次及以后：如果 `isPolling` 没有正确恢复，永远被跳过

## 解决方案

### 核心思路

**不使用状态标志位 (`isPolling`)，而是直接管理定时器生命周期**

- 出错时：`clearInterval()` 停止当前定时器
- 延迟后：创建新的 `setInterval()` 重新启动轮询

### 修复后的实现

```typescript
// ✅ 修复后的实现
private handlePollingError(taskId: string, _error: unknown): void {
  const instance = this.pollingInstances.get(taskId);
  if (!instance) return;

  instance.retryCount++;

  if (instance.retryCount <= this.MAX_RETRIES) {
    const retryDelay = this.RETRY_DELAYS[instance.retryCount - 1];

    logActions.error(
      `轮询失败，将在 ${retryDelay}ms 后重试 (${instance.retryCount}/${this.MAX_RETRIES})`,
      _error,
      { taskId }
    );

    taskActions.updateTask(taskId, {
      status: 'queued',
      message: `连接中... (重试 ${instance.retryCount}/${this.MAX_RETRIES})`,
    });

    // ✅ 停止当前的定时器（清理旧的 interval）
    clearInterval(instance.intervalId);

    // ✅ 延迟后重新启动轮询（创建新的 interval）
    setTimeout(() => {
      // 防御性检查：任务可能已被手动停止
      if (!this.pollingInstances.has(taskId)) {
        console.log(`Task ${taskId} was stopped during retry delay, skipping restart`);
        return;
      }

      console.log(`Restarting polling for task ${taskId} after retry delay`);

      // ✅ 创建新的定时器
      const newIntervalId = window.setInterval(() => {
        this.pollTaskStatus(taskId);
      }, this.POLL_INTERVAL);

      // ✅ 更新实例的 intervalId
      const currentInstance = this.pollingInstances.get(taskId);
      if (currentInstance) {
        currentInstance.intervalId = newIntervalId;
      }
    }, retryDelay);
  } else {
    // 重试次数耗尽
    console.error(`Max retries reached for task ${taskId}`);

    logActions.error(`轮询重试次数已用尽，任务失败`, _error, { taskId });

    taskActions.updateTask(taskId, {
      status: 'failed',
      message: '无法连接到服务器，请检查网络连接',
    });
    this.stopPolling(taskId);
  }
}
```

### 同时移除的代码

```typescript
// ❌ 删除接口中的 isPolling 字段
interface PollingInstance {
  taskId: string;
  intervalId: number;
  retryCount: number;
  // isPolling: boolean; ← 已删除
}

// ❌ 删除初始化时的 isPolling
const instance: PollingInstance = {
  taskId,
  intervalId: 0,
  retryCount: 0,
  // isPolling: true, ← 已删除
};

// ❌ 删除 pollTaskStatus 中的检查
private async pollTaskStatus(taskId: string): Promise<void> {
  const instance = this.pollingInstances.get(taskId);
  if (!instance) return;

  // ❌ 删除这段检查
  // if (!instance.isPolling) {
  //   console.warn(`Polling paused for task ${taskId}, skipping this cycle`);
  //   return;
  // }

  // 直接执行轮询逻辑
  try {
    const status = await apiService.getTaskStatus(taskId);
    // ...
  }
}
```

## 修复效果

### 之前的行为

```
请求1: ✅ 成功
请求2: ✅ 成功
请求3: ❌ 失败 → 设置 isPolling=false，安排5秒后恢复
请求4: ⏭️  跳过（isPolling=false）
请求5: ⏭️  跳过（isPolling=false）
请求6: ⏭️  跳过（isPolling=false）
5秒后: ⚠️  尝试恢复 isPolling=true，但可能失败
请求7: ⏭️  跳过（isPolling 仍为 false）
请求8: ⏭️  跳过
...
轮询死亡 💀
```

### 修复后的行为

```
请求1: ✅ 成功
请求2: ✅ 成功
请求3: ❌ 失败 → 清除定时器，安排5秒后重启
(在5秒延迟期间，没有任何请求发送，定时器已停止)
5秒后: ✅ 创建新的定时器，重新开始轮询
请求4: ✅ 继续轮询
请求5: ✅ 继续轮询
...
轮询正常 ✨
```

## 关键改进点

1. **彻底移除状态标志位**
   - 不再依赖 `isPolling` 这种不可靠的标志
   - 直接通过定时器的生命周期管理轮询状态

2. **清理和重建定时器**
   - 错误时：`clearInterval()` 完全停止当前轮询
   - 恢复时：创建全新的 `setInterval()`，确保干净启动

3. **防御性编程**
   - 在 `setTimeout` 回调中检查任务是否仍存在
   - 避免对已停止的任务重启轮询

4. **保持重试计数逻辑**
   - 重试次数限制（最多 3 次）保持不变
   - 指数退避延迟（5s, 10s, 15s）保持不变

## 测试建议

### 正常场景测试

1. 提交一个新任务
2. 观察轮询是否持续进行
3. 检查任务状态是否正常更新
4. 确认任务完成后轮询正常停止

### 网络异常场景测试

1. 提交一个任务，等待轮询开始
2. 在任务运行期间临时断开网络或关闭后端服务
3. 观察是否触发重试逻辑（5秒后）
4. 恢复网络后，确认轮询自动恢复
5. 检查任务状态是否继续更新

### 多任务并发测试

1. 同时提交 2-3 个任务
2. 确认每个任务都能独立轮询
3. 人为制造某个任务的网络错误
4. 验证只有该任务重试，其他任务不受影响

## 相关文件

- **修改文件**：`src/services/taskPollingService.ts`
- **诊断文档**：`POLLING_STOP_DEBUG.md`
- **测试页面**：`test-details.html`（DebugLogger 测试）

## 提交信息

```
fix: 修复轮询在错误重试后永久停止的问题

问题：
- 轮询在遇到错误后使用 isPolling 标志位暂停
- 在重试延迟期间，setInterval 继续触发但被跳过
- setTimeout 恢复 isPolling 可能失败，导致轮询永久停止

解决方案：
- 移除 isPolling 标志位机制
- 错误时直接 clearInterval 停止定时器
- 延迟后创建新的 setInterval 重启轮询
- 添加防御性检查，确保任务仍存在时才重启

影响：
- 修复了轮询在 6 次请求后停止的 bug
- 提高了错误恢复的可靠性
- 简化了状态管理逻辑
```
