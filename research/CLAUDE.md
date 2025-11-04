# 研究模块文档 (research)

[根目录](../CLAUDE.md) > **research**

## 模块概述

**研究模块 (research)** 是 AutoCAD COM API 探索和实验代码的集合，包含了从基础 COM 连接到完整工作流的演进过程。这是项目的技术研发核心，所有生产代码都源于此模块的实验成果。

**职责：**
- AutoCAD COM API 技术探索
- 工作流原型开发和验证
- OCR 识别方案测试
- UI 自动化方案研究
- 最佳实践提炼

**重要性：** ⭐⭐⭐⭐⭐ 理解此模块是掌握整个项目的关键

## 目录结构

```
research/
└── autocad_com_api/              # AutoCAD COM API 研究
    ├── README.md                 # 研究模块说明
    ├── _archived/                # 已归档的历史实验代码
    │   ├── 1_connect_to_autocad.py
    │   ├── 2_file_operations.py
    │   ├── 3_command_execution.py
    │   ├── 4_error_handling.py
    │   ├── 5_version_check.py
    │   ├── 6_autocad_workflow.py
    │   ├── 6b_alternative_workflow.py
    │   ├── 7_menu_automation.py
    │   ├── 8_complete_example.py
    │   └── WORKFLOW_GUIDE.md
    ├── 9_configurable_workflow.py    # 可配置工作流 ✅
    ├── 10_bplot_workflow.py          # BPLOT 工作流 ✅
    ├── 11_bplot_auto_workflow.py     # BPLOT 自动化 ✅
    └── enhanced_workflow.py          # 增强型工作流 ⭐
```

## 工作流演进历程

### 第一阶段：基础探索（已归档）

**1_connect_to_autocad.py** - COM 连接建立
- 探索 `win32com.client.Dispatch()` 基础用法
- 处理连接失败和超时
- 实现自动启动 AutoCAD

**2_file_operations.py** - 文件操作
- 打开/关闭 DWG 文件
- 处理文件路径（双引号、正斜杠）
- 文件锁定和权限问题

**3_command_execution.py** - 命令执行
- `SendCommand()` 方法使用
- 命令序列执行
- 等待命令完成

**4_error_handling.py** - 错误处理
- COM 异常捕获
- 进程清理
- 失败恢复

**5_version_check.py** - 版本检测
- 检测 AutoCAD 版本
- 兼容性处理

**6_autocad_workflow.py** - 基础工作流
- 完整的打开→操作→关闭流程
- 固定参数和硬编码

**6b_alternative_workflow.py** - 替代方案
- 不同的工作流实现思路

**7_menu_automation.py** - 菜单自动化
- pyautogui 点击菜单
- 坐标定位
- OCR 识别菜单文本

**8_complete_example.py** - 完整示例
- 集成所有功能的完整示例

### 第二阶段：配置驱动（生产代码）

#### 9_configurable_workflow.py - 可配置工作流

**特性：**
- 从数据库读取配置（`autocad_config` 表）
- 支持 JSON 格式的操作序列
- 操作类型：`command`、`menu`、`wait`

**配置格式：**
```json
{
  "menu_operations": [
    {
      "type": "command",
      "command": "ZOOM",
      "arguments": ["E"],
      "wait_time": 1.0
    },
    {
      "type": "menu",
      "text": "打印",
      "region": [0, 0, 1920, 200],
      "timeout": 10
    }
  ]
}
```

**使用场景：**
- 通用 AutoCAD 自动化任务
- 需要灵活配置的场景

**运行方式：**
```bash
python research/autocad_com_api/9_configurable_workflow.py
```

### 第三阶段：BPLOT 专用工作流

#### 10_bplot_workflow.py - BPLOT 工作流

**特性：**
- 专门用于批量打印（Batch Plot）
- 集成 OCR 识别菜单和按钮
- 自动图框识别
- PDF 生成

**核心流程：**
1. 打开 DWG 文件
2. 执行 BPLOT 命令（批量打印）
3. OCR 识别弹出的对话框
4. 自动点击"确定"按钮
5. 等待 PDF 生成
6. 关闭 AutoCAD

**关键技术：**
- UMI-OCR API 调用
- 图像预处理优化
- 动态坐标计算

#### 11_bplot_auto_workflow.py - BPLOT 自动化

**改进：**
- 完全自动化，无需手动干预
- 更智能的 OCR 识别策略
- 多重失败重试机制
- 详细的日志记录

**运行方式：**
```bash
python research/autocad_com_api/11_bplot_auto_workflow.py
```

### 第四阶段：增强型工作流（最终版本）

#### enhanced_workflow.py - 增强型工作流 ⭐

**最完整的实现，集大成之作！**

**核心特性：**

1. **三阶段操作**
   - 前置操作（Pre-operations）
   - 主流程（Main Workflow）
   - 后置操作（Post-operations）

