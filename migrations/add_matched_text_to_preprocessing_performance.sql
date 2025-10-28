-- ========================================
-- 添加最匹配文字字段到 ocr_preprocessing_performance 表
-- Author: CAD Auto Processor Team
-- Date: 2025-10-27
-- ========================================

-- 添加最匹配文字字段
ALTER TABLE ocr_preprocessing_performance
ADD COLUMN matched_text VARCHAR(200) NULL COMMENT '最匹配的文字' AFTER target_found;
