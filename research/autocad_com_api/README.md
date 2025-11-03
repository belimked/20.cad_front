# AutoCAD COM API - 生产工作流程

AutoCAD 自动化工作流程（基于数据库配置）

---

## 🎯 核心程序

**主程序：** `configurable_workflow.py` (111KB)

**运行方式：**
```bash
python research/autocad_com_api/configurable_workflow.py
```

---

## ✨ 核心功能

### 1. 数据库配置管理
- ✅ 所有参数可通过数据库配置（`autocad_config` 表）
- ✅ 支持多套配置（通过 `config_name` 切换）
- ✅ 支持运行时参数覆盖

### 2. 文件自动化
- ✅ 自动关闭现有 AutoCAD 进程
- ✅ 启动 AutoCAD 并打开指定 DWG 文件
- ✅ 验证文件加载（带超时和重试机制）
- ✅ 输出目录自动清理（可配置备份）

### 3. 菜单操作自动化（4种方式）
- ✅ **键盘快捷键** - 适合有 `(H)` 标识的菜单
- ✅ **鼠标点击** - 使用 pywinauto 定位和点击
- ✅ **图像识别** - 使用 pyautogui 匹配图标
- ✅ **OCR文字识别** - 使用 Umi-OCR 识别菜单文本（最智能）

### 4. 全屏截图 + OCR文本提取
- ✅ 全屏截图并进行 OCR 识别
- ✅ 正则表达式提取动态数据（如：总页数、进度）
- ✅ 自动保存截图和识别结果到文件
- ✅ 结果自动存入数据库（`ocr_recognition_logs` 表）

### 5. 图像预处理（增强OCR准确率）
- ✅ 生成多个预处理版本（二值化、高对比度、去噪、RGB通道分离等）
- ✅ 并行OCR识别（`ThreadPoolExecutor` 多线程）
- ✅ 智能结果合并（去重、按置信度排序）
- ✅ 保存所有预处理版本的截图（方便调试）

### 6. 日志和监控
- ✅ 任务执行日志（`autocad_task_logs` 表）
- ✅ OCR识别日志（`ocr_recognition_logs` 表）
- ✅ 预处理性能统计（`ocr_preprocessing_performance` 表）
- ✅ 详细的控制台输出

---

## 🚀 快速开始

### 1. 环境要求

- ✅ Windows 系统
- ✅ AutoCAD 2013-2024（任意版本）
- ✅ Python 3.8+
- ✅ MySQL 数据库

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**核心依赖：**
- `pywin32` - AutoCAD COM API
- `psutil` - 进程管理
- `pywinauto` - UI自动化
- `pyautogui` - 图像识别
- `opencv-python` - 图像预处理
- `Pillow` - 图像处理
- `sqlalchemy` - 数据库ORM
- `pymysql` - MySQL驱动
- `requests` - Umi-OCR API调用

### 3. 配置数据库

**默认配置：** `config_name='default'`

**查看配置：**
```bash
python scripts/autocad_config_manager.py show 1
```

**更新配置：**
```bash
# 更新菜单操作
python scripts/update_menu_operations.py

# 启用输出目录清理
python scripts/enable_output_cleanup.py

# 添加全屏截图提取步骤
python scripts/add_screenshot_extract_step.py
```

### 4. 运行工作流程

```bash
python research/autocad_com_api/configurable_workflow.py
```

**或者在代码中使用：**
```python
from research.autocad_com_api.configurable_workflow import ConfigurableAutoCADWorkflow

# 使用默认配置
workflow = ConfigurableAutoCADWorkflow(config_name='default')

# 运行完整流程
success = workflow.run(dwg_file_path=r"F:\path\to\drawing.dwg")

# 访问提取的数据
if success:
    total_pages = workflow.extracted_data.get('total_pages')
    print(f"总页数: {total_pages}")
```

---

## 📋 典型工作流程配置

### 示例：CAD批量打图自动化

```json
[
  {
    "type": "menu",
    "method": "ocr",
    "text": "依云",
    "wait_time": 0.5
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "CAD批量打图精灵",
    "wait_time": 1.0
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "打印",
    "wait_time": 2.0
  },
  {
    "type": "screenshot_extract",
    "target_pattern": "共\\s*(\\d+)\\s*页",
    "save_to": "total_pages",
    "required": false,
    "wait_time": 1.0
  }
]
```

---

## 📚 相关文档