2. **丰富的操作类型**
   - `command` - AutoCAD 命令
   - `menu` - OCR 菜单点击
   - `input` - 键盘输入
   - `screenshot_extract` - OCR 信息提取
   - `system_command` - 系统命令
   - `directory_cleanup` - 目录清理
   - `file_monitor` - 文件监控

3. **变量系统**
   - 保存 OCR 提取的值到变量
   - 在后续操作中引用变量（`${变量名}`）

4. **数据库集成**
   - 读取配置：`autocad_config` 表
   - 记录日志：`dwg_task_steps` 表
   - OCR 日志：`ocr_recognition_logs` 表

**配置格式示例：**
```json
{
  "前置操作": [
    {
      "type": "directory_cleanup",
      "path": "C:\\output",
      "description": "清理输出目录"
    }
  ],
  "主流程": [
    {
      "type": "command",
      "command": "_OPEN",
      "description": "打开文件"
    },
    {
      "type": "menu",
      "text": "批量打印",
      "region": [0, 0, 1920, 200],
      "click_offset": [0, 0],
      "timeout": 10,
      "description": "点击批量打印菜单"
    },
    {
      "type": "screenshot_extract",
      "region": [100, 200, 300, 250],
      "extract_pattern": "图纸数量:\\s*(\\d+)",
      "save_to_var": "sheet_count",
      "description": "提取图纸数量"
    }
  ],
  "后置操作": [
    {
      "type": "file_monitor",
      "watch_directory": "C:\\output",
      "file_pattern": "*.pdf",
      "expected_count": "${sheet_count}",
      "timeout": 600,
      "check_interval": 5,
      "description": "监控 PDF 生成"
    }
  ]
}
```

**类设计：**
```python
class EnhancedWorkflow:
    def __init__(self, config, task_id, task_service):
        self.acad = None
        self.config = config
        self.variables = {}  # 变量存储
        self.task_id = task_id
        self.task_service = task_service

    def execute(self, dwg_file_path):
        """执行完整工作流"""
        # 1. 前置操作
        self._execute_operations(self.config.get("前置操作", []))

        # 2. 主流程
        self._connect_to_autocad()
        self._open_file(dwg_file_path)
        self._execute_operations(self.config.get("主流程", []))
        self._close_autocad()

        # 3. 后置操作
        self._execute_operations(self.config.get("后置操作", []))

    def _execute_operations(self, operations):
        """执行操作序列"""
        for op in operations:
            op_type = op.get("type")
            if op_type == "command":
                self._execute_command(op)
            elif op_type == "menu":
                self._execute_menu_click(op)
            elif op_type == "screenshot_extract":
                self._execute_screenshot_extract(op)
            # ... 其他操作类型
```

**使用方式：**
```python
from research.autocad_com_api.enhanced_workflow import EnhancedWorkflow
from src.services.autocad_config_service import AutoCADConfigService
from src.services.task_service import TaskService

# 1. 获取配置
config_service = AutoCADConfigService()
config = config_service.get_config_by_name("bplot_enhanced")

# 2. 创建工作流
workflow = EnhancedWorkflow(
    config=config,
    task_id="task_123",
    task_service=TaskService()
)

# 3. 执行
workflow.execute(dwg_file_path="C:/test.dwg")
```

## OCR 识别技术

### UMI-OCR API 集成

**服务地址：** `http://127.0.0.1:1224/api/ocr`

**调用流程：**
1. 截取屏幕区域（`PIL.ImageGrab`）
2. 图像预处理（`src.utils.image_processing`）
3. 调用 UMI-OCR API
4. 解析识别结果
5. 计算点击坐标

**代码示例：**
```python
import requests
from PIL import ImageGrab

def ocr_and_click(text, region):
    # 1. 截图
    screenshot = ImageGrab.grab(bbox=region)
    screenshot.save("temp.png")

    # 2. OCR 识别
    with open("temp.png", "rb") as f:
        response = requests.post(
            "http://127.0.0.1:1224/api/ocr",
            files={"image": f}
        )
    result = response.json()

    # 3. 查找匹配文本
    for item in result["data"]:
        if text in item["text"]:
            # 4. 计算点击坐标
            x = item["box"][0][0]
            y = item["box"][0][1]
            pyautogui.click(x, y)
            return True

    return False
```

### 图像预处理策略

**预处理方法：**
- 二值化（Adaptive Thresholding）
- 去噪（Bilateral Filter）
- 对比度增强（CLAHE）
- 锐化（Sharpening）

**配置存储：**
- 表：`dict_preprocessing`
- 字段：`dict_key`, `dict_value` (JSON)

**优化建议：**
- 针对不同 UI 场景使用不同预处理方法
- 查看 OCR 日志调优参数
- 使用 `scripts/check_ocr_logs.py` 分析识别率

