# CAD 自动化处理系统 - AI 协助开发阶段任务分解

**项目名称：** CAD 文件自动化处理系统
**开发模式：** AI 协助开发
**总工期：** 8.5 天（1.5-2 周）

---

## 📅 Phase 1: 基础框架搭建（1 天）

**目标：** 搭建完整的项目骨架，完成文件下载模块

**总耗时：** 1 天（传统开发：5 天，节省 80%）

---

### Task 1.1: 项目初始化（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词 | 预计时间 | 输出物 |
|---|------|-----------|---------|--------|
| 1 | 创建项目目录结构 | "生成标准 Python 项目目录：src/modules, src/services, src/utils, tests, data, logs, config" | 15 分钟 | 目录结构 |
| 2 | 生成 requirements.txt | "生成依赖列表：requests≥2.28.0, pywin32≥305, watchdog≥3.0.0, loguru≥0.7.0, tenacity≥8.2.0, pytest≥7.0.0, tqdm≥4.65.0" | 10 分钟 | requirements.txt |
| 3 | 创建配置文件 | "生成 config.yaml 配置模板，包含：server, paths, autocad, monitor, upload, logging 配置项" | 20 分钟 | config.yaml |
| 4 | 配置管理模块 | "创建 config.py，使用 PyYAML 加载配置，支持环境变量覆盖，单例模式" | 30 分钟 | config.py |
| 5 | 日志系统配置 | "使用 loguru 配置日志系统：控制台输出+文件轮转（100MB），保留30天" | 30 分钟 | logger.py |
| 6 | Git 仓库初始化 | "生成 .gitignore（Python, IDE, data/, logs/）并初始化 Git" | 15 分钟 | .gitignore |
| 7 | 虚拟环境和依赖安装 | 手动执行：`python -m venv venv && pip install -r requirements.txt` | 30 分钟 | 开发环境 |
| 8 | 项目 README | "生成项目 README.md：项目简介、目录结构、快速开始" | 30 分钟 | README.md |

**交付物：**
- ✅ 完整的项目目录结构
- ✅ 配置文件和依赖管理
- ✅ 可运行的基础框架
- ✅ Git 仓库

**时间检查点：**
- ⏰ 上午 9:00 - 13:00（4 小时）

---

### Task 1.2: 远程文件下载模块（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 下载器类设计 | "创建 CadFileDownloader 类，实现获取文件列表、下载文件、哈希对比" | 45 分钟 | downloader.py 骨架 |
| 2 | HTTP 文件列表获取 | "实现 get_pending_files()，调用 GET /api/cad/files/pending，返回文件列表" | 30 分钟 | 文件列表功能 |
| 3 | 文件哈希对比 | "实现 is_file_new()，计算 MD5 哈希，对比本地和远程文件" | 30 分钟 | 哈希对比逻辑 |
| 4 | 断点续传下载 | "实现 download_file()，支持 Range headers 断点续传，tqdm 进度条" | 60 分钟 | 下载功能 |
| 5 | 异常处理和重试 | "使用 tenacity 实现重试机制（指数退避），处理网络异常" | 30 分钟 | 健壮的下载 |
| 6 | 单元测试生成 | "生成 pytest 测试用例：正常下载、断点续传、哈希校验、异常处理" | 30 分钟 | test_downloader.py |
| 7 | 集成测试 | "创建 Mock API 服务器，测试完整下载流程" | 30 分钟 | 集成测试 |

**AI 提示词完整示例：**
```
"创建 CadFileDownloader 类（src/modules/downloader.py），实现：

核心功能：
1. get_pending_files(): 调用 HTTP API 获取待下载文件列表
2. is_file_new(file_info): 使用 MD5 哈希对比判断是否需要下载
3. download_file(file_info): 下载文件，支持断点续传（Range headers）
4. 使用 tqdm 显示下载进度条

技术要求：
- 使用 requests 库
- 完整的异常处理（网络错误、磁盘满、权限错误）
- tenacity 实现自动重试（最多3次，指数退避）
- 详细的 loguru 日志记录
- 遵循单一职责原则（SOLID）
- 类型注解（typing）

并生成完整的 pytest 单元测试，覆盖：
- 正常下载流程
- 断点续传恢复
- 哈希校验失败
- 网络异常重试
- Mock HTTP 响应
"
```

**交付物：**
- ✅ 完整的文件下载模块
- ✅ 支持断点续传和进度显示
- ✅ 完整的单元测试（覆盖率 > 80%）

**时间检查点：**
- ⏰ 下午 14:00 - 18:00（4 小时）

---

**Phase 1 总结：**
- ✅ 总耗时：8 小时（1 天）
- ✅ 传统开发需要：40 小时（5 天）
- ✅ 节省时间：32 小时（80%）

