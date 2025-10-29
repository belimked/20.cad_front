"""
AutoCAD 版本兼容性检测

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client


def parse_version_string(version_str: str) -> float:
    """
    解析 AutoCAD 版本字符串，提取数字部分

    支持的格式:
    - "24.0" -> 24.0
    - "19.1s (LMS Tech)" -> 19.1
    - "23.1.49.0" -> 23.1
    """
    import re

    # 提取版本字符串中的第一个数字部分（格式: XX.X）
    match = re.search(r'(\d+\.\d+)', str(version_str))
    if match:
        return float(match.group(1))

    # 如果没有匹配到，尝试直接转换
    raise ValueError(f"无法解析版本字符串: {version_str}")


def check_autocad_version():
    """检测 AutoCAD 版本并验证兼容性"""
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        version_raw = acad.Version

        # 解析版本号
        version = parse_version_string(version_raw)

        version_map = {
            19.0: "AutoCAD 2013",
            19.1: "AutoCAD 2014",
            20.0: "AutoCAD 2015",
            20.1: "AutoCAD 2016",
            21.0: "AutoCAD 2017",
            22.0: "AutoCAD 2018",
            23.0: "AutoCAD 2019",
            23.1: "AutoCAD 2020",
            24.0: "AutoCAD 2021",
            24.1: "AutoCAD 2022",
            24.2: "AutoCAD 2023",
            24.3: "AutoCAD 2024",
        }

        version_name = version_map.get(version, f"AutoCAD (版本 {version})")

        print("=" * 60)
        print("AutoCAD 版本检测")
        print("=" * 60)
        print(f"原始版本信息: {version_raw}")
        print(f"解析版本号: {version}")
        print(f"版本名称: {version_name}")
        print(f"安装路径: {acad.Path}")

        # 检查兼容性（放宽到支持 2013+）
        if version < 19.0:
            print("\n⚠️ 警告：版本过低（<2013），可能不兼容")
        elif version >= 19.0 and version < 22.0:
            print("\n⚠️ 提示：版本较旧（2013-2017），建议升级到 2018+")
        elif version > 24.3:
            print("\n⚠️ 警告：版本较新（>2024），未经测试")
        else:
            print("\n✅ 版本兼容性良好")

        return True

    except Exception as e:
        print(f"❌ 检测失败: {e}")
        return False


if __name__ == "__main__":
    check_autocad_version()
    input("\n按 Enter 键退出...")
