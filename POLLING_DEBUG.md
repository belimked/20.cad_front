# 轮询只执行一次问题诊断

## 问题现象

调试日志显示只有6个请求(应该每3秒一次,持续轮询),任务状态停在 `downloading (27%)`.

## 可能的原因

### 1. 轮询遇到错误并暂停 (最可能)

**表现**:
- 第一次轮询成功
- 之后遇到错误,触发重试机制
- `instance.isPolling = false` 导致后续轮询被跳过

**检查方法**:
1. 打开浏览器控制台 (F12)
2. 查找以下警告信息:
   ```
   Polling paused for task xxx, skipping this cycle
   ```
3. 查找错误信息:
   ```
   Failed to poll task xxx:
   ```

### 2. 轮询被意外停止

**表现**:
- `stopPolling()` 被调用
- `clearInterval()` 清除了定时器

**检查方法**:
在浏览器控制台执行:
```javascript
// 检查轮询服务状态
console.log('轮询数量:', taskPollingService.getPollingCount());
console.log('任务在轮询:', taskPollingService.isTaskPolling('task_20251110_171147_e93faa'));
```

### 3. API 超时或网络错误

**表现**:
- 请求超时(>10秒)
- 网络断开
- API 返回错误

**检查方法**:
查看调试日志中的 ERROR 类型日志

## 立即诊断步骤

### 步骤1: 检查浏览器控制台

打开浏览器开发者工具,执行以下代码:

\`\`\`javascript
// === 轮询诊断脚本 ===
const taskId = 'task_20251110_171147_e93faa';

console.log('=== 轮询状态诊断 ===');
console.log('任务ID:', taskId);

// 1. 检查轮询服务
if (typeof taskPollingService !== 'undefined') {
  console.log('✓ 轮询服务存在');
  console.log('  - 当前轮询任务数:', taskPollingService.getPollingCount());
  console.log('  - 该任务是否在轮询:', taskPollingService.isTaskPolling(taskId));
} else {
  console.error('✗ 轮询服务不存在!');
}

// 2. 检查控制台历史日志
console.log('\n查找关键日志:');
console.log('- 查找 "Polling paused" - 表示轮询被暂停');
console.log('- 查找 "Failed to poll" - 表示轮询失败');
console.log('- 查找 "Stopping polling" - 表示轮询被停止');
console.log('- 查找 "Polling instance not found" - 表示实例丢失');

console.log('=== 诊断完成 ===');
\`\`\`

### 步骤2: 查看调试日志面板

1. 打开应用底部的"调试日志"
2. 筛选 **ERROR** 类型
3. 查看是否有轮询失败的错误
4. 点击"查看数据"展开错误详情

### 步骤3: 查看网络请求

1. 浏览器开发者工具 -> Network 标签
2. 刷新页面或重新提交任务
3. 筛选 `tasks` 相关的请求
4. 检查:
   - 请求是否每3秒发送一次?
   - 请求状态码是否为 200?
   - 响应时间是否正常 (< 1秒)?

## 预期的正常行为

### 浏览器控制台日志

每3秒应该看到:
\`\`\`
Task task_xxx status update: { status: "downloading", progress: 27, ... }
Task task_xxx store updated: { status: "downloading", progress: 27, ... }
\`\`\`

### 调试日志面板

应该看到持续的 POLLING 类型日志:
\`\`\`
🔄 POLLING  17:11:48.862
任务状态: downloading (27%)

🔄 POLLING  17:11:51.862
任务状态: downloading (35%)

🔄 POLLING  17:11:54.862
任务状态: downloading (42%)
...
\`\`\`

### 网络请求

Network 标签应该看到:
\`\`\`
GET /api/v1/tasks/task_xxx   200   0.5s
GET /api/v1/tasks/task_xxx   200   0.5s  (3秒后)
GET /api/v1/tasks/task_xxx   200   0.5s  (3秒后)
...
\`\`\`

## 异常情况判断

### 情况A: 控制台有 "Polling paused" 警告

**原因**: 轮询遇到错误,进入重试延迟期

**解决方法**:
1. 查看前面的错误信息
2. 检查 API 是否正常响应
3. 等待重试延迟结束(5秒/10秒/15秒)

### 情况B: 轮询数量为 0

**原因**: 轮询未启动或被停止

**解决方法**:
1. 检查任务创建后是否调用了 `startPolling()`
2. 查看是否有 "Stopping polling" 日志
3. 重新提交任务

### 情况C: Network 标签无请求

**原因**: `setInterval` 未工作或被清除

**解决方法**:
1. 检查是否有 JavaScript 错误
2. 刷新页面重试
3. 清除浏览器缓存

### 情况D: 请求频繁失败 (4xx/5xx)

**原因**: API 错误或任务不存在

**解决方法**:
1. 检查后端日志
2. 验证任务ID是否正确
3. 运行 `./scripts/test_task_api.sh task_xxx` 测试API

## 临时解决方案

如果轮询卡住,可以在浏览器控制台手动重启:

\`\`\`javascript
const taskId = 'task_20251110_171147_e93faa';

// 停止当前轮询
taskPollingService.stopPolling(taskId);

// 等待1秒
setTimeout(() => {
  // 重新启动轮询
  taskPollingService.startPolling(taskId);
  console.log('轮询已重启');
}, 1000);
\`\`\`

## 已知问题修复

在最新代码中,我已经添加了:
1. ✅ 更详细的警告日志 (区分"实例不存在"和"轮询暂停")
2. ✅ 分离的检查逻辑 (先检查实例,再检查isPolling)
3. ✅ 更完整的错误日志记录

## 下一步

请按照"立即诊断步骤"检查,并提供:
1. 浏览器控制台的完整输出
2. 调试日志中的 ERROR 日志 (如果有)
3. Network 标签的截图或日志
4. 诊断脚本的执行结果

这样我可以准确判断问题原因!
