-- 数据库迁移脚本：为 autocad_config 表添加 OCR 预处理配置字段
-- Author: CAD Auto Processor Team
-- Date: 2025-10-27

-- 添加 OCR 预处理方法字段
ALTER TABLE `autocad_config`
ADD COLUMN `ocr_preprocessing_methods` TEXT NULL COMMENT 'OCR预处理方法列表（JSON格式）' AFTER `menu_operations`;

-- 添加 OCR 预处理参数字段
ALTER TABLE `autocad_config`
ADD COLUMN `ocr_preprocessing_params` TEXT NULL COMMENT 'OCR预处理参数配置（JSON格式）' AFTER `ocr_preprocessing_methods`;

-- 更新现有配置，设置默认推荐方法
UPDATE `autocad_config`
SET `ocr_preprocessing_methods` = '["binary_adaptive", "binary_otsu", "high_contrast", "denoise_bilateral"]'
WHERE `ocr_preprocessing_methods` IS NULL;

-- 查看更新结果
SELECT
    id,
    config_name,
    ocr_preprocessing_methods,
    ocr_preprocessing_params
FROM `autocad_config`;
