#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bplot 全自动化工作流依赖检查脚本

检查所有必需的依赖库是否已安装

Usage:
    python scripts/check_bplot_dependencies.py
"""

import sys


def check_dependency(module_name, package_name=None):
    """检查单个依赖"""
    if package_name is None:
        package_name = module_name

    try:
        __import__(module_name)
        print(f"  ✅ {module_name:20s} - 已安装")
        return True
    except ImportError:
        print(f"  ❌ {module_name:20s} - 未安装")
        print(f"     安装命令: pip install {package_name}")
        return False


def main():
    print("\n" + "=" * 80)
    print("Bplot 全自动化工作流 - 依赖检查")
    print("=" * 80)

    dependencies = [
        # Windows COM 和进程管理
        ("win32com.client", "pywin32"),
        ("psutil", "psutil"),

        # HTTP 请求
        ("requests", "requests"),

        # UI 自动化
        ("pyautogui", "pyautogui"),
        ("PIL", "pillow"),

        # 数据库（API 需要）
        ("pymysql", "pymysql"),
        ("sqlalchemy", "sqlalchemy"),

        # Web 框架（API 需要）
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
    ]

    print("\n📋 检查必需依赖:")
    print("-" * 80)

    all_ok = True
    missing = []

    for dep in dependencies:
        if len(dep) == 2:
            module, package = dep
        else:
            module = package = dep[0]

        if not check_dependency(module, package):
            all_ok = False
            missing.append(package)

    print("-" * 80)

    if all_ok:
        print("\n✅ 所有依赖已安装！可以运行 bplot 全自动化工作流。")
        print("\n🚀 启动命令:")
        print("   .\\start_api.ps1")
        return 0
    else:
        print(f"\n❌ 缺少 {len(missing)} 个依赖")
        print("\n📦 一键安装所有缺失依赖:")
        print(f"   pip install {' '.join(missing)}")
        print("\n或使用 requirements.txt:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
