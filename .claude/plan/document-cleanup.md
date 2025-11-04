# 项目文档清理规划

**规划日期:** 2025-11-04
**规划类型:** 文档重组工程
**预估工作量:** 52 小时（6-7 个工作日）

---

## 📋 执行概要

本规划旨在清理和重组 CAD 文件自动化处理系统的项目文档,消除冗余,建立清晰的信息架构。

### 核心目标

1. **消除文档冗余** - 将 5 个 BPLOT 文档合并为 2-3 个清晰的文档
2. **建立清晰的信息架构** - 重组 docs/ 目录为 6 个功能分类
3. **精简主文档** - 将 README.md 从 463 行精简到 200 行以内
4. **建立文档导航** - 创建 docs/README.md 作为文档中心
5. **统一命名规范** - 使用一致的文档命名格式
6. **确保零信息丢失** - 所有内容重组而非删除

### 当前文档状况

**主文档:**
- README.md (464 行) - 需要精简
- CLAUDE.md (506 行) - 保持独立
- QUICK_START.md - 保持不变

**docs/ 目录 (21 个文档):**

**BPLOT 工作流 (5 个,存在重复):**
- BPLOT_AUTO_WORKFLOW_GUIDE.md
- BPLOT_CONFIGURABLE_GUIDE.md
- BPLOT_CONFIG_FIX_NOTES.md
- BPLOT_CONFIG_GUIDE.md
- BPLOT_VERSION_COMPARISON.md

**OCR 相关 (4 个):**
- UMI_OCR_API_GUIDE.md
- image_preprocessing_guide.md
- ocr_preprocessing_config_guide.md
- ocr_logging_user_guide.md

**配置和操作指南 (7 个):**
- API_GUIDE.md
- DATABASE_CONFIG_GUIDE.md
- ENHANCED_WORKFLOW_GUIDE.md
- MENU_CLICKING_GUIDE.md
- MENU_OPERATIONS_GUIDE.md
- SCREENSHOT_EXTRACT_GUIDE.md
- OUTPUT_DIR_CLEANUP_GUIDE.md

**AutoCAD 相关 (2 个):**
- autocad/AUTOCAD_COM_API_SUMMARY.md
- autocad/TESTING_GUIDE.md

**其他 (3 个):**
- OCR_URL_UPDATE_GUIDE.md
- PDF_EXTRACTION_TROUBLESHOOTING.md
- TESSERACT_INSTALLATION_GUIDE.md

---

## 🗂️ 新目录结构设计

```
docs/
├── README.md                          # 文档中心导航（新建）
├── setup/                             # 环境搭建与配置（新建）
│   ├── INSTALLATION.md                # 详细安装指南（从 README 迁移）
│   ├── CONFIGURATION.md               # 配置详解（从 README 迁移）
│   └── TESSERACT_INSTALLATION.md      # Tesseract 安装（保留）
├── api/                               # API 相关（新建）
│   └── API_GUIDE.md                   # HTTP API 使用指南（移动）
├── autocad/                           # AutoCAD 自动化（已存在）
│   ├── AUTOCAD_COM_API_SUMMARY.md     # COM API 总结（保留）
│   ├── TESTING_GUIDE.md               # 测试指南（保留）
│   └── CONFIG_SYSTEM.md               # 配置系统完整文档（新建）
├── workflows/                         # 工作流文档（新建）
│   ├── bplot/                         # BPLOT 专题（新建）
│   │   ├── WORKFLOW_GUIDE.md          # 工作流指南（合并后）
│   │   ├── CONFIG_REFERENCE.md        # 配置参考（合并后）
│   │   └── VERSION_COMPARISON.md      # 版本对比（保留）
│   ├── ENHANCED_WORKFLOW_GUIDE.md     # 增强型工作流（移动）
│   ├── WORKFLOW_OPERATIONS.md         # 工作流操作完全指南（合并后）
│   └── DATABASE_CONFIG_GUIDE.md       # 数据库配置（移动）
├── ocr/                               # OCR 相关（新建）
│   ├── OCR_API_GUIDE.md               # UMI-OCR API 指南（重命名）
│   ├── OCR_IMAGE_PREPROCESSING.md     # 图像预处理（重命名）
│   ├── OCR_CONFIG_REFERENCE.md        # 配置参考（重命名）
│   └── OCR_LOGGING_GUIDE.md           # 日志指南（重命名）
└── troubleshooting/                   # 故障排查（新建）
    ├── PDF_EXTRACTION.md              # PDF 提取问题（移动）
    └── OCR_URL_UPDATE.md              # OCR URL 更新（移动）
```

