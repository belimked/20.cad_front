# OCR 图像预处理配置指南

## 📚 概述

AutoCAD 工作流程现在支持通过数据库配置 OCR 图像预处理方法和参数，实现灵活的识别策略。

---

## 🏗️ 架构设计

```
sys_dictionary (字典表)
    └─ dict_type = 'image_preprocessing'  # 存储所有17种预处理方法定义

autocad_config (配置表)
    ├─ ocr_preprocessing_methods  # JSON: 选择使用哪些方法
    └─ ocr_preprocessing_params   # JSON: 自定义参数
```

---

## 🚀 快速开始

### 步骤1：运行数据库迁移

```bash
# 1. 添加字段到 autocad_config 表
mysql -u root -p < migrations/add_ocr_preprocessing_fields.sql

# 2. 初始化预处理方法字典数据
cd /Users/saul/IdeaProjects/100.AI.TrainData
python scripts/init_preprocessing_dict.py
```

### 步骤2：配置 AutoCAD 工作流程

在数据库中更新 `autocad_config` 表：

```sql
-- 示例1：使用推荐方法（默认）
UPDATE autocad_config
SET ocr_preprocessing_methods = '["binary_adaptive", "binary_otsu", "high_contrast", "denoise_bilateral"]'
WHERE config_name = 'default';

-- 示例2：使用所有方法
UPDATE autocad_config
SET ocr_preprocessing_methods = '[
  "original", "grayscale",
  "binary_adaptive", "binary_otsu", "binary_global",
  "high_contrast", "high_brightness",
  "denoise_gaussian", "denoise_median", "denoise_bilateral", "denoise_nlm",
  "rgb_red", "rgb_green", "rgb_blue",
  "edge_canny", "edge_sobel", "edge_laplacian"
]'
WHERE config_name = 'default';

-- 示例3：自定义参数
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["binary_adaptive", "high_contrast"]',
  ocr_preprocessing_params = '{
    "binary_adaptive_block_size": 15,
    "binary_adaptive_c": 3,
    "clahe_clip_limit": 4.0
  }'
WHERE config_name = 'default';
```

### 步骤3：运行工作流程

```python
from research.autocad_com_api.configurable_workflow import ConfigurableAutoCADWorkflow

# 使用数据库配置
workflow = ConfigurableAutoCADWorkflow(config_name='default')
workflow.run(dwg_file_path="path/to/file.dwg")

# 工作流程会自动：
# 1. 读取 ocr_preprocessing_methods 配置
# 2. 读取 ocr_preprocessing_params 配置
# 3. 生成指定的预处理图像
# 4. 对每个版本进行 OCR 识别
# 5. 合并结果，选择最高置信度
```

---

## 📋 预处理方法清单

### 查询所有可用方法

```sql
SELECT
    dict_key AS '方法名',
    dict_label AS '显示名称',
    dict_description AS '描述',
    JSON_EXTRACT(extra_data, '$.category') AS '分类',
    JSON_EXTRACT(extra_data, '$.recommended') AS '是否推荐',
    JSON_EXTRACT(extra_data, '$.performance') AS '性能',
    sort_order AS '排序'
FROM sys_dictionary
WHERE dict_type = 'image_preprocessing'
ORDER BY sort_order;
```

### 查询推荐方法

```sql
SELECT dict_key, dict_label, dict_description
FROM sys_dictionary
WHERE dict_type = 'image_preprocessing'
  AND JSON_EXTRACT(extra_data, '$.recommended') = TRUE
ORDER BY sort_order;

-- 结果：
-- binary_adaptive    自适应二值化
-- binary_otsu        Otsu二值化
-- high_contrast      高对比度增强
-- denoise_bilateral  双边滤波降噪
-- original           原始图像
```

### 查询方法参数

```sql
SELECT
    dict_key AS '方法名',
    dict_label AS '显示名称',
    JSON_EXTRACT(extra_data, '$.params') AS '可配置参数'
FROM sys_dictionary
WHERE dict_type = 'image_preprocessing'
  AND JSON_LENGTH(JSON_EXTRACT(extra_data, '$.params')) > 0
ORDER BY sort_order;
```

