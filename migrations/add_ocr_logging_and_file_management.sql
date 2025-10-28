-- OCR识别日志记录表
-- 记录每次OCR识别的详细信息和性能指标

CREATE TABLE IF NOT EXISTS ocr_recognition_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',

    -- 关联信息
    config_id INT NULL COMMENT '关联的配置ID (autocad_config.id)',
    task_log_id BIGINT NULL COMMENT '关联的任务日志ID (autocad_task_logs.id)',

    -- 识别信息
    target_text VARCHAR(100) NOT NULL COMMENT '目标文本',
    found BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否找到目标文本',
    matched_text VARCHAR(200) NULL COMMENT '匹配到的文本',
    confidence DECIMAL(5,4) NULL COMMENT '置信度 (0-1)',
    matched_version VARCHAR(50) NULL COMMENT '匹配到的预处理版本',
    position_x INT NULL COMMENT '位置X坐标',
    position_y INT NULL COMMENT '位置Y坐标',

    -- 时间统计
    total_time DECIMAL(10,3) NOT NULL COMMENT '总耗时(秒)',
    screenshot_time DECIMAL(10,3) NULL COMMENT '截图耗时(秒)',
    preprocessing_time DECIMAL(10,3) NULL COMMENT '预处理总耗时(秒)',
    ocr_time DECIMAL(10,3) NULL COMMENT 'OCR识别总耗时(秒)',
    merge_time DECIMAL(10,3) NULL COMMENT '结果合并耗时(秒)',

    -- 预处理统计
    preprocessing_methods TEXT NULL COMMENT '使用的预处理方法(JSON数组)',
    preprocessing_count INT DEFAULT 0 COMMENT '预处理图像数量',

    -- 识别统计
    ocr_results_summary TEXT NULL COMMENT 'OCR识别结果汇总(JSON)',
    total_texts_found INT DEFAULT 0 COMMENT '总共识别到的文本数量',
    unique_texts_count INT DEFAULT 0 COMMENT '去重后的唯一文本数量',

    -- 文件信息
    screenshot_dir VARCHAR(500) NULL COMMENT '截图保存目录',
    screenshots_saved INT DEFAULT 0 COMMENT '保存的截图数量',

    -- 元数据
    status VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT '状态: success/failed/partial',
    error_message TEXT NULL COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_config_id (config_id),
    INDEX idx_task_log_id (task_log_id),
    INDEX idx_target_text (target_text),
    INDEX idx_found (found),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='OCR识别日志表';


-- 预处理方法性能日志表（详细记录每个方法的性能）
CREATE TABLE IF NOT EXISTS ocr_preprocessing_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    recognition_log_id BIGINT NOT NULL COMMENT '关联的识别日志ID',

    -- 方法信息
    method_name VARCHAR(50) NOT NULL COMMENT '预处理方法名称',
    method_order INT NOT NULL COMMENT '执行顺序',

    -- 性能指标
    processing_time DECIMAL(10,3) NOT NULL COMMENT '预处理耗时(秒)',
    ocr_time DECIMAL(10,3) NOT NULL COMMENT 'OCR识别耗时(秒)',
    total_time DECIMAL(10,3) NOT NULL COMMENT '总耗时(秒)',

    -- 识别结果
    texts_found INT DEFAULT 0 COMMENT '识别到的文本数量',
    target_found BOOLEAN DEFAULT FALSE COMMENT '是否找到目标文本',
    max_confidence DECIMAL(5,4) NULL COMMENT '最高置信度',
    avg_confidence DECIMAL(5,4) NULL COMMENT '平均置信度',

    -- 文件信息
    image_path VARCHAR(500) NULL COMMENT '预处理图像路径',
    image_size_kb INT NULL COMMENT '图像大小(KB)',

    -- 元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_recognition_log_id (recognition_log_id),
    INDEX idx_method_name (method_name),
    INDEX idx_target_found (target_found),
    FOREIGN KEY (recognition_log_id) REFERENCES ocr_recognition_logs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='OCR预处理方法性能日志表';


-- 添加配置字段到 autocad_config 表
ALTER TABLE autocad_config
ADD COLUMN ocr_screenshot_base_dir VARCHAR(500) NULL COMMENT 'OCR截图基础目录' AFTER ocr_preprocessing_params,
ADD COLUMN ocr_screenshot_timestamp_format VARCHAR(50) DEFAULT '%Y%m%d_%H%M%S' COMMENT '时间戳格式' AFTER ocr_screenshot_base_dir,
ADD COLUMN ocr_file_cleanup_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用文件清理' AFTER ocr_screenshot_timestamp_format,
ADD COLUMN ocr_file_cleanup_strategy VARCHAR(20) DEFAULT 'archive' COMMENT '清理策略: delete/archive/none' AFTER ocr_file_cleanup_enabled,
ADD COLUMN ocr_file_archive_dir VARCHAR(500) NULL COMMENT '归档目录' AFTER ocr_file_cleanup_strategy,
ADD COLUMN ocr_file_retention_days INT DEFAULT 7 COMMENT '文件保留天数' AFTER ocr_file_archive_dir,
ADD COLUMN ocr_enable_detailed_logging BOOLEAN DEFAULT TRUE COMMENT '是否启用详细日志记录' AFTER ocr_file_retention_days;


-- 插入字典配置项
INSERT INTO sys_dictionary (dict_type, dict_key, dict_label, dict_value, dict_description, sort_order, extra_data) VALUES
-- 清理策略
('ocr_cleanup_strategy', 'delete', '删除', 'delete', '直接删除旧文件，不保留', 1, '{"risk_level": "high", "space_saved": "maximum"}'),
('ocr_cleanup_strategy', 'archive', '归档', 'archive', '移动到归档目录保存', 2, '{"risk_level": "low", "space_saved": "none"}'),
('ocr_cleanup_strategy', 'none', '不清理', 'none', '不清理旧文件，持续累积', 3, '{"risk_level": "none", "space_saved": "none"}'),

-- 时间戳格式
('ocr_timestamp_format', '%Y%m%d_%H%M%S', '年月日_时分秒', '%Y%m%d_%H%M%S', '20251027_143025', 1, '{"example": "20251027_143025"}'),
('ocr_timestamp_format', '%Y%m%d_%H%M%S_%f', '年月日_时分秒_微秒', '%Y%m%d_%H%M%S_%f', '20251027_143025_123456', 2, '{"example": "20251027_143025_123456"}'),
('ocr_timestamp_format', '%Y-%m-%d_%H-%M-%S', '年-月-日_时-分-秒', '%Y-%m-%d_%H-%M-%S', '2025-10-27_14-30-25', 3, '{"example": "2025-10-27_14-30-25"}'),
('ocr_timestamp_format', '%Y%m%d', '年月日', '%Y%m%d', '20251027', 4, '{"example": "20251027"}');
