"""
OCR文件管理工具

负责OCR截图的存储、清理和归档管理

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import json


class OCRFileManager:
    """OCR文件管理器"""

    def __init__(
        self,
        base_dir: str = "screenshots",
        timestamp_format: str = "%Y%m%d_%H%M%S",
        cleanup_enabled: bool = False,
        cleanup_strategy: str = "archive",
        archive_dir: Optional[str] = None,
        retention_days: int = 7
    ):
        """
        初始化文件管理器

        Args:
            base_dir: 截图基础目录
            timestamp_format: 时间戳格式
            cleanup_enabled: 是否启用清理
            cleanup_strategy: 清理策略 (delete/archive/none)
            archive_dir: 归档目录
            retention_days: 文件保留天数
        """
        self.base_dir = Path(base_dir)
        self.timestamp_format = timestamp_format
        self.cleanup_enabled = cleanup_enabled
        self.cleanup_strategy = cleanup_strategy
        self.archive_dir = Path(archive_dir) if archive_dir else self.base_dir.parent / "screenshots_archive"
        self.retention_days = retention_days

        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if self.cleanup_strategy == 'archive':
            self.archive_dir.mkdir(parents=True, exist_ok=True)

    def get_screenshot_dir(self, create_new: bool = True) -> Path:
        """
        获取截图保存目录

        Args:
            create_new: 是否创建新的时间戳目录

        Returns:
            截图目录路径
        """
        if create_new:
            # 创建新的时间戳目录
            timestamp = datetime.now().strftime(self.timestamp_format)
            screenshot_dir = self.base_dir / timestamp
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            return screenshot_dir
        else:
            # 返回基础目录
            return self.base_dir

    def cleanup_old_files(self) -> Dict[str, int]:
        """
        清理旧的截图文件

        Returns:
            清理统计信息
        """
        if not self.cleanup_enabled:
            return {
                'deleted': 0,
                'archived': 0,
                'skipped': 0,
                'errors': 0
            }

        stats = {
            'deleted': 0,
            'archived': 0,
            'skipped': 0,
            'errors': 0
        }

        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # 遍历基础目录下的所有子目录
        if not self.base_dir.exists():
            return stats

        for item in self.base_dir.iterdir():
            if not item.is_dir():
                continue

            try:
                # 尝试从目录名解析时间戳
                dir_timestamp = self._parse_timestamp_from_dirname(item.name)

                if dir_timestamp and dir_timestamp < cutoff_date:
                    # 需要清理
                    if self.cleanup_strategy == 'delete':
                        # 删除
                        shutil.rmtree(item)
                        stats['deleted'] += 1
                        print(f"  🗑️ 已删除: {item.name}")

                    elif self.cleanup_strategy == 'archive':
                        # 归档
                        archive_path = self.archive_dir / item.name
                        if archive_path.exists():
                            # 如果归档目录已存在，删除旧的
                            shutil.rmtree(archive_path)

                        shutil.move(str(item), str(archive_path))
                        stats['archived'] += 1
                        print(f"  📦 已归档: {item.name} -> {archive_path}")

                    else:
                        # none: 不清理
                        stats['skipped'] += 1
                else:
                    stats['skipped'] += 1

            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ 清理失败 {item.name}: {e}")

        return stats

    def _parse_timestamp_from_dirname(self, dirname: str) -> Optional[datetime]:
        """
        从目录名解析时间戳

        Args:
            dirname: 目录名

        Returns:
            解析后的datetime对象，失败返回None
        """
        try:
            # 尝试使用配置的格式解析
            return datetime.strptime(dirname, self.timestamp_format)
        except:
            try:
                # 尝试常见格式
                common_formats = [
                    "%Y%m%d_%H%M%S",
                    "%Y%m%d_%H%M%S_%f",
                    "%Y-%m-%d_%H-%M-%S",
                    "%Y%m%d"
                ]
                for fmt in common_formats:
                    try:
                        return datetime.strptime(dirname, fmt)
                    except:
                        continue
            except:
                pass

        return None

    def get_directory_stats(self) -> Dict[str, any]:
        """
        获取目录统计信息

        Returns:
            统计信息字典
        """
        stats = {
            'base_dir': str(self.base_dir),
            'archive_dir': str(self.archive_dir),
            'total_dirs': 0,
            'total_files': 0,
            'total_size_mb': 0,
            'oldest_dir': None,
            'newest_dir': None,
            'dirs_to_cleanup': 0
        }

        if not self.base_dir.exists():
            return stats

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        dir_timestamps = []

        for item in self.base_dir.iterdir():
            if not item.is_dir():
                continue

            stats['total_dirs'] += 1

            # 统计文件数和大小
            for file in item.rglob('*'):
                if file.is_file():
                    stats['total_files'] += 1
                    stats['total_size_mb'] += file.stat().st_size / (1024 * 1024)

            # 解析时间戳
            dir_timestamp = self._parse_timestamp_from_dirname(item.name)
            if dir_timestamp:
                dir_timestamps.append(dir_timestamp)
                if dir_timestamp < cutoff_date:
                    stats['dirs_to_cleanup'] += 1

        # 最老和最新的目录
        if dir_timestamps:
            stats['oldest_dir'] = min(dir_timestamps).strftime("%Y-%m-%d %H:%M:%S")
            stats['newest_dir'] = max(dir_timestamps).strftime("%Y-%m-%d %H:%M:%S")

        stats['total_size_mb'] = round(stats['total_size_mb'], 2)

        return stats

    def get_recent_directories(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的目录列表

        Args:
            limit: 返回数量限制

        Returns:
            目录信息列表
        """
        if not self.base_dir.exists():
            return []

        dirs_info = []

        for item in self.base_dir.iterdir():
            if not item.is_dir():
                continue

            # 统计文件数
            file_count = sum(1 for f in item.rglob('*') if f.is_file())

            # 解析时间戳
            dir_timestamp = self._parse_timestamp_from_dirname(item.name)

            dirs_info.append({
                'name': item.name,
                'path': str(item),
                'timestamp': dir_timestamp,
                'file_count': file_count,
                'age_days': (datetime.now() - dir_timestamp).days if dir_timestamp else None
            })

        # 按时间戳排序（最新的在前）
        dirs_info.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)

        return dirs_info[:limit]

    def export_config(self) -> Dict:
        """
        导出当前配置

        Returns:
            配置字典
        """
        return {
            'base_dir': str(self.base_dir),
            'timestamp_format': self.timestamp_format,
            'cleanup_enabled': self.cleanup_enabled,
            'cleanup_strategy': self.cleanup_strategy,
            'archive_dir': str(self.archive_dir),
            'retention_days': self.retention_days
        }

    def __repr__(self) -> str:
        config = self.export_config()
        return f"OCRFileManager({json.dumps(config, ensure_ascii=False, indent=2)})"


def test_file_manager():
    """测试文件管理器"""
    print("=" * 80)
    print("OCR文件管理器测试")
    print("=" * 80)

    # 创建管理器
    manager = OCRFileManager(
        base_dir="screenshots",
        timestamp_format="%Y%m%d_%H%M%S",
        cleanup_enabled=True,
        cleanup_strategy="archive",
        archive_dir="screenshots_archive",
        retention_days=7
    )

    print(f"\n配置信息:")
    print(manager)

    # 获取统计信息
    print(f"\n目录统计:")
    stats = manager.get_directory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 获取最近的目录
    print(f"\n最近10个目录:")
    recent = manager.get_recent_directories(10)
    for i, dir_info in enumerate(recent, 1):
        print(f"  {i}. {dir_info['name']}")
        print(f"     文件数: {dir_info['file_count']}")
        print(f"     年龄: {dir_info['age_days']} 天")

    # 测试清理
    print(f"\n清理旧文件...")
    cleanup_stats = manager.cleanup_old_files()
    print(f"  删除: {cleanup_stats['deleted']}")
    print(f"  归档: {cleanup_stats['archived']}")
    print(f"  跳过: {cleanup_stats['skipped']}")
    print(f"  错误: {cleanup_stats['errors']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_file_manager()
