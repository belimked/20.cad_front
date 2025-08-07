import os
import httpx
import aiofiles
import logging
import time
from typing import Optional, Dict
from urllib.parse import quote

# 配置日志
logger = logging.getLogger(__name__)

class AlistService:
    def __init__(self, config: Dict):
        self.base_url = config.get("url")
        self.username = config.get("username")
        self.password = config.get("password")
        self.target_dir = config.get("target_dir", "/").strip('/')
        self.token = None
        # 确保基础URL不以斜杠结尾
        self.base_url = self.base_url.rstrip('/')

        # 记录初始化信息
        logger.info(f"初始化 AlistService - URL: {self.base_url}, 用户名: {self.username}, 目标目录: {self.target_dir}")

        # 验证配置
        if not self.base_url:
            logger.error("Alist URL 配置为空")
            raise ValueError("Alist URL 不能为空")
        if not self.username:
            logger.error("Alist 用户名配置为空")
            raise ValueError("Alist 用户名不能为空")
        if not self.password:
            logger.error("Alist 密码配置为空")
            raise ValueError("Alist 密码不能为空")

    async def _login(self):
        """
        登录 Alist 并获取 token
        """
        login_url = f"{self.base_url}/api/auth/login"
        login_data = {"username": self.username, "password": self.password}

        logger.info(f"开始登录 Alist - URL: {login_url}")
        logger.debug(f"登录数据: {{'username': '{self.username}', 'password': '***'}}")

        # 配置超时设置：连接超时30秒，读取超时60秒
        timeout = httpx.Timeout(connect=30.0, read=60.0, write=30.0, pool=10.0)

        start_time = time.time()

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                logger.info("正在尝试连接到 Alist 服务器...")

                response = await client.post(login_url, json=login_data)

                elapsed_time = time.time() - start_time
                logger.info(f"收到响应，耗时: {elapsed_time:.2f}秒")
                logger.info(f"响应状态码: {response.status_code}")
                logger.debug(f"响应头: {dict(response.headers)}")

                response.raise_for_status()

                data = response.json()
                logger.debug(f"响应数据: {data}")

                self.token = data.get("data", {}).get("token")
                if not self.token:
                    logger.error("登录响应中未找到 token")
                    logger.error(f"完整响应数据: {data}")
                    raise ValueError("Alist login failed, token not found in response.")

                logger.info("Alist 登录成功，已获取 token")

            except httpx.ConnectTimeout as e:
                elapsed_time = time.time() - start_time
                logger.error(f"连接超时 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"无法连接到 Alist 服务器: {self.base_url}")
                logger.error(f"连接超时详情: {e}")
                raise Exception(f"Failed to connect to Alist server (connection timeout after {elapsed_time:.2f}s): {e}") from e

            except httpx.ReadTimeout as e:
                elapsed_time = time.time() - start_time
                logger.error(f"读取超时 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"服务器响应超时: {e}")
                raise Exception(f"Alist server response timeout after {elapsed_time:.2f}s: {e}") from e

            except httpx.HTTPStatusError as e:
                elapsed_time = time.time() - start_time
                logger.error(f"HTTP 状态错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"状态码: {e.response.status_code}")
                logger.error(f"响应内容: {e.response.text}")
                raise Exception(f"Alist login HTTP error {e.response.status_code}: {e.response.text}") from e

            except httpx.RequestError as e:
                elapsed_time = time.time() - start_time
                logger.error(f"请求错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"请求错误类型: {type(e).__name__}")
                logger.error(f"请求错误详情: {e}")
                raise Exception(f"Network error during Alist login ({type(e).__name__}): {e}") from e

            except ValueError as e:
                logger.error(f"数据解析错误: {e}")
                raise Exception(f"Failed to parse Alist login response: {e}") from e

            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"未知错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"未知错误类型: {type(e).__name__}")
                logger.error(f"未知错误详情: {e}")
                raise Exception(f"Unexpected error during Alist login: {e}") from e

    async def upload_file(self, local_file_path: str, remote_subdir: str = "") -> str:
        """
        上传单个文件到 Alist

        Args:
            local_file_path (str): 本地文件路径
            remote_subdir (str): 在Alist目标目录下的子目录 (可选)

        Returns:
            str: 上传后文件的可访问URL
        """
        logger.info(f"开始上传文件: {local_file_path}")
        logger.info(f"远程子目录: {remote_subdir}")

        # 检查本地文件是否存在
        if not os.path.exists(local_file_path):
            logger.error(f"本地文件不存在: {local_file_path}")
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        # 获取文件大小
        file_size = os.path.getsize(local_file_path)
        logger.info(f"文件大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")

        if not self.token:
            logger.info("未找到 token，开始登录...")
            await self._login()

        file_name = os.path.basename(local_file_path)
        # 确保远程子目录不是绝对路径
        remote_subdir = remote_subdir.strip('/')

        # 构造远程路径, 并确保是unix风格
        full_remote_path = f"/{self.target_dir}/{remote_subdir}/{file_name}".replace("\\", "/")
        # 移除可能的多余斜杠
        full_remote_path = os.path.normpath(full_remote_path).replace("\\", "/")

        logger.info(f"目标远程路径: {full_remote_path}")

        # Alist API需要固定的 /api/fs/put 端点
        upload_url = f"{self.base_url}/api/fs/put"

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/octet-stream",
            # 路径通过请求头传递, 且需要URL编码
            "File-Path": quote(full_remote_path)
        }

        logger.info(f"上传 URL: {upload_url}")
        logger.debug(f"请求头: {dict(headers)}")
        logger.debug(f"编码后的文件路径: {quote(full_remote_path)}")

        upload_start_time = time.time()

        async with aiofiles.open(local_file_path, "rb") as f:
            try:
                logger.info("开始读取文件内容...")
                read_start_time = time.time()

                # 核心改动: 先将文件完整读入内存, 再进行上传
                file_content = await f.read()

                read_elapsed = time.time() - read_start_time
                logger.info(f"文件读取完成，耗时: {read_elapsed:.2f}秒")

                # 配置上传超时：连接30秒，读写各300秒
                timeout = httpx.Timeout(connect=30.0, read=300.0, write=300.0, pool=10.0)

                logger.info("开始上传文件到 Alist...")
                upload_request_start = time.time()

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(upload_url, headers=headers, content=file_content)

                    upload_request_elapsed = time.time() - upload_request_start
                    logger.info(f"上传请求完成，耗时: {upload_request_elapsed:.2f}秒")
                    logger.info(f"响应状态码: {response.status_code}")
                    logger.debug(f"响应头: {dict(response.headers)}")

                    response.raise_for_status()

                    # 检查响应内容
                    result = response.json()
                    logger.debug(f"上传响应数据: {result}")

                    if result.get("code") != 200:
                        error_message = f"Alist API returned an error: {result.get('message', 'Unknown error')}"
                        logger.error(f"Alist API 错误: {error_message}")
                        logger.error(f"完整响应: {result}")
                        raise Exception(error_message)

                    total_elapsed = time.time() - upload_start_time
                    logger.info(f"文件上传成功！总耗时: {total_elapsed:.2f}秒")

            except httpx.ConnectTimeout as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传连接超时 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"无法连接到 Alist 上传端点: {upload_url}")
                error_message = f"Upload connection timeout after {elapsed_time:.2f}s: {e}"
                raise Exception(error_message) from e

            except httpx.ReadTimeout as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传读取超时 - 耗时: {elapsed_time:.2f}秒")
                error_message = f"Upload read timeout after {elapsed_time:.2f}s: {e}"
                raise Exception(error_message) from e

            except httpx.WriteTimeout as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传写入超时 - 耗时: {elapsed_time:.2f}秒")
                error_message = f"Upload write timeout after {elapsed_time:.2f}s: {e}"
                raise Exception(error_message) from e

            except httpx.HTTPStatusError as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传 HTTP 状态错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"状态码: {e.response.status_code}")
                logger.error(f"响应内容: {e.response.text}")
                error_message = f"HTTP error during Alist upload: {e.response.status_code} - {e.response.text}"
                raise Exception(error_message) from e

            except httpx.RequestError as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传网络错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"网络错误类型: {type(e).__name__}")
                logger.error(f"网络错误详情: {e}")
                error_message = f"Network error during Alist upload ({type(e).__name__}): {e}"
                raise Exception(error_message) from e

            except Exception as e:
                elapsed_time = time.time() - upload_start_time
                logger.error(f"上传未知错误 - 耗时: {elapsed_time:.2f}秒")
                logger.error(f"错误类型: {type(e).__name__}")
                logger.error(f"错误详情: {e}")
                # 捕获其他所有异常, 如JSON解码失败
                error_message = f"An unexpected error occurred during Alist upload: {str(e)}"
                raise Exception(error_message) from e

        final_url = f"{self.base_url}{full_remote_path}"
        logger.info(f"文件上传完成，访问 URL: {final_url}")
        return final_url

    async def test_connection(self) -> Dict:
        """
        测试与 Alist 服务器的连接

        Returns:
            Dict: 连接测试结果
        """
        logger.info("开始测试 Alist 服务器连接...")

        result = {
            "success": False,
            "server_reachable": False,
            "login_successful": False,
            "error_message": None,
            "response_time": None,
            "server_info": None
        }

        start_time = time.time()

        try:
            # 测试基本连接
            timeout = httpx.Timeout(connect=10.0, read=30.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                # 先测试服务器是否可达
                logger.info(f"测试服务器连通性: {self.base_url}")

                try:
                    # 尝试访问根路径或健康检查端点
                    health_response = await client.get(f"{self.base_url}/")
                    result["server_reachable"] = True
                    result["response_time"] = time.time() - start_time
                    logger.info(f"服务器可达，响应时间: {result['response_time']:.2f}秒")
                    logger.info(f"服务器响应状态: {health_response.status_code}")

                except Exception as e:
                    logger.warning(f"服务器根路径访问失败: {e}")

                # 测试登录
                logger.info("测试登录功能...")
                login_start = time.time()

                login_url = f"{self.base_url}/api/auth/login"
                login_data = {"username": self.username, "password": self.password}

                response = await client.post(login_url, json=login_data)
                login_time = time.time() - login_start

                logger.info(f"登录请求完成，耗时: {login_time:.2f}秒")
                logger.info(f"登录响应状态: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    token = data.get("data", {}).get("token")

                    if token:
                        result["login_successful"] = True
                        result["success"] = True
                        result["server_info"] = {
                            "status_code": response.status_code,
                            "response_data": data
                        }
                        logger.info("登录测试成功")
                    else:
                        result["error_message"] = "登录响应中未找到 token"
                        logger.error(result["error_message"])
                else:
                    result["error_message"] = f"登录失败，状态码: {response.status_code}"
                    logger.error(f"{result['error_message']}, 响应: {response.text}")

        except httpx.ConnectTimeout as e:
            result["error_message"] = f"连接超时: {e}"
            logger.error(result["error_message"])

        except httpx.RequestError as e:
            result["error_message"] = f"网络请求错误: {e}"
            logger.error(result["error_message"])

        except Exception as e:
            result["error_message"] = f"未知错误: {e}"
            logger.error(result["error_message"])

        total_time = time.time() - start_time
        result["total_test_time"] = total_time

        logger.info(f"连接测试完成，总耗时: {total_time:.2f}秒")
        logger.info(f"测试结果: {result}")

        return result
