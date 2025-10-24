"""
AutoCAD 版本兼容性检测

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client


def check_autocad_version():
    """检测 AutoCAD 版本并验证兼容性"""
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        version = float(acad.Version)
        
        version_map = {
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
        print(f"版本号: {version}")
        print(f"版本名称: {version_name}")
        print(f"安装路径: {acad.Path}")
        
        # 检查兼容性
        if version < 22.0:
            print("\n⚠️ 警告：版本过低（<2018），可能不兼容")
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
