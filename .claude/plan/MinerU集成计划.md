# MinerU PDF 识别集成计划

## 任务背景

**需求：** 为 AutoCAD 批量打印输出的 PDF 文件添加 MinerU 识别功能，提取图号、表格信息、技术要求，并关联到 DWG 文件。

**关键信息：**
- MinerU API 服务: http://10.3.19.63:18080
- 识别内容: 图号、表格、技术要求
- 触发方式: 工作流后置自动触发
- 数据存储: 数据库（关联 CAD 图纸和图号）
- 超时配置: 30 秒/PDF（可配置）
- 批量处理: 支持一次提交多个 PDF

---

## 技术方案

### 选定方案：批量提交（方案 1）

**优势：**
- ✅ 简单高效：一次 HTTP 请求
- ✅ API 原生支持
- ✅ 代码复杂度低
- ✅ 满足当前需求

**批量策略：**
- 一次提交数量：可配置（默认 10 个）
- 超时计算：文件数 × 30 秒
- 分批处理：超过批次大小时分批提交

---

## 数据库设计

### 1. 扩展 autocad_config 表

新增字段：
```sql
mineru_api_url VARCHAR(200) DEFAULT 'http://127.0.0.1:18080'
mineru_enabled BOOLEAN DEFAULT FALSE
mineru_timeout_per_file INTEGER DEFAULT 30
mineru_pdf_render_timeout INTEGER DEFAULT 300
mineru_batch_size INTEGER DEFAULT 10
mineru_lang_list VARCHAR(100) DEFAULT '["ch"]'
mineru_parse_method VARCHAR(20) DEFAULT 'auto'
mineru_table_enable BOOLEAN DEFAULT TRUE
mineru_return_md BOOLEAN DEFAULT TRUE
mineru_return_content_list BOOLEAN DEFAULT TRUE
mineru_extraction_patterns TEXT
```

### 2. 图号关联表 (dwg_drawing_sheets)

存储 DWG 与图号的关系：
- task_id: 关联任务
- dwg_filename: DWG 文件名
- pdf_filename: PDF 文件名
- sheet_number: 图号 ⭐
- sheet_title: 图纸标题
- version: 版本号
- scale: 比例
- drawing_date: 绘图日期

### 3. 识别结果表 (dwg_recognition_results)

存储完整的识别内容：
- markdown_content: Markdown 全文
- content_list: 结构化内容（JSON）
- table_data: 表格数据（JSON）
- technical_requirements: 技术要求
- status: 识别状态
- processing_time_seconds: 处理时长

---

## 技术实现

### 1. MinerU 服务类 (src/services/mineru_service.py)

**核心方法：**
```python
class MinerUService:
    def batch_recognize_pdfs(pdf_directory, pattern) -> Dict:
        """批量识别 PDF"""
        # 1. 收集 PDF 文件
        # 2. 分批提交 MinerU API
        # 3. 解析响应
        # 4. 提取图号/表格/技术要求
        # 5. 存入数据库

    def _call_mineru_api(pdf_files) -> Dict:
        """调用 MinerU API"""
        # multipart/form-data 批量提交

    def _extract_drawing_info(markdown, content_list) -> Dict:
        """提取图号信息（正则匹配）"""
        # 图号、版本、比例、标题

    def _extract_tables_from_content(content_list) -> List:
        """提取表格数据"""

    def _extract_technical_requirements(markdown) -> str:
        """提取技术要求段落"""
```

### 2. Enhanced Workflow 集成

**新增操作类型：** `mineru_recognition`

**配置示例：**
```json
{
  "post_operations": [
    {
      "type": "file_monitor",
      "watch_path": "C:\\output",
      "file_pattern": "*.pdf",
      "timeout": 600
    },
    {
      "type": "mineru_recognition",
      "pdf_directory": "C:\\output",
      "pdf_pattern": "*.pdf",
      "required": false
    }
  ]
}
```

**实现方法：**
```python
def _execute_mineru_recognition(operation: Dict) -> bool:
    """执行 MinerU PDF 识别"""
    # 1. 检查是否启用
    # 2. 创建 MinerU 服务
    # 3. 批量识别
    # 4. 记录日志
```

