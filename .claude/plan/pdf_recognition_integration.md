# PDF 识别和转换集成计划

**状态：** ✅ 已完成
**创建时间：** 2025-11-06
**最后更新：** 2025-11-06
**负责人：** Claude Code

---

## 📋 集成目标

将 PDF 识别和转换功能（MinerU + PDFReorganizeService）集成到 TaskProcessor 主流程中，在 CAD 拆分打印完成后自动触发。

### 用户需求

> 目前PDF的流程，识别和转换需要迁移到 `/Users/saul/IdeaProjects/100.AI.TrainData/start_api.ps1` 的流程中在完成cad拆分打印之后，完成后续识别和转换操作

### 用户选择

- **触发方式：** B（自动触发，后台执行）
- **错误处理：** A（失败继续，记录日志，不中断主流程）

---

## 🏗️ 实施方案

### 方案选择

**✅ 方案1：最小侵入式集成（已采用）**

**优势：**
- 代码变动最小
- 复用现有服务（MinerUService, PDFReorganizeService）
- 失败隔离，不影响主流程

**实施路径：**
```
TaskProcessor.process_task()
  ├─ 步骤1: 下载 DWG 文件 (10-40%)
  ├─ 步骤2: 执行 AutoCAD 工作流 (40-70%)  ← 调整进度
  ├─ 🆕 步骤3: PDF 识别和转换 (70-90%)  ← 新增
  └─ 步骤4: 任务完成 (100%)
```

---

## 🔧 实施步骤

### 阶段 1: 准备工作 ✅

#### 1.1. 修改 `_run_autocad_workflow()` 返回值

**文件：** `api/services/task_processor.py`

**修改前：**
```python
def _run_autocad_workflow(...) -> bool:
    ...
    return success
```

**修改后：**
```python
def _run_autocad_workflow(...) -> tuple:
    """
    Returns:
        (success, output_dir): 成功标志和输出目录
    """
    ...
    # 获取输出目录（用于后续PDF识别）
    output_dir = None
    if hasattr(workflow, 'output_dir') and workflow.output_dir:
        output_dir = workflow.output_dir
    elif hasattr(workflow, 'config') and hasattr(workflow.config, 'output_dir'):
        output_dir = workflow.config.output_dir

    return (success, output_dir)
```

**调用方更新：**
```python
# Line 190
workflow_success, output_dir = await asyncio.to_thread(
    self._run_autocad_workflow, ...
)
```

#### 1.2. 调整进度条百分比

| 步骤 | 原进度 | 新进度 | 说明 |
|------|--------|--------|------|
| 下载文件 | 10-40% | 10-40% | 不变 |
| AutoCAD 工作流 | 40-90% | **40-70%** | 压缩 |
| 🆕 PDF 识别 | - | **70-90%** | 新增 |
| 任务完成 | 100% | 100% | 不变 |

**代码位置：**
- Line 314-318: 工作流执行中 50% → 55%
- Line 323-327: 工作流完成 90% → 70%

---

### 阶段 2: 核心功能实现 ✅

#### 2.1. 实现 `_recognize_and_convert_pdfs()` 方法

**文件：** `api/services/task_processor.py` (Line 351-464)

**方法签名：**
```python
def _recognize_and_convert_pdfs(
    self,
    output_dir: str,
    config_name: str,
    task_id: str,
    task_service: DWGTaskService
) -> bool:
    """
    识别和转换 PDF 文件（同步）

    Returns:
        是否成功（失败不中断主流程）
    """
```

**核心流程：**