---
---

## 📅 Phase 2: AutoCAD 自动化实现（2.5 天）

**目标：** 实现 AutoCAD 自动化操作模块

**总耗时：** 2.5 天（传统开发：7 天，节省 64%）

---

### Task 2.1: AutoCAD COM 接口调研（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | COM API 文档总结 | "总结 AutoCAD COM API 关键要点：启动、打开文件、执行命令、保存关闭" | 60 分钟 | 文档笔记 |
| 2 | 基础连接示例 | "生成 Python 代码：使用 pywin32 连接 AutoCAD 应用" | 30 分钟 | connect_cad.py |
| 3 | 文件操作示例 | "生成代码：打开 DWG 文件、关闭文件、保存文件" | 30 分钟 | file_ops.py |
| 4 | 命令执行示例 | "生成代码：执行 AutoCAD 命令字符串、调用 LISP 脚本" | 30 分钟 | command_exec.py |
| 5 | 错误处理研究 | "研究 COM 异常类型，生成常见错误处理代码" | 30 分钟 | error_handling.py |
| 6 | 版本兼容性测试 | "生成兼容性检测脚本，支持 AutoCAD 2018-2024" | 30 分钟 | version_check.py |
| 7 | 示例集成测试 | "测试所有示例代码，确保可运行" | 30 分钟 | 测试报告 |

**AI 提示词完整示例：**
```
"基于 AutoCAD COM API，生成 Python 示例代码集合：

1. connect_to_autocad.py - 连接 AutoCAD
   - 检测 AutoCAD 是否运行
   - 如果未运行，启动 AutoCAD
   - 获取 Application 对象
   - 错误处理

2. file_operations.py - 文件操作
   - 打开 DWG 文件（绝对路径）
   - 激活文档
   - 保存文件
   - 关闭文件
   - 批量操作示例

3. command_execution.py - 命令执行
   - 发送命令字符串到 AutoCAD
   - 执行 LISP 脚本
   - 等待命令完成
   - 获取命令结果

4. error_handling.py - 异常处理
   - COM 异常捕获
   - 常见错误码处理
   - 进程崩溃检测
   - 自动恢复机制

技术要求：
- 使用 win32com.client
- 兼容 AutoCAD 2018-2024
- 完整的类型注解
- 详细的注释说明
- 可独立运行的示例

并生成技术文档，说明：
- API 调用流程
- 注意事项
- 常见问题和解决方案
"
```

**交付物：**
- ✅ AutoCAD COM API 使用文档
- ✅ 可运行的示例代码集
- ✅ 兼容性测试报告

**时间检查点：**
- ⏰ Day 2 上午 9:00 - 13:00（4 小时）

---

### Task 2.2: 自动化操作模块开发（1.5 天 = 12 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 主类设计 | "创建 CadAutomation 类，定义接口和属性" | 30 分钟 | cad_automation.py 骨架 |
| 2 | CAD 连接管理 | "实现 connect()、disconnect()、is_connected()" | 60 分钟 | 连接管理 |
| 3 | 文件操作封装 | "实现 open_file()、close_file()、save_file()" | 60 分钟 | 文件操作 |
| 4 | 操作序列执行器 | "实现 execute_operations()，支持 YAML 配置" | 120 分钟 | 操作执行引擎 |
| 5 | 操作类型实现 | "实现 menu_click、button_click、wait、send_command 操作" | 120 分钟 | 操作类型处理 |
| 6 | YAML 配置设计 | "设计操作序列 YAML 格式，生成配置示例" | 45 分钟 | operations.yaml |
| 7 | 进程监控 | "实现 CAD 进程状态监控、崩溃检测" | 60 分钟 | 进程监控 |
| 8 | 崩溃恢复机制 | "实现自动重启 CAD、恢复操作" | 60 分钟 | 恢复机制 |
| 9 | 日志和调试 | "添加详细的操作日志、调试信息输出" | 30 分钟 | 日志增强 |
| 10 | 单元测试 | "生成 pytest 测试用例" | 60 分钟 | test_cad_automation.py |
| 11 | 集成测试 | "端到端测试：打开CAD→执行操作→保存关闭" | 90 分钟 | 集成测试 |
| 12 | 文档编写 | "生成使用文档和 API 文档" | 45 分钟 | CAD_AUTOMATION.md |

