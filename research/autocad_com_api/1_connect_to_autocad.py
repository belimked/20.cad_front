"""
AutoCAD COM 连接示例

演示如何使用 Python (pywin32) 连接到 AutoCAD

Author: CAD Auto Processor Team
Date: 2025-10-24
Python Version: 3.9+
Required: pip install pywin32 psutil
"""

import win32com.client
import pythoncom
import pywintypes
import psutil
import time
from typing import Optional


class AutoCADConnection:
    """
    AutoCAD 连接管理器

    功能：
    - 连接到正在运行的 AutoCAD
    - 自动启动 AutoCAD（如果未运行）
    - 检测连接状态
    - 自动重连机制
    - 进程监控
    """

    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        """
        初始化连接管理器

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.acad = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._version = None
        self._version_name = None

    def connect(self, start_if_not_running: bool = True) -> bool:
        """
        连接到 AutoCAD

        Args:
            start_if_not_running: 如果 AutoCAD 未运行，是否启动它

        Returns:
            True 表示连接成功，False 表示失败
        """
        print("=" * 60)
        print("开始连接 AutoCAD...")
        print("=" * 60)

        # 尝试连接到已运行的 AutoCAD
        for attempt in range(self.max_retries):
            try:
                print(f"\n尝试 {attempt + 1}/{self.max_retries}: 连接到运行中的 AutoCAD...")
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                self._version = self.acad.Version
                self._version_name = self._get_version_name(self._version)

                print(f"✅ 成功连接到 {self._version_name}")
                print(f"   版本号: {self._version}")
                print(f"   安装路径: {self.acad.Path}")
                print(f"   窗口状态: {'可见' if self.acad.Visible else '隐藏'}")
                return True

            except pywintypes.com_error as e:
                error_code = e.args[0] if e.args else 0
                print(f"⚠️ 连接失败 (错误代码: {error_code})")

                if attempt < self.max_retries - 1:
                    print(f"   {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)

        # 如果连接失败，尝试启动 AutoCAD
        if start_if_not_running:
            print(f"\n⚠️ AutoCAD 未运行，尝试启动...")
            return self._start_autocad()
        else:
            print("\n❌ 无法连接到 AutoCAD，且未启动 AutoCAD")
            return False

    def _start_autocad(self) -> bool:
        """
        启动 AutoCAD

        Returns:
            True 表示启动成功，False 表示失败
        """
        try:
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acad.Visible = True  # 显示 AutoCAD 窗口

            # 等待 AutoCAD 启动完成
            print("⏳ 等待 AutoCAD 启动...")
            time.sleep(5)  # 给 AutoCAD 5 秒启动时间

            self._version = self.acad.Version
            self._version_name = self._get_version_name(self._version)

            print(f"✅ AutoCAD 已启动: {self._version_name}")
            print(f"   版本号: {self._version}")
            print(f"   安装路径: {self.acad.Path}")
            return True

        except Exception as e:
            print(f"❌ 启动 AutoCAD 失败: {e}")
            return False

    def is_connected(self) -> bool:
        """
        检查是否仍然连接到 AutoCAD

        Returns:
            True 表示已连接，False 表示未连接
        """
        if self.acad is None:
            return False

        try:
            # 尝试访问一个简单的属性
            _ = self.acad.Version
            return True
        except:
            return False

    def reconnect(self) -> bool:
        """
        重新连接到 AutoCAD

        Returns:
            True 表示重连成功，False 表示失败
        """
        print("\n⚠️ 检测到连接断开，尝试重新连接...")
        self.acad = None
        return self.connect(start_if_not_running=False)

    def get_version_info(self) -> dict:
        """
        获取 AutoCAD 版本信息

        Returns:
            版本信息字典
        """
        if not self.is_connected():
            return {"error": "未连接到 AutoCAD"}

        return {
            "version": self._version,
            "version_name": self._version_name,
            "path": self.acad.Path,
            "visible": self.acad.Visible,
            "active_document": self.acad.ActiveDocument.Name if self.acad.Documents.Count > 0 else None,
            "documents_count": self.acad.Documents.Count,
        }

    def is_autocad_process_running(self) -> bool:
        """
        检测 AutoCAD 进程是否正在运行

        Returns:
            True 表示正在运行，False 表示未运行
        """
        for proc in psutil.process_iter(['name']):
            try:
                if 'acad.exe' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def wait_for_autocad_idle(self, timeout: int = 60) -> bool:
        """
        等待 AutoCAD 进程空闲

        Args:
            timeout: 超时时间（秒）

        Returns:
            True 表示已空闲，False 表示超时
        """
        print(f"\n⏳ 等待 AutoCAD 进程空闲（超时: {timeout} 秒）...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    if 'acad.exe' in proc.info['name'].lower():
                        cpu_usage = proc.cpu_percent(interval=1.0)

                        # CPU 使用率低于 5% 认为是空闲
                        if cpu_usage < 5.0:
                            print(f"✅ AutoCAD 已空闲（CPU 使用率: {cpu_usage:.1f}%）")
                            return True

                        print(f"⏳ AutoCAD 忙碌中（CPU 使用率: {cpu_usage:.1f}%）...")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            time.sleep(1)

        print("⚠️ 等待超时")
        return False

    def disconnect(self):
        """断开连接，释放 COM 对象"""
        if self.acad:
            print("\n🔌 断开 AutoCAD 连接...")
            self.acad = None

    @staticmethod
    def _get_version_name(version: str) -> str:
        """
        根据版本号获取 AutoCAD 名称

        Args:
            version: 版本号字符串（如 "24.0"）

        Returns:
            AutoCAD 名称（如 "AutoCAD 2021"）
        """
        version_map = {
            "22.0": "AutoCAD 2018",
            "23.0": "AutoCAD 2019",
            "23.1": "AutoCAD 2020",
            "24.0": "AutoCAD 2021",
            "24.1": "AutoCAD 2022",
            "24.2": "AutoCAD 2023",
            "24.3": "AutoCAD 2024",
        }
        return version_map.get(version, f"AutoCAD (版本 {version})")

    def __enter__(self):
        """上下文管理器支持"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时断开连接"""
        self.disconnect()


def demo_connection():
    """演示连接功能"""
    print("\n" + "=" * 60)
    print("AutoCAD 连接示例演示")
    print("=" * 60)

    # 方式1：直接使用
    print("\n【方式 1】直接连接")
    print("-" * 60)

    conn = AutoCADConnection()

    if conn.connect():
        # 获取版本信息
        info = conn.get_version_info()
        print("\n📋 AutoCAD 信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")

        # 检查连接状态
        print(f"\n🔗 连接状态: {'已连接' if conn.is_connected() else '未连接'}")

        # 检查进程状态
        print(f"🔍 进程状态: {'运行中' if conn.is_autocad_process_running() else '未运行'}")

        # 等待空闲
        conn.wait_for_autocad_idle(timeout=10)

        # 断开连接
        conn.disconnect()
    else:
        print("\n❌ 连接失败")

    # 方式2：使用上下文管理器
    print("\n\n【方式 2】使用上下文管理器")
    print("-" * 60)

    with AutoCADConnection() as conn:
        if conn.is_connected():
            print("✅ 已在上下文中连接")
            info = conn.get_version_info()
            print(f"   版本: {info['version_name']}")

    print("\n✅ 演示完成")


if __name__ == "__main__":
    # 运行演示
    demo_connection()

    # 保持窗口打开（方便查看结果）
    input("\n按 Enter 键退出...")
