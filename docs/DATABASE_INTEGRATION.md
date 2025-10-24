# 数据库集成文档

## 📋 概述

CAD 自动化处理系统已集成 MySQL 数据库支持，用于：
- 存储系统配置字典
- 管理远程下载 URL
- 记录 API 使用统计

---

## 🗄️ 数据库配置

### 连接信息
```yaml
# config/config.yaml
database:
  host: "10.3.19.189"
  port: 3313
  username: "fangda"
  password: "123456"
  database: "cad_mgt"
  charset: "utf8mb4"
```

### 连接池配置
```yaml
pool_size: 5           # 连接池大小
max_overflow: 10       # 最大溢出连接数
pool_timeout: 30       # 连接超时（秒）
pool_recycle: 3600     # 连接回收时间（秒）
echo: false            # 是否显示 SQL（调试用）
```

---

## 📊 数据库表结构

### 1. sys_dictionary（系统字典表）

用于存储系统配置参数和字典数据。

**表结构：**
```sql
CREATE TABLE `sys_dictionary` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `dict_type` VARCHAR(50) NOT NULL COMMENT '字典类型',
  `dict_key` VARCHAR(100) NOT NULL COMMENT '字典键',
  `dict_value` TEXT NOT NULL COMMENT '字典值',
  `dict_label` VARCHAR(200) COMMENT '字典标签',
  `dict_description` TEXT COMMENT '字典描述',
  `sort_order` INT DEFAULT 0 COMMENT '排序顺序',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  `extra_data` TEXT COMMENT '扩展数据（JSON）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(50) COMMENT '创建人',
  `updated_by` VARCHAR(50) COMMENT '更新人',
  `remark` TEXT COMMENT '备注',
  INDEX `idx_dict_type_key` (`dict_type`, `dict_key`),
  INDEX `idx_is_active` (`is_active`)
) COMMENT='系统字典表';
```

**字典类型说明：**
- `system`: 系统配置（app_name, app_version, environment）
- `download`: 下载配置（chunk_size, max_retries, timeout）
- `autocad`: AutoCAD 配置（install_path, timeout）

### 2. download_urls（远程下载 URL 配置表）

专门存储 CAD 文件下载相关的 URL 配置。

**表结构：**
```sql
CREATE TABLE `download_urls` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `url_name` VARCHAR(100) NOT NULL UNIQUE COMMENT 'URL 名称',
  `url_value` TEXT NOT NULL COMMENT 'URL 地址',
  `url_type` VARCHAR(50) DEFAULT 'api' COMMENT 'URL 类型',
  `url_description` VARCHAR(200) COMMENT 'URL 描述',
  `http_method` VARCHAR(10) DEFAULT 'GET' COMMENT 'HTTP 方法',
  `headers` TEXT COMMENT '请求头（JSON）',
  `timeout` INT DEFAULT 30 COMMENT '超时时间（秒）',
  `auth_type` VARCHAR(20) COMMENT '认证类型',
  `auth_value` VARCHAR(500) COMMENT '认证凭证',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  `priority` INT DEFAULT 0 COMMENT '优先级',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_used_at` DATETIME COMMENT '最后使用时间',
  `use_count` INT DEFAULT 0 COMMENT '使用次数',
  `success_count` INT DEFAULT 0 COMMENT '成功次数',
  `fail_count` INT DEFAULT 0 COMMENT '失败次数',
  `remark` TEXT COMMENT '备注',
  INDEX `idx_url_type` (`url_type`),
  INDEX `idx_is_active` (`is_active`),
  INDEX `idx_priority` (`priority`, `is_active`)
) COMMENT='远程下载URL配置表';
```

**预置 URL 配置：**
- `api_files_pending`: 获取待下载文件列表
- `api_file_download`: 下载指定文件
- `api_task_complete`: 标记任务完成
- `api_task_fail`: 标记任务失败
- `api_result_upload`: 上传处理结果

---

## 🚀 快速开始

### 1. 初始化数据库

运行初始化脚本创建表和初始数据：

```bash
python scripts/init_database.py
```

**脚本功能：**
- ✅ 创建所有数据库表
- ✅ 初始化系统字典数据
- ✅ 初始化 URL 配置
- ✅ 验证初始化结果

**预期输出：**
```
============================================================
  CAD 自动化处理系统 - 数据库初始化
============================================================

测试数据库连接...
✅ 数据库连接成功

开始创建数据库表...
✅ 数据库表创建成功

开始初始化字典数据...
✅ 字典数据初始化成功，共 8 条记录

开始初始化下载 URL 配置...
✅ URL 配置初始化成功，共 5 条记录

开始验证初始化结果...
字典表记录数: 8
URL 配置表记录数: 5
✅ 验证完成

============================================================
  ✅ 数据库初始化完成！
============================================================
```

### 2. 测试数据库连接

```python
from src.utils.database import get_db_manager

db_manager = get_db_manager()

# 测试连接
if db_manager.test_connection():
    print("✅ 数据库连接成功")

# 使用会话
with db_manager.session_scope() as session:
    result = session.execute("SELECT DATABASE()")
    print(f"当前数据库: {result.scalar()}")
```

---

## 💻 使用示例

### 1. 字典服务使用

```python
from src.services.dict_service import DictionaryService

# 获取字典值
app_name = DictionaryService.get_value('system', 'app_name', 'Unknown')
print(f"应用名称: {app_name}")

# 获取某类型的所有字典
download_configs = DictionaryService.get_by_type('download')
for config in download_configs:
    print(f"{config.dict_key} = {config.dict_value}")

# 创建新字典
new_dict = DictionaryService.create({
    'dict_type': 'custom',
    'dict_key': 'my_key',
    'dict_value': 'my_value',
    'dict_label': '自定义配置',
    'created_by': 'admin'
})

