-- 更新Umi-OCR服务地址
-- 从 http://10.3.19.121:1224 改为 http://127.0.0.1:11224

-- 更新 autocad_configs 表中的 umi_ocr_service_url
UPDATE autocad_configs
SET umi_ocr_service_url = 'http://127.0.0.1:11224'
WHERE umi_ocr_service_url = 'http://10.3.19.121:1224';

-- 验证更新结果
SELECT
    config_name,
    umi_ocr_service_url,
    umi_ocr_api_path,
    umi_ocr_enabled
FROM autocad_configs;
