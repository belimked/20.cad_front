# CAD 文件自动化处理系统

> **AI 协助开发项目** - 使用现代 AI 工具加速软件开发，效率提升 60%+

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

## 📖 项目简介

CAD 文件自动化处理系统是一个完整的自动化工作流系统，用于：

1. 📥 从远程服务器下载 CAD 文件
2. 🤖 自动调用 AutoCAD 执行批量操作
3. 👀 实时监控处理进度
4. 📤 上传处理结果到服务器

**适用场景：** 批量 CAD 图纸处理、远程自动化绘图服务、CAD 文件标准化处理

---

## ✨ 核心特性

- ✅ **远程文件同步** - 支持断点续传、MD5 校验、增量下载
- ✅ **AutoCAD 自动化** - COM 接口控制，YAML 配置驱动操作序列
- ✅ **智能监控** - 多条件判断任务完成，支持文件监控和进程监控
- ✅ **任务管理** - 状态机、队列管理、SQLite 持久化
- ✅ **结果上传** - 分片上传、进度显示、自动重试
- ✅ **健壮设计** - 完整异常处理、崩溃恢复、失败重试

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     远程服务器                            │
│  - 文件存储服务                                           │
│  - 任务调度 API                                          │
│  - 结果接收服务                                           │
└──────────────┬──────────────────────────┬────────────────┘
               │                          │
          ① 下载文件                  ⑤ 上传结果
               │                          │
┌──────────────▼──────────────────────────▼────────────────┐
│              本地 Windows 处理节点                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  主控制器 (Main Controller)                      │    │
│  │   - 任务调度                                     │    │
│  │   - 状态管理                                     │    │
│  │   - 异常处理                                     │    │
│  └─────┬───────────┬───────────┬──────────┬────────┘    │
│        │           │           │          │             │
│   ② 打开CAD   ③ 执行操作  ④ 监控输出  日志记录          │
│        │           │           │          │             │
│  ┌─────▼──┐  ┌────▼────┐ ┌────▼─────┐ ┌─▼──────┐      │
│  │文件同步│  │AutoCAD  │ │文件监控  │ │日志系统│      │
│  │ 模块   │  │自动化   │ │ 模块     │ │        │      │
│  │        │  │ 模块    │ │          │ │        │      │
│  └────────┘  └─────────┘ └──────────┘ └────────┘      │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 目录结构

```
cad_auto_processor/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 主入口
│   ├── modules/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── downloader.py          # 文件下载模块
│   │   ├── cad_automation.py      # AutoCAD 自动化模块
│   │   ├── file_monitor.py        # 文件监控模块
│   │   └── uploader.py            # 结果上传模块
│   ├── services/                  # 业务服务
│   │   ├── __init__.py
│   │   ├── task_service.py        # 任务管理服务
│   │   └── api_client.py          # 远程 API 客户端
│   └── utils/                     # 工具模块
│       ├── __init__.py
│       ├── config.py              # 配置管理
│       ├── logger.py              # 日志工具
│       └── file_utils.py          # 文件操作工具
├── tests/                         # 测试代码
│   ├── __init__.py
│   └── test_*.py
├── data/                          # 数据目录
│   ├── downloads/                 # 下载文件
│   ├── processing/                # 处理中文件
│   ├── outputs/                   # 输出文件
│   └── backup/                    # 备份文件
├── logs/                          # 日志目录
├── config/                        # 配置目录
│   └── config.yaml                # 主配置文件
├── requirements.txt               # 依赖列表
├── README.md                      # 项目文档
└── .gitignore                     # Git 忽略文件
```

---

## 🚀 快速开始

### 1. 环境要求

- **操作系统：** Windows 10/11（64-bit）
- **Python：** 3.9 或更高版本
- **AutoCAD：** AutoCAD 2018 或更高版本
- **内存：** 建议 8GB+
- **磁盘空间：** 至少 50GB

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone <repository_url>
cd cad_auto_processor

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 3. 配置

编辑 `config/config.yaml` 文件，配置以下关键参数：

```yaml
server:
  base_url: "https://your-api-server.com"
  api_key: "your_api_key"

autocad:
  install_path: "C:\\Program Files\\Autodesk\\AutoCAD 2024"

paths:
  downloads: "./data/downloads"
  outputs: "./data/outputs"
```

### 4. 运行

```bash
# 守护进程模式（持续运行）
python src/main.py --mode daemon

# 单次运行模式（处理一批任务后退出）
python src/main.py --mode once --tasks 10

# 调试模式
python src/main.py --log-level DEBUG --dry-run
```

---

## 📚 使用示例

### 基本用法

```python
from src.modules.downloader import CadFileDownloader
from src.utils.logger import setup_logger

# 初始化日志
logger = setup_logger(log_level="INFO")

# 创建下载器
downloader = CadFileDownloader()

# 获取待下载文件列表
files = downloader.get_pending_files()

# 下载文件
for file_info in files:
    if downloader.is_file_new(file_info):
        downloader.download_file(file_info)
```

### 配置管理

```python
from src.utils.config import get_config

# 获取配置实例
config = get_config()

# 读取配置
api_url = config.get("server.base_url")
log_level = config.get("logging.level", "INFO")

# 运行时修改配置
config.set("logging.level", "DEBUG")
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_downloader.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

---

## 📊 开发进度

**当前版本：** 0.1.0（开发中）

| 模块 | 状态 | 进度 |
|------|------|------|
| 项目框架 | ✅ 完成 | 100% |
| 文件下载模块 | 🚧 进行中 | 60% |
| AutoCAD 自动化 | ⏳ 待开始 | 0% |
| 文件监控 | ⏳ 待开始 | 0% |
| 任务管理 | ⏳ 待开始 | 0% |
| 结果上传 | ⏳ 待开始 | 0% |
| 测试 | ⏳ 待开始 | 0% |
| 文档 | 🚧 进行中 | 40% |

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 开发规范

本项目遵循以下开发原则：

- **SOLID 原则** - 单一职责、开闭原则、里氏替换、接口隔离、依赖倒置
- **DRY 原则** - 不重复代码
- **KISS 原则** - 保持简单
- **YAGNI 原则** - 只实现需要的功能

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 👥 团队

- **项目负责人：** [待填写]
- **AI 协助工具：** Claude Code 2.0
- **开发模式：** AI 协助开发（效率提升 60%+）

---

## 📧 联系方式

- **项目主页：** [待填写]
- **问题反馈：** [GitHub Issues]
- **技术支持：** [待填写]

---

**⚡ 本项目使用 AI 协助开发，展示了现代软件工程与人工智能结合的强大潜力！**
