-- ============================================================================
-- 添加 MinerU 输出目录配置字段
-- 创建日期: 2025-11-05
-- 描述: 解决 MinerU 服务端 output 目录不存在的问题
-- ============================================================================

-- 添加 mineru_output_dir 字段
ALTER TABLE autocad_config
ADD COLUMN IF NOT EXISTS mineru_output_dir VARCHAR(1000) 
    DEFAULT 'F:\\cad\\caddd\\cadpython\\CAD_AutoProcessor\\downloads\\000_outputs' 
    COMMENT 'MinerU PDF 识别输出目录（服务端绝对路径）';
