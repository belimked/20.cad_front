# 轮询停止问题诊断脚本

请在浏览器控制台执行以下代码来诊断轮询问题:

```javascript
// ==================== 轮询诊断工具 ====================

const taskId = 'task_20251110_171147_e93faa'; // 替换为你的任务ID

console.log('%c=== 轮询状态诊断开始 ===', 'color: #3b82f6; font-weight: bold; font-size: 14px');

// 1. 检查轮询服务状态
console.log('\n%c1. 轮询服务状态:', 'font-weight: bold');
if (typeof taskPollingService !== 'undefined') {
  const pollingCount = taskPollingService.getPollingCount();
  const isPolling = taskPollingService.isTaskPolling(taskId);

  console.log('  ✓ 服务存在');
  console.log('  - 当前轮询任务数:', pollingCount);
  console.log('  - 该任务是否在轮询:', isPolling);

  if (pollingCount === 0) {
    console.error('  ✗ 没有任务在轮询! 轮询可能已停止');
  } else if (!isPolling) {
    console.warn('  ⚠ 该任务不在轮询列表中');
  }
} else {
  console.error('  ✗ 轮询服务不存在!');
}

// 2. 查看浏览器控制台历史日志
console.log('\n%c2. 控制台日志分析:', 'font-weight: bold');
console.log('  请查找以下关键日志:');
console.log('  ➜ "Starting polling for task"    - 轮询开始');
console.log('  ➜ "Task xxx status update"       - 轮询成功');
console.log('  ➜ "Polling paused for task"      - 轮询暂停(进入重试)');
console.log('  ➜ "Failed to poll task"          - 轮询失败');
console.log('  ➜ "Retry X/3 for task"           - 正在重试');
console.log('  ➜ "Max retries reached"          - 重试耗尽,轮询停止');
console.log('  ➜ "Stopping polling for task"    - 轮询被停止');

// 3. 统计日志
console.log('\n%c3. 请求统计:', 'font-weight: bold');
console.log('  请打开 Network 标签,筛选包含 "tasks" 的请求');
console.log('  统计以下信息:');
console.log('  - 总请求数');
console.log('  - 成功请求数 (HTTP 200)');
console.log('  - 失败请求数 (4xx/5xx)');
console.log('  - 最后一次请求的时间');

// 4. 检查调试日志Store
console.log('\n%c4. 调试日志检查:', 'font-weight: bold');
// 尝试访问日志store (可能需要根据实际情况调整)
try {
  // 这里假设可以通过某种方式访问store
  console.log('  请在调试日志面板中:');
  console.log('  1. 筛选 ERROR 类型');
  console.log('  2. 查找包含该任务ID的错误');
  console.log('  3. 展开查看错误详情');
} catch (e) {
  console.log('  (无法直接访问日志store)');
}

// 5. 手动测试API
console.log('\n%c5. 手动API测试:', 'font-weight: bold');
console.log('  在浏览器控制台执行以下代码测试API:');
console.log(`
  // 测试获取任务详情
  const testApi = async () => {
    try {
      const response = await window.__TAURI__.invoke('get_task_detail', {
        taskId: '${taskId}',
        apiUrl: 'http://10.3.19.63:8000' // 替换为你的API地址
      });
      console.log('✓ API调用成功:', response);
      return response;
    } catch (error) {
      console.error('✗ API调用失败:', error);
      return null;
    }
  };

  testApi();
`);

// 6. 诊断建议
console.log('\n%c6. 常见原因诊断:', 'font-weight: bold');
console.log(`
  如果轮询只进行了6次就停止,可能的原因:

  A. 连续失败3次触发重试机制
     表现: 控制台有 "Polling paused" 或 "Retry X/3" 日志
     检查: 查看ERROR日志,找到失败原因
     解决: 修复API问题或网络问题

  B. API返回错误但被忽略
     表现: Network显示200,但响应内容有错误
     检查: 查看API响应的 code 字段是否为200
     解决: 检查后端日志

  C. 任务状态变为 completed/failed
     表现: 控制台有 "Task reached terminal state"
     检查: 查看任务当前状态
     解决: 这是正常行为

  D. 轮询实例被意外清除
     表现: getPollingCount() 返回 0
     检查: 查找 "Stopping polling" 日志
     解决: 检查是否有代码调用了 stopPolling()

  E. 页面被重新渲染或组件卸载
     表现: 没有 "Stopping" 日志,但轮询停止
     检查: 查看页面是否刷新或路由变化
     解决: 确保轮询服务在全局scope
`);

console.log('\n%c=== 诊断完成 ===', 'color: #3b82f6; font-weight: bold; font-size: 14px');
console.log('请将以上信息和Network标签截图一起提供');
```

## 快速检查清单

在浏览器开发者工具中:

### Console 标签
- [ ] 是否有 "Polling paused" 警告?
- [ ] 是否有 "Failed to poll task" 错误?
- [ ] 是否有 "Retry" 日志?
- [ ] 是否有 "Max retries reached" 错误?

### Network 标签
- [ ] 总共发送了几次请求?
- [ ] 最后一次请求的状态码是什么?
- [ ] 响应时间是否正常(<1秒)?
- [ ] 响应内容的 `code` 字段是否为 200?

### 调试日志面板
- [ ] 筛选 ERROR 类型,是否有错误?
- [ ] POLLING 类型日志的数量?
- [ ] 最后一条日志的时间?

## 预期的正常行为

如果轮询正常工作,应该看到:

**控制台 (每3秒一次)**:
```
Task task_xxx status update: { status: "processing", progress: 25, ... }
Task task_xxx store updated: { status: "processing", progress: 25, ... }
```

**Network (每3秒一次)**:
```
GET /api/v1/tasks/task_xxx   200   0.5s
GET /api/v1/tasks/task_xxx   200   0.5s
GET /api/v1/tasks/task_xxx   200   0.5s
... (持续到任务完成)
```

**调试日志 (每3秒一次)**:
```
🔄 POLLING  17:11:48.862
任务状态: processing (25%)

🔄 POLLING  17:11:51.862
任务状态: processing (30%)

🔄 POLLING  17:11:54.862
任务状态: processing (35%)
...
```
