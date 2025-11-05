-- ============================================================================
-- MinerU 集成数据库迁移脚本
-- 创建日期: 2025-11-05
-- 描述: 添加 MinerU PDF 识别功能支持
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. 扩展 autocad_config 表 - 添加 MinerU 配置字段
-- ----------------------------------------------------------------------------

ALTER TABLE autocad_config
ADD COLUMN IF NOT EXISTS mineru_api_url VARCHAR(200) DEFAULT 'http://127.0.0.1:18080' COMMENT 'MinerU API 服务地址',
ADD COLUMN IF NOT EXISTS mineru_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用 MinerU 识别',
ADD COLUMN IF NOT EXISTS mineru_timeout_per_file INTEGER DEFAULT 30 COMMENT '单个 PDF 处理超时（秒）',
ADD COLUMN IF NOT EXISTS mineru_pdf_render_timeout INTEGER DEFAULT 300 COMMENT 'PDF 渲染超时（秒）',
ADD COLUMN IF NOT EXISTS mineru_batch_size INTEGER DEFAULT 10 COMMENT '批量处理数量（一次提交多少个 PDF）',
ADD COLUMN IF NOT EXISTS mineru_lang_list VARCHAR(100) DEFAULT '["ch"]' COMMENT '识别语言列表（JSON数组）',
ADD COLUMN IF NOT EXISTS mineru_parse_method VARCHAR(20) DEFAULT 'auto' COMMENT '解析方法: auto/ocr/txt',
ADD COLUMN IF NOT EXISTS mineru_table_enable BOOLEAN DEFAULT TRUE COMMENT '是否启用表格识别',
ADD COLUMN IF NOT EXISTS mineru_return_md BOOLEAN DEFAULT TRUE COMMENT '是否返回 Markdown',
ADD COLUMN IF NOT EXISTS mineru_return_content_list BOOLEAN DEFAULT TRUE COMMENT '是否返回结构化内容列表',
ADD COLUMN IF NOT EXISTS mineru_extraction_patterns TEXT COMMENT '图号提取正则表达式（JSON格式）';

-- ----------------------------------------------------------------------------
-- 2. 创建图号关联表 - 存储 DWG 与图号的关系
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dwg_drawing_sheets (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    task_id VARCHAR(64) NOT NULL COMMENT '关联任务ID（dwg_process_tasks.task_id）',
    dwg_filename VARCHAR(255) COMMENT 'DWG文件名',
    pdf_filename VARCHAR(255) COMMENT 'PDF文件名',
    pdf_path VARCHAR(1000) COMMENT 'PDF文件完整路径',

    -- 提取的图号信息
    sheet_number VARCHAR(100) COMMENT '图号',
    sheet_title VARCHAR(255) COMMENT '图纸标题',
    version VARCHAR(50) COMMENT '版本号',
    scale VARCHAR(50) COMMENT '比例',
    drawing_date DATE COMMENT '绘图日期',

    -- 元数据
    page_number INT COMMENT '页码（如果PDF是多页）',
    recognition_confidence FLOAT COMMENT '识别置信度（0-1）',
    extraction_source VARCHAR(50) DEFAULT 'mineru' COMMENT '提取来源: mineru/manual/other',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_task_id (task_id),
    INDEX idx_sheet_number (sheet_number),
    INDEX idx_dwg_filename (dwg_filename),
    INDEX idx_pdf_filename (pdf_filename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='DWG图纸图号关联表';

-- ----------------------------------------------------------------------------
-- 3. 创建识别结果详细表 - 存储完整的识别内容
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dwg_recognition_results (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    task_id VARCHAR(64) NOT NULL COMMENT '关联任务ID',
    pdf_filename VARCHAR(255) COMMENT 'PDF文件名',
    pdf_path VARCHAR(1000) COMMENT 'PDF文件完整路径',

    -- 识别内容
    markdown_content LONGTEXT COMMENT 'Markdown格式全文内容',
    content_list JSON COMMENT 'MinerU返回的结构化内容列表',
    table_data JSON COMMENT '表格数据（JSON数组）',
    technical_requirements TEXT COMMENT '技术要求文本',

    -- 识别状态
    status VARCHAR(32) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
    error_message TEXT COMMENT '错误信息',

    -- 性能指标
    processing_time_seconds FLOAT COMMENT '处理耗时（秒）',
    file_size_bytes BIGINT COMMENT '文件大小（字节）',
    page_count INT COMMENT '页数',

    -- 元数据
    mineru_api_version VARCHAR(50) COMMENT 'MinerU API 版本',
    parse_method VARCHAR(20) COMMENT '使用的解析方法',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_pdf_filename (pdf_filename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MinerU PDF识别结果表';

-- ----------------------------------------------------------------------------
-- 4. 验证创建结果
-- ----------------------------------------------------------------------------

-- 显示表结构
SHOW CREATE TABLE dwg_drawing_sheets;
SHOW CREATE TABLE dwg_recognition_results;

-- 显示 autocad_config 新增字段
SHOW COLUMNS FROM autocad_config LIKE 'mineru%';
