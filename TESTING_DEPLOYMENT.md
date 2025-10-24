# AutoCAD COM API 测试部署说明

**创建日期：** 2025-10-24
**目标：** 在 Windows 测试机器上测试 AutoCAD COM API 功能

---

## 📦 测试包位置

测试包已自动生成并保存在：

```
项目目录/dist/autocad_com_test.zip
```

**包含内容：**
- ✅ 5个示例代码（连接、文件操作、命令执行等）
- ✅ 完整的 API 文档（350行）
- ✅ 详细的测试指南（500行）
- ✅ 使用说明和快速开始
- ✅ Day 2 完成报告

---

## 🚀 快速部署（3步）

### 步骤 1：复制文件到测试机器

```powershell
# 将 autocad_com_test.zip 复制到 Windows 测试机
# 建议路径：C:\AutoCAD_Test\

# 解压 ZIP 文件
# 解压后目录结构：
C:\AutoCAD_Test\autocad_com_test\
├── research\autocad_com_api\     # 测试代码
│   ├── 1_connect_to_autocad.py
│   ├── 2_file_operations.py
│   ├── 3_command_execution.py
│   ├── 4_error_handling.py
│   ├── 5_version_check.py
│   └── README.md
├── docs\autocad\                  # 文档
│   ├── AUTOCAD_COM_API_SUMMARY.md
│   └── TESTING_GUIDE.md
├── requirements.txt
└── README.txt
```

### 步骤 2：安装 Python 依赖

```powershell
# 打开 PowerShell（建议以管理员身份运行）
cd C:\AutoCAD_Test\autocad_com_test

# 安装依赖
pip install pywin32 psutil

# 重要：运行 pywin32 安装后配置
python -m pip install pywin32
python <Python安装目录>\Scripts\pywin32_postinstall.py -install

# 验证安装
python -c "import win32com.client; print('✅ 安装成功')"
```

### 步骤 3：运行测试

```powershell
# 确保 AutoCAD 已启动
# 然后运行测试

cd research\autocad_com_api

# 测试 1：版本检测（最简单）
python 5_version_check.py

# 测试 2：连接测试
python 1_connect_to_autocad.py

# 测试 3：错误处理测试
python 4_error_handling.py
```

---

## ✅ 预期测试结果

### 测试 1：版本检测

**预期输出：**
```
============================================================
AutoCAD 版本检测
============================================================
版本号: 24.0
版本名称: AutoCAD 2021
安装路径: C:\Program Files\Autodesk\AutoCAD 2021

✅ 版本兼容性良好
```

### 测试 2：连接测试

**预期输出：**
```
============================================================
开始连接 AutoCAD...
============================================================

尝试 1/3: 连接到运行中的 AutoCAD...
✅ 成功连接到 AutoCAD 2021
   版本号: 24.0
   安装路径: C:\Program Files\Autodesk\AutoCAD 2021
   窗口状态: 可见

📋 AutoCAD 信息:
   version: 24.0
   version_name: AutoCAD 2021
   documents_count: 0

🔗 连接状态: 已连接
🔍 进程状态: 运行中
⏳ 等待 AutoCAD 进程空闲（超时: 10 秒）...
✅ AutoCAD 已空闲（CPU 使用率: 2.3%）

🔌 断开 AutoCAD 连接...

✅ 演示完成
```

### 测试 3：错误处理

**AutoCAD 运行时：**
```
✅ 连接成功: AutoCAD 24.0
```

**AutoCAD 未运行时：**
```
❌ 连接失败: COM 错误 (-2147467259): 未找到 AutoCAD（未安装或未注册）
```

---

## 🔧 常见问题快速修复

### 问题 1：找不到 pywin32 模块

```powershell
# 解决方法：
pip uninstall pywin32
pip install pywin32
python <Python安装目录>\Scripts\pywin32_postinstall.py -install
```

### 问题 2：找不到 AutoCAD

```powershell
# 解决方法：
cd "C:\Program Files\Autodesk\AutoCAD 2024"
acad.exe /regserver
```

### 问题 3：权限被拒绝

```
# 解决方法：
# 以管理员身份运行 PowerShell
# 右键 PowerShell → "以管理员身份运行"
```

---

## 📚 详细文档位置

1. **完整测试指南：**
   ```
   docs\autocad\TESTING_GUIDE.md
   ```
   - 详细的部署步骤
   - 完整的测试清单
   - 故障排查指南

2. **API 使用文档：**
   ```
   docs\autocad\AUTOCAD_COM_API_SUMMARY.md
   ```
   - COM API 层次结构
   - 核心对象说明
   - 代码示例
   - 最佳实践

3. **示例代码说明：**
   ```
   research\autocad_com_api\README.md
   ```
   - 各示例文件的功能说明
   - 使用方法
   - 常见问题

---

## 📊 测试清单

```
测试前准备：
[ ] Windows 10/11 系统
[ ] AutoCAD 已安装（2018-2024 任意版本）
[ ] Python 3.9+ 已安装
[ ] pywin32 已安装并配置
[ ] 测试包已解压

基础测试：
[ ] 版本检测测试（5_version_check.py）
[ ] 连接测试（1_connect_to_autocad.py）
[ ] 错误处理测试（4_error_handling.py）

可选测试（需要测试文件）：
[ ] 文件操作测试（2_file_operations.py）
[ ] 命令执行测试（3_command_execution.py）
```

---

## 🎯 测试成功标准

- ✅ 版本检测能正确识别 AutoCAD 版本
- ✅ 连接测试能成功连接到 AutoCAD
- ✅ 错误处理能正确捕获和显示错误
- ✅ 所有脚本运行无异常
- ✅ 日志输出清晰可读

---

## 📞 技术支持

如遇到问题，请查看：

1. **测试指南：** `docs\autocad\TESTING_GUIDE.md` - 完整的故障排查
2. **API 文档：** `docs\autocad\AUTOCAD_COM_API_SUMMARY.md` - 常见问题解答
3. **项目报告：** `DAY2_MORNING_COMPLETION_REPORT.md` - 项目详情

---

## 🚀 快速命令总结

```powershell
# 1. 安装依赖
pip install pywin32 psutil

# 2. 配置 pywin32（重要！）
python <Python安装目录>\Scripts\pywin32_postinstall.py -install

# 3. 启动 AutoCAD

# 4. 运行测试
cd research\autocad_com_api
python 5_version_check.py       # 版本检测
python 1_connect_to_autocad.py  # 连接测试
python 4_error_handling.py      # 错误处理
```

---

## ✨ 额外说明

### 文件操作测试（可选）

如果要测试文件操作功能，需要：

1. 准备一个测试 DWG 文件
2. 修改 `2_file_operations.py` 中的文件路径：
   ```python
   test_file = r"C:\AutoCAD_Test\autocad_com_test\data\test.dwg"
   ```
3. 运行测试：
   ```powershell
   python 2_file_operations.py
   ```

### 命令执行测试（可选）

如果要测试命令执行功能，需要：

1. 在 AutoCAD 中手动打开一个 DWG 文件
2. 运行测试：
   ```powershell
   python 3_command_execution.py
   ```
3. 观察 AutoCAD 窗口的视图变化

---

**部署完成后，预计测试时间：15-20 分钟**

祝测试顺利！🎉
