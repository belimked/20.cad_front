"""
AutoCAD COM 异常处理示例

Author: CAD Auto Processor Team  
Date: 2025-10-24
"""

import pywintypes
import win32com.client


class AutoCADError:
    """AutoCAD COM 错误代码映射"""
    
    ERROR_CODES = {
        -2147467259: "未找到 AutoCAD（未安装或未注册）",
        -2147221005: "AutoCAD 无法启动",
        -2147024894: "文件未找到",
        -2147352567: "自动化错误（命令执行失败）",
        -2147417848: "对象已断开连接",
        -2147023170: "拒绝访问",
    }
    
    @staticmethod
    def get_error_message(error_code):
        return AutoCADError.ERROR_CODES.get(
            error_code,
            f"未知错误代码: {error_code}"
        )


def safe_connect():
    """安全地连接 AutoCAD"""
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        return acad, None
    except pywintypes.com_error as e:
        error_code = e.args[0] if e.args else 0
        error_msg = AutoCADError.get_error_message(error_code)
        return None, f"COM 错误 ({error_code}): {error_msg}"
    except Exception as e:
        return None, f"未知错误: {str(e)}"


if __name__ == "__main__":
    acad, error = safe_connect()
    if acad:
        print(f"✅ 连接成功: AutoCAD {acad.Version}")
    else:
        print(f"❌ 连接失败: {error}")