**文档数量变化:**
- 原: 21 个文档
- 新: 18 个文档（合并减少 3 个）
- 新增子目录: 6 个

---

## 🚀 执行阶段

### 阶段 1: 文档内容分析与去重 (12 小时)

#### 任务 1.1: BPLOT 文档族群分析 (4h)

**目标:** 分析 5 个 BPLOT 文档的差异和重复内容

**操作步骤:**
1. 使用 diff 工具逐对比较文档内容
2. 提取每个文档的独特章节和重复章节
3. 识别文档的目标受众
4. 绘制内容重叠矩阵

**合并方案选项:**

**方案 A (推荐): 合并为 3 个文档**
```
├─ WORKFLOW_GUIDE.md (用户指南)
│  ├─ 从 BPLOT_AUTO_WORKFLOW_GUIDE.md 提取全自动流程
│  └─ 从 BPLOT_CONFIGURABLE_GUIDE.md 提取配置化流程
├─ CONFIG_REFERENCE.md (配置参考)
│  ├─ 从 BPLOT_CONFIG_GUIDE.md 提取配置说明
│  └─ 从 BPLOT_CONFIG_FIX_NOTES.md 提取已知问题
└─ VERSION_COMPARISON.md (保留，作为历史参考)
```

**方案 B: 激进合并为 2 个文档**
```
├─ BPLOT_COMPLETE_GUIDE.md (综合指南)
└─ BPLOT_VERSION_HISTORY.md (版本演进历史)
```

**方案 C: 保守方案**
- 仅合并 CONFIG_GUIDE + CONFIG_FIX_NOTES
- 保留其他 4 个文档

**输出:**
- `analysis/bplot_docs_overlap_matrix.md`
- `analysis/bplot_merge_strategy.md`

---

#### 任务 1.2: OCR 文档族群分析 (2h)

**目标:** 分析 4 个 OCR 文档的关系

**建议:** 保持 4 个文档分离，因为它们面向不同的使用场景

**操作步骤:**
1. 识别每个文档的核心主题
2. 检查内容是否有递进关系
3. 统一命名为 OCR_*.md 格式

**输出:**
- `analysis/ocr_docs_structure.md`

---

#### 任务 1.3: 菜单操作文档分析 (3h)

**目标:** 分析菜单操作相关文档的重复度

**涉及文档:**
- MENU_OPERATIONS_GUIDE.md
- MENU_CLICKING_GUIDE.md
- SCREENSHOT_EXTRACT_GUIDE.md
- OUTPUT_DIR_CLEANUP_GUIDE.md

**方案选项:**

**方案 A: 合并为 WORKFLOW_OPERATIONS.md**
```
├─ 第1章: 菜单点击操作
├─ 第2章: 菜单操作配置
├─ 第3章: 截图提取操作
└─ 第4章: 目录清理操作
```

**方案 B: 保持独立，移动到 workflows/ 子目录**

**输出:**
- `analysis/menu_ops_merge_plan.md`

---

#### 任务 1.4: README.md 内容审计 (3h)

**目标:** 识别 README.md 中可以迁移到专门文档的内容

**拆分计划:**
- `docs/setup/INSTALLATION.md` - 详细安装指南
- `docs/setup/CONFIGURATION.md` - 配置详解
- `docs/autocad/CONFIG_SYSTEM.md` - AutoCAD 配置系统完整文档

**目标 README.md 结构 (<200 行):**
```markdown
# CAD 文件自动化处理系统
## 项目简介 (30行)
## 核心特性 (20行)
## 快速开始 (50行) - 最简化版本
## 文档导航 (30行)
## 项目状态 (20行)
## 贡献指南 (20行)
## 许可证 (10行)
```

**输出:**
- `analysis/readme_split_plan.md`

---

### 阶段 2: 目录结构重组设计 (3 小时)

#### 任务 2.1: 设计新的目录分类体系 (2h)

**目标:** 设计 6 个功能分类子目录

**目录功能说明:**
- `setup/` - 环境搭建与配置
- `api/` - HTTP API 服务
- `autocad/` - AutoCAD 自动化
- `workflows/` - 工作流文档（含 bplot 子目录）
- `ocr/` - OCR 识别系统
- `troubleshooting/` - 故障排查

**命名规范:**
- 文档: `UPPER_SNAKE_CASE.md`
- 目录: `lowercase`

---

#### 任务 2.2: 制定文档迁移映射表 (1h)

