# PDF 提取功能故障排除指南

**日期**: 2025-10-31
**问题**: 测试机器上PDF OCR处理失败

---

## 🔍 快速诊断

### 步骤1: 运行诊断脚本

```bash
# 基础诊断（不测试PDF）
python scripts/diagnose_pdf_extraction.py

# 完整诊断（包含PDF测试）
python scripts/diagnose_pdf_extraction.py "path/to/test.pdf"

# 包含输出目录检查
python scripts/diagnose_pdf_extraction.py "path/to/test.pdf" "F:\cad\outputs"
```

诊断脚本会检查：
- ✅ Python环境
- ✅ 必需模块
- ✅ Umi-OCR服务连接
- ✅ 脚本文件存在性
- ✅ PDF OCR功能测试
- ✅ 输出目录权限

---

## 🐛 常见问题及解决方案

### 问题1: "🔍 OCR识别中..." 后卡住

**可能原因**:
1. OCR脚本路径问题（Windows路径分隔符）
2. Python解释器路径问题
3. OCR超时

**解决方案A**: 检查Python路径

```python
# 在工作流代码中（9_configurable_workflow.py:2932）
# 当前代码：
cmd = [
    sys.executable,  # ← 可能有问题
    str(Path(__file__).parent.parent.parent / "scripts" / "pdf_ocr_with_umi.py"),
    ...
]

# 临时修复：使用绝对路径
cmd = [
    r"C:\Python39\python.exe",  # 明确指定Python路径
    r"F:\cad\100.AI.TrainData\scripts\pdf_ocr_with_umi.py",  # 绝对路径
    str(pdf_file),
    "text",
    "jsonl"
]
```

**解决方案B**: 增加超时和错误输出

修改 `9_configurable_workflow.py:2939` 的 subprocess 调用：

```python
# 原代码：
with open(jsonl_file, 'w', encoding='utf-8') as f:
    result = subprocess.run(
        cmd,
        stdout=f,
        stderr=subprocess.DEVNULL,  # ← 吞掉了错误信息
        timeout=120
    )

# 修复：捕获错误输出
with open(jsonl_file, 'w', encoding='utf-8') as f_out:
    # 记录错误到临时文件
    err_file = jsonl_file.with_suffix('.err')
    with open(err_file, 'w', encoding='utf-8') as f_err:
        result = subprocess.run(
            cmd,
            stdout=f_out,
            stderr=f_err,  # ← 保存错误信息
            timeout=120
        )

    # 如果失败，打印错误
    if result.returncode != 0 and err_file.exists():
        with open(err_file, 'r', encoding='utf-8') as f:
            error_msg = f.read()
            with lock:
                print(f"    ❌ OCR错误: {error_msg[:200]}")
```

### 问题2: Umi-OCR 服务连接失败

**诊断**:
```bash
# 测试连接
curl http://10.3.19.63:11224/api/doc/upload

# 或使用Python
python -c "import requests; print(requests.get('http://10.3.19.63:11224/api/doc/upload').status_code)"
```

**可能原因**:
- OCR服务未启动
- 网络连接问题
- 防火墙阻止

**解决方案**:
1. 检查OCR服务状态
2. 重启OCR服务
3. 检查防火墙设置
4. 尝试使用本地服务（如果测试机有OCR服务）

### 问题3: 多线程导致的问题

**临时禁用多线程**:

```sql
-- 改为单线程处理
UPDATE autocad_config SET
    pdf_extraction_parallel_workers = 1
WHERE config_name = 'default';
```

单线程模式更稳定，便于调试。

### 问题4: 文件路径编码问题

**问题**: PDF文件名包含特殊字符或中文

**解决方案**: 修改 `pdf_ocr_with_umi.py`，确保正确处理路径编码

```python
# 在 pdf_ocr_with_umi.py 开头添加
import sys
if sys.platform == 'win32':
    # Windows下确保正确处理路径
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### 问题5: 权限问题

**Windows权限问题**:

```powershell
# 检查输出目录权限
icacls "F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs"

