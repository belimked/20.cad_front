"""
AutoCAD 配置管理服务

管理 AutoCAD 自动化的配置参数

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.autocad_config import AutoCADConfig, AutoCADTaskLog
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutoCADConfigService:
    """AutoCAD 配置管理服务"""

    def __init__(self, db_session: Session):
        """
        初始化服务

        Args:
            db_session: 数据库会话
        """
        self.db = db_session

    def create_config(self, config_data: Dict[str, Any]) -> AutoCADConfig:
        """
        创建配置

        Args:
            config_data: 配置数据字典

        Returns:
            创建的配置对象
        """
        try:
            # 处理 menu_operations（转换为 JSON 字符串）
            menu_ops = config_data.get('menu_operations')
            if menu_ops and isinstance(menu_ops, (list, dict)):
                config_data['menu_operations'] = json.dumps(menu_ops, ensure_ascii=False)

            # 创建配置对象
            config = AutoCADConfig(**config_data)

            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

            logger.info(f"Created AutoCAD config: {config.config_name}")
            return config

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create config: {e}")
            raise

    def get_config(self, config_id: Optional[int] = None,
                   config_name: Optional[str] = None) -> Optional[AutoCADConfig]:
        """
        获取配置

        Args:
            config_id: 配置ID
            config_name: 配置名称

        Returns:
            配置对象，未找到返回 None
        """
        try:
            if config_id:
                return self.db.query(AutoCADConfig).filter(
                    AutoCADConfig.id == config_id
                ).first()
            elif config_name:
                return self.db.query(AutoCADConfig).filter(
                    AutoCADConfig.config_name == config_name
                ).first()
            else:
                # 获取默认激活的配置
                return self.db.query(AutoCADConfig).filter(
                    AutoCADConfig.is_active == True
                ).first()

        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            return None

    def get_all_configs(self, active_only: bool = False) -> List[AutoCADConfig]:
        """
        获取所有配置

        Args:
            active_only: 是否仅获取激活的配置

        Returns:
            配置列表
        """
        try:
            query = self.db.query(AutoCADConfig)

            if active_only:
                query = query.filter(AutoCADConfig.is_active == True)

            return query.order_by(AutoCADConfig.created_at.desc()).all()

        except Exception as e:
            logger.error(f"Failed to get configs: {e}")
            return []

    def update_config(self, config_id: int, update_data: Dict[str, Any]) -> Optional[AutoCADConfig]:
        """
        更新配置

        Args:
            config_id: 配置ID
            update_data: 更新数据

        Returns:
            更新后的配置对象
        """
        try:
            config = self.db.query(AutoCADConfig).filter(
                AutoCADConfig.id == config_id
            ).first()

            if not config:
                logger.warning(f"Config not found: {config_id}")
                return None

            # 处理 menu_operations
            menu_ops = update_data.get('menu_operations')
            if menu_ops and isinstance(menu_ops, (list, dict)):
                update_data['menu_operations'] = json.dumps(menu_ops, ensure_ascii=False)

            # 更新字段
            for key, value in update_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            self.db.commit()
            self.db.refresh(config)

            logger.info(f"Updated config: {config.config_name}")
            return config

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update config: {e}")
            raise

    def delete_config(self, config_id: int) -> bool:
        """
        删除配置

        Args:
            config_id: 配置ID

        Returns:
            是否成功
        """
        try:
            config = self.db.query(AutoCADConfig).filter(
                AutoCADConfig.id == config_id
            ).first()

            if not config:
                return False

            self.db.delete(config)
            self.db.commit()

            logger.info(f"Deleted config: {config.config_name}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete config: {e}")
            return False

    def log_task_start(self, config_id: int, task_name: str, dwg_file: str) -> AutoCADTaskLog:
        """
        记录任务开始

        Args:
            config_id: 配置ID
            task_name: 任务名称
            dwg_file: DWG 文件路径

        Returns:
            任务日志对象
        """
        try:
            log = AutoCADTaskLog(
                config_id=config_id,
                task_name=task_name,
                dwg_file=dwg_file,
                status='running',
                start_time=datetime.now()
            )

            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)

            return log

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log task start: {e}")
            raise

    def log_task_end(self, log_id: int, status: str, error_message: Optional[str] = None,
                    execution_log: Optional[str] = None) -> bool:
        """
        记录任务结束

        Args:
            log_id: 日志ID
            status: 状态（success/failed）
            error_message: 错误信息
            execution_log: 执行日志

        Returns:
            是否成功
        """
        try:
            log = self.db.query(AutoCADTaskLog).filter(
                AutoCADTaskLog.id == log_id
            ).first()

            if not log:
                return False

            log.status = status
            log.error_message = error_message
            log.execution_log = execution_log
            log.end_time = datetime.now()

            # 计算时长
            if log.start_time:
                duration = (log.end_time - log.start_time).total_seconds()
                log.duration_seconds = duration

            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log task end: {e}")
            return False

    def get_task_logs(self, config_id: Optional[int] = None,
                     status: Optional[str] = None,
                     limit: int = 100) -> List[AutoCADTaskLog]:
        """
        获取任务日志

        Args:
            config_id: 配置ID（可选）
            status: 状态（可选）
            limit: 返回数量限制

        Returns:
            日志列表
        """
        try:
            query = self.db.query(AutoCADTaskLog)

            if config_id:
                query = query.filter(AutoCADTaskLog.config_id == config_id)

            if status:
                query = query.filter(AutoCADTaskLog.status == status)

            return query.order_by(
                AutoCADTaskLog.created_at.desc()
            ).limit(limit).all()

        except Exception as e:
            logger.error(f"Failed to get task logs: {e}")
            return []


def create_default_config(db_session: Session) -> AutoCADConfig:
    """
    创建默认配置

    Args:
        db_session: 数据库会话

    Returns:
        默认配置对象
    """
    service = AutoCADConfigService(db_session)

    default_config = {
        'config_name': 'default',
        'description': '默认 AutoCAD 自动化配置',
        'autocad_exe_path': None,  # 将使用 COM 自动查找
        'autocad_version': '2014',
        'dwg_file_path': None,  # 需要在使用时指定
        'force_close_existing': True,
        'startup_wait_time': 10.0,
        'startup_check_interval': 1.0,
        'post_startup_wait': 2.0,
        'file_open_retry_delay': 3.0,
        'file_open_max_retries': 3,
        'verification_wait_time': 30.0,
        'verification_check_interval': 2.0,
        'menu_operations': [],
        'is_active': True,
    }

    return service.create_config(default_config)