**AI 提示词完整示例：**
```
"创建 CadAutomation 类（src/modules/cad_automation.py），实现 AutoCAD 自动化操作：

核心功能：
1. 连接管理
   - connect(): 连接/启动 AutoCAD
   - disconnect(): 断开连接
   - is_connected(): 检查连接状态
   - 单例模式确保唯一连接

2. 文件操作
   - open_file(file_path): 打开 DWG 文件
   - close_file(save=True): 关闭文件
   - save_file(path=None): 保存文件

3. 操作序列执行
   - execute_operations(operations): 执行 YAML 配置的操作序列
   - 支持操作类型：
     * menu_click: 点击菜单（通过 COM 或坐标）
     * button_click: 点击按钮
     * wait: 等待指定时间
     * send_command: 发送命令字符串
     * wait_for_dialog: 等待对话框出现

4. 进程监控
   - monitor_process(): 监控 CAD 进程状态
   - detect_crash(): 检测崩溃
   - auto_restart(): 自动重启

5. 异常处理
   - COM 异常捕获
   - 超时处理
   - 崩溃恢复

技术要求：
- 使用 pywin32（win32com.client）
- YAML 配置文件驱动（PyYAML）
- 进程监控使用 psutil
- 完整的类型注解
- 详细的 docstring
- 遵循 SOLID 和 DRY 原则
- loguru 日志记录

并生成：
1. operations.yaml 配置示例（包含完整的批处理操作序列）
2. pytest 单元测试（Mock COM 接口）
3. 集成测试脚本
4. API 使用文档
"
```

**YAML 配置示例：**
```yaml
# operations.yaml - CAD 操作序列配置
cad_operations:
  - type: menu_click
    path: "Tools > Batch Plot"
    description: "打开批处理绘图工具"
    timeout: 5

  - type: wait
    seconds: 2
    description: "等待对话框加载"

  - type: button_click
    name: "Auto Detect"
    method: "com"  # com 或 coordinate
    description: "点击自动识别按钮"

  - type: wait_for_dialog
    title: "Frame Detection"
    timeout: 30
    description: "等待图框识别完成"

  - type: button_click
    name: "OK"
    description: "确认操作"

  - type: wait
    seconds: 1

  - type: send_command
    command: "_BATCHPLOT"
    description: "执行批量绘图命令"

  - type: wait_for_completion
    indicator: "file_count"  # 或 "process_idle"
    timeout: 600
    description: "等待处理完成"
```

**交付物：**
- ✅ 完整的 AutoCAD 自动化模块
- ✅ YAML 配置文件和示例
- ✅ 进程监控和崩溃恢复
- ✅ 单元测试和集成测试
- ✅ API 使用文档

**时间检查点：**
- ⏰ Day 2 下午 14:00 - 18:00（4 小时）
- ⏰ Day 3 全天 9:00 - 18:00（8 小时）

---

### Task 2.3: UI 自动化备选方案（0.5 天 = 4 小时，可选）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | UI 自动化类设计 | "创建 UIAutomation 类，使用 pyautogui" | 30 分钟 | ui_automation.py |
| 2 | 屏幕坐标点击 | "实现按坐标点击、双击、右键" | 45 分钟 | 点击功能 |
| 3 | 图像识别定位 | "使用 OpenCV 模板匹配定位按钮" | 90 分钟 | 图像识别 |
| 4 | 分辨率适配 | "实现多分辨率坐标自动转换" | 45 分钟 | 适配逻辑 |
| 5 | 测试验证 | "测试 UI 自动化功能" | 30 分钟 | 测试报告 |

**AI 提示词示例：**
```
"创建 UI 自动化备选方案（ui_automation.py），用于 COM 无法处理的操作：

功能：
1. 屏幕坐标点击（pyautogui）
2. 图像识别定位（OpenCV 模板匹配）
3. 键盘输入模拟
4. 分辨率适配（1920x1080 → 其他分辨率）

技术要求：
- pyautogui 实现鼠标键盘操作
- OpenCV + Pillow 实现图像识别
- 支持相对坐标和绝对坐标
- 失败重试机制
- 截图保存用于调试
"
```

**交付物：**
- ✅ UI 自动化备选模块
- ✅ 图像识别功能
- ✅ 测试脚本

**时间检查点：**
- ⏰ Day 4 上午 9:00 - 13:00（4 小时，如需要）

---

**Phase 2 总结：**
- ✅ 总耗时：20 小时（2.5 天）
- ✅ 传统开发需要：56 小时（7 天）
- ✅ 节省时间：36 小时（64%）

---
---

## 📅 Phase 3: 文件监控与任务管理（1.5 天）

**目标：** 实现文件监控模块和任务管理服务

**总耗时：** 1.5 天（传统开发：4 天，节省 62%）

---