**目标:** 为每个文档制定明确的迁移目标路径

**输出:**
- `analysis/migration_mapping.csv`

**映射表格式:**
```csv
原路径,操作类型,目标路径,备注
docs/API_GUIDE.md,移动,docs/api/API_GUIDE.md,直接移动
docs/BPLOT_AUTO_WORKFLOW_GUIDE.md,合并,docs/workflows/bplot/WORKFLOW_GUIDE.md,合并到工作流指南
```

---

### 阶段 3: 文档迁移与合并执行 (18 小时)

#### 任务 3.1: 创建新目录结构 (0.5h)

```bash
cd docs
mkdir -p setup api workflows/bplot ocr troubleshooting
```

---

#### 任务 3.2: 执行 BPLOT 文档合并 (6h)

**假设选择方案 A:**

1. **创建 `workflows/bplot/WORKFLOW_GUIDE.md`**
   - 合并 BPLOT_AUTO_WORKFLOW_GUIDE.md + BPLOT_CONFIGURABLE_GUIDE.md
   - 结构: 简介 -> 全自动流程 -> 配置化流程 -> 快速开始

2. **创建 `workflows/bplot/CONFIG_REFERENCE.md`**
   - 合并 BPLOT_CONFIG_GUIDE.md + BPLOT_CONFIG_FIX_NOTES.md
   - 结构: 配置参数 -> 配置示例 -> 已知问题 -> 故障排查

3. **移动 `BPLOT_VERSION_COMPARISON.md`**

**验证方法:**
- 检查新文档包含所有原文档的关键章节
- 交叉引用链接正确
- 代码示例完整

---

#### 任务 3.3: 执行 OCR 文档重命名与迁移 (1h)

```bash
mv UMI_OCR_API_GUIDE.md ocr/OCR_API_GUIDE.md
mv image_preprocessing_guide.md ocr/OCR_IMAGE_PREPROCESSING.md
mv ocr_preprocessing_config_guide.md ocr/OCR_CONFIG_REFERENCE.md
mv ocr_logging_user_guide.md ocr/OCR_LOGGING_GUIDE.md
```

---

#### 任务 3.4: 执行菜单操作文档处理 (4h 或 1h)

**方案 A (4h): 合并为 WORKFLOW_OPERATIONS.md**
- 按章节合并 4 个文档

**方案 B (1h): 移动到 workflows/ 子目录**
```bash
mv MENU_*.md workflows/
mv SCREENSHOT_EXTRACT_GUIDE.md workflows/
mv OUTPUT_DIR_CLEANUP_GUIDE.md workflows/
```

---

#### 任务 3.5: 拆分 README.md 并创建新文档 (5h)

1. **创建 `docs/setup/INSTALLATION.md`**
   - 从 README 提取 "安装步骤" 完整章节

2. **创建 `docs/setup/CONFIGURATION.md`**
   - 从 README 提取 "配置" 完整章节

3. **创建 `docs/autocad/CONFIG_SYSTEM.md`**
   - 从 README 提取 "AutoCAD 配置系统" 完整章节

4. **精简 README.md**
   - 目标: ≤ 200 行

**验证方法:**
- README.md 行数 ≤ 200
- 新文档包含所有原内容
- 快速开始步骤完整可执行

---

#### 任务 3.6: 移动其余独立文档 (1h)

```bash
# API 相关
mv API_GUIDE.md api/

# 工作流相关
mv DATABASE_CONFIG_GUIDE.md workflows/
mv ENHANCED_WORKFLOW_GUIDE.md workflows/

# 故障排查相关
mv PDF_EXTRACTION_TROUBLESHOOTING.md troubleshooting/PDF_EXTRACTION.md
mv OCR_URL_UPDATE_GUIDE.md troubleshooting/OCR_URL_UPDATE.md

# 环境搭建相关
mv TESSERACT_INSTALLATION_GUIDE.md setup/
```

---

### 阶段 4: 交叉引用更新 (9 小时)

#### 任务 4.1: 扫描所有文档链接 (2h)

```bash
# 查找所有 Markdown 链接
grep -r "\[.*\](.*\.md)" --include="*.md" . > analysis/all_links.txt

# 查找指向 docs/ 的链接
grep -r "docs/" --include="*.md" . > analysis/docs_links.txt
```

**输出:**
- `analysis/all_links.txt`
- `analysis/docs_links.txt`
- `analysis/broken_links.txt`

---

#### 任务 4.2: 批量更新文档链接 (4h)