## 关键技术要点

### 1. COM 对象生命周期管理

```python
import win32com.client

try:
    acad = win32com.client.Dispatch("AutoCAD.Application")
    acad.Visible = True
    # ... 操作
finally:
    # 释放 COM 对象
    acad = None
```

### 2. 窗口焦点控制

```python
import pyautogui

# 确保 AutoCAD 窗口在前台
acad.WindowState = 1  # acMaximized
pyautogui.click(100, 100)  # 点击窗口获得焦点
```

### 3. 命令执行同步

```python
# 发送命令并等待完成
acad.ActiveDocument.SendCommand("ZOOM E\n")
time.sleep(2)  # 等待命令执行

# 或使用更复杂的等待逻辑
while acad.GetAcadState().IsBusy:
    time.sleep(0.1)
```

### 4. 路径处理

```python
# 始终使用双引号和正斜杠
dwg_path = "C:/Program Files/AutoCAD/drawing.dwg"
acad.ActiveDocument.Open(f'"{dwg_path}"')
```

### 5. 异常处理

```python
try:
    acad.ActiveDocument.SendCommand(command)
except pywintypes.com_error as e:
    logger.error(f"COM error: {e}")
    # 清理 AutoCAD 进程
    kill_autocad_process()
```

## 测试和验证

### 单个工作流测试

```bash
# 测试可配置工作流
python research/autocad_com_api/9_configurable_workflow.py

# 测试 BPLOT 工作流
python research/autocad_com_api/10_bplot_workflow.py

# 测试增强型工作流
python research/autocad_com_api/enhanced_workflow.py
```

### 验证脚本

```bash
# 检查 BPLOT 依赖
python scripts/check_bplot_dependencies.py

# 验证工作流配置
python scripts/verify_workflow_config.py

# 验证增强型工作流
python scripts/verify_bplot_enhanced.py
```

### OCR 识别测试

```bash
# 查看 OCR 日志
python scripts/check_ocr_logs.py

# 测试多图像 OCR
python _archived/scripts_testing/test_multi_image_ocr.py

# 测试 UMI-OCR API
python _archived/scripts_testing/test_umi_ocr_api.py
```

## 常见问题和解决方案

### 1. AutoCAD 启动失败

**问题：** `pywintypes.com_error: (-2147221005, '无效的类字符串', None, None)`

**原因：** AutoCAD 未正确注册或未安装

**解决：**
1. 确认 AutoCAD 已安装
2. 以管理员权限运行脚本
3. 检查 AutoCAD 版本兼容性

### 2. OCR 识别失败

**问题：** 无法识别菜单文本

**原因：** 图像预处理不当或 UI 变化

**解决：**
1. 调整截图区域 (`region` 参数)
2. 尝试不同的预处理方法
3. 增加识别超时时间
4. 查看保存的截图文件

### 3. 文件监控超时

**问题：** `file_monitor` 操作超时

**原因：** AutoCAD 处理时间超过预期

**解决：**
1. 增加 `timeout` 参数
2. 检查 `expected_count` 是否正确
3. 验证 `file_pattern` 匹配规则
4. 查看 AutoCAD 是否实际生成文件

### 4. 菜单点击位置不准

**问题：** OCR 识别正确但点击位置错误

**原因：** 坐标偏移计算有误

**解决：**
1. 调整 `click_offset` 参数
2. 使用 `pyautogui.position()` 获取实际坐标
3. 考虑不同分辨率的影响

## 最佳实践

1. **使用增强型工作流**
   - 最完整、最稳定的实现
   - 支持所有操作类型
   - 有完整的日志记录

2. **配置外部化**
   - 所有参数存储在数据库
   - 避免硬编码
   - 支持多套配置方案

3. **详细日志记录**
   - 记录每个操作步骤
   - 保存 OCR 识别结果
   - 便于问题排查

4. **容错和重试**
   - OCR 识别失败重试
   - 命令执行超时处理
   - 进程清理确保资源释放

5. **测试驱动开发**
   - 先在 research/ 验证方案
   - 稳定后迁移到生产代码
   - 保留测试脚本

## 相关文档

- [根目录文档](../CLAUDE.md)
- [核心模块文档](../src/CLAUDE.md)
- [增强型工作流指南](../docs/ENHANCED_WORKFLOW_GUIDE.md)
- [BPLOT 工作流指南](../docs/BPLOT_AUTO_WORKFLOW_GUIDE.md)
- [UMI-OCR API 指南](../docs/UMI_OCR_API_GUIDE.md)
- [菜单操作配置指南](../docs/MENU_OPERATIONS_GUIDE.md)

---

**最后更新：** 2025-11-04
**维护者：** 老王团队
**重要提示：** 此模块包含项目的核心技术积累，建议完整阅读以深入理解系统设计。
