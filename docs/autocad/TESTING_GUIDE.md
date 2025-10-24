# AutoCAD COM API 测试部署指南

**文档版本：** 1.0
**创建日期：** 2025-10-24
**目标系统：** Windows + AutoCAD 2018-2024

---

## 📋 测试环境要求

### 硬件要求
- ✅ Windows 10/11 操作系统
- ✅ 至少 4GB 内存
- ✅ 10GB 可用磁盘空间

### 软件要求
- ✅ **AutoCAD 2018-2024**（任意版本）
- ✅ **Python 3.9+**
- ✅ **Git**（可选，用于克隆代码）

---

## 📦 需要复制的文件

### 方案 1：最小化测试（仅测试 COM API）

```
测试机器目录结构：
autocad_com_test/
├── requirements.txt                    # Python 依赖
├── research/
│   └── autocad_com_api/
│       ├── 1_connect_to_autocad.py    # 连接测试
│       ├── 2_file_operations.py        # 文件操作测试
│       ├── 3_command_execution.py      # 命令执行测试
│       ├── 4_error_handling.py         # 错误处理测试
│       ├── 5_version_check.py          # 版本检测测试
│       └── README.md                   # 使用说明
└── docs/
    └── autocad/
        └── AUTOCAD_COM_API_SUMMARY.md  # 完整文档
```

### 方案 2：完整项目部署

```
测试机器目录结构：
100.AI.TrainData/
├── requirements.txt
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   └── modules/
│       └── __init__.py
├── research/
│   └── autocad_com_api/
│       └── [所有测试文件]
├── docs/
│   └── autocad/
│       └── AUTOCAD_COM_API_SUMMARY.md
├── logs/
│   └── .gitkeep
└── data/
    └── downloads/
        └── test.dwg    # 测试用的 DWG 文件
```

---

## 🚀 快速部署步骤

### 步骤 1：准备测试机器

```powershell
# 1. 创建测试目录
mkdir C:\AutoCAD_Test
cd C:\AutoCAD_Test

# 2. 检查 Python 版本
python --version
# 应该显示：Python 3.9.x 或更高版本

# 3. 检查 AutoCAD 安装
# 在 Windows 搜索中输入 "AutoCAD"，确保已安装
```

### 步骤 2：复制文件到测试机器

#### 方式 A：使用 Git 克隆（推荐）

```powershell
# 克隆整个项目
git clone http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git
cd 100.AI.TrainData
git checkout cad
```

#### 方式 B：手动复制文件

将以下文件/文件夹从开发机复制到测试机：

```
从开发机复制：
/Users/saul/IdeaProjects/100.AI.TrainData/research/autocad_com_api/
  → C:\AutoCAD_Test\research\autocad_com_api\

/Users/saul/IdeaProjects/100.AI.TrainData/docs/autocad/
  → C:\AutoCAD_Test\docs\autocad\

/Users/saul/IdeaProjects/100.AI.TrainData/requirements.txt
  → C:\AutoCAD_Test\requirements.txt
```

### 步骤 3：安装 Python 依赖

```powershell
# 切换到测试目录
cd C:\AutoCAD_Test

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装核心依赖（仅测试 COM API）
pip install pywin32 psutil

# 或安装完整依赖
pip install -r requirements.txt
```

### 步骤 4：验证 pywin32 安装

```powershell
# 运行 pywin32 安装后脚本（重要！）
python .\venv\Scripts\pywin32_postinstall.py -install

# 验证安装
python -c "import win32com.client; print('✅ pywin32 安装成功')"
```

---

## 🧪 测试步骤

### 测试 1：版本检测（最简单，先测试这个）

```powershell
# 确保 AutoCAD 已启动
# 打开 AutoCAD（任意版本）

# 运行版本检测脚本
cd C:\AutoCAD_Test\research\autocad_com_api
python 5_version_check.py
```

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

**如果失败：**
- ❌ 错误 `-2147467259`: AutoCAD 未启动或未注册 COM
  - 解决：启动 AutoCAD 或运行 `acad.exe /regserver`

### 测试 2：连接测试

```powershell
# 确保 AutoCAD 正在运行
python 1_connect_to_autocad.py
```

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
   ...

🔗 连接状态: 已连接
🔍 进程状态: 运行中
```

**如果失败：**
- ❌ AutoCAD 未启动：脚本会自动尝试启动 AutoCAD
- ❌ 连接超时：检查防火墙设置

### 测试 3：文件操作测试

**准备工作：**
```powershell
# 1. 准备一个测试 DWG 文件
# 复制任意 DWG 文件到：C:\AutoCAD_Test\data\test.dwg

