# 任务步骤排序功能

## 问题描述

后端API返回的任务步骤(`steps`数组)顺序混乱,不是按照实际执行时间排序的。例如:

```json
{
  "steps": [
    {
      "step_name": "下载DWG文件",
      "step_order": 1,
      "started_at": "2025-11-10T17:11:48"
    },
    {
      "step_name": "执行系统命令",
      "step_order": 1,
      "started_at": "2025-11-10T17:11:53"
    },
    {
      "step_name": "执行AutoCAD工作流",
      "step_order": 2,
      "started_at": "2025-11-10T17:11:53"
    },
    // ... 顺序混乱
  ]
}
```

## 解决方案

在Rust后端(`src-tauri/src/commands/task.rs`)中,对API返回的步骤按 `started_at` 时间排序。

### 实现逻辑

```rust
/// 按 started_at 时间对步骤进行排序
/// 如果 started_at 为 None,则放到最后
fn sort_steps_by_time(steps: &mut Vec<TaskStep>) {
    steps.sort_by(|a, b| {
        match (&a.started_at, &b.started_at) {
            (Some(time_a), Some(time_b)) => time_a.cmp(time_b),
            (Some(_), None) => std::cmp::Ordering::Less,  // 有时间的排前面
            (None, Some(_)) => std::cmp::Ordering::Greater, // 无时间的排后面
            (None, None) => a.step_order.cmp(&b.step_order), // 都无时间则按 step_order
        }
    });
}
```

### 排序规则

1. **有 started_at 的步骤** 按时间升序排列(早的在前)
2. **无 started_at 的步骤** 排在最后
3. **都无时间的步骤** 按 `step_order` 排序

### 调用位置

在 `get_task_detail()` 函数中,解析API响应后立即排序:

```rust
// 新格式
if let Ok(api_response) = serde_json::from_str::<ApiResponse<TaskDetailResponse>>(&response_text) {
    let mut data = api_response.data;
    sort_steps_by_time(&mut data.steps);  // ← 排序
    return Ok(data);
}

// 旧格式
if let Ok(mut detail) = serde_json::from_str::<TaskDetailResponse>(&response_text) {
    sort_steps_by_time(&mut detail.steps);  // ← 排序
    return Ok(detail);
}
```

## 效果

排序后的步骤按实际执行时间顺序显示:

```json
{
  "steps": [
    {
      "step_name": "下载DWG文件",
      "started_at": "2025-11-10T17:11:48"
    },
    {
      "step_name": "执行系统命令",
      "started_at": "2025-11-10T17:11:53"
    },
    {
      "step_name": "执行AutoCAD工作流",
      "started_at": "2025-11-10T17:11:53"
    },
    {
      "step_name": "清理目录",
      "started_at": "2025-11-10T17:11:55"
    },
    // ... 按时间顺序排列
  ]
}
```

## 测试

1. 重新编译应用:
   ```bash
   npm run tauri build
   # 或开发模式
   npm run tauri dev
   ```

2. 提交一个新任务

3. 任务完成后,检查步骤顺序是否按 `started_at` 时间排列

## 修改文件

- ✅ `src-tauri/src/commands/task.rs`
  - 新增 `sort_steps_by_time()` 函数
  - 在 `get_task_detail()` 中调用排序

## 相关类型定义

```rust
// src-tauri/src/models/response.rs
pub struct TaskStep {
    pub step_order: i32,
    pub step_name: String,
    pub status: String,
    pub started_at: Option<String>,  // ISO 8601 格式时间字符串
    pub completed_at: Option<String>,
    pub duration_seconds: Option<f64>,
    pub message: Option<String>,
    pub error_message: Option<String>,
}
```

## 注意事项

1. **时间格式**: `started_at` 是 ISO 8601 字符串 (如 "2025-11-10T17:11:48")
   - Rust 的字符串比较 (`cmp()`) 对这种格式天然支持字典序 = 时间序

2. **处理 None 值**: 某些步骤可能没有 `started_at`(如还未开始的步骤)
   - 这些步骤会被排到最后
   - 如果都是 None,则按 `step_order` 排序

3. **不影响原有逻辑**: 排序只在返回前端前进行,不修改后端数据

4. **性能**: O(n log n) 复杂度,对于典型的10-20个步骤可以忽略不计
