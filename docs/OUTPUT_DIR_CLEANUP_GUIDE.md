# 输出目录自动清理功能

## 📋 功能简介

在工作流程开始前自动清理指定的输出目录，确保每次运行都是从干净的状态开始。

### 应用场景

- ✅ 清理CAD批量打图的输出文件
- ✅ 清理临时生成的中间文件
- ✅ 确保输出目录整洁
- ✅ 支持清理前自动备份

---

## 🎯 核心特性

1. **自动清理**：工作流程开始前自动执行
2. **可配置路径**：支持自定义输出目录
3. **备份选项**：可选择清理前自动备份
4. **安全机制**：仅删除文件，不影响系统
5. **详细日志**：显示清理进度和结果

---

## 🚀 快速开始

### 1. 数据库迁移（仅首次）

```bash
python scripts/migrate_add_output_dir_cleanup.py
```

**输出：**
```
================================================================================
数据库迁移 - 添加输出目录清理配置字段
================================================================================
✅ 迁移成功!
新增字段:
  1. output_dir_cleanup_enabled (BOOLEAN) - 是否启用清理
  2. output_dir_path (VARCHAR(1000)) - 输出目录路径
  3. output_dir_backup_before_cleanup (BOOLEAN) - 是否备份
  4. output_dir_backup_path (VARCHAR(1000)) - 备份目录路径
```

### 2. 启用清理功能

```bash
# 默认配置（不备份）
python scripts/enable_output_cleanup.py

# 自定义配置
python scripts/enable_output_cleanup.py \
    --config default \
    --output-dir "F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs" \
    --backup \
    --backup-dir "F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs_backup"
```

**输出：**
```
✅ 配置已更新!

📋 输出目录清理配置:
  启用状态: ✅ 已启用
  输出目录: F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs
  清理前备份: ❌ 否
  备份目录: （自动生成）
```

### 3. 运行工作流程

```bash
python research/autocad_com_api/9_configurable_workflow.py
```

**输出示例：**
```
================================================================================
AutoCAD 自动化工作流程（数据库配置）
================================================================================
配置: default
文件: F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg
================================================================================

▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶
步骤 0: 清理输出目录
▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶
📁 输出目录: F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs
  📊 待清理: 125 个文件 (45.23 MB)

  🧹 开始清理...
  ✅ 清理完成: 删除 125 个文件

[后续步骤...]
```

---

## ⚙️ 配置说明

### 数据库字段

| 字段 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `output_dir_cleanup_enabled` | BOOLEAN | `FALSE` | 是否启用清理 |
| `output_dir_path` | VARCHAR(1000) | `F:\cad\...\outputs` | 输出目录路径 |
| `output_dir_backup_before_cleanup` | BOOLEAN | `FALSE` | 清理前是否备份 |
| `output_dir_backup_path` | VARCHAR(1000) | `NULL` | 备份目录（NULL=自动生成） |

### 命令行参数

```bash
python scripts/enable_output_cleanup.py [OPTIONS]

Options:
  --config TEXT        配置名称 (默认: default)
  --output-dir TEXT    输出目录路径
  --backup             清理前备份
  --backup-dir TEXT    备份目录路径（可选）
```

---

## 📚 使用示例

### 示例1：基本使用（不备份）

```bash
python scripts/enable_output_cleanup.py
```

### 示例2：启用备份（自动生成备份目录）

```bash
python scripts/enable_output_cleanup.py --backup
```

备份目录自动命名为：`outputs_backup_20251028_105126`

### 示例3：启用备份（指定备份目录）

```bash
python scripts/enable_output_cleanup.py \
    --backup \
    --backup-dir "F:\cad\backup\outputs"
```

### 示例4：自定义输出目录

```bash
python scripts/enable_output_cleanup.py \
    --output-dir "D:\MyProject\output"
```

### 示例5：完整配置

```bash
python scripts/enable_output_cleanup.py \
    --config default \
    --output-dir "F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs" \
    --backup \
    --backup-dir "F:\cad\backup\$(date +%Y%m%d)"
```

---

## 🔧 手动配置（SQL）

如果需要直接修改数据库：

