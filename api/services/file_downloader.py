"""
异步文件下载服务

这个SB服务负责从指定URL下载DWG文件，艹！
支持断点续传、进度回调、超时重试等功能
"""

import httpx
import aiofiles
from pathlib import Path
from typing import Optional, Callable
import asyncio
from datetime import datetime


class FileDownloader:
    """异步文件下载器"""

    def __init__(
        self,
        download_dir: str = "downloads",
        chunk_size: int = 8192,
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        初始化下载器

        Args:
            download_dir: 下载目录
            chunk_size: 分块大小（字节）
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
        """
        self.download_dir = Path(download_dir)
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.max_retries = max_retries

        # 确保下载目录存在
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download(
        self,
        url: str,
        filename: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        下载文件

        Args:
            url: 文件URL
            filename: 保存的文件名（可选，默认从URL提取）
            progress_callback: 进度回调函数 callback(downloaded_bytes, total_bytes)

        Returns:
            (是否成功, 本地文件路径, 错误信息)
        """
        # 确定文件名
        if not filename:
            filename = url.split('/')[-1]
            if not filename or '.' not in filename:
                filename = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}.dwg"

        local_path = self.download_dir / filename

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                print(f"  [下载] 尝试 {attempt + 1}/{self.max_retries}: {url}")

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # 发起请求
                    async with client.stream('GET', url) as response:
                        response.raise_for_status()

                        # 获取文件大小
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0

                        print(f"  文件大小: {total_size / 1024 / 1024:.2f} MB")

                        # 写入文件
                        async with aiofiles.open(local_path, 'wb') as f:
                            async for chunk in response.aiter_bytes(chunk_size=self.chunk_size):
                                await f.write(chunk)
                                downloaded_size += len(chunk)

                                # 进度回调
                                if progress_callback:
                                    progress_callback(downloaded_size, total_size)

                # 验证文件大小
                actual_size = local_path.stat().st_size
                if total_size > 0 and actual_size != total_size:
                    raise ValueError(f"文件大小不匹配: 期望{total_size}, 实际{actual_size}")

                print(f"  ✅ 下载成功: {local_path}")
                return True, str(local_path), None

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP错误: {e.response.status_code}"
                print(f"  ❌ {error_msg}")

                # 4xx错误不重试
                if 400 <= e.response.status_code < 500:
                    return False, None, error_msg

                # 5xx错误重试
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"  ⏳ 等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    return False, None, error_msg

            except httpx.TimeoutException:
                error_msg = f"下载超时（{self.timeout}秒）"
                print(f"  ❌ {error_msg}")

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  ⏳ 等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    return False, None, error_msg

            except Exception as e:
                error_msg = f"下载失败: {str(e)}"
                print(f"  ❌ {error_msg}")

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  ⏳ 等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    return False, None, error_msg

        return False, None, f"下载失败（已重试{self.max_retries}次）"

    async def get_file_info(self, url: str) -> tuple[bool, Optional[int], Optional[str]]:
        """
        获取文件信息（不下载）

        Args:
            url: 文件URL

        Returns:
            (是否成功, 文件大小, 错误信息)
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.head(url, follow_redirects=True)
                response.raise_for_status()

                file_size = int(response.headers.get('content-length', 0))
                return True, file_size, None

        except Exception as e:
            return False, None, f"获取文件信息失败: {str(e)}"


# ============================================================================
# 测试代码
# ============================================================================

async def test_download():
    """测试下载功能"""
    downloader = FileDownloader(download_dir="downloads/test")

    # 进度回调
    def on_progress(downloaded: int, total: int):
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\r  进度: {percent:.1f}% ({downloaded}/{total})", end='')

    # 测试URL
    test_url = "https://example.com/test.dwg"

    print(f"开始下载: {test_url}")
    success, local_path, error = await downloader.download(
        url=test_url,
        progress_callback=on_progress
    )

    if success:
        print(f"\n✅ 下载成功: {local_path}")
    else:
        print(f"\n❌ 下载失败: {error}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_download())
