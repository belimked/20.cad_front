"""
数据库模型 - 字典表
存储系统配置和字典数据

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func

try:
    from src.utils.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class Dictionary(Base):
    """
    系统字典表

    用途：
    - 存储系统配置参数
    - 存储远程下载 URL 等字典数据
    - 支持按类型分组
    """

    __tablename__ = 'sys_dictionary'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 字典信息
    dict_type = Column(String(50), nullable=False, index=True, comment='字典类型')
    dict_key = Column(String(100), nullable=False, index=True, comment='字典键')
    dict_value = Column(Text, nullable=False, comment='字典值')
    dict_label = Column(String(200), comment='字典标签（显示名称）')
    dict_description = Column(Text, comment='字典描述')

    # 排序和状态
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_active = Column(Boolean, default=True, comment='是否启用')

    # 扩展字段（JSON 格式存储额外信息）
    extra_data = Column(Text, comment='扩展数据（JSON）')

    # 审计字段
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    created_by = Column(String(50), comment='创建人')
    updated_by = Column(String(50), comment='更新人')

    # 备注
    remark = Column(Text, comment='备注')

    # 复合索引
    __table_args__ = (
        Index('idx_dict_type_key', 'dict_type', 'dict_key'),
        Index('idx_is_active', 'is_active'),
        {'comment': '系统字典表'}
    )

    def __repr__(self):
        return (
            f"<Dictionary(id={self.id}, type='{self.dict_type}', "
            f"key='{self.dict_key}', value='{self.dict_value}')>"
        )

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'dict_type': self.dict_type,
            'dict_key': self.dict_key,
            'dict_value': self.dict_value,
            'dict_label': self.dict_label,
            'dict_description': self.dict_description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'remark': self.remark
        }


class DownloadUrl(Base):
    """
    远程下载 URL 配置表

    专门存储 CAD 文件下载相关的 URL 配置
    """

    __tablename__ = 'download_urls'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # URL 信息
    url_name = Column(String(100), nullable=False, unique=True, comment='URL 名称（唯一标识）')
    url_value = Column(Text, nullable=False, comment='URL 地址')
    url_type = Column(String(50), default='api', comment='URL 类型（api/download/upload）')
    url_description = Column(String(200), comment='URL 描述')

    # HTTP 配置
    http_method = Column(String(10), default='GET', comment='HTTP 方法')
    headers = Column(Text, comment='请求头（JSON 格式）')
    timeout = Column(Integer, default=30, comment='超时时间（秒）')

    # 认证信息
    auth_type = Column(String(20), comment='认证类型（bearer/basic/apikey）')
    auth_value = Column(String(500), comment='认证凭证')

    # 状态和优先级
    is_active = Column(Boolean, default=True, comment='是否启用')
    priority = Column(Integer, default=0, comment='优先级（数字越大优先级越高）')

    # 审计字段
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    last_used_at = Column(DateTime, comment='最后使用时间')

    # 统计信息
    use_count = Column(Integer, default=0, comment='使用次数')
    success_count = Column(Integer, default=0, comment='成功次数')
    fail_count = Column(Integer, default=0, comment='失败次数')

    # 备注
    remark = Column(Text, comment='备注')

    # 索引
    __table_args__ = (
        Index('idx_url_type', 'url_type'),
        Index('idx_is_active', 'is_active'),
        Index('idx_priority', 'priority', 'is_active'),
        {'comment': '远程下载URL配置表'}
    )

    def __repr__(self):
        return (
            f"<DownloadUrl(id={self.id}, name='{self.url_name}', "
            f"type='{self.url_type}', url='{self.url_value[:50]}...')>"
        )

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'url_name': self.url_name,
            'url_value': self.url_value,
            'url_type': self.url_type,
            'url_description': self.url_description,
            'http_method': self.http_method,
            'headers': self.headers,
            'timeout': self.timeout,
            'auth_type': self.auth_type,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'use_count': self.use_count,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'remark': self.remark
        }

    def increment_use_count(self, success: bool = True):
        """增加使用计数"""
        self.use_count += 1
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1
        self.last_used_at = datetime.now()


if __name__ == "__main__":
    # 测试模型
    print("=== 测试数据库模型 ===\n")

    # 创建字典实例
    dict_item = Dictionary(
        dict_type='system',
        dict_key='app_name',
        dict_value='CAD Auto Processor',
        dict_label='应用名称',
        dict_description='CAD 文件自动化处理系统'
    )

    print(f"✅ 字典模型: {dict_item}")
    print(f"✅ 字典数据: {dict_item.to_dict()}")

    # 创建下载 URL 实例
    download_url = DownloadUrl(
        url_name='api_files_pending',
        url_value='https://api.example.com/api/cad/files/pending',
        url_type='api',
        url_description='获取待下载文件列表',
        http_method='GET',
        timeout=30
    )

    print(f"\n✅ URL 模型: {download_url}")
    print(f"✅ URL 数据: {download_url.to_dict()}")

    print("\n✅ 模型测试完成")