### 核心文档
- [全屏截图提取功能指南](../../docs/SCREENSHOT_EXTRACT_GUIDE.md)
- [输出目录清理功能指南](../../docs/OUTPUT_DIR_CLEANUP_GUIDE.md)
- [菜单操作完整指南](../../docs/MENU_OPERATIONS_GUIDE.md)
- [OCR配置指南](../../docs/TESSERACT_INSTALLATION_GUIDE.md)
- [数据库配置指南](../../docs/DATABASE_CONFIG_GUIDE.md)

### 历史文档
- [历史研究代码](_archived/) - 早期研究和测试代码（已归档）

---

## 🔧 数据库表结构

### 1. `autocad_config` - 配置表
- 存储工作流程配置参数
- 支持多套配置（通过 `config_name` 区分）

### 2. `autocad_task_logs` - 任务日志表
- 记录每次工作流程执行
- 包含开始/结束时间、状态、错误信息

### 3. `ocr_recognition_logs` - OCR识别日志表
- 记录每次OCR识别（菜单OCR 和 全屏OCR）
- 包含目标文本、匹配结果、置信度、性能统计

### 4. `ocr_preprocessing_performance` - 预处理性能表
- 记录每个预处理方法的性能数据
- 包含处理时间、识别数量、是否找到目标

---

## ⚙️ OCR引擎配置

### 推荐引擎：Umi-OCR（首选）

**优势：**
- ✅ 准确率最高（基于 PaddleOCR）
- ✅ 速度快（局域网HTTP服务）
- ✅ 无需本地安装

**配置：**
```python
# 在数据库 autocad_config 表中配置
umi_ocr_enabled = True
umi_ocr_service_url = "http://10.3.19.121:1224"
umi_ocr_api_path = "/api/ocr"
umi_ocr_timeout = 30
umi_ocr_limit_side_len = 2880
umi_ocr_max_workers = 8  # 并行线程数
```

### 备选引擎

1. **Tesseract** - 中文UI识别好，需要安装引擎
2. **EasyOCR** - 轻量级，安装简单，速度较慢

---

## 🐛 故障排查

### Q1: OCR识别不到文本
- 检查 Umi-OCR 服务是否运行
- 查看保存的截图文件检查识别质量
- 尝试调整 `wait_time` 确保界面完全加载

### Q2: 正则表达式不匹配
- 查看 OCR 文本文件检查实际识别的文本
- 使用 https://regex101.com/ 测试正则表达式
- 使用 `\s*` 让空格可有可无

### Q3: 菜单点击失败
- 检查使用的方法（keyboard/mouse/image/ocr）
- OCR 方式最智能，推荐优先使用
- 查看控制台日志了解具体失败原因

### Q4: 文件加载超时
- 增加 `startup_wait_time` 和 `verification_wait_time`
- 检查 DWG 文件是否损坏
- 确认 AutoCAD 版本兼容性

---

## 📊 性能优化建议

1. **启用 Umi-OCR** - 比本地OCR快3-5倍
2. **调整并行线程数** - `umi_ocr_max_workers` 根据网络和服务器性能调整
3. **精简预处理方法** - 只使用对当前场景有效的预处理方式
4. **合理设置等待时间** - 避免过长的 `wait_time`

---

## 📝 更新日志

### v2.0 (2025-10-29)
- ✅ 全屏OCR新增多版本预处理支持
- ✅ 修复字典遍历Bug
- ✅ 修复OCR数据结构不匹配Bug
- ✅ 优化正则表达式（支持空格可有可无）
- ✅ 归档历史研究代码

### v1.5 (2025-10-28)
- ✅ 新增全屏截图 + OCR文本提取功能
- ✅ 新增输出目录自动清理功能
- ✅ 完善数据库日志记录

### v1.0 (2025-10-24)
- ✅ 基于数据库配置的工作流程
- ✅ 多种菜单操作方式
- ✅ 完整的错误处理和日志

---

## 🔗 相关项目

- [AutoCAD COM API 研究文档](../../docs/autocad/)
- [测试部署指南](../../docs/autocad/TESTING_GUIDE.md)
- [数据库设计文档](../../docs/DATABASE_DESIGN.md)

---

**创建时间：** 2025-10-24
**最后更新：** 2025-10-29
**状态：** ✅ 生产使用
**支持版本：** AutoCAD 2013-2024
**维护者：** 老王团队
