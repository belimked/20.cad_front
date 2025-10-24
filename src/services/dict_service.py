"""
字典服务模块
提供字典和下载 URL 的 CRUD 操作

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from datetime import datetime

try:
    from src.utils.database import db_session
    from src.utils.logger import get_logger
    from src.models.dictionary import Dictionary, DownloadUrl
    logger = get_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DictionaryService:
    """
    字典服务类

    提供字典数据的增删改查操作
    """

    @staticmethod
    def get_by_type_and_key(dict_type: str, dict_key: str) -> Optional[Dictionary]:
        """
        根据类型和键获取字典

        Args:
            dict_type: 字典类型
            dict_key: 字典键

        Returns:
            Dictionary 对象或 None
        """
        try:
            with db_session() as session:
                return session.query(Dictionary).filter_by(
                    dict_type=dict_type,
                    dict_key=dict_key,
                    is_active=True
                ).first()
        except Exception as e:
            logger.error(f"获取字典失败: {e}")
            return None

    @staticmethod
    def get_value(dict_type: str, dict_key: str, default: Any = None) -> Any:
        """
        获取字典值（便捷方法）

        Args:
            dict_type: 字典类型
            dict_key: 字典键
            default: 默认值

        Returns:
            字典值或默认值
        """
        dict_item = DictionaryService.get_by_type_and_key(dict_type, dict_key)
        return dict_item.dict_value if dict_item else default

    @staticmethod
    def get_by_type(dict_type: str, active_only: bool = True) -> List[Dictionary]:
        """
        根据类型获取所有字典

        Args:
            dict_type: 字典类型
            active_only: 是否只返回启用的字典

        Returns:
            Dictionary 列表
        """
        try:
            with db_session() as session:
                query = session.query(Dictionary).filter_by(dict_type=dict_type)

                if active_only:
                    query = query.filter_by(is_active=True)

                return query.order_by(Dictionary.sort_order).all()
        except Exception as e:
            logger.error(f"获取字典列表失败: {e}")
            return []

    @staticmethod
    def create(dict_data: Dict[str, Any]) -> Optional[Dictionary]:
        """
        创建字典

        Args:
            dict_data: 字典数据

        Returns:
            创建的 Dictionary 对象或 None
        """
        try:
            with db_session() as session:
                dict_item = Dictionary(**dict_data)
                session.add(dict_item)
                session.commit()
                logger.info(f"创建字典成功: {dict_item.dict_type}.{dict_item.dict_key}")
                return dict_item
        except Exception as e:
            logger.error(f"创建字典失败: {e}")
            return None

    @staticmethod
    def update(dict_id: int, update_data: Dict[str, Any]) -> bool:
        """
        更新字典

        Args:
            dict_id: 字典 ID
            update_data: 更新数据

        Returns:
            是否成功
        """
        try:
            with db_session() as session:
                dict_item = session.query(Dictionary).filter_by(id=dict_id).first()

                if not dict_item:
                    logger.warning(f"字典不存在: ID={dict_id}")
                    return False

                for key, value in update_data.items():
                    if hasattr(dict_item, key):
                        setattr(dict_item, key, value)

                session.commit()
                logger.info(f"更新字典成功: ID={dict_id}")
                return True
        except Exception as e:
            logger.error(f"更新字典失败: {e}")
            return False

    @staticmethod
    def delete(dict_id: int, soft_delete: bool = True) -> bool:
        """
        删除字典

        Args:
            dict_id: 字典 ID
            soft_delete: 是否软删除（设置 is_active=False）

        Returns:
            是否成功
        """
        try:
            with db_session() as session:
                dict_item = session.query(Dictionary).filter_by(id=dict_id).first()

                if not dict_item:
                    logger.warning(f"字典不存在: ID={dict_id}")
                    return False

                if soft_delete:
                    dict_item.is_active = False
                    session.commit()
                    logger.info(f"软删除字典成功: ID={dict_id}")
                else:
                    session.delete(dict_item)
                    session.commit()
                    logger.info(f"硬删除字典成功: ID={dict_id}")

                return True
        except Exception as e:
            logger.error(f"删除字典失败: {e}")
            return False


class DownloadUrlService:
    """
    下载 URL 服务类

    提供下载 URL 的增删改查操作
    """

    @staticmethod
    def get_by_name(url_name: str) -> Optional[DownloadUrl]:
        """
        根据名称获取 URL

        Args:
            url_name: URL 名称

        Returns:
            DownloadUrl 对象或 None
        """
        try:
            with db_session() as session:
                return session.query(DownloadUrl).filter_by(
                    url_name=url_name,
                    is_active=True
                ).first()
        except Exception as e:
            logger.error(f"获取 URL 失败: {e}")
            return None

    @staticmethod
    def get_url_value(url_name: str, **kwargs) -> Optional[str]:
        """
        获取 URL 地址（支持参数替换）

        Args:
            url_name: URL 名称
            **kwargs: URL 参数（用于替换模板）

        Returns:
            URL 地址或 None

        Examples:
            >>> get_url_value('api_file_download', file_id='123')
            'https://api.example.com/api/cad/files/123/download'
        """
        url_obj = DownloadUrlService.get_by_name(url_name)

        if not url_obj:
            return None

        url = url_obj.url_value

        # 替换 URL 中的参数
        if kwargs:
            try:
                url = url.format(**kwargs)
            except KeyError as e:
                logger.error(f"URL 参数缺失: {e}")
                return None

        return url

    @staticmethod
    def get_by_type(url_type: str, active_only: bool = True) -> List[DownloadUrl]:
        """
        根据类型获取所有 URL

        Args:
            url_type: URL 类型
            active_only: 是否只返回启用的 URL

        Returns:
            DownloadUrl 列表
        """
        try:
            with db_session() as session:
                query = session.query(DownloadUrl).filter_by(url_type=url_type)

                if active_only:
                    query = query.filter_by(is_active=True)

                return query.order_by(DownloadUrl.priority.desc()).all()
        except Exception as e:
            logger.error(f"获取 URL 列表失败: {e}")
            return []

    @staticmethod
    def record_usage(url_name: str, success: bool = True) -> bool:
        """
        记录 URL 使用情况

        Args:
            url_name: URL 名称
            success: 是否成功

        Returns:
            是否记录成功
        """
        try:
            with db_session() as session:
                url_obj = session.query(DownloadUrl).filter_by(url_name=url_name).first()

                if not url_obj:
                    logger.warning(f"URL 不存在: {url_name}")
                    return False

                url_obj.increment_use_count(success=success)
                session.commit()

                logger.debug(f"记录 URL 使用: {url_name} (成功={success})")
                return True
        except Exception as e:
            logger.error(f"记录 URL 使用失败: {e}")
            return False

    @staticmethod
    def create(url_data: Dict[str, Any]) -> Optional[DownloadUrl]:
        """
        创建 URL

        Args:
            url_data: URL 数据

        Returns:
            创建的 DownloadUrl 对象或 None
        """
        try:
            with db_session() as session:
                url_obj = DownloadUrl(**url_data)
                session.add(url_obj)
                session.commit()
                logger.info(f"创建 URL 成功: {url_obj.url_name}")
                return url_obj
        except Exception as e:
            logger.error(f"创建 URL 失败: {e}")
            return None

    @staticmethod
    def update(url_id: int, update_data: Dict[str, Any]) -> bool:
        """
        更新 URL

        Args:
            url_id: URL ID
            update_data: 更新数据

        Returns:
            是否成功
        """
        try:
            with db_session() as session:
                url_obj = session.query(DownloadUrl).filter_by(id=url_id).first()

                if not url_obj:
                    logger.warning(f"URL 不存在: ID={url_id}")
                    return False

                for key, value in update_data.items():
                    if hasattr(url_obj, key):
                        setattr(url_obj, key, value)

                session.commit()
                logger.info(f"更新 URL 成功: ID={url_id}")
                return True
        except Exception as e:
            logger.error(f"更新 URL 失败: {e}")
            return False

    @staticmethod
    def get_all_active_urls() -> Dict[str, str]:
        """
        获取所有启用的 URL（返回字典格式）

        Returns:
            {url_name: url_value} 格式的字典
        """
        try:
            with db_session() as session:
                urls = session.query(DownloadUrl).filter_by(is_active=True).all()
                return {url.url_name: url.url_value for url in urls}
        except Exception as e:
            logger.error(f"获取所有 URL 失败: {e}")
            return {}


if __name__ == "__main__":
    # 测试字典服务
    print("=== 测试字典服务 ===\n")

    # 测试获取字典值
    app_name = DictionaryService.get_value('system', 'app_name', 'Unknown')
    print(f"✅ 应用名称: {app_name}")

    # 测试获取字典列表
    system_dicts = DictionaryService.get_by_type('system')
    print(f"✅ 系统字典数量: {len(system_dicts)}")

    # 测试 URL 服务
    print("\n=== 测试 URL 服务 ===\n")

    # 获取 URL
    api_url = DownloadUrlService.get_url_value('api_files_pending')
    print(f"✅ API URL: {api_url}")

    # 获取带参数的 URL
    download_url = DownloadUrlService.get_url_value('api_file_download', file_id='123')
    print(f"✅ 下载 URL: {download_url}")

    # 获取所有 API 类型的 URL
    api_urls = DownloadUrlService.get_by_type('api')
    print(f"✅ API URL 数量: {len(api_urls)}")

    print("\n✅ 服务测试完成")
