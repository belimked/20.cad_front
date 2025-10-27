"""
测试pywinauto导入

快速检测pywinauto是否正确安装和可导入
"""

print("=" * 60)
print("测试 pywinauto 导入")
print("=" * 60)

# 测试1：检查是否安装
print("\n[测试 1/3] 检查pip列表...")
import subprocess
result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'pywinauto' in line.lower():
        print(f"  ✅ 找到: {line}")
        break
else:
    print("  ❌ pip list中未找到pywinauto")

# 测试2：尝试导入
print("\n[测试 2/3] 尝试导入pywinauto...")
try:
    import pywinauto
    print(f"  ✅ 导入成功")
    print(f"  版本: {pywinauto.__version__}")
    print(f"  路径: {pywinauto.__file__}")
except ImportError as e:
    print(f"  ❌ 导入失败: {e}")
except Exception as e:
    print(f"  ❌ 其他错误: {e}")

# 测试3：尝试导入具体模块
print("\n[测试 3/3] 尝试导入Desktop...")
try:
    from pywinauto import Desktop
    print(f"  ✅ Desktop导入成功")

    from pywinauto.findwindows import ElementNotFoundError
    print(f"  ✅ ElementNotFoundError导入成功")

    print("\n✅ 所有测试通过！pywinauto可以正常使用")

except ImportError as e:
    print(f"  ❌ 导入失败: {e}")
    print("\n可能的原因:")
    print("  1. pywinauto未正确安装")
    print("  2. 依赖项缺失（如comtypes, six, pywin32）")
    print("  3. 安装到了错误的Python环境")
except Exception as e:
    print(f"  ❌ 其他错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

input("\n按 Enter 键退出...")