**操作步骤:**
1. 创建链接替换脚本 `scripts/update_doc_links.py`
2. 定义路径映射规则
3. 批量替换所有文档中的链接
4. 手动检查复杂的相对路径链接

**路径映射示例:**
```python
path_mapping = {
    "docs/UMI_OCR_API_GUIDE.md": "docs/ocr/OCR_API_GUIDE.md",
    "docs/BPLOT_AUTO_WORKFLOW_GUIDE.md": "docs/workflows/bplot/WORKFLOW_GUIDE.md",
}
```

**输出:**
- `analysis/link_update_report.txt`

---

#### 任务 4.3: 创建文档中心导航 (2h)

**目标:** 创建 `docs/README.md` 作为统一的文档导航

**内容结构:**
```markdown
# 📚 CAD 文件自动化处理系统 - 文档中心

## 🚀 快速开始
## 📖 核心文档
  ### API 服务
  ### AutoCAD 自动化
  ### 工作流
  ### OCR 识别
  ### 环境搭建
  ### 故障排查
## 🔍 按角色查找
  ### 新用户
  ### 开发者
  ### 运维人员
## 📊 文档统计
## 🤝 贡献指南
```

---

#### 任务 4.4: 更新主 README.md 的文档导航 (1h)

在 README.md 添加 "📚 文档导航" 章节:

```markdown
## 📚 文档导航

完整的技术文档请访问 **[文档中心](docs/README.md)**。

### 主要文档分类
- **[快速开始](QUICK_START.md)**
- **[环境搭建](docs/setup/)**
- **[API 服务](docs/api/)**
- **[AutoCAD 自动化](docs/autocad/)**
- **[工作流](docs/workflows/)**
- **[OCR 识别](docs/ocr/)**
- **[故障排查](docs/troubleshooting/)**
```

---

### 阶段 5: 验证与发布 (10 小时)

#### 任务 5.1: 文档完整性验证 (3h)

**验证方法:**
1. 行数统计对比
```bash
# 统计原 docs/ 文档总行数
find docs/ -name "*.md" -exec wc -l {} + | tail -1
```

2. 关键词覆盖检查
3. 代码示例检查

**输出:**
- `analysis/completeness_report.md`
- 确认: ✅ 无内容丢失

---

#### 任务 5.2: 链接有效性验证 (2h)

```bash
npm install -g markdown-link-check
find . -name "*.md" -exec markdown-link-check {} \;
```

**输出:**
- `analysis/link_validation_report.txt`
- 确认: ✅ 所有链接有效

---

#### 任务 5.3: 用户体验测试 (2h)

**测试场景:**
1. 新用户场景 - 从 README.md 开始，能否顺利找到安装、配置文档
2. 开发者场景 - 能否快速找到 AutoCAD、工作流、OCR 技术文档
3. 问题排查场景 - 能否快速定位故障排查文档

**输出:**
- `analysis/ux_test_report.md`

---

#### 任务 5.4: 创建迁移日志 (1h)

**目标:** 创建 `docs/MIGRATION_LOG.md` 记录本次文档重组

**内容结构:**
```markdown
# 文档重组迁移日志

**迁移日期:** 2025-11-04

## 📊 变更统计
## 🔄 目录结构变更
## 📝 详细变更清单
  ### BPLOT 文档合并
  ### OCR 文档重命名
  ### 菜单操作文档处理
  ### README.md 拆分
## 🔗 链接更新
## ⚠️ 重要说明
## ✅ 验证结果
```

---

#### 任务 5.5: 备份原文档并提交 Git (1h)

```bash
# 备份原文档
mkdir -p _archived/docs_before_reorganization
cp -r docs/* _archived/docs_before_reorganization/
cp README.md _archived/docs_before_reorganization/README_original.md

# Git 提交
git add .
git commit -m "docs: 重组文档结构，消除冗余，建立清晰的信息架构

- 将 docs/ 目录重组为 6 个功能分类子目录
- 合并 5 个 BPLOT 文档为 3 个清晰的文档
- 统一 OCR 文档命名规范
- 精简 README.md 从 463 行到 195 行
- 创建 docs/README.md 作为文档中心导航
- 更新所有文档间的交叉引用链接
- 备份原文档到 _archived/docs_before_reorganization/

详细变更请参考: docs/MIGRATION_LOG.md"
```

---

#### 任务 5.6: 更新 CLAUDE.md 中的文档引用 (1h)

**目标:** 确保 AI 开发指南中的文档路径都是最新的

**操作步骤:**
1. 查找 CLAUDE.md 中所有 docs/ 路径引用
2. 根据迁移映射表更新路径
3. 验证更新后的引用正确