```python
# 1. 验证输出目录
if not output_dir or not Path(output_dir).exists():
    return False

# 2. 检查 PDF 文件
pdf_files = list(Path(output_dir).glob('*.pdf'))
if not pdf_files:
    return False

# 3. 获取 AutoCAD 配置
autocad_config = AutoCADConfigService().get_config_by_name(config_name)

# 4. 检查是否启用
if not getattr(autocad_config, 'mineru_enabled', True):
    return False

# 5. 创建 MinerU 服务并执行
mineru_db = SessionLocal()
try:
    mineru_service = MinerUService(config, task_id, mineru_db)
    result = mineru_service.batch_recognize_pdfs(str(output_dir))

    # 输出统计信息
    if result.get('success'):
        print(f"  ✅ 识别: {result['success_count']}/{result['total_files']}")
        print(f"  📁 转换: {reorg['completed']} 个文件")
        return True
finally:
    mineru_db.close()
```

**关键特性：**
- ✅ 独立数据库会话（避免线程冲突）
- ✅ 失败继续策略（异常返回 False，不抛出）
- ✅ 详细日志输出（识别统计、重组织统计）
- ✅ 进度更新（75% 识别开始，90% 识别完成）

#### 2.2. 集成到 `process_task()` 主流程

**插入位置：** Line 222-271（步骤2和步骤3之间）

```python
# ============================================================================
# 步骤3: PDF 识别和转换（新增）
# ============================================================================
if output_dir:  # 只有当有输出目录时才执行
    step_order += 1
    print(f"\n▶ 步骤{step_order}: PDF 识别和转换")

    step = task_service.add_step_log(
        task_id=task_id,
        step_name="PDF 识别和转换",
        step_order=step_order,
        status='running',
        message="正在识别 PDF 文件并提取图号信息"
    )

    # 更新任务状态
    task_service.update_task_status(
        task_id=task_id,
        status='processing',
        current_step='PDF 识别和转换',
        progress=70
    )

    # 在线程池中运行 PDF 识别
    pdf_success = await asyncio.to_thread(
        self._recognize_and_convert_pdfs,
        output_dir,
        task.config_name,
        task_id,
        task_service
    )

    if not pdf_success:
        # 失败继续策略：记录警告，不中断流程
        task_service.update_step_log(
            step_id=step.id,
            status='warning',
            message="PDF 识别失败或跳过，主流程继续"
        )
        print(f"⚠️  PDF 识别失败或跳过，主流程继续")
    else:
        # PDF 识别成功
        task_service.update_step_log(
            step_id=step.id,
            status='completed',
            message="PDF 识别和转换完成"
        )
        print(f"✅ PDF 识别和转换完成")
else:
    print(f"⚠️  未获取到输出目录，跳过 PDF 识别")
```

---

### 阶段 3: 错误处理和日志 ✅

#### 失败继续策略

**设计原则：** PDF 识别失败不应中断主流程

**实现细节：**

| 场景 | 处理方式 | 数据库状态 | 任务状态 |
|------|---------|-----------|---------|
| PDF 识别成功 | 正常流程 | `completed` | 继续 |
| 无输出目录 | 跳过识别 | - | 继续 |
| 无 PDF 文件 | 跳过识别 | - | 继续 |
| 识别异常 | 记录警告 | `warning` | 继续 |
| 配置未启用 | 跳过识别 | - | 继续 |

**日志示例：**
```
步骤3: PDF 识别和转换
  📋 发现 10 个 PDF 文件
  🔍 开始 PDF 识别和转换...
  ✅ PDF 识别完成:
     - 总文件数: 10
     - 成功识别: 10
     - 失败: 0
  📁 PDF 文件重组织:
     - 成功转换: 8
     - 跳过: 2
     - 转换目录: /output_convert
```

---

### 阶段 4: 配置检查 ✅

#### 配置字段

**表：** `autocad_config`

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mineru_enabled` | BOOLEAN | TRUE | 是否启用 MinerU 识别 |
| `auto_reorganize_pdfs` | BOOLEAN | TRUE | 是否自动重组织 PDF |

**检查逻辑：**
```python
mineru_enabled = getattr(autocad_config, 'mineru_enabled', True)
if not mineru_enabled:
    print(f"  ⚠️  MinerU 识别未启用，跳过")
    return False
