-- ========================================
-- 添加 Umi-OCR 配置字段到 autocad_config 表
-- Author: CAD Auto Processor Team
-- Date: 2025-10-27
-- ========================================

-- 添加 Umi-OCR 服务配置字段
ALTER TABLE autocad_config
ADD COLUMN umi_ocr_service_url VARCHAR(200) DEFAULT 'http://10.3.19.121:1224' COMMENT 'Umi-OCR服务地址',
ADD COLUMN umi_ocr_api_path VARCHAR(100) DEFAULT '/api/ocr' COMMENT 'Umi-OCR API路径',
ADD COLUMN umi_ocr_timeout INT DEFAULT 30 COMMENT 'Umi-OCR请求超时时间(秒)',
ADD COLUMN umi_ocr_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用Umi-OCR';

-- 更新现有配置（可选：为已有记录设置默认值）
UPDATE autocad_config
SET
    umi_ocr_service_url = 'http://10.3.19.121:1224',
    umi_ocr_api_path = '/api/ocr',
    umi_ocr_timeout = 30,
    umi_ocr_enabled = TRUE
WHERE umi_ocr_service_url IS NULL;
