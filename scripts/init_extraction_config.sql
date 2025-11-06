-- ============================================================
-- 初始化提取配置到 sys_dictionary 表
--
-- 该脚本用于初始化图号/材料/标题提取所需的配置参数
--
-- 使用方法：
--   mysql -h10.3.19.189 -P3313 -uroot -p'密码' cad_mgt < scripts/init_extraction_config.sql
--
-- Author: CAD Auto Processor Team
-- Date: 2025-11-05
-- ============================================================

USE cad_mgt;

-- 1. 标题提取排除词汇列表
INSERT INTO sys_dictionary (
    dict_type,
    dict_key,
    dict_value,
    dict_label,
    dict_description,
    is_active,
    sort_order,
    created_at,
    updated_at
)
VALUES (
    'extraction',
    'extraction_excluded_keywords',
    '["技术要求", "材料", "数量", "备注", "名称", "代号", "序号", "设计", "审核", "批准", "标记", "处数", "修改日期", "签名", "重量", "版号", "比例", "深圳市", "有限公司", "单重", "总重"]',
    '标题提取排除词汇',
    '从表格中提取标题时需要排除的通用词汇列表',
    TRUE,
    1,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    dict_value = VALUES(dict_value),
    dict_label = VALUES(dict_label),
    dict_description = VALUES(dict_description),
    updated_at = NOW();

-- 2. 材料关键字列表
INSERT INTO sys_dictionary (
    dict_type,
    dict_key,
    dict_value,
    dict_label,
    dict_description,
    is_active,
    sort_order,
    created_at,
    updated_at
)
VALUES (
    'extraction',
    'extraction_material_keywords',
    '["材料:", "Material:", "material:"]',
    '材料关键字列表',
    '用于识别材料信息的关键字（支持中英文）',
    TRUE,
    2,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    dict_value = VALUES(dict_value),
    dict_label = VALUES(dict_label),
    dict_description = VALUES(dict_description),
    updated_at = NOW();

-- 3. 提取规则参数
INSERT INTO sys_dictionary (
    dict_type,
    dict_key,
    dict_value,
    dict_label,
    dict_description,
    is_active,
    sort_order,
    created_at,
    updated_at
)
VALUES (
    'extraction',
    'extraction_rules',
    '{"min_chinese_chars": 4, "min_title_length": 4, "drawing_number_min_length": 10, "drawing_number_min_hyphens": 3}',
    '提取规则参数',
    '提取图号、标题、材料时使用的规则参数',
    TRUE,
    3,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE
    dict_value = VALUES(dict_value),
    dict_label = VALUES(dict_label),
    dict_description = VALUES(dict_description),
    updated_at = NOW();

-- ============================================================
-- 验证插入结果
-- ============================================================

SELECT
    '配置验证' AS '步骤',
    COUNT(*) AS '配置数量'
FROM sys_dictionary
WHERE dict_type = 'extraction' AND is_active = TRUE;

SELECT
    dict_key AS '配置键',
    dict_label AS '标签',
    LEFT(dict_value, 50) AS '配置值（前50字符）',
    is_active AS '启用',
    created_at AS '创建时间'
FROM sys_dictionary
WHERE dict_type = 'extraction'
ORDER BY sort_order;

-- ============================================================
-- 完成
-- ============================================================
SELECT '✅ 提取配置初始化完成!' AS '状态';