```

---

### 阶段 5: 返回值修改 ✅

#### 调用方更新

**检查范围：** 所有调用 `_run_autocad_workflow()` 的地方

**结果：** 仅一处调用（Line 190），已更新：

```python
# 修改前
workflow_success = await asyncio.to_thread(...)

# 修改后
workflow_success, output_dir = await asyncio.to_thread(...)
```

**测试代码：** 未调用此方法，无需修改

---

### 阶段 6: 测试验证 ✅

#### 测试脚本

**文件：** `scripts/test_task_processor_integration.py`

**测试项：**
1. ✅ 方法存在性检查
2. ✅ 配置验证（mineru_enabled, auto_reorganize_pdfs）
3. ✅ 数据库表结构检查（conversion 字段）
4. ✅ 集成流程说明
5. ✅ 手动测试指南

**运行：**
```bash
python scripts/test_task_processor_integration.py
```

---

## 📊 修改汇总

### 文件变更

| 文件 | 行数变化 | 主要修改 |
|------|---------|---------|
| `api/services/task_processor.py` | +119 | 新增 PDF 识别方法和集成步骤 |
| `scripts/test_task_processor_integration.py` | +217 (新建) | 创建测试脚本 |

### 代码修改点

#### 1. `api/services/task_processor.py`

| 位置 | 类型 | 说明 |
|------|------|------|
| Line 263-283 | 修改 | `_run_autocad_workflow()` 返回值改为元组 |
| Line 336-342 | 修改 | 添加 output_dir 获取逻辑 |
| Line 190 | 修改 | 调用方接收元组返回值 |
| Line 314-318 | 修改 | 进度调整 55% |
| Line 323-327 | 修改 | 进度调整 70% |
| Line 351-464 | 新增 | `_recognize_and_convert_pdfs()` 方法 |
| Line 222-271 | 新增 | PDF 识别集成步骤 |

---

## 🔍 依赖关系

### 服务依赖

```
TaskProcessor
  └─> _recognize_and_convert_pdfs()
       ├─> AutoCADConfigService.get_config_by_name()
       ├─> MinerUService.batch_recognize_pdfs()
       │     └─> PDFReorganizeService.reorganize_pdfs()  (自动触发)
       └─> DWGTaskService.update_task_status()
```

### 数据库依赖

| 表 | 用途 |
|---|------|
| `autocad_config` | 读取 MinerU 配置 |
| `dwg_recognition_results` | 保存识别结果 |
| `dwg_drawing_sheets` | 保存图号记录 + 转换状态 |
| `dwg_task_steps` | 记录步骤日志 |

---

## ✅ 验证清单

### 功能验证

- [x] `_run_autocad_workflow()` 返回元组
- [x] 调用方正确接收返回值
- [x] 进度条百分比调整正确（40-70%, 70-90%, 100%）
- [x] `_recognize_and_convert_pdfs()` 方法实现完整
- [x] PDF 识别步骤集成到主流程
- [x] 失败继续策略生效（status='warning'）
- [x] 详细日志输出
- [x] 配置检查（mineru_enabled）
- [x] 文件验证（目录、PDF 存在性）
- [x] 独立数据库会话

### 代码质量

- [x] 类型注解完整
- [x] 文档字符串清晰
- [x] 异常处理健全
- [x] 日志输出详细
- [x] 代码格式一致

### 测试覆盖

- [x] 单元测试脚本已创建
- [x] 集成验证脚本已创建
- [x] 手动测试指南已提供

---

## 🚀 后续优化建议

### 1. 性能优化

**当前状态：** MinerU 已使用并发处理（ThreadPoolExecutor）

**可选优化：**
- [ ] 添加 PDF 识别进度回调（更细粒度的进度更新）
- [ ] 支持大文件分批处理（避免内存溢出）
- [ ] 添加识别结果缓存（避免重复识别）

### 2. 配置增强

**建议添加：**
- [ ] `mineru_timeout`: 单个 PDF 超时时间
- [ ] `mineru_max_retries`: 识别失败重试次数
- [ ] `mineru_batch_size`: 并发处理数量

### 3. 监控和告警

**建议添加：**
- [ ] 识别成功率监控
- [ ] 识别耗时统计
- [ ] 异常告警（识别失败率超阈值）

### 4. 用户体验

**建议添加：**
- [ ] 识别进度实时推送（WebSocket）
- [ ] 识别结果预览（前端展示）
- [ ] 手动重试机制（识别失败后）

---

## 📝 测试指南

### 环境准备

1. **启动 MinerU 服务：**
   ```bash
   # 确保 MinerU 服务运行在 http://127.0.0.1:18080
   ```

2. **检查数据库配置：**
   ```bash
   python scripts/autocad_config_manager.py get default
   # 确认 mineru_enabled=True, auto_reorganize_pdfs=True
   ```

3. **验证表结构：**
   ```bash
   python scripts/test_task_processor_integration.py
   ```

### 手动测试

#### 步骤 1: 启动 API 服务

```bash
# Windows
start_api.bat

