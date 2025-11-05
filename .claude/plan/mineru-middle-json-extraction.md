# MinerU Middle JSON 图号提取增强

## 任务上下文

**目标**：改进 MinerU PDF 识别的图号和标题提取准确率
**当前问题**：现有从 Markdown/HTML 提取逻辑准确率低，table_data 和 drawing_info 为空
**解决方案**：使用 MinerU API 的 `return_middle_json` 结构化数据进行提取
**目标准确率**：≥ 90%

## 核心改进

### 1. API 参数增强
- 添加 `return_middle_json=true` 参数
- 获取原始结构化识别结果

### 2. 提取逻辑重构
- 优先使用 middle_json 的 preproc_blocks 数据
- 从表格 HTML 中提取图号和标题
- 使用通用模式匹配（不依赖固定位置）

### 3. 提取规则

**图号规则**：
- 格式：大写字母开头 + 多组数字（连字符分隔）
- 示例：`PCX-01-01-03-01-3`
- 最小长度：10 字符，至少 3 个连字符

**标题规则**：
- 特征：4+ 中文字符
- 排除：技术要求、材料、数量等通用词
- 优先：字符数多的

## 实施步骤

1. ✅ 修改 API 调用参数
2. ✅ 更新响应解析逻辑
3. ✅ 新增 `_extract_from_middle_json` 方法
4. ✅ 实现 `_extract_table_html` 辅助方法
5. ✅ 实现 `_extract_drawing_number` 图号提取
6. ✅ 实现 `_extract_drawing_title` 标题提取
7. ✅ 改进 `_extract_drawing_info` 集成新逻辑
8. ✅ 测试验证准确率

## 关键代码位置

**主文件**：`src/services/mineru_service.py`

**修改方法**：
- `_call_mineru_api` (line ~210)
- `_parse_single_result` (line ~264)
- `_extract_drawing_info` (line ~364)

**新增方法**：
- `_extract_from_middle_json`
- `_extract_table_html`
- `_extract_drawing_number`
- `_extract_drawing_title`

## 预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| 图号提取率 | 0% | 90%+ |
| 标题提取率 | 0% | 85%+ |
| table_data 保存 | 失败 | 成功 |
| drawing_sheets 记录 | 0 | > 0 |

## 测试命令

```bash
# 清除旧数据
python -c "from src.utils.database import db_session; from src.models.dwg_recognition_result import DWGRecognitionResult; from src.models.dwg_drawing_sheet import DWGDrawingSheet; session = db_session().__enter__(); session.query(DWGRecognitionResult).delete(); session.query(DWGDrawingSheet).delete(); session.commit()"

# 运行测试
python scripts/test_mineru_integration.py

# 验证准确率
python -c "from src.utils.database import db_session; from src.models.dwg_drawing_sheet import DWGDrawingSheet; session = db_session().__enter__(); sheets = session.query(DWGDrawingSheet).all(); success = sum(1 for s in sheets if s.sheet_number and s.sheet_title); print(f'准确率: {success/len(sheets)*100:.1f}%')"
```

## 创建时间

2025-11-05 15:50:00

## 执行状态

- [x] 计划已批准
- [ ] 代码实施中
- [ ] 测试验证
- [ ] 完成