### Task 3.1: 文件监控模块（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 监控类设计 | "创建 FileMonitor 类，使用 watchdog" | 30 分钟 | file_monitor.py 骨架 |
| 2 | 实时监控实现 | "实现文件系统事件监听（创建、修改、删除）" | 60 分钟 | 监控功能 |
| 3 | 文件数量统计 | "实现文件计数、类型分类统计" | 30 分钟 | 统计功能 |
| 4 | 稳定性检测 | "实现文件稳定检测（30秒无变化判断完成）" | 45 分钟 | 稳定检测 |
| 5 | 进程状态联动 | "与 CAD 进程状态联动判断完成" | 45 分钟 | 进程联动 |
| 6 | 超时机制 | "实现可配置的超时检测" | 30 分钟 | 超时处理 |
| 7 | 单元测试 | "生成 pytest 测试用例" | 30 分钟 | test_file_monitor.py |

**AI 提示词完整示例：**
```
"创建 FileMonitor 类（src/modules/file_monitor.py），实现文件监控功能：

核心功能：
1. start_monitoring(watch_dir): 开始监控指定目录
2. stop_monitoring(): 停止监控
3. is_task_complete(): 判断任务是否完成
4. wait_for_completion(timeout): 等待任务完成（阻塞）
5. get_file_stats(): 获取文件统计信息

完成条件判断（多条件 AND）：
- 条件1：文件数量达到预期（如果指定了 expected_count）
- 条件2：最后一个文件写入后，30秒内无新变化
- 条件3：所有文件无锁定（可读写）
- 条件4：CAD 进程状态为空闲（可选）

技术要求：
- 使用 watchdog 监控文件系统
- 使用 psutil 检测进程状态
- 线程安全（threading.Event）
- 超时处理（可配置）
- 详细的日志记录
- 支持多种文件类型过滤（*.pdf, *.dwg）

并生成：
1. pytest 单元测试（Mock 文件系统事件）
2. 集成测试（实际文件操作）
3. 使用示例代码
"
```

**交付物：**
- ✅ 文件监控模块
- ✅ 多条件完成判断
- ✅ 单元测试和集成测试

**时间检查点：**
- ⏰ Day 4 下午 14:00 - 18:00（4 小时）

---

### Task 3.2: 任务管理服务（1 天 = 8 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 服务类设计 | "创建 TaskService 类，定义任务状态机" | 30 分钟 | task_service.py 骨架 |
| 2 | 状态机实现 | "实现状态转换：PENDING→DOWNLOADING→PROCESSING→UPLOADING→COMPLETED" | 90 分钟 | 状态机 |
| 3 | 任务队列 | "实现优先级队列（queue.PriorityQueue）" | 60 分钟 | 队列管理 |
| 4 | SQLite 持久化 | "实现任务数据库存储（SQLite）" | 90 分钟 | 数据持久化 |
| 5 | 失败重试机制 | "实现指数退避重试（最多3次）" | 60 分钟 | 重试逻辑 |
| 6 | 任务并发控制 | "实现最大并发数控制（ThreadPoolExecutor）" | 60 分钟 | 并发控制 |
| 7 | API 接口 | "定义任务 CRUD 接口（创建、查询、更新、删除）" | 45 分钟 | API 接口 |
| 8 | 单元测试 | "生成 pytest 测试用例" | 60 分钟 | test_task_service.py |
| 9 | 集成测试 | "测试完整任务生命周期" | 45 分钟 | 集成测试 |

**AI 提示词完整示例：**
```
"创建 TaskService 类（src/services/task_service.py），实现任务管理功能：

核心功能：
1. 任务状态机
   - 状态：PENDING, DOWNLOADING, PROCESSING, UPLOADING, COMPLETED, FAILED
   - 状态转换规则和验证
   - 状态历史记录

2. 任务队列管理
   - create_task(task_info): 创建任务
   - get_next_task(): 获取下一个待处理任务
   - update_task_status(task_id, status): 更新状态
   - get_task(task_id): 查询任务
   - list_tasks(status=None): 列出任务

3. 数据持久化（SQLite）
   - 任务表结构：id, file_url, status, priority, retry_count, created_at, updated_at
   - 自动创建数据库和表
   - 事务支持

4. 失败重试机制
   - 失败任务自动重试（最多3次）
   - 指数退避延迟（1min, 5min, 15min）
   - 超过次数标记为 FAILED

5. 并发控制
   - 最大并发任务数限制（可配置，默认3）
   - ThreadPoolExecutor 实现
   - 优雅关闭

技术要求：
- SQLite3 数据库
- 线程安全（threading.Lock）
- 类型注解和 docstring
- 单例模式
- 遵循单一职责原则
- 详细的日志记录

并生成：
1. 数据库 Schema（SQL）
2. pytest 单元测试
3. 使用示例
4. API 文档
"
```

