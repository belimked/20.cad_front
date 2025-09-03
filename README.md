# 100.AI.TrainData

## 项目概述

本项目用于生成和管理大模型训练数据，包括语义理解、问答对和指令遵循等类型的训练数据。

## 项目结构

- **src/**: 源代码目录
  - **service/**: 服务层代码，处理数据生成和加工的核心逻辑
  - **entity/**: 实体层代码，定义基础数据结构和关系
  - **dict/**: 字典数据，提供各种业务对象的词汇映射
  - **common/**: 通用工具和函数

- **test/**: 测试代码和脚本
  - **service/**: 服务测试，包含针对各个服务的测试脚本
    - [test_qwen_service.py](test/service/docs/test_qwen_service_usage.md): 千问服务测试和数据生成脚本
    - **docs/**: 测试脚本文档

- **outputs/**: 输出目录，存放生成的数据文件
  - **data/**: 存放生成的训练数据
    - **qwen/**: 千问模型的训练数据

## 功能特点

- 支持多业务对象的训练数据生成
- 批量生成符合大模型训练格式的问答对
- 内置关键字过滤机制，便于生成特定场景的训练数据
- 支持数据统计和分析

## 快速开始

1. **设置环境**
   ```bash
   # 克隆项目
   git clone [项目地址]
   
   # 进入项目目录
   cd 100.AI.TrainData
   
   # 设置PYTHONPATH
   export PYTHONPATH=$PWD
   ```

2. **生成训练数据**
   ```bash
   # 使用默认关键字生成数据
   python test/service/test_qwen_service.py
   
   # 使用自定义关键字生成数据
   python test/service/test_qwen_service.py "关键字1,关键字2,关键字3"
   ```

3. **查看输出**
   
   生成的数据将保存在`outputs/data/`目录下，文件名格式为`qwen_data_YYYYMMDD_HHMMSS.jsonl`。

## 详细文档

- [千问服务测试脚本使用文档](test/service/docs/test_qwen_service_usage.md)
- [服务模块文档](src/service/README.md)

# 多线程URL下载工具

Linux环境下的多线程URL下载工具，支持并行下载多个URL资源，具有进度显示、重试机制和友好的命令行界面。

## 功能特点

- 多线程并行下载，提高下载效率
- 显示每个文件的下载进度条
- 支持下载失败自动重试
- 支持从文件批量导入URL
- 避免文件名冲突，自动重命名
- 完整的命令行参数支持

## 安装依赖

```bash
pip install requests tqdm
```

## 使用方法

### 下载单个URL

```bash
python multi_downloader.py -u https://example.com/file.zip
```

### 下载多个URL

```bash
python multi_downloader.py -l https://example.com/file1.zip https://example.com/file2.zip
```

### 从文件读取URL列表

创建一个文本文件，每行一个URL：

```text
https://example.com/file1.zip
https://example.com/file2.zip
# 这是注释行
https://example.com/file3.zip
```

然后执行：

```bash
python multi_downloader.py -f urls.txt
```

### 自定义下载选项

```bash
# 使用10个线程下载
python multi_downloader.py -f urls.txt -t 10

# 指定下载目录
python multi_downloader.py -f urls.txt -o /path/to/downloads

# 设置下载超时和重试次数
python multi_downloader.py -f urls.txt --timeout 60 -r 5
```

## 完整参数说明

| 参数 | 说明 |
|------|------|
| `-u, --url URL` | 要下载的单个URL |
| `-f, --file FILE` | 包含URL列表的文件路径 |
| `-l, --list URL [URL ...]` | 要下载的URL列表 |
| `-t, --threads N` | 下载线程数（默认: 5） |
| `-o, --output-dir DIR` | 下载文件保存目录（默认: ./downloads） |
| `--timeout SEC` | 下载超时时间，单位秒（默认: 30） |
| `-r, --retry N` | 下载失败重试次数（默认: 3） |

## 使用示例

1. 下载单个文件:
   ```bash
   python multi_downloader.py -u https://example.com/large-file.zip -o ~/Downloads
   ```

2. 下载多个文件，使用8个线程:
   ```bash
   python multi_downloader.py -l https://example.com/file1.zip https://example.com/file2.zip -t 8
   ```

3. 从文件批量下载，超时设置为60秒:
   ```bash
   python multi_downloader.py -f download_list.txt --timeout 60
   ```

## 小提示

- 对于大文件下载，建议适当增加超时时间
- 线程数过多可能不会提高下载速度，反而会因为资源竞争降低效率
- 可以在URL文件中使用`#`开头的行添加注释
## 🚀 Swift 模型部署

本项目集成了 Swift 模型部署功能，支持 Qwen2.5 模型的训练、部署和推理。

### 快速开始

1. **安装 Swift**
   ```bash
   pip install ms-swift[llm]
   ```

2. **启动模型服务**
   ```bash
   # 使用管理脚本启动
   ./scripts/swift_manager.sh start
   
   # 或手动启动
   swift deploy \
       --model_type qwen2_5-3b-instruct \
       --model_id_or_path /path/to/model \
       --port 8000
   ```

3. **测试服务**
   ```bash
   # 测试API接口
   ./scripts/swift_manager.sh test
   
   # 或使用curl测试
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "qwen2_5-3b-instruct",
       "messages": [{"role": "user", "content": "你好"}],
       "max_tokens": 100
     }'
   ```

### 管理脚本

使用 `scripts/swift_manager.sh` 脚本可以方便地管理 Swift 服务：

```bash
# 启动服务
./scripts/swift_manager.sh start

# 停止服务
./scripts/swift_manager.sh stop

# 重启服务
./scripts/swift_manager.sh restart

# 查看状态
./scripts/swift_manager.sh status

# 查看日志
./scripts/swift_manager.sh logs

# 测试服务
./scripts/swift_manager.sh test
```

### 文档

- [Swift 部署与使用指南](docs/swift-deployment-guide.md) - 详细的部署和配置文档
- [模型训练记录](docs/training-logs.md) - 训练过程和结果记录

### 训练结果

最新训练结果：
- **模型**: Qwen2.5-3B + LoRA微调
- **数据集**: 549条ERD相关问答数据
- **最终验证损失**: 0.934226
- **训练时长**: 46分钟 (620步)
- **配置**: 学习率1e-6, LoRA rank=16, alpha=16

### 服务器部署

在服务器上部署Swift服务的完整流程：

1. **环境准备**
   ```bash
   # 安装依赖
   pip install ms-swift[llm]
   
   # 下载模型
   python -c "
   from modelscope import snapshot_download
   snapshot_download('qwen/Qwen2.5-3B-Instruct', cache_dir='./models')
   "
   ```

2. **启动服务**
   ```bash
   # 使用训练好的LoRA模型
   swift deploy \
       --model_type qwen2_5-3b-instruct \
       --model_id_or_path ./models/qwen/Qwen2___5-3B-Instruct \
       --adapters_id_or_path ./outputs/4table_training_20250903_105534 \
       --port 8000 \
       --host 0.0.0.0 \
       --api_mode openai
   ```

3. **服务监控**
   ```bash
   # 查看服务状态
   ./scripts/swift_manager.sh status
   
   # 查看GPU使用情况
   nvidia-smi
   
   # 查看日志
   ./scripts/swift_manager.sh logs
   ```

