# AutoCAD 菜单操作完整配置指南

## 🎯 从数据库配置自动执行菜单操作

本指南说明如何将菜单操作（包括OCR识别）添加到数据库配置，实现完全自动化执行。

---

## 📋 支持的操作类型

### 1. AutoCAD命令
直接执行AutoCAD命令

### 2. 菜单点击（键盘/鼠标）
- 有快捷键：自动使用Alt+键方式
- 无快捷键：使用pywinauto鼠标点击

### 3. OCR文字识别（推荐⭐⭐⭐⭐⭐）
- **无需截图**
- **无需手动测试**
- 只需输入文字
- 自动识别并点击
- **推荐使用Tesseract** - 中文UI小字体识别最佳

---

## ⚙️ OCR方案配置（首次使用）

### 推荐：Tesseract OCR（中文识别最佳）

**为什么选择Tesseract**:
- ✅ 中文UI小字体识别准确率90%+
- ✅ 轻量快速（~50MB安装包）
- ✅ 免费开源
- ✅ 已自动集成到工作流程

**快速安装**:

1. 安装Python库:
```bash
pip install pytesseract
```

2. 下载并安装Tesseract引擎:
   - 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
   - **重要**: 安装时勾选 **Chinese (Simplified) - chi_sim** 语言包

3. 验证安装:
```bash
tesseract --version
tesseract --list-langs  # 应该看到 chi_sim
```

**详细安装指南**: 参见 `docs/TESSERACT_INSTALLATION_GUIDE.md`

**备选方案**: 如果无法安装Tesseract，系统会自动回退到EasyOCR（识别质量稍差）

---

## 🚀 完整使用流程

### 方式一：使用配置工具（推荐）

#### 步骤1：查看配置列表

```bash
# 激活虚拟环境
venv\Scripts\activate

# 查看所有配置
python scripts\autocad_config_manager.py list
```

**输出示例**：
```
配置列表:
  [1] default - 默认配置
  [2] fast - 快速配置
  [3] stable - 稳定配置
```

#### 步骤2：添加菜单操作

```bash
# 为default配置添加菜单操作
python scripts\add_menu_operations.py 1
```

**交互过程**：
```
============================================================
添加菜单操作
============================================================

操作类型:
  [1] AutoCAD命令
  [2] 菜单点击（键盘/鼠标）
  [3] OCR文字识别（推荐）
  [0] 完成并保存

请选择操作类型 (0-3): 3

OCR文字识别 - 智能方案
  只需输入菜单文字，系统自动识别并点击
  示例: '依云'、'帮助'、'工具' 等

请输入要识别的菜单文字: 依云
点击后等待时间（秒，默认1.0）: 1

✅ 已添加OCR识别: '依云'

【已添加操作】（共1个）
  1. OCR识别: '依云' (等待1.0秒)

------------------------------------------------------------

请选择操作类型 (0-3): 0

============================================================
✅ 菜单操作已保存
============================================================
```

#### 步骤3：运行工作流程

```bash
# 直接运行，自动从数据库读取并执行
python research\autocad_com_api\configurable_workflow.py
```

**预期输出**：
```
================================================================================
AutoCAD 自动化工作流程（数据库配置）
================================================================================
配置: default
文件: F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg
================================================================================

步骤 1: 关闭现有 CAD 并打开指定文件
✅ AutoCAD 已启动
✅ 文件已打开

步骤 2: 验证文件已加载
✅ 文件验证成功！

步骤 3: 执行菜单操作
📋 操作 1/1: menu
  [模式] OCR文字识别
  查找文本: '依云'
  截图完成: 1920x1080
  ✅ 找到文本: '依云' (置信度:0.98)
  位置: (856, 234)
  ✅ 已点击文本

✅ 菜单操作完成

================================================================================
✅ 自动化流程完成！
================================================================================
```

---

### 方式二：直接修改数据库（高级）

#### 1. 查看现有配置

```bash
python scripts\autocad_config_manager.py show 1
```

#### 2. 直接操作数据库

使用MySQL客户端或Navicat等工具，编辑`autocad_configs`表的`menu_operations`字段：

```json
[
  {
    "type": "command",
    "command": "ZOOM",
    "wait_time": 0.5
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "依云",
    "wait_time": 1.0
  },
  {
    "type": "menu",
    "path": ["帮助(H)", "欢迎屏幕(W)"],
    "wait_time": 1.0
  }
]
```

---

## 📦 完整配置示例

### 示例1：纯OCR方案

```json
[
  {
    "type": "menu",
    "method": "ocr",
    "text": "依云",
    "wait_time": 1.0
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "工具",
    "wait_time": 1.0
  }
]
```

### 示例2：混合方案

```json
[
  {
    "type": "command",
    "command": "REGEN",
    "wait_time": 0.5
  },
  {
    "type": "menu",
    "path": ["帮助(H)", "欢迎屏幕(W)"],
    "wait_time": 1.0
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "依云",
    "wait_time": 1.0
  },
  {
    "type": "command",
    "command": "QSAVE",
    "wait_time": 0.5
  }
]
```

**注意**: 使用OCR方法前，请确保已安装Tesseract OCR（见上文"OCR方案配置"）

### 示例3：图像识别方案（备用）

```json
[
  {
    "type": "menu",
    "method": "image",
    "icon_path": "menu_icons/依云.png",
    "confidence": 0.8,
    "wait_time": 1.0
  }
]
```

---

## 🔧 配置参数说明