# 2. 修改测试脚本中的文件路径
# 编辑 2_file_operations.py，找到这一行：
test_file = r"C:\path\to\your\test.dwg"

# 改为：
test_file = r"C:\AutoCAD_Test\data\test.dwg"
```

**运行测试：**
```powershell
python 2_file_operations.py
```

**预期输出：**
```
============================================================
AutoCAD 文件操作示例
============================================================
✅ 已连接到 AutoCAD 24.0

📋 打开的文档列表（共 0 个）:
   （无打开的文档）

📂 打开文件: C:\AutoCAD_Test\data\test.dwg
   只读模式: False
✅ 文件已打开: test.dwg
   模型空间对象数: 125
   图层数: 8
   活动状态: True

📋 文档信息:
   name: test.dwg
   path: C:\AutoCAD_Test\data
   ...

💾 另存为: C:\AutoCAD_Test\data\test_copy.dwg
✅ 文件已另存为: C:\AutoCAD_Test\data\test_copy.dwg

🗙 关闭文件: test.dwg
   保存更改: False
✅ 文件已关闭
```

### 测试 4：命令执行测试

```powershell
# 确保有文档打开（手动在 AutoCAD 中打开一个文件）
python 3_command_execution.py
```

**预期输出：**
```
📤 发送命令: ._ZOOM _E
✅ 命令执行完成

📤 发送命令: ._REGEN
✅ 命令执行完成
```

**验证方法：**
- 观察 AutoCAD 窗口，应该看到视图缩放和重新生成

### 测试 5：错误处理测试

```powershell
# 关闭 AutoCAD
# 然后运行测试
python 4_error_handling.py
```

**预期输出（AutoCAD 未运行）：**
```
❌ 连接失败: COM 错误 (-2147467259): 未找到 AutoCAD（未安装或未注册）
```

**预期输出（AutoCAD 正在运行）：**
```
✅ 连接成功: AutoCAD 24.0
```

---

## 📝 完整测试清单

### 测试清单 1：基础功能测试

```
测试环境准备：
[ ] Windows 10/11 系统
[ ] AutoCAD 已安装（2018-2024）
[ ] Python 3.9+ 已安装
[ ] pywin32 已安装并配置
[ ] 测试文件已复制

测试项目：
[ ] 版本检测测试（5_version_check.py）
    - [ ] AutoCAD 已启动
    - [ ] 正确显示版本号
    - [ ] 兼容性检查通过

[ ] 连接测试（1_connect_to_autocad.py）
    - [ ] 连接到运行中的 AutoCAD
    - [ ] 获取版本信息
    - [ ] 进程状态检测
    - [ ] 等待空闲功能

[ ] 错误处理测试（4_error_handling.py）
    - [ ] AutoCAD 未运行时的错误提示
    - [ ] AutoCAD 运行时的正常连接
    - [ ] 友好的错误消息

[ ] 文件操作测试（2_file_operations.py）
    - [ ] 打开 DWG 文件
    - [ ] 获取文档信息
    - [ ] 另存为功能
    - [ ] 关闭文档

[ ] 命令执行测试（3_command_execution.py）
    - [ ] 发送缩放命令
    - [ ] 发送重生成命令
    - [ ] 观察 AutoCAD 窗口变化
```

### 测试清单 2：异常场景测试

```
异常场景：
[ ] AutoCAD 未安装
    - 预期：友好的错误提示

[ ] AutoCAD 未启动
    - 预期：自动启动或提示启动

[ ] 文件不存在
    - 预期：文件未找到错误

[ ] 文件被锁定
    - 预期：访问被拒绝错误

[ ] AutoCAD 版本过旧（<2018）
    - 预期：版本警告

[ ] AutoCAD 版本过新（>2024）
    - 预期：未测试警告
```

---

## 🔧 常见问题排查

### 问题 1：找不到 AutoCAD

**错误消息：**
```
❌ 连接失败: COM 错误 (-2147467259): 未找到 AutoCAD（未安装或未注册）
```

**解决方法：**

```powershell
# 方法 1：重新注册 AutoCAD COM 接口
cd "C:\Program Files\Autodesk\AutoCAD 2024"
acad.exe /regserver

# 方法 2：检查 AutoCAD 是否已安装
dir "C:\Program Files\Autodesk\" /s /b | findstr acad.exe

# 方法 3：手动启动 AutoCAD
# 在 Windows 搜索框输入 "AutoCAD" 并启动
```

### 问题 2：pywin32 导入错误

**错误消息：**
```
ImportError: DLL load failed while importing win32api
```

**解决方法：**

```powershell
# 重新安装 pywin32
pip uninstall pywin32
pip install pywin32