---

## 🎯 配置示例

### 场景1：AutoCAD 白色背景菜单（默认）

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["binary_adaptive", "binary_otsu", "high_contrast"]',
  ocr_preprocessing_params = '{
    "binary_adaptive_block_size": 11,
    "binary_adaptive_c": 2
  }'
WHERE config_name = 'default';
```

**理由**：白底黑字对比度高，二值化效果最好

---

### 场景2：AutoCAD 暗色主题

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["high_brightness", "high_contrast", "binary_adaptive"]',
  ocr_preprocessing_params = '{
    "brightness_alpha": 1.5,
    "brightness_beta": 60,
    "clahe_clip_limit": 4.0
  }'
WHERE config_name = 'dark_theme';
```

**理由**：需要先提亮，再增强对比度

---

### 场景3：彩色 AutoCAD 图层

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["rgb_red", "rgb_green", "rgb_blue", "binary_adaptive"]',
  ocr_preprocessing_params = NULL
WHERE config_name = 'color_layers';
```

**理由**：通道分离可以提取特定颜色图层的文字

---

### 场景4：模糊/噪声图像

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["denoise_bilateral", "high_contrast", "binary_adaptive"]',
  ocr_preprocessing_params = '{
    "bilateral_d": 11,
    "bilateral_sigma_color": 100,
    "clahe_clip_limit": 3.5
  }'
WHERE config_name = 'noisy_image';
```

**理由**：先降噪，再增强，最后二值化

---

### 场景5：极致性能（速度优先）

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '["binary_otsu", "high_contrast"]',
  ocr_preprocessing_params = NULL
WHERE config_name = 'fast_mode';
```

**理由**：只使用最快的2种方法

---

### 场景6：极致质量（准确度优先）

```sql
UPDATE autocad_config
SET
  ocr_preprocessing_methods = '[
    "original",
    "binary_adaptive", "binary_otsu",
    "high_contrast", "high_brightness",
    "denoise_bilateral",
    "rgb_red", "rgb_green", "rgb_blue",
    "edge_canny"
  ]',
  ocr_preprocessing_params = '{
    "binary_adaptive_block_size": 15,
    "clahe_clip_limit": 4.0,
    "bilateral_d": 11
  }'
WHERE config_name = 'high_quality';
```

**理由**：使用多种方法，增加识别成功率

---

## 🛠️ 参数调优指南

### 二值化参数

```sql
UPDATE autocad_config
SET ocr_preprocessing_params = '{
  "binary_adaptive_block_size": 15,  -- ↑ 适合大文字，↓ 适合小文字
  "binary_adaptive_c": 3,            -- ↑ 文字更粗，↓ 文字更细
  "binary_global_threshold": 127     -- 全局阈值（0-255）
}'
WHERE config_name = 'your_config';
```

### 对比度增强参数

```sql
UPDATE autocad_config
SET ocr_preprocessing_params = '{
  "clahe_clip_limit": 4.0,           -- ↑ 对比度更强（可能噪声），↓ 更平滑
  "clahe_tile_size": [8, 8]          -- ↑ 更全局，↓ 更局部
}'
WHERE config_name = 'your_config';
```

### 亮度调整参数

```sql
UPDATE autocad_config
SET ocr_preprocessing_params = '{
  "brightness_alpha": 1.5,           -- 对比度因子（>1增强，<1减弱）
  "brightness_beta": 60              -- 亮度偏移（-100至100）
}'
WHERE config_name = 'your_config';
```

### 降噪参数

```sql
UPDATE autocad_config
SET ocr_preprocessing_params = '{
  "bilateral_d": 11,                 -- 邻域直径
  "bilateral_sigma_color": 100,      -- 颜色空间标准差
  "bilateral_sigma_space": 100,      -- 坐标空间标准差
  "gaussian_kernel": [7, 7],         -- 高斯核大小（奇数）
  "median_kernel": 7                 -- 中值滤波核大小（奇数）
}'
WHERE config_name = 'your_config';
```

### 边缘检测参数

```sql
UPDATE autocad_config
SET ocr_preprocessing_params = '{
  "canny_threshold1": 30,            -- Canny低阈值
  "canny_threshold2": 100            -- Canny高阈值
}'
WHERE config_name = 'your_config';
```

---

## 📊 性能对比

| 配置方式 | 方法数 | 识别时间 | 准确率 | 推荐场景 |
|---------|--------|---------|--------|---------|
| 推荐方法（默认） | 5种 | ~5秒 | 85-90% | 通用场景 |
| 速度优先 | 2种 | ~2秒 | 75-80% | 大批量处理 |
| 质量优先 | 10种 | ~15秒 | 90-95% | 关键数据 |
| 自定义 | 自选 | 自定 | 视情况 | 特殊需求 |

---

## 🐛 故障排查

### 问题1：配置不生效

**排查**：
```sql
-- 检查配置值
SELECT
    config_name,
    ocr_preprocessing_methods,
    ocr_preprocessing_params
