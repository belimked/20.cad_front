#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存管理模块
提供统一的缓存清理接口，确保数据一致性
"""

import logging
from typing import Optional

# 配置日志
logger = logging.getLogger(__name__)

def clear_all_related_caches(business_object: str) -> None:
    """
    清理指定业务对象的所有相关缓存
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
    """
    try:
        # 导入缓存清理函数
        from .base_elements import clear_base_elements_cache
        from .business_rules import clear_business_rules_cache
        from .answer_elements import clear_answer_elements_cache
        
        # 清理基础元素缓存
        clear_base_elements_cache(business_object)
        logger.info(f"已清理业务对象 {business_object} 的基础元素缓存")
        
        # 清理业务规则缓存（规则文件通常以 {business_object}Rules 命名）
        rules_object = f"{business_object}Rules"
        clear_business_rules_cache(rules_object)
        logger.info(f"已清理业务对象 {business_object} 的业务规则缓存")
        
        # 清理回答元素缓存
        clear_answer_elements_cache(business_object)
        logger.info(f"已清理业务对象 {business_object} 的回答元素缓存")
        
        # 清理数据生成服务中的规则缓存
        _clear_generation_services_cache()
        logger.info(f"已清理数据生成服务的规则缓存")
        
        logger.info(f"成功清理业务对象 {business_object} 的所有相关缓存")
        
    except Exception as e:
        logger.error(f"清理业务对象 {business_object} 缓存时发生错误: {str(e)}")
        raise

def clear_all_caches() -> None:
    """
    清理所有缓存
    """
    try:
        # 导入缓存清理函数
        from .base_elements import clear_base_elements_cache
        from .business_rules import clear_business_rules_cache
        from .answer_elements import clear_answer_elements_cache
        
        # 清理所有缓存
        clear_base_elements_cache()
        clear_business_rules_cache()
        clear_answer_elements_cache()
        _clear_generation_services_cache()
        
        logger.info("成功清理所有缓存")
        
    except Exception as e:
        logger.error(f"清理所有缓存时发生错误: {str(e)}")
        raise

def _clear_generation_services_cache() -> None:
    """
    清理数据生成服务中的规则缓存
    """
    try:
        # 清理各个数据生成服务的 _rules_cache
        # 这些服务使用实例级别的缓存，我们通过调用它们的清理方法来清理
        
        generation_services = [
            'src.service.staffing_service',
            'src.service.staffing_update_service', 
            'src.service.cargo_search_service',
            'src.service.cargo_update_service',
            'src.service.contract_search_service',
            'src.service.search_po_service'
        ]
        
        for service_module in generation_services:
            try:
                # 动态导入模块并调用清理缓存方法
                import importlib
                module = importlib.import_module(service_module)
                
                # 调用模块的清理缓存函数（如果存在）
                if hasattr(module, 'clear_rules_cache'):
                    module.clear_rules_cache()
                    logger.info(f"已清理 {service_module} 的规则缓存")
                else:
                    logger.debug(f"{service_module} 没有 clear_rules_cache 方法")
                    
            except ImportError as e:
                logger.warning(f"无法导入 {service_module}: {str(e)}")
            except Exception as e:
                logger.warning(f"清理 {service_module} 缓存时发生错误: {str(e)}")
        
        logger.info("数据生成服务缓存清理完成")
        
    except Exception as e:
        logger.error(f"清理数据生成服务缓存时发生错误: {str(e)}")

def get_cache_status(business_object: Optional[str] = None) -> dict:
    """
    获取缓存状态信息
    
    Args:
        business_object: 业务对象名称，如果为None则获取所有缓存状态
        
    Returns:
        包含缓存状态信息的字典
    """
    try:
        from .base_elements import get_base_elements_service
        from .business_rules import get_business_rules_service
        from .answer_elements import get_answer_elements_service
        
        base_service = get_base_elements_service()
        rules_service = get_business_rules_service()
        answer_service = get_answer_elements_service()
        
        if business_object:
            # 获取特定业务对象的缓存状态
            status = {
                "business_object": business_object,
                "base_elements_cached": business_object in base_service.base_elements_cache,
                "business_rules_cached": f"{business_object}Rules" in rules_service.business_rules_cache,
                "answer_elements_cached": business_object in answer_service.answer_elements_cache
            }
        else:
            # 获取所有缓存状态
            status = {
                "base_elements_cache_count": len(base_service.base_elements_cache),
                "business_rules_cache_count": len(rules_service.business_rules_cache),
                "answer_elements_cache_count": len(answer_service.answer_elements_cache),
                "cached_base_elements": list(base_service.base_elements_cache.keys()),
                "cached_business_rules": list(rules_service.business_rules_cache.keys()),
                "cached_answer_elements": list(answer_service.answer_elements_cache.keys())
            }
        
        return status
        
    except Exception as e:
        logger.error(f"获取缓存状态时发生错误: {str(e)}")
        return {"error": str(e)} 