**数据库 Schema：**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_uuid TEXT UNIQUE NOT NULL,
    file_url TEXT NOT NULL,
    file_name TEXT,
    local_path TEXT,
    status TEXT NOT NULL,  -- PENDING, DOWNLOADING, PROCESSING, UPLOADING, COMPLETED, FAILED
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_status ON tasks(status);
CREATE INDEX idx_priority ON tasks(priority DESC);
CREATE INDEX idx_created_at ON tasks(created_at);
```

**交付物：**
- ✅ 任务管理服务
- ✅ 状态机和队列
- ✅ SQLite 持久化
- ✅ 失败重试机制
- ✅ 单元测试和集成测试
- ✅ 数据库设计文档

**时间检查点：**
- ⏰ Day 5 全天 9:00 - 18:00（8 小时）

---

**Phase 3 总结：**
- ✅ 总耗时：12 小时（1.5 天）
- ✅ 传统开发需要：32 小时（4 天）
- ✅ 节省时间：20 小时（62%）

---
---

## 📅 Phase 4: 结果上传与集成（1.5 天）

**目标：** 实现结果上传模块和主流程集成

**总耗时：** 1.5 天（传统开发：3 天，节省 50%）

---

### Task 4.1: 结果上传模块（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 上传类设计 | "创建 ResultUploader 类" | 30 分钟 | uploader.py 骨架 |
| 2 | 文件打包功能 | "实现 ZIP 压缩（zipfile），排除临时文件" | 45 分钟 | 打包功能 |
| 3 | 分片上传实现 | "实现大文件分片上传（5MB 分片）" | 90 分钟 | 分片上传 |
| 4 | 上传进度监控 | "使用 tqdm 显示上传进度" | 30 分钟 | 进度显示 |
| 5 | 重试机制 | "使用 tenacity 实现上传重试" | 30 分钟 | 重试逻辑 |
| 6 | API 回调 | "实现任务完成/失败回调通知" | 30 分钟 | 回调功能 |
| 7 | 单元测试 | "生成 pytest 测试用例" | 30 分钟 | test_uploader.py |

**AI 提示词完整示例：**
```
"创建 ResultUploader 类（src/modules/uploader.py），实现结果上传功能：

核心功能：
1. pack_results(output_dir, exclude_patterns): 打包输出文件为 ZIP
   - 排除临时文件（*.tmp, *.lock）
   - 保持目录结构
   - 压缩级别可配置

2. upload_file(file_path, task_id): 上传文件到服务器
   - 支持大文件分片上传（5MB 分片）
   - 每个分片独立上传，支持失败重传
   - tqdm 进度条显示总进度
   - 上传完成后校验（MD5）

3. notify_completion(task_id, status, metadata): 通知服务器任务完成
   - POST /api/cad/tasks/{task_id}/complete
   - 包含任务元数据（耗时、文件数、大小）

4. notify_failure(task_id, error_message): 通知任务失败
   - POST /api/cad/tasks/{task_id}/fail
   - 包含错误信息和堆栈跟踪

5. cleanup_local_files(task_id, keep_backup): 清理本地文件
   - 可选保留备份（默认保留）
   - 删除临时文件

技术要求：
- zipfile 打包
- requests 上传（支持 multipart）
- tenacity 重试（最多3次）
- tqdm 进度条
- 详细的日志记录
- 遵循单一职责原则

并生成：
1. pytest 单元测试（Mock HTTP 上传）
2. 分片上传集成测试
3. 使用示例
"
```

**交付物：**
- ✅ 结果上传模块
- ✅ 文件打包和分片上传
- ✅ 上传进度显示
- ✅ API 回调通知
- ✅ 单元测试

**时间检查点：**
- ⏰ Day 6 上午 9:00 - 13:00（4 小时）

---

### Task 4.2: 主流程集成（1 天 = 8 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 主控制器设计 | "创建 MainController 类，编排完整工作流" | 45 分钟 | main.py 骨架 |
| 2 | 工作流实现 | "实现：下载→处理→监控→上传 完整流程" | 120 分钟 | 工作流引擎 |
| 3 | 全局异常处理 | "实现顶层异常捕获和错误恢复" | 60 分钟 | 异常处理 |
| 4 | 命令行接口 | "使用 argparse 实现 CLI 参数" | 45 分钟 | CLI 接口 |
| 5 | 多任务并发 | "实现多任务并发处理（ThreadPoolExecutor）" | 90 分钟 | 并发处理 |
| 6 | 日志系统配置 | "配置 loguru 日志系统（控制台+文件）" | 30 分钟 | 日志配置 |
| 7 | 优雅退出 | "实现 Ctrl+C 信号处理和优雅关闭" | 30 分钟 | 退出处理 |
| 8 | 集成测试 | "端到端测试完整流程" | 90 分钟 | 集成测试 |
| 9 | 文档编写 | "生成用户手册和部署文档" | 60 分钟 | 文档 |

**AI 提示词完整示例：**
```
"创建主程序（src/main.py），整合所有模块实现完整工作流：