---

## ✅ 验收标准

### 阶段 1 验收标准
- [ ] BPLOT 文档重叠矩阵完成
- [ ] OCR 文档结构分析完成
- [ ] 菜单操作文档合并计划确定
- [ ] README 拆分计划明确

### 阶段 2 验收标准
- [ ] 新目录结构设计图完成
- [ ] 文档迁移映射表完成（21 个文档全覆盖）
- [ ] 命名规范文档化

### 阶段 3 验收标准
- [ ] 6 个新子目录创建完成
- [ ] BPLOT 文档合并完成
- [ ] OCR 文档重命名迁移完成
- [ ] README.md 精简到 ≤ 200 行
- [ ] 3 个新文档从 README 拆分创建

### 阶段 4 验收标准
- [ ] 所有文档链接扫描完成
- [ ] 批量链接更新完成
- [ ] docs/README.md 文档导航创建
- [ ] 主 README.md 文档导航章节添加
- [ ] CLAUDE.md 路径引用更新

### 阶段 5 验收标准
- [ ] 内容完整性验证通过
- [ ] 链接有效性验证通过
- [ ] 用户体验测试通过
- [ ] docs/MIGRATION_LOG.md 创建
- [ ] 原文档备份到 _archived/
- [ ] Git 提交完成

### 🎯 最终验收标准
- [ ] docs/ 根目录仅有 README.md 和 6 个子目录
- [ ] 文档总数从 21 个优化到 18 个
- [ ] README.md 行数 ≤ 200
- [ ] 所有文档链接有效
- [ ] 无内容丢失
- [ ] 文档分类清晰，查找便捷

---

## ⚠️ 待用户决策的问题

### 问题 1: BPLOT 文档合并方案选择

请选择：
- [ ] 方案 A - 合并为 3 个文档（推荐）
- [ ] 方案 B - 激进合并为 2 个文档
- [ ] 方案 C - 保守合并
- [ ] 其他方案：_______________

### 问题 2: 菜单操作文档处理方式

请选择：
- [ ] 方案 A - 合并为一个完整指南
- [ ] 方案 B - 保持独立，移动到子目录
- [ ] 其他方案：_______________

### 问题 3: 向后兼容策略

请选择：
- [ ] 方案 A - 不创建符号链接（推荐）
- [ ] 方案 B - 创建符号链接
- [ ] 方案 C - 创建路径变更说明文档
- [ ] 其他方案：_______________

### 问题 4: README.md 精简目标行数

请选择：
- [ ] 接受 180-200 行
- [ ] 建议更短：_______ 行
- [ ] 建议更长：_______ 行

---

## 📊 工作量预估

| 阶段 | 预估时间 | 关键任务 |
|------|---------|---------|
| 阶段 1：文档内容分析 | 12 小时 | BPLOT/OCR/菜单分析、README 审计 |
| 阶段 2：目录结构重组设计 | 3 小时 | 设计新目录、制定映射表 |
| 阶段 3：文档迁移与合并 | 18 小时 | BPLOT 合并、OCR 迁移、README 拆分 |
| 阶段 4：交叉引用更新 | 9 小时 | 链接扫描、批量更新、创建导航 |
| 阶段 5：验证与发布 | 10 小时 | 完整性验证、链接验证、Git 提交 |
| **总计** | **52 小时** | **约 6-7 个工作日** |

---

## 🛡️ 风险控制措施

### 风险 1: 内容丢失
- ✅ 完整备份原文档到 _archived/
- ✅ 行数统计对比验证
- ✅ Git 版本控制，可随时回滚

### 风险 2: 链接失效
- ✅ 扫描所有链接
- ✅ 批量更新并验证
- ✅ 使用工具全面检查

### 风险 3: 用户体验下降
- ✅ 用户场景测试
- ✅ 创建清晰的文档导航
- ✅ 保持 QUICK_START.md 不变

### 风险 4: 合并文档内容冲突
- ✅ 深入分析后再合并
- ✅ 保留版本对比文档
- ✅ 迁移日志记录合并细节

---

## 📝 用户反馈区域

请在此区域补充您对整体规划的意见和建议：

```
用户补充内容：

1. 对文档分类的建议：


2. 对合并方案的偏好：


3. 对命名规范的意见：


4. 其他特殊要求：


---
```

---

**规划完成日期:** 2025-11-04
**规划状态:** 待用户确认
**下一步:** 等待用户确认待决策问题后，开始阶段 1 执行

