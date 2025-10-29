"""
AutoCAD 命令执行示例

演示如何执行 AutoCAD 命令和 LISP 脚本

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client
import time


class AutoCADCommands:
    """AutoCAD 命令执行类"""

    def __init__(self, acad_app):
        self.acad = acad_app

    def send_command(self, command_string: str, wait_time: float = 0.5):
        """
        发送命令字符串到 AutoCAD

        Args:
            command_string: 命令字符串
            wait_time: 等待时间（秒）
        """
        try:
            doc = self.acad.ActiveDocument
            print(f"\n📤 发送命令: {command_string}")
            
            # 发送命令（末尾空格代表回车）
            doc.SendCommand(command_string + " ")
            
            # 等待命令完成
            time.sleep(wait_time)
            print(f"✅ 命令执行完成")
            
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")

    def execute_lisp(self, lisp_code: str):
        """执行 LISP 代码"""
        try:
            doc = self.acad.ActiveDocument
            print(f"\n📜 执行 LISP: {lisp_code}")
            doc.SendCommand(f"(progn {lisp_code}) ")
            time.sleep(0.5)
            print("✅ LISP 执行完成")
        except Exception as e:
            print(f"❌ LISP 执行失败: {e}")

    def zoom_extents(self):
        """缩放到图形范围"""
        self.send_command("._ZOOM _E")

    def regen(self):
        """重新生成图形"""
        self.send_command("._REGEN")


if __name__ == "__main__":
    # 连接 AutoCAD
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    
    # 创建命令执行对象
    cmd = AutoCADCommands(acad)
    
    # 演示命令执行
    cmd.zoom_extents()
    cmd.regen()
    
    print("\n✅ 演示完成")
