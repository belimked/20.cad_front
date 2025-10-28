-- ========================================
-- 添加 Umi-OCR 图像边长限制参数到 autocad_config 表
-- Author: CAD Auto Processor Team
-- Date: 2025-10-27
-- ========================================

-- 添加 Umi-OCR 图像边长限制参数
ALTER TABLE autocad_config
ADD COLUMN umi_ocr_limit_side_len INT DEFAULT 2880 COMMENT 'Umi-OCR图像边长限制(像素): 960=标准, 2880=高精度, 4320=超高精度';

-- 更新现有配置（可选：为已有记录设置默认值）
UPDATE autocad_config
SET umi_ocr_limit_side_len = 2880
WHERE umi_ocr_limit_side_len IS NULL;
