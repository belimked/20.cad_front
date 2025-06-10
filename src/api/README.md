# 训练数据生成API文档

## 概述

本API提供了生成AI训练数据的功能，支持多种业务对象的数据生成。API基于FastAPI框架实现，提供了REST风格的接口。

## 安装与启动

### 依赖项

确保已安装以下Python依赖：

```bash
pip install fastapi uvicorn
```

### 启动服务

```bash
# 从项目根目录启动
python -m src.api.app
```

服务默认在 `http://localhost:8000` 启动。启动后，可以通过浏览器访问 `http://localhost:8000/docs` 查看API交互文档。

## API端点

### 1. 根路径

- **路径**：`/`
- **方法**：`GET`
- **描述**：返回API服务的基本信息
- **响应示例**：
  ```json
  {
    "message": "训练数据生成API服务",
    "version": "1.0.0"
  }
  ```

### 2. 生成训练数据

- **路径**：`/api/generate-data`
- **方法**：`POST`
- **描述**：根据指定的业务对象生成训练数据

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| business_object | string | 是 | - | 业务对象代码，如searchStaff、updateCargo等 |
| total_samples | integer | 否 | 100 | 要生成的总样本数 |
| variations_per_rule | integer | 否 | 2 | 每个规则的变种数量 |
| ruleids | string | 否 | null | 规则ID过滤，格式如'1,2,3'或'-1,-2,-3'，正数表示包含，负数表示排除 |
| keyword | string | 否 | null | 关键字过滤，多个关键字用逗号分隔 |

#### 响应格式

```json
{
  "status": "success",
  "message": "成功生成X条训练数据",
  "files": {
    "dialogs_file": "输出的对话数据文件路径",
    "raw_file": "输出的原始数据文件路径"
  },
  "statistics": {
    "total_count": 100,
    "rule_distribution": [
      {
        "rule_id": "1",
        "rule_name": "规则1",
        "count": 50
      },
      {
        "rule_id": "2",
        "rule_name": "规则2",
        "count": 30
      },
      {
        "rule_id": "3",
        "rule_name": "规则3",
        "count": 20
      }
    ]
  },
  "examples": [
    {
      "messages": [
        {
          "role": "user",
          "content": "用户问题示例1"
        },
        {
          "role": "assistant",
          "content": "助手回答示例1"
        }
      ]
    },
    {
      "messages": [
        {
          "role": "user",
          "content": "用户问题示例2"
        },
        {
          "role": "assistant",
          "content": "助手回答示例2"
        }
      ]
    }
  ]
}
```

## 示例调用

### 使用curl

```bash
curl -X 'POST' \
  'http://localhost:8000/api/generate-data?business_object=searchStaff&total_samples=10&variations_per_rule=2' \
  -H 'accept: application/json'
```

### 使用Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate-data",
    params={
        "business_object": "searchStaff",
        "total_samples": 10,
        "variations_per_rule": 2,
        "ruleids": "1,2,3",
        "keyword": "最近,月"  # 可选的关键字过滤
    }
)

data = response.json()
print(f"生成了 {data['statistics']['total_count']} 条训练数据")
print(f"数据已保存到: {data['files']['dialogs_file']}")
print(f"数据规则分布: {data['statistics']['rule_distribution']}")
```

## 错误处理

API会返回适当的HTTP状态码和错误信息：

- **400 Bad Request**：参数错误，如不支持的业务对象
- **500 Internal Server Error**：服务器内部错误

错误响应格式：

```json
{
  "detail": "错误信息"
}
```

## 支持的业务对象

目前API支持以下业务对象：

- `searchContract`：合同查询
- `updateStaff`：人员更新
- `updateCargo`：货物更新
- `searchStaff`：人员查询
- `searchCargo`：货物查询
- `searchPo`：订单查询 