# OCR地址更新指南

## 问题原因

虽然代码中的默认地址已更新为 `http://127.0.0.1:11224`，但**数据库中已存在的配置记录**仍然保存着旧地址 `http://10.3.19.121:1224`。

## 解决方案

### 方案1: 运行更新脚本（推荐）✅

在项目根目录运行：

```powershell
python scripts/update_ocr_url.py
```

**脚本会：**
1. ✅ 查找所有使用旧地址的配置
2. ✅ 批量更新为新地址 `http://127.0.0.1:11224`
3. ✅ 显示更新结果和当前配置

### 方案2: 手动执行SQL

连接到数据库后执行：

```sql
-- 查看当前配置
SELECT config_name, umi_ocr_service_url FROM autocad_configs;

-- 更新所有旧地址
UPDATE autocad_configs
SET umi_ocr_service_url = 'http://127.0.0.1:11224'
WHERE umi_ocr_service_url = 'http://10.3.19.121:1224';
```

## ⚠️ 重要：重启API服务

更新数据库后，**必须重启API服务**才能生效：

```powershell
# 1. 停止当前服务 (Ctrl+C)

# 2. 重新启动
.\start_api.ps1
```

## 验证是否生效

重启后再次调用API，日志中应该显示：

```
发送 OCR 请求到: http://127.0.0.1:11224/api/ocr
```

而不是：

```
❌ HTTPConnectionPool(host='10.3.19.121', port=1224): ...
```

## 技术说明

**为什么会有这个问题？**

1. **代码层**：默认值已更新 ✅
   - `11_bplot_auto_workflow.py`: `http://127.0.0.1:11224/api/ocr`
   - `9_configurable_workflow.py`: `http://127.0.0.1:11224`
   - `autocad_config.py` Model: `http://127.0.0.1:11224`

2. **数据库层**：已有记录仍是旧值 ❌
   - `autocad_configs` 表中的 `umi_ocr_service_url` 字段
   - 创建时使用了当时的默认值（旧地址）

3. **运行时**：API优先读取数据库配置
   ```python
   umi_ocr_base_url = self.config.umi_ocr_service_url or "http://127.0.0.1:11224"
   #                  ↑ 数据库中的值                     ↑ 代码默认值
   ```

**解决原理：**

更新数据库中的值，确保运行时读取到新地址。

---

**最后更新：** 2025-11-02
