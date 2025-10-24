"""
数据库初始化脚本
创建数据库表并初始化字典数据

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.database import get_db_manager, db_session
from src.utils.logger import setup_logger, logger
from src.models import Base, Dictionary, DownloadUrl


def create_tables():
    """创建所有数据库表"""
    logger.info("开始创建数据库表...")

    db_manager = get_db_manager()

    try:
        # 创建所有表
        db_manager.create_all_tables()
        logger.info("✅ 数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"❌ 创建数据库表失败: {e}")
        return False


def init_dictionary_data():
    """初始化字典数据"""
    logger.info("开始初始化字典数据...")

    # 系统配置字典
    system_dicts = [
        {
            'dict_type': 'system',
            'dict_key': 'app_name',
            'dict_value': 'CAD Auto Processor',
            'dict_label': '应用名称',
            'dict_description': 'CAD 文件自动化处理系统',
            'sort_order': 1
        },
        {
            'dict_type': 'system',
            'dict_key': 'app_version',
            'dict_value': '1.0.0',
            'dict_label': '应用版本',
            'dict_description': '当前应用版本号',
            'sort_order': 2
        },
        {
            'dict_type': 'system',
            'dict_key': 'environment',
            'dict_value': 'development',
            'dict_label': '运行环境',
            'dict_description': '当前运行环境（development/production）',
            'sort_order': 3
        },
    ]

    # 文件下载配置字典
    download_dicts = [
        {
            'dict_type': 'download',
            'dict_key': 'chunk_size',
            'dict_value': '8192',
            'dict_label': '下载分块大小',
            'dict_description': '文件下载时的分块大小（字节）',
            'sort_order': 1
        },
        {
            'dict_type': 'download',
            'dict_key': 'max_retries',
            'dict_value': '3',
            'dict_label': '最大重试次数',
            'dict_description': '下载失败时的最大重试次数',
            'sort_order': 2
        },
        {
            'dict_type': 'download',
            'dict_key': 'timeout',
            'dict_value': '30',
            'dict_label': '下载超时时间',
            'dict_description': '下载超时时间（秒）',
            'sort_order': 3
        },
    ]

    # AutoCAD 配置字典
    autocad_dicts = [
        {
            'dict_type': 'autocad',
            'dict_key': 'install_path',
            'dict_value': 'C:\\Program Files\\Autodesk\\AutoCAD 2024',
            'dict_label': 'AutoCAD 安装路径',
            'dict_description': 'AutoCAD 软件安装路径',
            'sort_order': 1
        },
        {
            'dict_type': 'autocad',
            'dict_key': 'timeout',
            'dict_value': '600',
            'dict_label': '操作超时时间',
            'dict_description': 'AutoCAD 操作超时时间（秒）',
            'sort_order': 2
        },
    ]

    all_dicts = system_dicts + download_dicts + autocad_dicts

    try:
        with db_session() as session:
            for dict_data in all_dicts:
                # 检查是否已存在
                existing = session.query(Dictionary).filter_by(
                    dict_type=dict_data['dict_type'],
                    dict_key=dict_data['dict_key']
                ).first()

                if not existing:
                    dict_item = Dictionary(**dict_data, created_by='system')
                    session.add(dict_item)
                    logger.debug(f"添加字典: {dict_data['dict_type']}.{dict_data['dict_key']}")
                else:
                    logger.debug(f"字典已存在，跳过: {dict_data['dict_type']}.{dict_data['dict_key']}")

            session.commit()

        logger.info(f"✅ 字典数据初始化成功，共 {len(all_dicts)} 条记录")
        return True
    except Exception as e:
        logger.error(f"❌ 初始化字典数据失败: {e}")
        return False


def init_download_urls():
    """初始化下载 URL 配置"""
    logger.info("开始初始化下载 URL 配置...")

    download_urls = [
        {
            'url_name': 'api_files_pending',
            'url_value': 'https://api.example.com/api/cad/files/pending',
            'url_type': 'api',
            'url_description': '获取待下载文件列表',
            'http_method': 'GET',
            'timeout': 30,
            'priority': 100,
            'is_active': True
        },
        {
            'url_name': 'api_file_download',
            'url_value': 'https://api.example.com/api/cad/files/{file_id}/download',
            'url_type': 'download',
            'url_description': '下载指定文件',
            'http_method': 'GET',
            'timeout': 300,
            'priority': 90,
            'is_active': True
        },
        {
            'url_name': 'api_task_complete',
            'url_value': 'https://api.example.com/api/cad/tasks/{task_id}/complete',
            'url_type': 'api',
            'url_description': '标记任务完成',
            'http_method': 'POST',
            'timeout': 30,
            'priority': 80,
            'is_active': True
        },
        {
            'url_name': 'api_task_fail',
            'url_value': 'https://api.example.com/api/cad/tasks/{task_id}/fail',
            'url_type': 'api',
            'url_description': '标记任务失败',
            'http_method': 'POST',
            'timeout': 30,
            'priority': 70,
            'is_active': True
        },
        {
            'url_name': 'api_result_upload',
            'url_value': 'https://api.example.com/api/cad/results/upload',
            'url_type': 'upload',
            'url_description': '上传处理结果',
            'http_method': 'POST',
            'timeout': 600,
            'priority': 60,
            'is_active': True
        },
    ]

    try:
        with db_session() as session:
            for url_data in download_urls:
                # 检查是否已存在
                existing = session.query(DownloadUrl).filter_by(
                    url_name=url_data['url_name']
                ).first()

                if not existing:
                    url_item = DownloadUrl(**url_data)
                    session.add(url_item)
                    logger.debug(f"添加 URL: {url_data['url_name']}")
                else:
                    logger.debug(f"URL 已存在，跳过: {url_data['url_name']}")

            session.commit()

        logger.info(f"✅ URL 配置初始化成功，共 {len(download_urls)} 条记录")
        return True
    except Exception as e:
        logger.error(f"❌ 初始化 URL 配置失败: {e}")
        return False


def verify_initialization():
    """验证初始化结果"""
    logger.info("开始验证初始化结果...")

    try:
        with db_session() as session:
            # 统计字典数量
            dict_count = session.query(Dictionary).count()
            logger.info(f"字典表记录数: {dict_count}")

            # 统计 URL 数量
            url_count = session.query(DownloadUrl).count()
            logger.info(f"URL 配置表记录数: {url_count}")

            # 显示部分数据
            logger.info("\n=== 字典示例数据 ===")
            dicts = session.query(Dictionary).limit(5).all()
            for d in dicts:
                logger.info(f"  {d.dict_type}.{d.dict_key} = {d.dict_value}")

            logger.info("\n=== URL 配置示例数据 ===")
            urls = session.query(DownloadUrl).limit(3).all()
            for u in urls:
                logger.info(f"  {u.url_name}: {u.url_value}")

        logger.info("\n✅ 验证完成")
        return True
    except Exception as e:
        logger.error(f"❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("  CAD 自动化处理系统 - 数据库初始化")
    print("=" * 60)
    print()

    # 初始化日志
    setup_logger(log_level="INFO")

    # 测试数据库连接
    logger.info("测试数据库连接...")
    db_manager = get_db_manager()
    if not db_manager.test_connection():
        logger.error("❌ 数据库连接失败，请检查配置")
        return False

    logger.info("✅ 数据库连接成功\n")

    # 创建表
    if not create_tables():
        return False

    print()

    # 初始化字典数据
    if not init_dictionary_data():
        return False

    print()

    # 初始化下载 URL
    if not init_download_urls():
        return False

    print()

    # 验证初始化
    if not verify_initialization():
        return False

    print()
    print("=" * 60)
    print("  ✅ 数据库初始化完成！")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"初始化过程发生异常: {e}", exc_info=True)
        sys.exit(1)
