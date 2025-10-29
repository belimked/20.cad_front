-- ============================================================================
-- DWG文件处理任务表 - 迁移脚本
-- 创建时间: 2025-10-29
-- 作者: 老王团队
-- 描述: 新增HTTP服务所需的任务表和步骤日志表
-- ============================================================================

-- 任务表（主表）
CREATE TABLE IF NOT EXISTS `dwg_process_tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `task_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '任务唯一ID',
  `dwg_url` TEXT NOT NULL COMMENT 'DWG文件下载地址',
  `dwg_filename` VARCHAR(255) COMMENT '原始文件名',
  `local_path` TEXT COMMENT '本地保存路径',
  `file_size` BIGINT COMMENT '文件大小（字节）',
  `status` VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '状态: pending/downloading/processing/completed/failed',
  `current_step` VARCHAR(64) COMMENT '当前步骤',
  `progress` INT DEFAULT 0 COMMENT '进度百分比（0-100）',
  `error_message` TEXT COMMENT '错误信息',
  `config_name` VARCHAR(64) DEFAULT 'default' COMMENT '使用的配置名称',
  `config_id` INT COMMENT '配置ID（关联autocad_config表）',
  `autocad_task_log_id` INT COMMENT '关联的AutoCAD任务日志ID',
  `callback_url` TEXT COMMENT '完成后回调地址',
  `callback_status` VARCHAR(32) COMMENT '回调状态: pending/success/failed',
  `callback_retry_count` INT DEFAULT 0 COMMENT '回调重试次数',
  `started_at` DATETIME COMMENT '开始时间',
  `completed_at` DATETIME COMMENT '完成时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_config_id` (`config_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='DWG文件处理任务表';

-- 任务步骤日志表（子表）
CREATE TABLE IF NOT EXISTS `dwg_task_steps` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `task_id` VARCHAR(64) NOT NULL COMMENT '关联任务ID',
  `step_name` VARCHAR(128) NOT NULL COMMENT '步骤名称',
  `step_order` INT NOT NULL COMMENT '步骤顺序',
  `status` VARCHAR(32) NOT NULL COMMENT '状态: running/completed/failed',
  `message` TEXT COMMENT '步骤消息',
  `error_message` TEXT COMMENT '错误信息',
  `metadata` JSON COMMENT '步骤元数据（JSON格式）',
  `started_at` DATETIME COMMENT '开始时间',
  `completed_at` DATETIME COMMENT '完成时间',
  `duration_seconds` DECIMAL(10, 3) COMMENT '执行时长（秒）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_step_order` (`step_order`),
  INDEX `idx_status` (`status`),

  FOREIGN KEY (`task_id`) REFERENCES `dwg_process_tasks`(`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务步骤日志表';

-- 添加外键约束（如果需要关联现有表）
-- ALTER TABLE `dwg_process_tasks`
-- ADD CONSTRAINT `fk_config_id`
-- FOREIGN KEY (`config_id`) REFERENCES `autocad_config`(`id`) ON DELETE SET NULL;

-- ALTER TABLE `dwg_process_tasks`
-- ADD CONSTRAINT `fk_autocad_task_log_id`
-- FOREIGN KEY (`autocad_task_log_id`) REFERENCES `autocad_task_logs`(`id`) ON DELETE SET NULL;