主工作流：
1. 初始化
   - 加载配置
   - 初始化日志系统
   - 连接数据库
   - 验证 AutoCAD 环境

2. 任务循环（无限循环或单次运行）
   - 从服务器获取待处理文件列表
   - 为每个文件创建任务
   - 并发执行任务（最多 N 个同时）

3. 单个任务流程
   a. 下载文件（CadFileDownloader）
   b. 打开 CAD 并执行操作（CadAutomation）
   c. 监控输出文件（FileMonitor）
   d. 打包并上传结果（ResultUploader）
   e. 更新任务状态（TaskService）

4. 异常处理
   - 顶层 try-except 捕获所有异常
   - 网络异常、CAD 崩溃、磁盘满等
   - 失败任务重新入队
   - 详细的错误日志

5. 优雅退出
   - 捕获 SIGINT (Ctrl+C) 和 SIGTERM
   - 等待当前任务完成
   - 保存状态到数据库
   - 关闭所有资源

命令行接口（argparse）：
- --config: 配置文件路径（默认 config.yaml）
- --mode: 运行模式（daemon/once）
- --tasks: 任务数量限制
- --log-level: 日志级别（DEBUG/INFO/WARNING/ERROR）
- --dry-run: 干运行模式（不实际执行）

技术要求：
- 使用所有已实现的模块
- ThreadPoolExecutor 并发控制
- signal 信号处理
- argparse CLI
- loguru 日志
- 清晰的控制台输出（Rich 或 tqdm）
- 遵循 KISS 原则

并生成：
1. 端到端集成测试
2. 用户使用手册（README.md）
3. 部署文档（DEPLOYMENT.md）
4. 示例配置文件
"
```

**CLI 使用示例：**
```bash
# 守护进程模式（持续运行）
python src/main.py --mode daemon --config config.yaml

# 单次运行模式（处理一批任务后退出）
python src/main.py --mode once --tasks 10

# 调试模式
python src/main.py --log-level DEBUG --dry-run

# 自定义配置
python src/main.py --config production.yaml --tasks 5
```

**交付物：**
- ✅ 主控制器和完整工作流
- ✅ 命令行接口
- ✅ 多任务并发处理
- ✅ 全局异常处理
- ✅ 优雅退出机制
- ✅ 端到端集成测试
- ✅ 用户手册和部署文档

**时间检查点：**
- ⏰ Day 6 下午 14:00 - 18:00（4 小时）
- ⏰ Day 7 上午 9:00 - 13:00（4 小时）

---

**Phase 4 总结：**
- ✅ 总耗时：12 小时（1.5 天）
- ✅ 传统开发需要：24 小时（3 天）
- ✅ 节省时间：12 小时（50%）

---
---

## 📅 Phase 5: 测试与优化（2 天）

**目标：** 全面测试、性能优化、文档完善

**总耗时：** 2 天（传统开发：5 天，节省 60%）

---

### Task 5.1: 集成测试（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 端到端测试 | "生成完整流程测试脚本" | 60 分钟 | test_e2e.py |
| 2 | 异常场景测试 | "测试网络中断、CAD 崩溃、磁盘满" | 90 分钟 | test_exceptions.py |
| 3 | 性能测试 | "生成批量文件处理性能测试（100个文件）" | 60 分钟 | test_performance.py |
| 4 | Mock API 服务器 | "创建 Flask Mock 服务器模拟远程 API" | 30 分钟 | mock_server.py |

**AI 提示词完整示例：**
```
"生成完整的测试套件（tests/ 目录）：

1. test_e2e.py - 端到端测试
   - 正常流程：下载→处理→上传→完成
   - 使用真实 CAD 文件（小样本）
   - 验证输出文件正确性
   - 验证任务状态更新

2. test_exceptions.py - 异常场景测试
   - 网络中断恢复测试（Mock 网络错误）
   - CAD 崩溃恢复测试（Kill 进程）
   - 磁盘空间不足测试
   - 无效文件处理测试
   - 并发任务冲突测试

3. test_performance.py - 性能测试
   - 批量处理 100 个文件
   - 测量总耗时、平均耗时
   - 测量内存占用峰值
   - 测量 CPU 使用率
   - 生成性能报告

