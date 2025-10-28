-- ========================================
-- 添加 Umi-OCR 并行线程数参数到 autocad_config 表
-- Author: CAD Auto Processor Team (老王优化版)
-- Date: 2025-10-28
-- ========================================

-- 添加 Umi-OCR 并行线程数参数
ALTER TABLE autocad_config
ADD COLUMN umi_ocr_max_workers INT DEFAULT 8 COMMENT 'Umi-OCR并行线程数(1-16): 建议值=CPU核心数或8';

-- 更新现有配置（为已有记录设置默认值）
UPDATE autocad_config
SET umi_ocr_max_workers = 8
WHERE umi_ocr_max_workers IS NULL;
