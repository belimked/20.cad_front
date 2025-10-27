# 🗄️ MySQL 数据库配置 - 快速参考

## 📋 当前数据库连接信息

### 连接配置
```
服务器地址: 10.3.19.189
端口:       3313  (注意: 不是默认的 3306!)
用户名:     fangda
密码:       123456
数据库名:   cad_mgt
字符集:     utf8mb4
```

### 连接字符串
```
mysql+pymysql://fangda:123456@10.3.19.189:3313/cad_mgt?charset=utf8mb4
```

---

## 📍 配置文件位置

```
src/utils/database.py
第 80-92 行
```

---

## 🔧 如何修改配置

打开 `src/utils/database.py`，找到第 80-92 行:

```python
# 默认配置
db_config = {
    'host': '10.3.19.189',     # ← 改这里
    'port': 3313,               # ← 改这里
    'username': 'fangda',       # ← 改这里
    'password': '123456',       # ← 改这里
    'database': 'cad_mgt',      # ← 改这里
    'charset': 'utf8mb4',
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'echo': False
}
```

---

## ✅ 测试连接

```powershell
# 方式 1: 运行数据库模块
python src\utils\database.py

# 方式 2: 使用 MySQL 客户端
mysql -h 10.3.19.189 -P 3313 -u fangda -p123456 cad_mgt

# 方式 3: 初始化配置表 (会自动测试连接)
python scripts\init_autocad_config.py
```

---

## ⚠️ 安全提醒

**当前问题:**
- ❌ 密码明文存储在代码中
- ❌ 密码会被提交到 Git

**改进建议:**
- 使用环境变量
- 使用 .env 文件 (不要提交到 Git)
- 不同环境使用不同配置

---

## 📝 初始化检查清单

运行 `init_autocad_config.py` 前确认:

- [ ] MySQL 服务器运行中
- [ ] 数据库 `cad_mgt` 已创建
- [ ] 用户 `fangda` 有足够权限
- [ ] 网络可访问 `10.3.19.189:3313`
- [ ] pymysql 已安装

---

## 🆘 常见问题

### 连接超时
```
解决: 检查 MySQL 是否运行，防火墙是否开放 3313 端口
```

### 认证失败
```
解决: 确认用户名密码，检查用户权限
```

### 数据库不存在
```sql
解决: CREATE DATABASE cad_mgt CHARACTER SET utf8mb4;
```

---

详细配置说明见: **DATABASE_CONNECTION_CONFIG.md**