# 授予完全控制权限
icacls "F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs" /grant Users:F /T
```

---

## 🔧 临时调试版本

创建一个带详细日志的测试版本：

```python
# test_pdf_extraction.py
import sys
from pathlib import Path
import subprocess

def test_single_pdf(pdf_file):
    """测试单个PDF处理"""
    print(f"测试PDF: {pdf_file}")

    # 检查文件存在
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        print(f"❌ 文件不存在: {pdf_file}")
        return False

    print(f"✅ 文件存在，大小: {pdf_path.stat().st_size / 1024:.2f} KB")

    # 准备OCR命令
    ocr_script = Path(__file__).parent / "scripts" / "pdf_ocr_with_umi.py"

    cmd = [
        sys.executable,
        str(ocr_script),
        str(pdf_file),
        "text",
        "jsonl"
    ]

    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}")

    # 执行OCR（捕获所有输出）
    print("\n--- OCR 输出 ---")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120
    )

    print(result.stdout)

    if result.stderr:
        print("\n--- 错误输出 ---")
        print(result.stderr)

    print(f"\n返回码: {result.returncode}")

    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python test_pdf_extraction.py <pdf_file>")
        sys.exit(1)

    success = test_single_pdf(sys.argv[1])
    sys.exit(0 if success else 1)
```

**使用方法**:
```bash
python test_pdf_extraction.py "F:\cad\outputs\tz0001.pdf"
```

---

## 📊 日志收集

如果问题持续，请收集以下信息：

### 1. 系统信息
```bash
python --version
pip list | grep requests
```

### 2. 错误日志
查看数据库日志：
```sql
SELECT * FROM dwg_task_step_log
WHERE step_name LIKE '%步骤5%'
ORDER BY created_at DESC
LIMIT 10;
```

### 3. 文件信息
```bash
# 检查第一个失败的PDF
ls -lh "F:\cad\outputs\tz0001.pdf"

# 尝试手动OCR
python scripts/pdf_ocr_with_umi.py "F:\cad\outputs\tz0001.pdf" text jsonl
```

---

## 🚀 快速修复方案

如果急需上线，使用以下临时方案：

### 方案1: 单线程 + 详细日志

```python
# 修改 9_configurable_workflow.py:2939
# 添加详细错误日志

result = subprocess.run(
    cmd,
    stdout=f,
    stderr=subprocess.PIPE,  # 捕获错误
    timeout=120,
    text=True
)

if result.returncode != 0:
    with lock:
        print(f"    ❌ OCR失败: {result.stderr}")
    raise Exception(f"OCR失败: {result.stderr[:200]}")
```

### 方案2: 跳过失败文件继续处理

确保配置：
```sql
UPDATE autocad_config SET
    pdf_extraction_fail_on_error = FALSE,  -- 失败不中断
    pdf_extraction_parallel_workers = 1    -- 单线程
WHERE config_name = 'default';
```

### 方案3: 分批处理

```sql
-- 先处理少量文件测试
-- 修改工作流，只处理前10个PDF
```

---

## 📞 紧急联系

如需立即支持，请提供：

1. **诊断脚本输出**:
   ```bash
   python scripts/diagnose_pdf_extraction.py > diagnosis.txt 2>&1
   ```

2. **第一个失败的PDF测试**:
   ```bash
   python scripts/test_pdf_extraction.py "path/to/first_failed.pdf" > test.txt 2>&1
   ```

3. **数据库日志**:
   ```sql
   SELECT * FROM dwg_task_step_log
   WHERE step_name LIKE '%步骤5%' AND status = 'failed'
   ORDER BY created_at DESC LIMIT 1;
   ```

4. **系统环境**:
   - Windows版本
   - Python版本
   - 是否有杀毒软件

---

**更新时间**: 2025-10-31
**版本**: 1.0
