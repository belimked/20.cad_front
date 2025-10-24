"""
CAD 文件下载模块 - 远程文件下载和同步
支持断点续传、MD5 校验、自动重试

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import hashlib
import os
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 假设 logger 和 config 已经设置
try:
    from src.utils.logger import get_logger
    from src.utils.config import get_config
    from src.services.dict_service import DownloadUrlService
    logger = get_logger()
    config = get_config()
    use_db_urls = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    config = None
    use_db_urls = False


@dataclass
class FileInfo:
    """文件信息数据类"""
    file_id: str
    file_name: str
    file_url: str
    file_size: int
    md5_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CadFileDownloader:
    """
    CAD 文件下载器

    功能：
    - 从 HTTP API 获取待下载文件列表
    - MD5 哈希对比避免重复下载
    - 支持断点续传（Range headers）
    - tqdm 进度条显示
    - 异常处理和自动重试
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        download_dir: Optional[str] = None,
        timeout: int = 30,
        chunk_size: int = 8192
    ):
        """
        初始化下载器

        Args:
            base_url: API 基础 URL
            api_key: API 认证密钥
            download_dir: 下载目录
            timeout: 请求超时时间（秒）
            chunk_size: 下载分块大小（字节）
        """
        # 从配置加载参数
        if config:
            self.base_url = base_url or config.get("server.base_url")
            self.api_key = api_key or config.get("server.api_key")
            self.download_dir = download_dir or config.get("paths.downloads", "./data/downloads")
            self.timeout = config.get("server.timeout", timeout)
        else:
            self.base_url = base_url or "https://api.example.com"
            self.api_key = api_key or ""
            self.download_dir = download_dir or "./data/downloads"
            self.timeout = timeout

        self.chunk_size = chunk_size

        # 确保下载目录存在
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)

        # HTTP 会话
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "CAD-Auto-Processor/1.0"
        })

        logger.info(f"文件下载器初始化完成 - 下载目录: {self.download_dir}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True
    )
    def get_pending_files(self) -> List[FileInfo]:
        """
        获取待下载文件列表

        Returns:
            FileInfo 列表

        Raises:
            requests.RequestException: HTTP 请求失败
        """
        # 优先从数据库获取 URL
        if use_db_urls:
            try:
                api_url = DownloadUrlService.get_url_value('api_files_pending')
                if api_url:
                    endpoint = api_url
                    logger.debug(f"从数据库获取 API URL: {endpoint}")
                else:
                    endpoint = f"{self.base_url}/api/cad/files/pending"
                    logger.debug(f"数据库中未找到 API URL，使用配置: {endpoint}")
            except Exception as e:
                logger.warning(f"从数据库获取 URL 失败，使用配置: {e}")
                endpoint = f"{self.base_url}/api/cad/files/pending"
        else:
            endpoint = f"{self.base_url}/api/cad/files/pending"

        try:
            logger.info(f"正在获取待下载文件列表: {endpoint}")
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()

            # 记录 URL 使用情况（如果启用了数据库）
            if use_db_urls:
                try:
                    DownloadUrlService.record_usage('api_files_pending', success=True)
                except Exception:
                    pass  # 忽略记录失败

            data = response.json()

            # 解析文件列表
            files = []
            for item in data.get("files", []):
                file_info = FileInfo(
                    file_id=item.get("id"),
                    file_name=item.get("name"),
                    file_url=item.get("download_url"),
                    file_size=item.get("size", 0),
                    md5_hash=item.get("md5"),
                    metadata=item.get("metadata", {})
                )
                files.append(file_info)

            logger.info(f"获取到 {len(files)} 个待下载文件")
            return files

        except requests.HTTPError as e:
            # 记录失败
            if use_db_urls:
                try:
                    DownloadUrlService.record_usage('api_files_pending', success=False)
                except Exception:
                    pass

            logger.error(f"获取文件列表失败 (HTTP {e.response.status_code}): {e}")
            raise
        except requests.RequestException as e:
            # 记录失败
            if use_db_urls:
                try:
                    DownloadUrlService.record_usage('api_files_pending', success=False)
                except Exception:
                    pass

            logger.error(f"网络请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"解析文件列表失败: {e}")
            raise

    def is_file_new(self, file_info: FileInfo) -> bool:
        """
        判断文件是否需要下载（通过 MD5 对比）

        Args:
            file_info: 文件信息

        Returns:
            True 表示需要下载，False 表示已存在且相同
        """
        local_path = os.path.join(self.download_dir, file_info.file_name)

        # 文件不存在，需要下载
        if not os.path.exists(local_path):
            logger.debug(f"文件不存在，需要下载: {file_info.file_name}")
            return True

        # 如果没有提供 MD5，比较文件大小
        if not file_info.md5_hash:
            local_size = os.path.getsize(local_path)
            if local_size != file_info.file_size:
                logger.debug(f"文件大小不匹配，需要重新下载: {file_info.file_name}")
                return True
            logger.debug(f"文件大小匹配，跳过下载: {file_info.file_name}")
            return False

        # 计算本地文件 MD5
        local_md5 = self._calculate_md5(local_path)

        if local_md5 != file_info.md5_hash:
            logger.debug(
                f"MD5 不匹配，需要重新下载: {file_info.file_name}\n"
                f"  本地: {local_md5}\n"
                f"  远程: {file_info.md5_hash}"
            )
            return True

        logger.info(f"文件已存在且校验通过，跳过下载: {file_info.file_name}")
        return False

    @staticmethod
    def _calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
        """
        计算文件 MD5 哈希值

        Args:
            file_path: 文件路径
            chunk_size: 读取分块大小

        Returns:
            MD5 哈希值（小写十六进制字符串）
        """
        md5_hash = hashlib.md5()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)

        return md5_hash.hexdigest()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
        reraise=True
    )
    def download_file(
        self,
        file_info: FileInfo,
        force: bool = False,
        show_progress: bool = True
    ) -> str:
        """
        下载文件（支持断点续传）

        Args:
            file_info: 文件信息
            force: 强制重新下载（忽略已存在文件）
            show_progress: 是否显示进度条

        Returns:
            下载后的文件路径

        Raises:
            requests.RequestException: 下载失败
            IOError: 文件写入失败
        """
        local_path = os.path.join(self.download_dir, file_info.file_name)

        # 检查是否需要下载
        if not force and not self.is_file_new(file_info):
            logger.info(f"文件已存在，跳过下载: {file_info.file_name}")
            return local_path

        # 检查是否支持断点续传
        resume_byte_pos = 0
        mode = "wb"

        if os.path.exists(local_path):
            resume_byte_pos = os.path.getsize(local_path)
            if resume_byte_pos < file_info.file_size:
                logger.info(
                    f"检测到未完成的下载，从 {resume_byte_pos} 字节处继续: "
                    f"{file_info.file_name}"
                )
                mode = "ab"
            else:
                # 文件大小匹配或超过，重新下载
                resume_byte_pos = 0
                mode = "wb"

        # 设置 Range header 用于断点续传
        headers = {}
        if resume_byte_pos > 0:
            headers["Range"] = f"bytes={resume_byte_pos}-"

        try:
            logger.info(f"开始下载: {file_info.file_name} ({file_info.file_size} 字节)")

            response = self.session.get(
                file_info.file_url,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            # 获取总大小
            total_size = int(response.headers.get("content-length", 0))
            if resume_byte_pos > 0:
                total_size += resume_byte_pos

            # 下载文件
            with open(local_path, mode) as f:
                if show_progress:
                    with tqdm(
                        total=total_size,
                        initial=resume_byte_pos,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=file_info.file_name
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)

            # 验证下载
            if file_info.md5_hash:
                downloaded_md5 = self._calculate_md5(local_path)
                if downloaded_md5 != file_info.md5_hash:
                    os.remove(local_path)  # 删除损坏文件
                    raise ValueError(
                        f"文件下载后 MD5 校验失败: {file_info.file_name}\n"
                        f"  期望: {file_info.md5_hash}\n"
                        f"  实际: {downloaded_md5}"
                    )

            logger.info(f"文件下载成功: {file_info.file_name} -> {local_path}")
            return local_path

        except requests.HTTPError as e:
            logger.error(f"下载失败 (HTTP {e.response.status_code}): {file_info.file_name}")
            raise
        except IOError as e:
            logger.error(f"文件写入失败: {file_info.file_name} - {e}")
            raise
        except Exception as e:
            logger.error(f"下载过程中发生异常: {file_info.file_name} - {e}")
            raise

    def download_all(
        self,
        force: bool = False,
        show_progress: bool = True
    ) -> List[str]:
        """
        下载所有待处理文件

        Args:
            force: 强制重新下载
            show_progress: 是否显示进度条

        Returns:
            下载成功的文件路径列表
        """
        logger.info("开始批量下载任务...")

        # 获取文件列表
        files = self.get_pending_files()

        if not files:
            logger.info("没有待下载文件")
            return []

        downloaded_paths = []
        failed_files = []

        for file_info in files:
            try:
                path = self.download_file(file_info, force=force, show_progress=show_progress)
                downloaded_paths.append(path)
            except Exception as e:
                logger.error(f"下载文件失败: {file_info.file_name} - {e}")
                failed_files.append(file_info.file_name)

        logger.info(
            f"批量下载完成 - 成功: {len(downloaded_paths)}, 失败: {len(failed_files)}"
        )

        if failed_files:
            logger.warning(f"失败文件列表: {', '.join(failed_files)}")

        return downloaded_paths

    def cleanup_old_files(self, keep_days: int = 7) -> int:
        """
        清理旧文件

        Args:
            keep_days: 保留天数

        Returns:
            删除的文件数量
        """
        import time

        logger.info(f"清理 {keep_days} 天前的旧文件...")

        current_time = time.time()
        cutoff_time = current_time - (keep_days * 24 * 60 * 60)

        deleted_count = 0
        download_path = Path(self.download_dir)

        for file_path in download_path.iterdir():
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"删除旧文件: {file_path.name}")
                    except Exception as e:
                        logger.error(f"删除文件失败: {file_path.name} - {e}")

        logger.info(f"清理完成，删除了 {deleted_count} 个旧文件")
        return deleted_count

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时关闭会话"""
        self.session.close()


if __name__ == "__main__":
    # 测试下载器
    print("=== 测试 CAD 文件下载器 ===\n")

    # 创建下载器实例
    downloader = CadFileDownloader()

    # 示例：创建测试文件信息
    test_file = FileInfo(
        file_id="test001",
        file_name="test.dwg",
        file_url="https://example.com/files/test.dwg",
        file_size=1024000,
        md5_hash="abcd1234"
    )

    print(f"下载器配置:")
    print(f"  - 基础 URL: {downloader.base_url}")
    print(f"  - 下载目录: {downloader.download_dir}")
    print(f"  - 超时设置: {downloader.timeout}秒")

    print("\n✅ 下载器模块测试完成")