# Linux/Mac
./start_api.sh
```

#### 步骤 2: 提交测试任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks/print \
  -H 'Content-Type: application/json' \
  -d '{
    "dwg_url": "http://your-server/test.dwg",
    "config_name": "default",
    "use_bplot": true
  }'
```

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "dwg_task_20251106_143000",
    "status": "pending"
  }
}
```

#### 步骤 3: 查询任务状态

```bash
# 查询任务详情
curl http://localhost:8000/api/v1/tasks/{task_id}

# 查询任务步骤
python scripts/query_task_steps.py {task_id}
```

**期望输出：**
```
步骤1: 下载DWG文件 [completed]
步骤2: 执行AutoCAD工作流 [completed]
🆕 步骤3: PDF 识别和转换 [completed]
   - 识别成功: 10/10
   - 重组织完成: 8 个文件
步骤4: 任务完成 [completed]
```

#### 步骤 4: 验证识别结果

```bash
# 查询识别记录
python scripts/query_recent_tasks.py

# 验证图号提取
python scripts/diagnose_reorganize_issue.py {task_id}

# 检查转换目录
ls /path/to/output_convert/
```

**期望结果：**
```
output_convert/
  ├─ PCX-01-01-03-01-1.pdf
  ├─ PCX-01-01-03-01-2.pdf
  └─ ...
```

---

## 🐛 故障排查

### 问题 1: PDF 识别未触发

**现象：** 日志显示 "未获取到输出目录，跳过 PDF 识别"

**原因：**
- `_run_autocad_workflow()` 未返回 output_dir
- workflow 对象缺少 `output_dir` 或 `config.output_dir` 属性

**解决：**
1. 检查 workflow 实现是否设置 `output_dir`
2. 检查配置中是否有 `output_dir` 字段
3. 手动指定输出目录

### 问题 2: 识别失败但主流程继续

**现象：** 步骤3显示 warning 状态

**原因：** 这是预期行为（失败继续策略）

**排查：**
1. 查看详细日志：`tail -f logs/cad_processor_*.log`
2. 检查 MinerU 服务状态
3. 验证 PDF 文件存在性
4. 检查配置是否启用

### 问题 3: 数据库字段缺失

**现象：** 识别成功但转换记录未更新

**原因：** `dwg_drawing_sheets` 表缺少转换字段

**解决：**
```bash
python scripts/migrate_add_conversion_fields.py
```

---

## 📚 相关文档

- [MinerU Service 文档](../src/services/CLAUDE.md#mineruservice)
- [PDF Reorganize Service 文档](../src/services/CLAUDE.md#pdfreorganizeservice)
- [Task Processor API](../api/CLAUDE.md)
- [数据库迁移指南](../scripts/CLAUDE.md)

---

## 📜 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2025-11-06 | 1.0 | 初始版本：完成 PDF 识别集成 |

---

**最后更新：** 2025-11-06
**维护者：** CAD Auto Processor Team