4. mock_server.py - Mock API 服务器
   - Flask 实现
   - 模拟文件列表接口
   - 模拟文件下载接口
   - 模拟任务回调接口
   - 支持错误注入（500, 404, timeout）

技术要求：
- pytest + pytest-mock + pytest-cov
- Flask（Mock 服务器）
- psutil（性能监控）
- 生成 HTML 测试报告
- 代码覆盖率报告（>80%）

并生成：
1. pytest.ini 配置
2. 测试运行脚本（run_tests.sh）
3. 测试报告模板
"
```

**交付物：**
- ✅ 端到端测试套件
- ✅ 异常场景测试
- ✅ 性能测试
- ✅ Mock API 服务器
- ✅ 测试报告

**时间检查点：**
- ⏰ Day 7 下午 14:00 - 18:00（4 小时）

---

### Task 5.2: 性能优化（1 天 = 8 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | 性能分析 | "使用 cProfile 分析代码，找出瓶颈" | 60 分钟 | 性能报告 |
| 2 | 下载优化 | "实现多线程并发下载（ThreadPoolExecutor）" | 90 分钟 | 优化代码 |
| 3 | 内存优化 | "流式处理大文件，避免全部加载到内存" | 90 分钟 | 优化代码 |
| 4 | 日志优化 | "实现异步日志写入（QueueHandler）" | 60 分钟 | 优化代码 |
| 5 | 数据库优化 | "添加索引、批量操作优化" | 45 分钟 | 优化 SQL |
| 6 | 监控仪表盘 | "生成性能监控指标（处理速度、内存、CPU）" | 75 分钟 | 监控模块 |
| 7 | 基准测试 | "对比优化前后的性能数据" | 60 分钟 | 基准报告 |

**AI 提示词完整示例：**
```
"分析当前代码并提供性能优化方案：

1. 下载模块优化
   - 改为多线程并发下载（ThreadPoolExecutor，最多5个并发）
   - 每个线程独立下载一个文件
   - 共享进度条更新
   - 提供具体代码修改

2. 内存使用优化
   - 文件打包使用流式处理（不一次性加载）
   - 大文件分片读取（chunk_size=8192）
   - 及时释放不用的对象
   - 提供代码示例

3. 日志系统优化
   - 使用 QueueHandler 异步写入日志
   - 避免日志写入阻塞主线程
   - 日志轮转优化
   - 提供配置代码

4. 数据库优化
   - 添加必要的索引（status, created_at）
   - 批量插入/更新操作
   - 连接池管理
   - 提供 SQL 优化建议

5. 性能监控
   - 实时监控指标：
     * 处理速度（文件/小时）
     * 内存占用（当前/峰值）
     * CPU 使用率
     * 磁盘 I/O
   - 生成监控模块代码

对每个优化点：
- 提供具体代码修改
- 说明预期提升幅度
- 给出 before/after 对比示例
"
```

**性能优化目标：**
- 📈 下载速度提升 **3-5 倍**（多线程）
- 📉 内存占用降低 **50%**（流式处理）
- ⚡ 日志性能提升 **10 倍**（异步写入）
- 🚀 整体吞吐量提升 **2-3 倍**

**交付物：**
- ✅ 性能分析报告
- ✅ 优化后的代码
- ✅ 性能监控模块
- ✅ 优化前后对比报告

**时间检查点：**
- ⏰ Day 8 全天 9:00 - 18:00（8 小时）

---

### Task 5.3: 文档编写（0.5 天 = 4 小时）

#### 📋 具体任务清单

| # | 任务 | AI 提示词核心 | 预计时间 | 输出物 |
|---|------|--------------|---------|--------|
| 1 | README.md | "生成项目主文档：介绍、快速开始、配置" | 60 分钟 | README.md |
| 2 | API.md | "生成所有类和函数的 API 文档" | 60 分钟 | API.md |
| 3 | DEPLOYMENT.md | "生成部署指南：环境要求、安装步骤" | 45 分钟 | DEPLOYMENT.md |
| 4 | TROUBLESHOOTING.md | "生成故障排查手册：常见问题和解决方案" | 45 分钟 | TROUBLESHOOTING.md |
| 5 | CHANGELOG.md | "生成版本更新日志" | 30 分钟 | CHANGELOG.md |

**AI 提示词完整示例：**
```
"基于代码库生成完整的项目文档：

1. README.md
   - 项目简介和特性
   - 快速开始（5分钟上手）
   - 配置文件说明
   - 使用示例
   - 架构图
   - 贡献指南
   - 许可证

2. API.md
   - 所有类的文档（自动提取 docstring）
   - 方法签名和参数说明
   - 返回值和异常
   - 使用示例
   - 按模块组织

