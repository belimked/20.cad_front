#!/usr/bin/env python3
"""
PDF提取功能诊断脚本

用于排查测试机器上的PDF提取失败问题
"""

import sys
import os
from pathlib import Path
import subprocess
import json
import requests
import time

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print_section("1. Python 环境检查")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")

    # 检查版本
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print("✅ Python版本符合要求 (>= 3.7)")
        return True
    else:
        print("❌ Python版本过低，需要 >= 3.7")
        return False

def check_required_modules():
    """检查必需的Python模块"""
    print_section("2. Python 模块检查")

    required_modules = [
        'requests',
        'pathlib',
        'json',
        'subprocess',
    ]

    all_ok = True
    for module_name in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError:
            print(f"❌ {module_name} - 未安装")
            all_ok = False

    return all_ok

def check_umi_ocr_service(service_url="http://10.3.19.63:11224"):
    """检查Umi-OCR服务"""
    print_section("3. Umi-OCR 服务检查")
    print(f"服务地址: {service_url}")

    try:
        # 测试连接
        response = requests.get(f"{service_url}/api/doc/upload", timeout=5)
        print(f"✅ 服务可访问 (状态码: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print("❌ 连接超时 (5秒)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 (服务可能未运行)")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def check_pdf_ocr_script():
    """检查PDF OCR脚本"""
    print_section("4. PDF OCR 脚本检查")

    script_path = Path(__file__).parent / "pdf_ocr_with_umi.py"

    if script_path.exists():
        print(f"✅ 脚本存在: {script_path}")

        # 检查是否可执行
        if os.access(script_path, os.X_OK):
            print("✅ 脚本可执行")
        else:
            print("⚠️  脚本不可执行（但可能不影响）")

        return True
    else:
        print(f"❌ 脚本不存在: {script_path}")
        return False

def check_extract_info_script():
    """检查信息提取脚本"""
    print_section("5. 信息提取脚本检查")

    script_path = Path(__file__).parent / "extract_drawing_info.py"

    if script_path.exists():
        print(f"✅ 脚本存在: {script_path}")
        return True
    else:
        print(f"❌ 脚本不存在: {script_path}")
        return False

def test_pdf_ocr(test_pdf=None, service_url="http://10.3.19.63:11224"):
    """测试PDF OCR功能"""
    print_section("6. PDF OCR 功能测试")

    if not test_pdf:
        print("⚠️  未提供测试PDF文件，跳过此测试")
        print("   使用方法: python diagnose_pdf_extraction.py <pdf_path>")
        return None

    test_pdf = Path(test_pdf)
    if not test_pdf.exists():
        print(f"❌ 测试PDF不存在: {test_pdf}")
        return False

    print(f"测试文件: {test_pdf}")

    # 调用OCR脚本
    script_path = Path(__file__).parent / "pdf_ocr_with_umi.py"
    cmd = [sys.executable, str(script_path), str(test_pdf), "text", "jsonl"]

    print(f"执行命令: {' '.join(cmd)}")
    print("\n--- OCR 输出 ---")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print("✅ OCR识别成功")

            # 尝试解析输出
            try:
                # 提取JSONL内容
                import re
                match = re.search(r'\{"code".*\}', result.stdout, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    print(f"✅ JSONL解析成功")
                    print(f"   识别文字块: {len(data.get('data', []))} 个")
                    print(f"   识别耗时: {data.get('time', 0):.2f} 秒")
                else:
                    print("⚠️  未找到JSONL内容")
            except Exception as e:
                print(f"⚠️  JSONL解析失败: {e}")

            return True
        else:
            print(f"❌ OCR识别失败 (返回码: {result.returncode})")
            print(f"\n标准输出:\n{result.stdout}")
            print(f"\n错误输出:\n{result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ OCR识别超时 (120秒)")
        return False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_output_directory(output_dir=None):
    """检查输出目录"""
    print_section("7. 输出目录检查")

    if not output_dir:
        print("⚠️  未指定输出目录")
        return None

    output_path = Path(output_dir)

    if output_path.exists():
        print(f"✅ 输出目录存在: {output_path}")

        # 检查写权限
        test_file = output_path / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✅ 输出目录可写")
            return True
        except Exception as e:
            print(f"❌ 输出目录不可写: {e}")
            return False
    else:
        print(f"⚠️  输出目录不存在: {output_path}")
        print("   (将在运行时自动创建)")
        return None

def print_summary(results):
    """打印诊断总结"""
    print_section("诊断总结")

    all_checks = [
        ("Python环境", results.get('python')),
        ("Python模块", results.get('modules')),
        ("Umi-OCR服务", results.get('umi_service')),
        ("PDF OCR脚本", results.get('pdf_ocr_script')),
        ("信息提取脚本", results.get('extract_script')),
    ]

    if results.get('test_pdf') is not None:
        all_checks.append(("PDF OCR测试", results.get('test_pdf')))

    if results.get('output_dir') is not None:
        all_checks.append(("输出目录", results.get('output_dir')))

    passed = sum(1 for _, result in all_checks if result is True)
    total = len([r for _, r in all_checks if r is not None])

    print(f"\n通过检查: {passed}/{total}")

    for name, result in all_checks:
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  跳过"
        print(f"  {status} - {name}")

    if passed == total:
        print("\n🎉 所有检查通过！PDF提取功能应该可以正常工作。")
    else:
        print("\n⚠️  部分检查失败，请根据上面的提示修复问题。")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  PDF提取功能诊断工具")
    print("  版本: 1.0")
    print("=" * 60)

    # 解析命令行参数
    test_pdf = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    # 执行检查
    results = {}
    results['python'] = check_python_version()
    results['modules'] = check_required_modules()
    results['umi_service'] = check_umi_ocr_service()
    results['pdf_ocr_script'] = check_pdf_ocr_script()
    results['extract_script'] = check_extract_info_script()
    results['test_pdf'] = test_pdf_ocr(test_pdf)
    results['output_dir'] = check_output_directory(output_dir)

    # 打印总结
    print_summary(results)

    # 返回状态码
    if all(v is True for v in results.values() if v is not None):
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