# 更新字典
DictionaryService.update(dict_id=1, update_data={
    'dict_value': 'new_value',
    'updated_by': 'admin'
})
```

### 2. URL 服务使用

```python
from src.services.dict_service import DownloadUrlService

# 获取 URL 地址
api_url = DownloadUrlService.get_url_value('api_files_pending')
print(f"API URL: {api_url}")

# 获取带参数的 URL（支持模板替换）
download_url = DownloadUrlService.get_url_value(
    'api_file_download',
    file_id='123'
)
print(f"下载 URL: {download_url}")

# 获取所有 API 类型的 URL
api_urls = DownloadUrlService.get_by_type('api')
for url in api_urls:
    print(f"{url.url_name}: {url.url_value}")

# 记录 URL 使用情况
DownloadUrlService.record_usage('api_files_pending', success=True)

# 获取所有活动的 URL（字典格式）
all_urls = DownloadUrlService.get_all_active_urls()
```

### 3. 下载器集成使用

下载器已自动集成数据库，会优先从数据库读取 URL 配置：

```python
from src.modules.downloader import CadFileDownloader

# 创建下载器（会自动从数据库获取 URL）
downloader = CadFileDownloader()

# 获取文件列表（使用数据库中的 api_files_pending URL）
files = downloader.get_pending_files()

# 下载文件（自动记录使用统计）
for file_info in files:
    downloader.download_file(file_info)
```

**工作流程：**
1. 下载器尝试从数据库获取 URL（`download_urls` 表）
2. 如果数据库中存在，使用数据库配置
3. 如果不存在，回退使用 YAML 配置
4. 每次调用 API 后，自动记录使用统计

---

## 🔧 数据库管理

### 查看字典数据

```sql
-- 查看所有字典
SELECT * FROM sys_dictionary ORDER BY dict_type, sort_order;

-- 查看特定类型的字典
SELECT * FROM sys_dictionary WHERE dict_type = 'system' AND is_active = 1;

-- 查看字典统计
SELECT dict_type, COUNT(*) as count
FROM sys_dictionary
GROUP BY dict_type;
```

### 查看 URL 配置

```sql
-- 查看所有 URL
SELECT * FROM download_urls ORDER BY priority DESC;

-- 查看 URL 使用统计
SELECT
    url_name,
    use_count,
    success_count,
    fail_count,
    ROUND(success_count * 100.0 / NULLIF(use_count, 0), 2) as success_rate
FROM download_urls
WHERE use_count > 0
ORDER BY use_count DESC;

-- 查看最近使用的 URL
SELECT url_name, last_used_at, use_count
FROM download_urls
WHERE last_used_at IS NOT NULL
ORDER BY last_used_at DESC
LIMIT 10;
```

### 常用管理操作

```sql
-- 添加新的 URL 配置
INSERT INTO download_urls (url_name, url_value, url_type, url_description, priority)
VALUES ('api_custom', 'https://api.example.com/custom', 'api', '自定义 API', 50);

-- 更新 URL
UPDATE download_urls
SET url_value = 'https://new.api.com/endpoint'
WHERE url_name = 'api_files_pending';

-- 禁用 URL
UPDATE download_urls
SET is_active = 0
WHERE url_name = 'api_old_endpoint';

-- 清零统计数据
UPDATE download_urls
SET use_count = 0, success_count = 0, fail_count = 0, last_used_at = NULL;
```

---

## 📝 最佳实践

### 1. URL 配置管理

- ✅ **使用数据库管理 URL**：所有远程 API URL 应存储在数据库中
- ✅ **设置优先级**：重要的 URL 设置更高的优先级
- ✅ **启用统计**：利用自动统计功能监控 API 使用情况
- ✅ **环境隔离**：不同环境使用不同的 URL 配置

### 2. 字典数据管理

- ✅ **分类清晰**：使用 `dict_type` 对字典进行分类
- ✅ **命名规范**：`dict_key` 使用小写下划线命名
- ✅ **软删除**：使用 `is_active` 标志而非物理删除
- ✅ **版本控制**：重要配置变更记录在 `remark` 中

### 3. 性能优化

- ✅ **使用连接池**：已配置连接池，避免频繁创建连接
- ✅ **批量操作**：大量数据操作使用批量提交
- ✅ **索引优化**：已创建常用查询索引
- ✅ **定期清理**：定期清理过期数据和日志

---

## 🐛 故障排查

### 连接失败

```python
# 检查连接
from src.utils.database import get_db_manager

db_manager = get_db_manager()
if not db_manager.test_connection():
    print("❌ 连接失败，请检查：")
    print("1. 数据库服务是否运行")
    print("2. 连接信息是否正确")
    print("3. 网络是否畅通")
    print("4. 用户权限是否足够")
```

### 查看日志

日志位置：`logs/cad_processor_*.log`

```bash
# 查看最新日志
tail -f logs/cad_processor_*.log | grep -i database
```

### 常见问题

**Q: 数据库连接超时**
A: 检查 `pool_timeout` 配置，增加超时时间或减少并发连接数

**Q: URL 未从数据库读取**
A: 确保已运行 `scripts/init_database.py` 初始化数据

**Q: 统计数据不准确**
A: 检查是否有异常导致 `record_usage` 调用失败

---

## 📚 相关文件

- `src/utils/database.py` - 数据库连接管理器
- `src/models/dictionary.py` - 数据库模型定义
- `src/services/dict_service.py` - 字典和 URL 服务
- `scripts/init_database.py` - 数据库初始化脚本
- `config/config.yaml` - 数据库配置

---

**文档版本：** 1.0
**更新日期：** 2025-10-24
**状态：** ✅ 已完成
