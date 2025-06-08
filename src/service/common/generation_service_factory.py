#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService

class GenerationServiceFactory:
    """
    生成服务工厂类
    用于创建和管理不同类型的数据生成服务
    """
    
    @staticmethod
    def create_variation_service() -> 'BaseGenerationService':
        """
        创建变种生成服务
        
        Returns:
            变种生成服务实例
        """
        # 延迟导入，避免循环导入问题
        from src.service.common.variation_generation_service import VariationGenerationService
        
        # 使用单例模式获取服务实例
        return VariationGenerationService.get_instance()
    
    @staticmethod
    def create_staffing_service() -> 'BaseGenerationService':
        """
        创建人员安排服务
        
        Returns:
            人员安排服务实例
        """
        # 延迟导入，避免循环导入问题
        from src.service.staffing_service import StaffingService
        
        # 使用单例模式获取服务实例
        return StaffingService.get_instance()
    
    @staticmethod
    def create_material_service() -> 'BaseGenerationService':
        """
        创建材料服务
        
        Returns:
            材料服务实例
        """
        # 延迟导入，避免循环导入问题
        from src.service.search_po_service import MaterialService
        
        # 使用单例模式获取服务实例
        return MaterialService.get_instance()
    
    @staticmethod
    def register_services() -> None:
        """
        注册所有服务实例
        在应用启动时调用此方法可确保所有服务被正确初始化
        """
        # 导入所有服务类
        from src.service.common.variation_generation_service import VariationGenerationService
        from src.service.staffing_service import StaffingService
        from src.service.search_po_service import MaterialService
        
        # 注册服务
        BaseGenerationService.register_service(VariationGenerationService)
        BaseGenerationService.register_service(StaffingService)
        BaseGenerationService.register_service(MaterialService)
    
    @staticmethod
    def get_service_for_business_object(business_object: str) -> 'BaseGenerationService':
        """
        根据业务对象类型获取对应的服务
        
        Args:
            business_object: 业务对象类型，如 searchStaff
            
        Returns:
            对应的服务实例
        """
        # 导入服务类，避免循环导入
        from src.service.staffing_service import StaffingService
        from src.service.search_po_service import MaterialService
        
        # 根据业务对象类型选择对应的服务
        if business_object.startswith('searchStaff'):
            return GenerationServiceFactory.create_staffing_service()
        elif business_object.startswith('searchMaterial'):
            return GenerationServiceFactory.create_material_service()
        else:
            # 默认使用变种生成服务
            return GenerationServiceFactory.create_variation_service() 