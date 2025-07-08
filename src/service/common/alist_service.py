import os
import httpx
import aiofiles
from typing import Optional, Dict
from urllib.parse import quote

class AlistService:
    def __init__(self, config: Dict):
        self.base_url = config.get("url")
        self.username = config.get("username")
        self.password = config.get("password")
        self.target_dir = config.get("target_dir", "/").strip('/')
        self.token = None
        # 确保基础URL不以斜杠结尾
        self.base_url = self.base_url.rstrip('/')

    async def _login(self):
        """
        登录 Alist 并获取 token
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/api/auth/login", json={"username": self.username, "password": self.password})
                response.raise_for_status()
                data = response.json()
                self.token = data.get("data", {}).get("token")
                if not self.token:
                    raise ValueError("Alist login failed, token not found in response.")
            except (httpx.RequestError, ValueError) as e:
                raise Exception(f"Failed to login to Alist: {e}") from e

    async def upload_file(self, local_file_path: str, remote_subdir: str = "") -> str:
        """
        上传单个文件到 Alist

        Args:
            local_file_path (str): 本地文件路径
            remote_subdir (str): 在Alist目标目录下的子目录 (可选)

        Returns:
            str: 上传后文件的可访问URL
        """
        if not self.token:
            await self._login()

        file_name = os.path.basename(local_file_path)
        # 确保远程子目录不是绝对路径
        remote_subdir = remote_subdir.strip('/')
        
        # 构造远程路径, 并确保是unix风格
        full_remote_path = f"/{self.target_dir}/{remote_subdir}/{file_name}".replace("\\", "/")
        # 移除可能的多余斜杠
        full_remote_path = os.path.normpath(full_remote_path).replace("\\", "/")

        # Alist API需要固定的 /api/fs/put 端点
        upload_url = f"{self.base_url}/api/fs/put"
        
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/octet-stream",
            # 路径通过请求头传递, 且需要URL编码
            "File-Path": quote(full_remote_path)
        }

        async with aiofiles.open(local_file_path, "rb") as f:
            try:
                # 核心改动: 先将文件完整读入内存, 再进行上传
                file_content = await f.read()
                
                # 增加客户端超时时间
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.put(upload_url, headers=headers, content=file_content)
                    response.raise_for_status()
                    
                    # 检查响应内容
                    result = response.json()
                    if result.get("code") != 200:
                        error_message = f"Alist API returned an error: {result.get('message', 'Unknown error')}"
                        raise Exception(error_message)

            except httpx.HTTPStatusError as e:
                error_message = f"HTTP error during Alist upload: {e.response.status_code} - {e.response.text}"
                raise Exception(error_message) from e
            except httpx.RequestError as e:
                error_message = f"Network error during Alist upload: {type(e).__name__}"
                raise Exception(error_message) from e
            except Exception as e:
                # 捕获其他所有异常, 如JSON解码失败
                error_message = f"An unexpected error occurred during Alist upload: {str(e)}"
                raise Exception(error_message) from e

        return f"{self.base_url}{full_remote_path}" 