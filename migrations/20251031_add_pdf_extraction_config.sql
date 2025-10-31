-- 数据库迁移脚本: 添加PDF提取配置字段
-- 日期: 2025-10-31
-- 版本: v2.0
-- 描述: 为 autocad_config 表添加 PDF 提取相关配置字段（包含日志、子目录、多线程支持）

-- 添加 PDF 提取配置字段
ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用PDF信息提取（在输出PDF后自动提取图纸信息）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_output_dir VARCHAR(1000) COMMENT 'PDF提取结果输出目录（为空则使用输出目录下的pdf_extraction子目录）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_jsonl_subdir VARCHAR(100) DEFAULT 'jsonl' COMMENT 'JSONL文件子目录名（相对于提取结果目录）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_info_subdir VARCHAR(100) DEFAULT 'extracted_info' COMMENT '提取信息JSON文件子目录名（相对于提取结果目录）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_umi_service_url VARCHAR(200) DEFAULT 'http://10.3.19.63:11224' COMMENT 'PDF提取使用的Umi-OCR文档API地址';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_mode VARCHAR(20) DEFAULT 'fullPage' COMMENT 'PDF提取模式：fullPage(全页)/mixed(混合)，推荐fullPage';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_parser VARCHAR(20) DEFAULT 'multi_line' COMMENT '文本解析器：multi_line(多列)/single_line(单列)，推荐multi_line';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_generate_csv BOOLEAN DEFAULT TRUE COMMENT '是否生成CSV汇总报告';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_csv_filename VARCHAR(100) DEFAULT 'extraction_summary.csv' COMMENT 'CSV汇总报告文件名';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_fail_on_error BOOLEAN DEFAULT FALSE COMMENT 'PDF提取失败是否中断整个流程（False=记录错误但继续）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_max_retries INTEGER DEFAULT 2 COMMENT '单个PDF提取失败时的最大重试次数';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_enable_logging BOOLEAN DEFAULT TRUE COMMENT '是否启用数据库日志记录（记录到dwg_task步骤日志）';

ALTER TABLE autocad_config ADD COLUMN IF NOT EXISTS pdf_extraction_parallel_workers INTEGER DEFAULT 1 COMMENT '并行处理PDF的线程数（1=单线程，2-8=多线程，推荐CPU核心数）';

-- 更新现有配置示例（可选，根据需要执行）
-- 启用PDF提取功能（推荐配置）
-- UPDATE autocad_config SET
--     pdf_extraction_enabled = TRUE,
--     pdf_extraction_parallel_workers = 4,
--     pdf_extraction_enable_logging = TRUE
-- WHERE config_name = 'default';

-- 验证添加的字段
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    TABLE_NAME = 'autocad_config'
    AND COLUMN_NAME LIKE 'pdf_extraction%'
ORDER BY
    ORDINAL_POSITION;

-- 查看示例配置
-- SELECT
--     config_name,
--     pdf_extraction_enabled,
--     pdf_extraction_parallel_workers,
--     pdf_extraction_enable_logging,
--     pdf_extraction_jsonl_subdir,
--     pdf_extraction_info_subdir
-- FROM autocad_config;
