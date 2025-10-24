"""
配置管理模块 - 使用单例模式加载和管理配置
支持从 YAML 文件加载配置，并支持环境变量覆盖

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache


class ConfigManager:
    """
    配置管理器 - 单例模式

    功能：
    - 从 YAML 文件加载配置
    - 支持环境变量覆盖
    - 提供配置项访问接口
    - 配置验证
    """

    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _config_file: Optional[str] = None

    def __new__(cls, config_file: str = None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file: str = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为 ./config/config.yaml
        """
        # 避免重复初始化
        if self._config and config_file == self._config_file:
            return

        if config_file is None:
            # 默认配置文件路径
            config_file = os.path.join(
                Path(__file__).parent.parent.parent,
                "config",
                "config.yaml"
            )

        self._config_file = config_file
        self._load_config()
        self._apply_env_overrides()

    def _load_config(self) -> None:
        """从 YAML 文件加载配置"""
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(
                f"配置文件未找到: {self._config_file}\n"
                "请确保 config/config.yaml 文件存在"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    def _apply_env_overrides(self) -> None:
        """
        应用环境变量覆盖

        环境变量格式：CAD_SECTION_KEY=value
        例如：CAD_SERVER_BASE_URL=http://localhost:8000
        """
        env_prefix = "CAD_"

        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # 移除前缀并转换为小写
                config_key = key[len(env_prefix):].lower()

                # 分割配置路径 (例如: server_base_url -> server.base_url)
                parts = config_key.split('_', 1)

                if len(parts) == 2:
                    section, sub_key = parts
                    if section in self._config:
                        # 将下划线转换为嵌套的键
                        sub_parts = sub_key.split('_')
                        current = self._config[section]

                        for part in sub_parts[:-1]:
                            if part in current:
                                current = current[part]
                            else:
                                break
                        else:
                            # 设置值
                            current[sub_parts[-1]] = self._parse_env_value(value)

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """
        解析环境变量值

        尝试将字符串转换为适当的类型（int, float, bool, str）
        """
        # 布尔值
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # 数字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # 默认返回字符串
        return value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key_path: 配置路径，使用点号分隔，例如 "server.base_url"
            default: 默认值，当配置项不存在时返回

        Returns:
            配置项的值

        Examples:
            >>> config = ConfigManager()
            >>> base_url = config.get("server.base_url")
            >>> timeout = config.get("server.timeout", 30)
        """
        keys = key_path.split('.')
        value = self._config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置段

        Args:
            section: 配置段名称，例如 "server", "paths"

        Returns:
            配置段字典
        """
        return self._config.get(section, {})

    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置项（运行时修改）

        Args:
            key_path: 配置路径，使用点号分隔
            value: 配置值
        """
        keys = key_path.split('.')
        config = self._config

        # 遍历到倒数第二个键
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # 设置最后一个键的值
        config[keys[-1]] = value

    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()
        self._apply_env_overrides()

    def validate(self) -> bool:
        """
        验证配置完整性

        Returns:
            配置是否有效
        """
        required_sections = ['server', 'paths', 'autocad', 'monitor', 'upload', 'logging']

        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"缺少必需的配置段: {section}")

        # 验证必需的配置项
        required_items = {
            'server.base_url': str,
            'paths.downloads': str,
            'paths.outputs': str,
            'logging.level': str,
        }

        for key_path, expected_type in required_items.items():
            value = self.get(key_path)
            if value is None:
                raise ValueError(f"缺少必需的配置项: {key_path}")
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"配置项 {key_path} 类型错误，期望 {expected_type.__name__}，"
                    f"实际 {type(value).__name__}"
                )

        return True

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<ConfigManager(config_file='{self._config_file}')>"


# 全局配置实例（使用 lru_cache 确保单例）
@lru_cache(maxsize=1)
def get_config(config_file: str = None) -> ConfigManager:
    """
    获取全局配置实例

    Args:
        config_file: 配置文件路径（可选）

    Returns:
        ConfigManager 实例
    """
    return ConfigManager(config_file)


# 便捷访问函数
def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    便捷函数：获取配置值

    Args:
        key_path: 配置路径
        default: 默认值

    Returns:
        配置值
    """
    return get_config().get(key_path, default)


if __name__ == "__main__":
    # 测试配置管理器
    try:
        config = get_config()
        config.validate()

        print("✅ 配置加载成功")
        print(f"服务器 URL: {config.get('server.base_url')}")
        print(f"日志级别: {config.get('logging.level')}")
        print(f"下载目录: {config.get('paths.downloads')}")

    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