3. DEPLOYMENT.md
   - 环境要求详细说明
   - Windows 安装步骤
   - AutoCAD 配置指南
   - 配置文件详解
   - 生产环境部署建议
   - Docker 部署（可选）
   - 常见安装问题

4. TROUBLESHOOTING.md
   - 错误代码对照表
   - 常见问题 FAQ
   - 日志分析指南
   - 性能调优建议
   - 联系支持

5. CHANGELOG.md
   - 版本历史
   - 新功能、改进、Bug 修复
   - 破坏性变更说明

格式要求：
- 清晰的 Markdown 格式
- 包含代码示例
- 包含截图（如适用）
- 目录导航
- 专业排版
"
```

**交付物：**
- ✅ README.md（项目主文档）
- ✅ API.md（API 文档）
- ✅ DEPLOYMENT.md（部署指南）
- ✅ TROUBLESHOOTING.md（故障排查）
- ✅ CHANGELOG.md（更新日志）

**时间检查点：**
- ⏰ Day 9 上午 9:00 - 13:00（4 小时）

---

**Phase 5 总结：**
- ✅ 总耗时：16 小时（2 天）
- ✅ 传统开发需要：40 小时（5 天）
- ✅ 节省时间：24 小时（60%）

---
---

## 📊 总体时间汇总

| 阶段 | 内容 | 传统开发 | AI 协助 | 节省 | 效率提升 |
|------|------|---------|---------|------|---------|
| **Phase 1** | 基础框架 + 下载模块 | 40h (5天) | 8h (1天) | 32h | ↓ 80% |
| **Phase 2** | AutoCAD 自动化 | 56h (7天) | 20h (2.5天) | 36h | ↓ 64% |
| **Phase 3** | 监控 + 任务管理 | 32h (4天) | 12h (1.5天) | 20h | ↓ 62% |
| **Phase 4** | 上传 + 集成 | 24h (3天) | 12h (1.5天) | 12h | ↓ 50% |
| **Phase 5** | 测试 + 优化 + 文档 | 40h (5天) | 16h (2天) | 24h | ↓ 60% |
| **总计** | **完整系统** | **192h (24天)** | **68h (8.5天)** | **124h** | **↓ 64.6%** |

---

## 🎯 每日工作安排建议

### **Day 1**（8小时）
- ✅ 上午：项目初始化（4h）
- ✅ 下午：文件下载模块（4h）

### **Day 2**（8小时）
- ✅ 上午：AutoCAD COM 接口调研（4h）
- ✅ 下午：开始自动化模块开发（4h）

### **Day 3**（8小时）
- ✅ 全天：继续 AutoCAD 自动化模块（8h）

### **Day 4**（8小时）
- ✅ 上午：UI 自动化备选方案（4h，可选）
- ✅ 下午：文件监控模块（4h）

### **Day 5**（8小时）
- ✅ 全天：任务管理服务（8h）

### **Day 6**（8小时）
- ✅ 上午：结果上传模块（4h）
- ✅ 下午：开始主流程集成（4h）

### **Day 7**（8小时）
- ✅ 上午：完成主流程集成（4h）
- ✅ 下午：集成测试（4h）

### **Day 8**（8小时）
- ✅ 全天：性能优化（8h）

### **Day 9**（4小时，半天）
- ✅ 上午：文档编写（4h）

---

## ✅ 关键检查点（里程碑）

| 时间点 | 里程碑 | 验收标准 |
|--------|--------|---------|
| **Day 1 结束** | 基础框架完成 | ✅ 可运行的项目骨架<br>✅ 下载模块通过单元测试 |
| **Day 3 结束** | CAD 自动化完成 | ✅ 能打开 CAD 文件<br>✅ 能执行操作序列<br>✅ 有崩溃恢复机制 |
| **Day 5 结束** | 监控和任务管理完成 | ✅ 文件监控正常工作<br>✅ 任务状态机正确运行<br>✅ 数据库持久化正常 |
| **Day 7 结束** | 系统集成完成 | ✅ 端到端流程可运行<br>✅ 集成测试通过<br>✅ 基础文档完成 |
| **Day 9 结束** | 项目交付 | ✅ 所有测试通过<br>✅ 性能达标<br>✅ 完整文档 |

---

## 🚀 立即开始？

现在你有了完整的 **68 小时（8.5 天）** 详细任务分解！

**下一步选择：**

1. **立即开始 Day 1** - 我可以帮你生成项目初始化的所有代码
2. **查看某个任务的详细实现** - 选择任何一个任务，我生成完整代码
3. **调整计划** - 修改时间安排或任务内容
4. **生成 AI 提示词库** - 把所有提示词整理成一个文档，方便复制使用

**你想从哪里开始？** 🎯
