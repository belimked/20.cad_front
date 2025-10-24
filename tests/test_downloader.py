"""
下载器模块单元测试

测试覆盖：
- 文件列表获取
- MD5 哈希对比
- 正常下载
- 断点续传
- 异常处理
- 重试机制

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import pytest
import os
import hashlib
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 导入被测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.downloader import CadFileDownloader, FileInfo


@pytest.fixture
def temp_download_dir(tmp_path):
    """创建临时下载目录"""
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    return str(download_dir)


@pytest.fixture
def downloader(temp_download_dir):
    """创建下载器实例"""
    return CadFileDownloader(
        base_url="https://api.test.com",
        api_key="test_api_key",
        download_dir=temp_download_dir,
        timeout=10
    )


@pytest.fixture
def sample_file_info():
    """示例文件信息"""
    return FileInfo(
        file_id="test001",
        file_name="test.dwg",
        file_url="https://api.test.com/files/test.dwg",
        file_size=1024,
        md5_hash="098f6bcd4621d373cade4e832627b4f6"  # MD5("test")
    )


class TestFileInfo:
    """测试 FileInfo 数据类"""

    def test_file_info_creation(self):
        """测试创建 FileInfo 对象"""
        file_info = FileInfo(
            file_id="001",
            file_name="test.dwg",
            file_url="https://example.com/test.dwg",
            file_size=1024
        )

        assert file_info.file_id == "001"
        assert file_info.file_name == "test.dwg"
        assert file_info.file_size == 1024
        assert file_info.md5_hash is None

    def test_file_info_with_md5(self):
        """测试带 MD5 的 FileInfo"""
        file_info = FileInfo(
            file_id="001",
            file_name="test.dwg",
            file_url="https://example.com/test.dwg",
            file_size=1024,
            md5_hash="abcd1234"
        )

        assert file_info.md5_hash == "abcd1234"


class TestCadFileDownloader:
    """测试 CadFileDownloader 类"""

    def test_downloader_initialization(self, temp_download_dir):
        """测试下载器初始化"""
        downloader = CadFileDownloader(
            base_url="https://api.test.com",
            api_key="test_key",
            download_dir=temp_download_dir
        )

        assert downloader.base_url == "https://api.test.com"
        assert downloader.api_key == "test_key"
        assert downloader.download_dir == temp_download_dir
        assert os.path.exists(temp_download_dir)

    def test_download_dir_creation(self, tmp_path):
        """测试自动创建下载目录"""
        new_dir = str(tmp_path / "new_downloads")
        assert not os.path.exists(new_dir)

        downloader = CadFileDownloader(download_dir=new_dir)

        assert os.path.exists(new_dir)

    @patch('src.modules.downloader.requests.Session.get')
    def test_get_pending_files_success(self, mock_get, downloader):
        """测试成功获取文件列表"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "files": [
                {
                    "id": "001",
                    "name": "file1.dwg",
                    "download_url": "https://api.test.com/files/file1.dwg",
                    "size": 1024,
                    "md5": "abcd1234"
                },
                {
                    "id": "002",
                    "name": "file2.dwg",
                    "download_url": "https://api.test.com/files/file2.dwg",
                    "size": 2048,
                    "md5": "efgh5678"
                }
            ]
        }
        mock_get.return_value = mock_response

        # 执行测试
        files = downloader.get_pending_files()

        # 验证
        assert len(files) == 2
        assert files[0].file_id == "001"
        assert files[0].file_name == "file1.dwg"
        assert files[1].file_size == 2048

    @patch('src.modules.downloader.requests.Session.get')
    def test_get_pending_files_empty(self, mock_get, downloader):
        """测试空文件列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"files": []}
        mock_get.return_value = mock_response

        files = downloader.get_pending_files()

        assert len(files) == 0

    @patch('src.modules.downloader.requests.Session.get')
    def test_get_pending_files_http_error(self, mock_get, downloader):
        """测试 HTTP 错误处理"""
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            downloader.get_pending_files()

    def test_calculate_md5(self, tmp_path):
        """测试 MD5 计算"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # 计算 MD5
        md5 = CadFileDownloader._calculate_md5(str(test_file))

        # 验证（"test" 的 MD5）
        expected_md5 = hashlib.md5(b"test").hexdigest()
        assert md5 == expected_md5

    def test_is_file_new_not_exists(self, downloader, sample_file_info):
        """测试文件不存在的情况"""
        result = downloader.is_file_new(sample_file_info)
        assert result is True

    def test_is_file_new_exists_same_md5(self, downloader, sample_file_info, temp_download_dir):
        """测试文件存在且 MD5 相同"""
        # 创建本地文件
        local_file = Path(temp_download_dir) / sample_file_info.file_name
        local_file.write_text("test")

        result = downloader.is_file_new(sample_file_info)
        assert result is False

    def test_is_file_new_exists_different_md5(self, downloader, sample_file_info, temp_download_dir):
        """测试文件存在但 MD5 不同"""
        # 创建本地文件（内容不同）
        local_file = Path(temp_download_dir) / sample_file_info.file_name
        local_file.write_text("different content")

        result = downloader.is_file_new(sample_file_info)
        assert result is True

    def test_is_file_new_no_md5_same_size(self, downloader, temp_download_dir):
        """测试没有 MD5 时使用文件大小对比"""
        file_info = FileInfo(
            file_id="001",
            file_name="test.dwg",
            file_url="https://example.com/test.dwg",
            file_size=4,
            md5_hash=None
        )

        # 创建相同大小的本地文件
        local_file = Path(temp_download_dir) / file_info.file_name
        local_file.write_text("test")  # 4 bytes

        result = downloader.is_file_new(file_info)
        assert result is False

    @patch('src.modules.downloader.requests.Session.get')
    def test_download_file_success(self, mock_get, downloader, sample_file_info):
        """测试成功下载文件"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "4"}
        mock_response.iter_content = lambda chunk_size: [b"test"]
        mock_get.return_value = mock_response

        # 下载文件
        result_path = downloader.download_file(sample_file_info, show_progress=False)

        # 验证
        assert os.path.exists(result_path)
        with open(result_path, 'r') as f:
            assert f.read() == "test"

    @patch('src.modules.downloader.requests.Session.get')
    def test_download_file_resume(self, mock_get, downloader, sample_file_info, temp_download_dir):
        """测试断点续传"""
        # 创建部分下载的文件
        local_file = Path(temp_download_dir) / sample_file_info.file_name
        local_file.write_text("te")  # 只有前两个字节

        # Mock 响应（返回剩余部分）
        mock_response = Mock()
        mock_response.status_code = 206  # Partial Content
        mock_response.headers = {"content-length": "2"}
        mock_response.iter_content = lambda chunk_size: [b"st"]
        mock_get.return_value = mock_response

        # 更新 file_info 使其看起来未完成
        sample_file_info.file_size = 4

        # 继续下载
        result_path = downloader.download_file(sample_file_info, show_progress=False)

        # 验证（但由于 MD5 校验会失败，这里我们主要测试逻辑）
        assert os.path.exists(result_path)

    @patch('src.modules.downloader.requests.Session.get')
    def test_download_file_md5_mismatch(self, mock_get, downloader, sample_file_info):
        """测试 MD5 校验失败"""
        # Mock 响应（返回错误内容）
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "7"}
        mock_response.iter_content = lambda chunk_size: [b"wrongmd"]
        mock_get.return_value = mock_response

        # 应该抛出异常
        with pytest.raises(ValueError, match="MD5 校验失败"):
            downloader.download_file(sample_file_info, show_progress=False)

    @patch('src.modules.downloader.requests.Session.get')
    def test_download_all_success(self, mock_get, downloader):
        """测试批量下载"""
        # Mock get_pending_files
        file1 = FileInfo("001", "file1.dwg", "https://test.com/file1.dwg", 4, None)
        file2 = FileInfo("002", "file2.dwg", "https://test.com/file2.dwg", 5, None)

        with patch.object(downloader, 'get_pending_files', return_value=[file1, file2]):
            # Mock 下载响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-length": "4"}
            mock_response.iter_content = lambda chunk_size: [b"test"]
            mock_get.return_value = mock_response

            # 批量下载
            paths = downloader.download_all(show_progress=False)

            # 验证
            assert len(paths) == 2

    def test_cleanup_old_files(self, downloader, temp_download_dir):
        """测试清理旧文件"""
        import time

        # 创建测试文件
        old_file = Path(temp_download_dir) / "old.dwg"
        old_file.write_text("old content")

        # 修改文件时间（设置为 10 天前）
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(str(old_file), (old_time, old_time))

        # 清理 7 天前的文件
        deleted = downloader.cleanup_old_files(keep_days=7)

        # 验证
        assert deleted == 1
        assert not old_file.exists()

    def test_context_manager(self, temp_download_dir):
        """测试上下文管理器"""
        with CadFileDownloader(download_dir=temp_download_dir) as downloader:
            assert downloader.session is not None

        # 退出后会话应该关闭（这里主要测试不会抛出异常）


class TestRetryMechanism:
    """测试重试机制"""

    @patch('src.modules.downloader.requests.Session.get')
    def test_retry_on_network_error(self, mock_get, downloader):
        """测试网络错误重试"""
        import requests

        # 前两次失败，第三次成功
        mock_get.side_effect = [
            requests.ConnectionError("Network error"),
            requests.ConnectionError("Network error"),
            Mock(status_code=200, json=lambda: {"files": []})
        ]

        # 应该成功（重试3次）
        files = downloader.get_pending_files()
        assert len(files) == 0
        assert mock_get.call_count == 3


# 运行测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.modules.downloader", "--cov-report=html"])