---

## 文件清单

### 新建文件

1. **migrations/20251105_add_mineru_integration.sql** - 数据库迁移脚本
2. **src/models/dwg_drawing_sheet.py** - 图号数据模型
3. **src/models/dwg_recognition_result.py** - 识别结果模型
4. **src/services/mineru_service.py** - MinerU 服务类 (~450 行)
5. **scripts/init_mineru_tables.py** - 数据库表初始化
6. **scripts/update_autocad_config_mineru.py** - 配置更新脚本
7. **scripts/test_mineru_integration.py** - 集成测试脚本

### 修改文件

1. **src/models/__init__.py** - 添加新模型导出
2. **research/autocad_com_api/enhanced_workflow.py** - 添加 mineru_recognition 操作类型

---

## 执行步骤

### 1. 数据库初始化

```bash
# 运行 SQL 迁移脚本
mysql -u root -p cad_mgt < migrations/20251105_add_mineru_integration.sql

# 或使用 Python 脚本创建表
python scripts/init_mineru_tables.py
```

### 2. 更新配置

```bash
# 为现有配置添加 MinerU 默认值
python scripts/update_autocad_config_mineru.py
```

### 3. 启用 MinerU

```sql
-- 在数据库中启用 MinerU
UPDATE autocad_config
SET mineru_enabled = TRUE,
    mineru_api_url = 'http://10.3.19.63:18080',
    mineru_batch_size = 10
WHERE config_name = 'default';
```

### 4. 测试集成

```bash
# 运行测试脚本
python scripts/test_mineru_integration.py
```

### 5. 工作流配置

更新 `autocad_config.menu_operations` 字段，添加后置操作：

```json
{
  "post_operations": [
    {
      "type": "mineru_recognition",
      "pdf_directory": "${output_dir}",
      "pdf_pattern": "*.pdf",
      "required": false,
      "description": "MinerU PDF 识别"
    }
  ]
}
```

---

## 配置说明

### 环境变量（可选）

```bash
export MINERU_API_URL=http://10.3.19.63:18080
export MINERU_TIMEOUT_PER_FILE=30
export MINERU_BATCH_SIZE=10
```

### 数据库配置

| 字段 | 默认值 | 说明 |
|------|--------|------|
| mineru_api_url | http://127.0.0.1:18080 | MinerU API 地址 |
| mineru_enabled | FALSE | 是否启用（默认禁用） |
| mineru_timeout_per_file | 30 | 单个 PDF 超时（秒） |
| mineru_batch_size | 10 | 批次大小 |
| mineru_lang_list | ["ch"] | 识别语言 |
| mineru_parse_method | auto | 解析方法 |

---

## 图号提取规则

### 正则表达式模式

**图号：**
- `图号: XXX`
- `Drawing No: XXX`
- `编号: XXX`

**版本：**
- `版本: V1.0`
- `Version: V1.0`
- `Rev: A`

**比例：**
- `比例: 1:100`
- `Scale: 1:100`

**自定义模式：**
可通过 `mineru_extraction_patterns` 字段配置自定义正则表达式（JSON 格式）

---

## 验收标准

- [x] 数据库表创建成功（3个表/字段）
- [x] ORM 模型可正常使用
- [x] MinerU 服务类实现完整
- [x] Enhanced Workflow 集成成功
- [x] 测试脚本可运行
- [ ] 实际 PDF 识别测试通过
- [ ] 图号信息正确提取
- [ ] 表格数据正确解析
- [ ] 技术要求正确识别

---

## 后续优化

1. **提取规则优化**
   - 根据实际 PDF 格式调整正则表达式
   - 支持多种图框格式
   - 机器学习模型识别图号

2. **性能优化**
   - 大批量处理时的并发策略
   - 识别结果缓存
   - 增量识别（只识别新增 PDF）

3. **功能扩展**
   - 图号与 DWG 文件自动关联
   - 识别结果可视化界面
   - 识别准确率统计

---

**执行时间：** 2025-11-05
**状态：** ✅ 已完成
**提交 Commit：** 待提交