```sql
-- 启用清理（不备份）
UPDATE autocad_config
SET output_dir_cleanup_enabled = TRUE,
    output_dir_path = 'F:\\cad\\caddd\\cadpython\\CAD_AutoProcessor\\outputs'
WHERE config_name = 'default';

-- 启用清理（带备份）
UPDATE autocad_config
SET output_dir_cleanup_enabled = TRUE,
    output_dir_path = 'F:\\cad\\caddd\\cadpython\\CAD_AutoProcessor\\outputs',
    output_dir_backup_before_cleanup = TRUE,
    output_dir_backup_path = 'F:\\cad\\backup\\outputs'
WHERE config_name = 'default';

-- 禁用清理
UPDATE autocad_config
SET output_dir_cleanup_enabled = FALSE
WHERE config_name = 'default';
```

---

## 📊 清理行为说明

### 清理范围

- ✅ 删除指定目录下所有文件
- ✅ 删除空的子目录
- ❌ 不删除目录本身
- ❌ 不删除隐藏文件（如果有权限限制）

### 备份机制

**不备份（默认）：**
- 直接清理，不保留任何文件
- 速度快，不占用额外空间

**启用备份：**
- 清理前将整个目录复制到备份位置
- 保留所有文件和目录结构
- 如果备份失败，清理操作中止

### 备份目录命名

- **指定备份目录**：使用指定路径
- **自动生成**：`{原目录名}_backup_{时间戳}`
  - 例如：`outputs_backup_20251028_105126`

---

## 🐛 故障排查

### 问题1：清理失败

**现象：**
```
❌ 清理失败: [Errno 13] Permission denied
```

**原因：**
- 文件被占用
- 没有删除权限

**解决：**
1. 关闭占用文件的程序
2. 以管理员权限运行
3. 检查文件权限

### 问题2：备份失败

**现象：**
```
❌ 备份失败: [Errno 28] No space left on device
```

**原因：**
- 磁盘空间不足
- 备份目录无法创建

**解决：**
1. 清理磁盘空间
2. 更换备份目录
3. 禁用备份功能

### 问题3：清理很慢

**原因：**
- 文件数量过多
- 网络驱动器延迟

**优化：**
1. 考虑禁用备份
2. 定期手动清理
3. 使用本地磁盘

---

## ⚠️ 注意事项

1. **重要文件备份**：清理会永久删除文件，确保重要文件已备份
2. **路径检查**：确认输出目录路径正确，避免误删其他目录
3. **权限要求**：确保有删除文件的权限
4. **磁盘空间**：启用备份时确保有足够空间
5. **测试环境**：首次使用建议先在测试环境验证

---

## 📝 最佳实践

### 推荐配置

**生产环境：**
```bash
python scripts/enable_output_cleanup.py \
    --backup \
    --backup-dir "F:\cad\backup\outputs"
```

**开发/测试环境：**
```bash
python scripts/enable_output_cleanup.py
```

### 定期维护

1. **检查备份目录**：定期清理旧备份
2. **监控磁盘空间**：避免空间不足
3. **验证清理结果**：确认文件正确清理

---

## 🔗 相关文档

- [全屏截图提取功能](SCREENSHOT_EXTRACT_GUIDE.md)
- [菜单操作完整指南](MENU_OPERATIONS_GUIDE.md)
- [数据库配置指南](DATABASE_CONFIG_GUIDE.md)

---

## 📝 更新日志

### v1.0.0 (2025-10-28)

- ✅ 新增输出目录自动清理功能
- ✅ 支持清理前备份
- ✅ 支持自定义输出目录路径
- ✅ 提供配置管理脚本
- ✅ 完整的错误处理和日志

---

## 🎉 总结

输出目录清理功能特点：

1. ✅ **自动执行**：工作流程开始前自动清理
2. ✅ **可选备份**：支持清理前自动备份
3. ✅ **灵活配置**：路径和选项可配置
4. ✅ **安全可靠**：完善的错误处理
5. ✅ **详细日志**：清理过程清晰可见

**一键启用：**

```bash
python scripts/enable_output_cleanup.py
```

**立即生效：**

```bash
python research/autocad_com_api/9_configurable_workflow.py
```

就这么简单！🚀
