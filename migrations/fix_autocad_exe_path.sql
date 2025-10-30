-- ============================================================================
-- 修复AutoCAD可执行文件路径
-- 问题：单反斜杠被Python字符串转义处理导致路径错误
-- 解决：使用双反斜杠或正斜杠
-- ============================================================================

USE cad_automation;

-- 方案1：使用双反斜杠（Windows标准）
UPDATE `autocad_config`
SET autocad_exe_path = 'C:\\Program Files\\Autodesk\\AutoCAD 2014\\acad.exe'
WHERE config_name = 'default';

-- 或者方案2：使用正斜杠（Python友好，Windows也支持）
-- UPDATE `autocad_config`
-- SET autocad_exe_path = 'C:/Program Files/Autodesk/AutoCAD 2014/acad.exe'
-- WHERE config_name = 'default';

-- 验证更新
SELECT
    config_name,
    autocad_exe_path,
    LENGTH(autocad_exe_path) as path_length
FROM `autocad_config`
WHERE config_name = 'default';

-- ============================================================================
-- 说明
-- ============================================================================
-- 正确格式示例：
-- 1. 双反斜杠：C:\\Program Files\\Autodesk\\AutoCAD 2014\\acad.exe
-- 2. 正斜杠：  C:/Program Files/Autodesk/AutoCAD 2014/acad.exe
--
-- 错误格式（不要使用）：
-- 单反斜杠：C:\Program Files\Autodesk\AutoCAD 2014\acad.exe
-- （会被Python转义，导致路径损坏）
-- ============================================================================
