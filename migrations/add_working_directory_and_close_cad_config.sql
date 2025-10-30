-- ============================================================================
-- 数据库迁移脚本
-- 功能：添加工作目录和关闭CAD配置字段
-- 创建时间: 2025-10-30
-- 作者: 老王团队
-- 描述:
--   1. 添加工作目录相关字段（working_directory, copy_to_working_dir）
--   2. 添加任务完成后关闭CAD配置字段（close_cad_after_completion）
-- ============================================================================

USE cad_automation;

-- 添加工作目录字段
ALTER TABLE `autocad_config`
ADD COLUMN `working_directory` VARCHAR(1000) NULL COMMENT '工作目录（文件处理时的工作路径）' AFTER `dwg_file_path`;

-- 添加是否复制到工作目录字段
ALTER TABLE `autocad_config`
ADD COLUMN `copy_to_working_dir` BOOLEAN DEFAULT FALSE COMMENT '是否复制文件到工作目录' AFTER `working_directory`;

-- 添加任务完成后关闭CAD字段
ALTER TABLE `autocad_config`
ADD COLUMN `close_cad_after_completion` BOOLEAN DEFAULT TRUE COMMENT '任务完成后是否关闭 CAD 进程' AFTER `force_close_existing`;

-- ============================================================================
-- 验证迁移
-- ============================================================================

-- 查看表结构（验证新字段已添加）
DESC `autocad_config`;

-- 查看配置数据
SELECT
    id,
    config_name,
    dwg_file_path,
    working_directory,
    copy_to_working_dir,
    force_close_existing,
    close_cad_after_completion
FROM `autocad_config`;

-- ============================================================================
-- 使用示例
-- ============================================================================

-- 示例1：更新默认配置，启用工作目录和关闭CAD
-- UPDATE `autocad_config`
-- SET
--     working_directory = 'F:/cad/working_dir',
--     copy_to_working_dir = TRUE,
--     close_cad_after_completion = TRUE
-- WHERE config_name = 'default';

-- 示例2：查询启用了工作目录复制的配置
-- SELECT * FROM `autocad_config` WHERE copy_to_working_dir = TRUE;

-- 示例3：查询不关闭CAD的配置（开发调试用）
-- SELECT * FROM `autocad_config` WHERE close_cad_after_completion = FALSE;

-- ============================================================================
-- 回滚脚本（如需回滚，请执行以下SQL）
-- ============================================================================

-- ALTER TABLE `autocad_config` DROP COLUMN `working_directory`;
-- ALTER TABLE `autocad_config` DROP COLUMN `copy_to_working_dir`;
-- ALTER TABLE `autocad_config` DROP COLUMN `close_cad_after_completion`;
