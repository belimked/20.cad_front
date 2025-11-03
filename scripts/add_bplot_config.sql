-- 添加 bplot 配置到 autocad_configs 表
-- 配置化的批量打印工作流

-- 检查是否已存在 bplot 配置
SELECT COUNT(*) as count FROM autocad_configs WHERE config_name = 'bplot';

-- 如果不存在则插入
INSERT INTO autocad_configs (
    config_name,
    description,
    workflow_steps,
    ocr_enabled,
    ocr_screenshot_enabled,
    ocr_screenshot_base_dir,
    ocr_screenshot_timestamp_format,
    ocr_file_retention_days,
    ocr_enable_detailed_logging,
    umi_ocr_enabled,
    umi_ocr_service_url,
    umi_ocr_api_path,
    umi_ocr_timeout,
    umi_ocr_limit_side_len,
    ocr_preprocessing_methods,
    created_at,
    updated_at
)
SELECT
    'bplot',
    'AutoCAD批量打印(bplot)全自动化工作流 - OCR识别按钮并自动输入',
    '[
        {
            "type": "command",
            "method": "keyboard",
            "text": "_.bplot",
            "description": "执行BPLOT命令（批量打印）",
            "wait_time": 5.0
        },
        {
            "type": "menu",
            "method": "ocr",
            "text": "设置批量打印图纸表",
            "description": "点击设置批量打印图纸表按钮",
            "alternative_texts": ["选择批量打印图纸", "选择图纸", "图纸表", "Select Drawings", "Add Sheets"],
            "wait_time": 1.0
        },
        {
            "type": "input",
            "method": "keyboard",
            "text": "all",
            "description": "键盘输入all选择所有图纸",
            "wait_time": 2.0
        },
        {
            "type": "screenshot_extract",
            "target_pattern": "选中图纸[:\\\\s]*(\\\\d+)",
            "save_to": "selected_sheets",
            "description": "提取选中图纸数量",
            "required": false,
            "wait_time": 0.5
        },
        {
            "type": "screenshot_extract",
            "target_pattern": "共\\\\s*(\\\\d+)\\\\s*页",
            "save_to": "total_pages",
            "description": "提取总页数",
            "alternative_patterns": ["Total[:\\\\s]*(\\\\d+)", "(\\\\d+)\\\\s*sheets", "页数[:\\\\s]*(\\\\d+)"],
            "required": false,
            "wait_time": 0.5
        }
    ]',
    1,
    1,
    'screenshots/bplot_auto',
    '%Y%m%d_%H%M%S',
    7,
    1,
    1,
    'http://127.0.0.1:11224',
    '/api/ocr',
    60,
    2880,
    '["original", "grayscale", "binary_otsu", "binary_adaptive", "denoise_gaussian", "high_contrast"]',
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM autocad_configs WHERE config_name = 'bplot'
);

-- 验证插入结果
SELECT
    config_name,
    description,
    ocr_enabled,
    umi_ocr_enabled,
    created_at
FROM autocad_configs
WHERE config_name = 'bplot';