# 运行安装后脚本（重要！）
python .\venv\Scripts\pywin32_postinstall.py -install

# 如果上面命令找不到，尝试：
python -c "import sys; import os; import win32api; print(os.path.dirname(win32api.__file__))"
# 然后手动运行该目录下的 pywin32_postinstall.py
```

### 问题 3：权限问题

**错误消息：**
```
❌ COM 错误 (-2147023170): 拒绝访问
```

**解决方法：**

```powershell
# 以管理员身份运行 PowerShell
# 右键 PowerShell → "以管理员身份运行"

# 然后再运行测试脚本
python 1_connect_to_autocad.py
```

### 问题 4：文件路径问题

**错误消息：**
```
❌ 文件不存在: C:\path\to\your\test.dwg
```

**解决方法：**

```powershell
# 检查文件是否存在
dir C:\AutoCAD_Test\data\test.dwg

# 如果不存在，复制一个测试文件
copy "C:\Users\你的用户名\Documents\*.dwg" C:\AutoCAD_Test\data\test.dwg

# 或者修改脚本中的文件路径为实际存在的文件
```

### 问题 5：AutoCAD 版本不兼容

**警告消息：**
```
⚠️ 警告：版本过低（<2018），可能不兼容
```

**解决方法：**

```
- 如果可能，升级到 AutoCAD 2018 或更高版本
- 或者根据实际版本修改代码中的版本检测逻辑
```

---

## 📊 测试报告模板

测试完成后，填写以下报告：

```markdown
# AutoCAD COM API 测试报告

## 测试环境
- 操作系统：Windows 10/11
- AutoCAD 版本：________
- Python 版本：________
- pywin32 版本：________

## 测试结果

### 1. 版本检测测试
- 状态：[ ] 通过  [ ] 失败
- 错误信息（如有）：

### 2. 连接测试
- 状态：[ ] 通过  [ ] 失败
- 错误信息（如有）：

### 3. 文件操作测试
- 状态：[ ] 通过  [ ] 失败
- 错误信息（如有）：

### 4. 命令执行测试
- 状态：[ ] 通过  [ ] 失败
- 错误信息（如有）：

### 5. 错误处理测试
- 状态：[ ] 通过  [ ] 失败
- 错误信息（如有）：

## 总体评价
- 所有测试通过：[ ] 是  [ ] 否
- 发现的问题：
- 改进建议：

## 测试人员
- 姓名：________
- 日期：________
```

---

## 🚀 自动化测试脚本（可选）

创建一个自动化测试脚本 `run_all_tests.py`：

```python
"""
自动化测试所有 AutoCAD COM API 示例
"""

import subprocess
import sys

def run_test(script_name, description):
    """运行单个测试脚本"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"脚本: {script_name}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {description} - 通过")
            return True
        else:
            print(f"❌ {description} - 失败")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - 超时")
        return False
    except Exception as e:
        print(f"❌ {description} - 异常: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("AutoCAD COM API 自动化测试")
    print("="*60)

    tests = [
        ("5_version_check.py", "版本检测"),
        ("1_connect_to_autocad.py", "连接测试"),
        ("4_error_handling.py", "错误处理"),
        # 文件操作和命令执行需要交互，跳过自动化测试
    ]

    results = []
    for script, desc in tests:
        results.append(run_test(script, desc))

    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {sum(results)} 个")
    print(f"失败: {len(results) - sum(results)} 个")

    if all(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**运行自动化测试：**
```powershell
cd C:\AutoCAD_Test\research\autocad_com_api
python run_all_tests.py
```

---

## 📚 相关文档

- [完整 API 文档](../../docs/autocad/AUTOCAD_COM_API_SUMMARY.md)
- [示例代码说明](README.md)
- [Day 2 完成报告](../../DAY2_MORNING_COMPLETION_REPORT.md)

---

**文档版本：** 1.0
**创建日期：** 2025-10-24
**最后更新：** 2025-10-24
**状态：** ✅ 完成

---

## ✅ 快速测试步骤总结

```powershell
# 1. 复制文件到测试机器
# 2. 安装依赖
pip install pywin32 psutil
python .\venv\Scripts\pywin32_postinstall.py -install

# 3. 启动 AutoCAD

# 4. 运行测试（按顺序）
python 5_version_check.py       # 版本检测
python 1_connect_to_autocad.py  # 连接测试
python 4_error_handling.py      # 错误处理
python 2_file_operations.py     # 文件操作（需要准备测试文件）
python 3_command_execution.py   # 命令执行（需要打开文档）
```

**测试成功标准：**
- ✅ 所有脚本运行无错误
- ✅ AutoCAD 能正常响应
- ✅ 日志输出符合预期

祝测试顺利！🎉
