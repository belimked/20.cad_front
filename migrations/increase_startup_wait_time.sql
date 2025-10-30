-- ============================================================================
-- 增加AutoCAD启动等待时间
-- 问题：COM接口连接超时（AutoCAD已启动但COM未就绪）
-- 解决：延长startup_wait_time从10秒到30秒
-- ============================================================================

USE cad_automation;

-- 增加启动等待时间
UPDATE `autocad_config`
SET startup_wait_time = 30.0  -- 从10秒增加到30秒
WHERE config_name = 'default';

-- 验证更新
SELECT
    config_name,
    startup_wait_time,
    startup_check_interval,
    post_startup_wait
FROM `autocad_config`
WHERE config_name = 'default';

-- ============================================================================
-- 说明
-- ============================================================================
-- startup_wait_time: 启动等待时间（秒），建议20-30秒
-- startup_check_interval: 检查间隔（秒），建议1秒
-- post_startup_wait: 启动后额外等待（秒），建议2秒
--
-- 如果还是超时，可以继续增加到40-60秒
-- ============================================================================
