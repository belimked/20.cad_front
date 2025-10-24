"""
数据库连接管理模块 - 基于 SQLAlchemy
提供数据库连接池管理和会话管理

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, Optional
import pymysql

try:
    from src.utils.logger import get_logger
    from src.utils.config import get_config
    logger = get_logger()
    config = get_config()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    config = None


# SQLAlchemy 基类
Base = declarative_base()


class DatabaseManager:
    """
    数据库连接管理器

    功能：
    - 数据库连接池管理
    - 会话管理
    - 自动重连
    - 连接测试
    """

    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _session_factory = None
    _scoped_session = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化数据库管理器"""
        if self._engine is not None:
            return  # 已初始化，避免重复

        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """初始化数据库引擎"""
        # 从配置读取数据库连接信息
        if config:
            db_config = {
                'host': config.get('database.host', 'localhost'),
                'port': config.get('database.port', 3306),
                'username': config.get('database.username', 'root'),
                'password': config.get('database.password', ''),
                'database': config.get('database.database', 'cad_mgt'),
                'charset': config.get('database.charset', 'utf8mb4'),
                'pool_size': config.get('database.pool_size', 5),
                'max_overflow': config.get('database.max_overflow', 10),
                'pool_timeout': config.get('database.pool_timeout', 30),
                'pool_recycle': config.get('database.pool_recycle', 3600),
                'echo': config.get('database.echo', False)
            }
        else:
            # 默认配置
            db_config = {
                'host': '10.3.19.189',
                'port': 3313,
                'username': 'fangda',
                'password': '123456',
                'database': 'cad_mgt',
                'charset': 'utf8mb4',
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 3600,
                'echo': False
            }

        # 构建数据库连接 URL
        database_url = (
            f"mysql+pymysql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset={db_config['charset']}"
        )

        # 创建引擎
        try:
            self._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=db_config['pool_size'],
                max_overflow=db_config['max_overflow'],
                pool_timeout=db_config['pool_timeout'],
                pool_recycle=db_config['pool_recycle'],
                echo=db_config['echo'],
                pool_pre_ping=True,  # 连接前自动 ping 检测
            )

            # 添加连接事件监听器
            @event.listens_for(self._engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                """连接建立时的回调"""
                logger.debug("数据库连接已建立")

            @event.listens_for(self._engine, "close")
            def receive_close(dbapi_conn, connection_record):
                """连接关闭时的回调"""
                logger.debug("数据库连接已关闭")

            # 创建会话工厂
            self._session_factory = sessionmaker(bind=self._engine)
            self._scoped_session = scoped_session(self._session_factory)

            logger.info(
                f"数据库连接初始化成功 - "
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )

        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise

    def get_engine(self):
        """获取数据库引擎"""
        return self._engine

    def get_session(self) -> Session:
        """
        获取数据库会话

        Returns:
            Session 对象
        """
        return self._scoped_session()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        数据库会话上下文管理器

        自动处理事务提交和回滚

        Usage:
            with db_manager.session_scope() as session:
                # 使用 session 进行数据库操作
                result = session.query(Model).all()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库事务回滚: {e}")
            raise
        finally:
            session.close()

    def create_all_tables(self) -> None:
        """创建所有表"""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise

    def drop_all_tables(self) -> None:
        """删除所有表（谨慎使用）"""
        try:
            Base.metadata.drop_all(self._engine)
            logger.warning("数据库表已全部删除")
        except Exception as e:
            logger.error(f"删除数据库表失败: {e}")
            raise

    def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            连接成功返回 True，否则返回 False
        """
        try:
            with self._engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False

    def close(self) -> None:
        """关闭所有连接"""
        try:
            if self._scoped_session:
                self._scoped_session.remove()
            if self._engine:
                self._engine.dispose()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时关闭连接"""
        self.close()


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    获取全局数据库管理器实例

    Returns:
        DatabaseManager 实例
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Session:
    """
    获取数据库会话（便捷函数）

    Returns:
        Session 对象
    """
    return get_db_manager().get_session()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器（便捷函数）

    Usage:
        with db_session() as session:
            result = session.query(Model).all()
    """
    db_manager = get_db_manager()
    with db_manager.session_scope() as session:
        yield session


if __name__ == "__main__":
    # 测试数据库连接
    print("=== 测试数据库连接 ===\n")

    try:
        db_manager = get_db_manager()

        # 测试连接
        if db_manager.test_connection():
            print("✅ 数据库连接成功")
        else:
            print("❌ 数据库连接失败")

        # 测试会话
        with db_manager.session_scope() as session:
            result = session.execute("SELECT DATABASE()")
            db_name = result.scalar()
            print(f"✅ 当前数据库: {db_name}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        if _db_manager:
            _db_manager.close()

    print("\n✅ 数据库模块测试完成")
