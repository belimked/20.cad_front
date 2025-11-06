# MinerU 并发优化计划

## 任务上下文

**目标**：将 MinerU PDF 识别从批量请求改为并发单请求，性能提升 3 倍

**当前问题**：
- 批量请求：一次性提交 10 个 PDF 到同一个请求
- MinerU 服务器串行处理，耗时 37.5 秒
- 未充分利用 `vlm-vllm-async-engine` 的并发能力

**目标性能**：
- 10 个 PDF：37.5 秒 → ~12 秒（3 倍加速）
- 参考 shell 脚本并发单请求实现

## 技术方案

**选择方案**：ThreadPoolExecutor（线程池）

**核心特性**：
- 使用 `concurrent.futures.ThreadPoolExecutor`
- 每个 PDF 独立请求 MinerU API
- `max_workers=10`（最多 10 个并发线程）
- 每个线程使用独立数据库会话（线程安全）
- 线程安全的日志输出（`threading.Lock`）

**不采用 asyncio 的原因**：
- 改动量大（需异步化多个方法）
- 需要新依赖（httpx、aiofiles）
- 当前项目 MinerU 服务是同步调用

## 关键改动

### 1. 新增依赖导入
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
```

### 2. 初始化线程锁
```python
self._print_lock = threading.Lock()
```

### 3. 重构 batch_recognize_pdfs()
- 移除批处理循环
- 使用线程池并发提交所有 PDF 任务
- 使用 `as_completed()` 按完成顺序收集结果

### 4. 新增 _process_single_pdf_thread_safe()
- 每个线程创建独立数据库会话（`SessionLocal()`）
- 处理单个 PDF 文件
- 完整的异常处理和清理

### 5. 新增 _thread_safe_print()
- 使用线程锁同步 print() 调用
- 避免多线程日志输出交错

### 6. 更新所有日志输出
- 将 `print()` 替换为 `self._thread_safe_print()`

### 7. 废弃 _process_batch()
- 该方法已被并发逻辑替代

## 文件改动

**主要文件**：`src/services/mineru_service.py`

**代码量**：
- 新增：~80 行
- 修改：~30 行
- 删除：~45 行
- 净增加：~65 行

## 性能目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 10 个 PDF | 37.5 秒 | ≤15 秒 |
| 100 个 PDF | ~375 秒 | ≤150 秒 |

## 测试验证

**成功标准**：
- ✅ 10 个 PDF 总耗时 ≤ 15 秒
- ✅ 所有 PDF 识别成功（10/10）
- ✅ 数据库记录完整无重复
- ✅ 无线程竞争或死锁
- ✅ 日志输出清晰可读

**测试命令**：
```bash
# 运行测试
python scripts/test_mineru_integration.py

# 验证数据
python -c "from src.utils.database import db_session; from src.models.dwg_drawing_sheet import DWGDrawingSheet; session = db_session().__enter__(); sheets = session.query(DWGDrawingSheet).all(); print(f'记录数: {len(sheets)}'); success = sum(1 for s in sheets if s.sheet_number and s.sheet_title); print(f'提取成功率: {success/len(sheets)*100:.1f}%')"
```

## 执行时间

**创建时间**：2025-11-05
**预计完成**：当天
**执行状态**：进行中

---

**注**：本计划由 /zcf:workflow 自动生成