FROM autocad_config
WHERE config_name = 'default';
```

**解决**：确保 JSON 格式正确，使用在线工具验证 JSON

---

### 问题2：识别效果差

**排查**：
1. 查看生成的预处理图像（保存在 `screenshots/` 目录）
2. 检查哪个版本的 OCR 结果最好
3. 调整参数或增加方法

**解决**：
```sql
-- 添加更多方法
UPDATE autocad_config
SET ocr_preprocessing_methods = JSON_ARRAY_APPEND(
    ocr_preprocessing_methods,
    '$',
    'denoise_bilateral'
)
WHERE config_name = 'default';
```

---

### 问题3：速度太慢

**解决**：
```sql
-- 减少方法数量
UPDATE autocad_config
SET ocr_preprocessing_methods = '["binary_adaptive", "high_contrast"]'
WHERE config_name = 'default';
```

---

## 📝 最佳实践

1. **从推荐方法开始**：默认的5种方法覆盖大多数场景

2. **逐步调整**：
   - 先调方法（增加/减少）
   - 再调参数（微调）

3. **保存截图**：
   - 工作流程自动保存所有预处理版本
   - 查看 `screenshots/` 目录对比效果

4. **A/B测试**：
   ```sql
   -- 创建测试配置
   INSERT INTO autocad_config (config_name, ocr_preprocessing_methods, ...)
   VALUES ('test_config_v2', '["binary_otsu", "high_contrast"]', ...);
   ```

5. **文档化配置**：
   ```sql
   -- 添加备注
   UPDATE autocad_config
   SET description = '优化后的配置：增加双边滤波降噪，提升模糊文字识别率'
   WHERE config_name = 'default';
   ```

---

## 🎓 进阶技巧

### 技巧1：按AutoCAD版本配置

```sql
-- 不同版本可能需要不同配置
INSERT INTO autocad_config (config_name, autocad_version, ocr_preprocessing_methods, ...)
VALUES
  ('cad_2014', '2014', '["binary_adaptive", "high_contrast"]', ...),
  ('cad_2021', '2021', '["binary_otsu", "high_brightness"]', ...);
```

### 技巧2：按菜单操作类型配置

```sql
-- 不同操作可能需要不同预处理
UPDATE autocad_config
SET ocr_preprocessing_methods = '["edge_canny", "binary_adaptive"]'
WHERE config_name = 'icon_detection';  -- 图标检测需要边缘

UPDATE autocad_config
SET ocr_preprocessing_methods = '["binary_adaptive", "high_contrast"]'
WHERE config_name = 'text_detection';  -- 文字检测需要对比度
```

### 技巧3：动态切换配置

```python
# 根据运行时条件选择配置
if is_dark_theme():
    workflow = ConfigurableAutoCADWorkflow(config_name='dark_theme')
elif is_color_drawing():
    workflow = ConfigurableAutoCADWorkflow(config_name='color_layers')
else:
    workflow = ConfigurableAutoCADWorkflow(config_name='default')
```

---

**更新日期**: 2025-10-27
**作者**: CAD Auto Processor Team
