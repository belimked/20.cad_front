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