### 通用参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| type | string | ✅ | 操作类型：command 或 menu |
| wait_time | float | ✅ | 操作后等待时间（秒） |

### command 类型参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| command | string | ✅ | AutoCAD命令名（大写） |

### menu 类型参数（根据method不同）

#### method: auto（默认）

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| path | array | ✅ | 菜单路径，如["帮助(H)", "欢迎屏幕(W)"] |

#### method: ocr（推荐）

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| text | string | ✅ | 要识别的文字，如"依云" |

#### method: image（备用）

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| icon_path | string | ✅ | 图标文件路径（相对于项目根目录） |
| confidence | float | ❌ | 匹配置信度（默认0.8） |

---

## 🎬 完整演示流程

### 从零开始配置"依云"菜单点击

```bash
# 1. 拉取最新代码
git pull origin cad

# 2. 安装OCR依赖（首次需要）
venv\Scripts\activate
pip install paddleocr

# 3. 查看配置列表
python scripts\autocad_config_manager.py list
# 假设要配置ID=1的default配置

# 4. 添加OCR操作
python scripts\add_menu_operations.py 1
# 选择 [3] OCR文字识别
# 输入: 依云
# 输入等待时间: 1（或直接回车使用默认值）
# 选择 [0] 完成并保存

# 5. 查看配置确认
python scripts\autocad_config_manager.py show 1

# 6. 启动AutoCAD并打开DWG文件
# （手动操作）

# 7. 运行自动化流程
python research\autocad_com_api\configurable_workflow.py

# 8. 观察输出，确认"依云"菜单被点击
```

---

## ⚡ 使用start.bat菜单

```bash
# 运行主菜单
start.bat

# 选择 [6] 运行工作流程 (default)
# 或 [7] 运行工作流程 (stable)

# 系统会自动：
# 1. 从数据库读取配置
# 2. 关闭并重启AutoCAD
# 3. 打开指定DWG文件
# 4. 执行所有菜单操作（包括OCR识别）
```

---

## 📊 方法对比

| 方法 | 配置难度 | 执行速度 | 成功率 | 推荐度 |
|-----|---------|---------|-------|--------|
| **OCR识别** | ⭐ 极简 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐⭐ |
| 键盘快捷键 | ⭐⭐ 简单 | ⭐⭐⭐⭐⭐ 快 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐ |
| 鼠标点击 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 较快 | ⭐⭐⭐ 中等 | ⭐⭐⭐ |
| 图像识别 | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐ 较快 | ⭐⭐⭐ 中等 | ⭐⭐ |

---

## 💡 最佳实践

### 1. 优先使用OCR

对于没有快捷键的菜单（如"依云"），直接使用OCR方案：

```json
{"type": "menu", "method": "ocr", "text": "依云"}
```

### 2. 有快捷键优先使用键盘

对于有快捷键的菜单，使用传统路径方式（自动用键盘）：

```json
{"type": "menu", "path": ["帮助(H)", "欢迎屏幕(W)"]}
```

### 3. 图像识别作为备选

只有在OCR和鼠标点击都失败时，才考虑图像识别：

```json
{"type": "menu", "method": "image", "icon_path": "menu_icons/特殊按钮.png"}
```

### 4. 合理设置等待时间

- 命令：0.5秒
- 菜单点击：1.0秒
- OCR识别：1.0-2.0秒（首次识别稍慢）

---

## 🔍 故障排查

### 问题1：OCR未找到文本

**现象**：
```
❌ 未找到文本: '依云'
```

**解决**：
1. 确认菜单可见且未被遮挡
2. 确认文字输入正确（大小写、空格）
3. 尝试输入更完整的文字

### 问题2：缺少paddleocr

**现象**：
```
❌ 缺少paddleocr库
```

**解决**：
```bash
venv\Scripts\activate
pip install paddleocr
```

### 问题3：识别速度慢

**原因**：首次运行OCR会下载模型文件（约100MB）

**解决**：等待模型下载完成，后续运行会很快

---

## 📝 常见问题

**Q: 能否同时使用多种方法？**

A: 可以！在同一个配置中混合使用：
```json
[
  {"type": "command", "command": "ZOOM"},
  {"type": "menu", "path": ["帮助(H)"]},
  {"type": "menu", "method": "ocr", "text": "依云"}
]
```

**Q: OCR识别会影响性能吗？**

A: 首次识别约2-3秒，后续约1秒。相比手动操作，仍然快很多。

**Q: 可以在循环中使用吗？**

A: 可以！配置会在每次执行工作流程时自动读取和执行。

**Q: 如何修改已有配置？**

A: 重新运行 `python scripts\add_menu_operations.py <config_id>`，会覆盖旧配置。

---

## 📚 相关文档

- **完整API文档**: `docs/DATABASE_CONFIG_GUIDE.md`
- **菜单点击详解**: `docs/MENU_CLICKING_GUIDE.md`
- **快速参考**: `docs/CONFIG_QUICK_REFERENCE.md`

---

## 🎉 总结

使用OCR方法配置菜单操作：

1. ✅ **无需手动截图**
2. ✅ **无需测试脚本**
3. ✅ **只需输入文字**
4. ✅ **自动保存到数据库**
5. ✅ **运行工作流程自动执行**

**3步完成配置**：
```bash
python scripts\add_menu_operations.py 1  # 1. 添加配置
# 选择[3]，输入"依云"                      # 2. 输入文字
python research\autocad_com_api\configurable_workflow.py  # 3. 运行
```

就这么简单！不再需要手动测试！🚀
