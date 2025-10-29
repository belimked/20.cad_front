#!/usr/bin/env python3
"""
AutoCAD COM API 测试包打包脚本

用途：打包所有需要复制到测试机器的文件

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_test_package():
    """创建测试包"""

    # 项目根目录（脚本在 scripts/ 目录下，需要回到上一级）
    project_root = Path(__file__).parent.parent

    # 创建打包目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"autocad_com_test_{timestamp}"
    package_dir = project_root / "dist" / package_name

    print("=" * 60)
    print("AutoCAD COM API 测试包打包")
    print("=" * 60)
    print(f"\n📦 打包目录: {package_dir}")

    # 创建目录结构
    print("\n创建目录结构...")
    dirs = [
        package_dir / "research" / "autocad_com_api",
        package_dir / "docs" / "autocad",
        package_dir / "data",
        package_dir / "logs",
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path.relative_to(package_dir)}")

    # 需要复制的文件
    files_to_copy = [
        # 研究示例代码
        ("research/autocad_com_api/1_connect_to_autocad.py", "research/autocad_com_api/"),
        ("research/autocad_com_api/2_file_operations.py", "research/autocad_com_api/"),
        ("research/autocad_com_api/3_command_execution.py", "research/autocad_com_api/"),
        ("research/autocad_com_api/4_error_handling.py", "research/autocad_com_api/"),
        ("research/autocad_com_api/5_version_check.py", "research/autocad_com_api/"),
        ("research/autocad_com_api/README.md", "research/autocad_com_api/"),

        # 文档
        ("docs/autocad/AUTOCAD_COM_API_SUMMARY.md", "docs/autocad/"),
        ("docs/autocad/TESTING_GUIDE.md", "docs/autocad/"),

        # 报告
        ("DAY2_MORNING_COMPLETION_REPORT.md", ""),
        ("DAY2_SUMMARY.md", ""),

        # 配置
        ("requirements.txt", ""),
    ]

    # 复制文件
    print("\n复制文件...")
    copied_count = 0
    for src_path, dest_dir in files_to_copy:
        src = project_root / src_path
        dest = package_dir / dest_dir / Path(src_path).name

        if src.exists():
            shutil.copy2(src, dest)
            print(f"  ✅ {src_path}")
            copied_count += 1
        else:
            print(f"  ⚠️ 未找到: {src_path}")

    print(f"\n已复制 {copied_count} 个文件")

    # 创建简化的 requirements.txt（仅核心依赖）
    print("\n创建简化的 requirements.txt...")
    test_requirements = package_dir / "requirements_test.txt"
    with open(test_requirements, "w") as f:
        f.write("# AutoCAD COM API 测试所需的最小依赖\n")
        f.write("pywin32>=305\n")
        f.write("psutil>=5.9.0\n")
    print(f"  ✅ requirements_test.txt")

    # 创建 README.txt（测试说明）
    print("\n创建 README.txt...")
    readme = package_dir / "README.txt"
    with open(readme, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("AutoCAD COM API 测试包\n")
        f.write("=" * 60 + "\n\n")
        f.write("快速开始：\n\n")
        f.write("1. 解压此文件到测试机器（Windows）\n\n")
        f.write("2. 安装 Python 依赖：\n")
        f.write("   pip install -r requirements_test.txt\n")
        f.write("   python -m pip install pywin32\n")
        f.write("   python <Python安装目录>\\Scripts\\pywin32_postinstall.py -install\n\n")
        f.write("3. 启动 AutoCAD\n\n")
        f.write("4. 运行测试（按顺序）：\n")
        f.write("   cd research\\autocad_com_api\n")
        f.write("   python 5_version_check.py\n")
        f.write("   python 1_connect_to_autocad.py\n")
        f.write("   python 4_error_handling.py\n\n")
        f.write("详细说明请查看：\n")
        f.write("  docs\\autocad\\TESTING_GUIDE.md\n\n")
        f.write("问题排查请查看：\n")
        f.write("  docs\\autocad\\AUTOCAD_COM_API_SUMMARY.md\n\n")
        f.write("=" * 60 + "\n")
    print(f"  ✅ README.txt")

    # 创建快速测试批处理脚本
    print("\n创建快速测试脚本...")
    batch_file = package_dir / "quick_test.bat"
    with open(batch_file, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("chcp 65001 >nul\n")
        f.write("echo ============================================================\n")
        f.write("echo AutoCAD COM API 快速测试\n")
        f.write("echo ============================================================\n")
        f.write("echo.\n")
        f.write("echo 测试 1/3: 版本检测\n")
        f.write("echo ------------------------------------------------------------\n")
        f.write("cd research\\autocad_com_api\n")
        f.write("python 5_version_check.py\n")
        f.write("echo.\n")
        f.write("pause\n")
        f.write("echo.\n")
        f.write("echo 测试 2/3: 连接测试\n")
        f.write("echo ------------------------------------------------------------\n")
        f.write("python 1_connect_to_autocad.py\n")
        f.write("echo.\n")
        f.write("pause\n")
        f.write("echo.\n")
        f.write("echo 测试 3/3: 错误处理测试\n")
        f.write("echo ------------------------------------------------------------\n")
        f.write("python 4_error_handling.py\n")
        f.write("echo.\n")
        f.write("echo ============================================================\n")
        f.write("echo 测试完成！\n")
        f.write("echo ============================================================\n")
        f.write("pause\n")
    print(f"  ✅ quick_test.bat")

    # 创建 ZIP 文件
    print("\n创建 ZIP 压缩包...")
    zip_path = project_root / "dist" / f"{package_name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    # 获取文件大小
    zip_size = zip_path.stat().st_size / 1024 / 1024  # MB

    print(f"  ✅ {zip_path.name}")
    print(f"  📦 大小: {zip_size:.2f} MB")

    # 总结
    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print(f"\n✅ ZIP 文件: {zip_path}")
    print(f"✅ 解压目录: {package_dir}")
    print(f"\n📋 包含文件: {copied_count + 3} 个（代码 + 文档 + 配置）")
    print(f"📦 压缩包大小: {zip_size:.2f} MB")

    print("\n📤 部署到测试机器的步骤：")
    print("1. 将 ZIP 文件复制到测试机器（Windows）")
    print("2. 解压到任意目录，如：C:\\AutoCAD_Test")
    print("3. 按照 README.txt 中的说明进行测试")
    print("4. 详细说明请查看：docs\\autocad\\TESTING_GUIDE.md")

    print("\n🚀 快速测试命令：")
    print(f"   cd {package_name}")
    print("   quick_test.bat")

    return zip_path


if __name__ == "__main__":
    try:
        zip_file = create_test_package()
        print("\n✅ 打包成功！")
        print(f"\n📦 测试包路径: {zip_file}")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
