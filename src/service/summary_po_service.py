#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
订单统计服务模块

这个模块提供了订单预结算审核单统计相关的数据生成服务。
基于 rules/po/summaryPo.txt 中定义的规则，生成各种订单统计问题和对应的答案。

主要功能：
1. 根据规则生成订单统计问题的多个变种
2. 生成符合格式要求的答案
3. 支持多种统计维度：项目、供应商、材料类型、状态、时间等
4. 支持多种统计指标：金额、数量、重量、面积、平均价格等
"""

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_draw_id, normalize_staff_id, normalize_project_name, \
    normalize_vendor_name, normalize_zts_id, normalize_cklx_id, normalize_gcsx_id, normalize_material_code_name, \
    normalize_number_name, normalize_meterialsfrompo_id
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.rule_logic import get_rule_components
from src.service.common.variation_generation_service import VariationGenerationService
from src.service.common.connector_manager import split_connected_string
import os
import json

# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')


class SummaryPoService(BaseGenerationService):
    """
    订单统计服务类，用于根据规则生成订单统计的问题和答案
    继承自BaseGenerationService基础类
    """

    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'summaryPo'

    def __init__(self):
        """
        初始化订单统计服务
        """
        super().__init__()

    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict,
                            num_variations: int = 2) -> List[Dict]:
        """
        根据规则和基础元素生成问题的多个变种

        Args:
            rule: 规则定义
            base_elements: 基础元素定义
            answer_elements: 回答元素定义
            num_variations: 要生成的变种数量，默认为2

        Returns:
            包含问题和答案的变种列表
        """
        variations = []

        for i in range(num_variations):
            try:
                # 获取规则组件
                rule_components = get_rule_components(rule, base_elements, answer_elements)

                # 生成问题
                question = self._generate_question(rule_components)

                # 生成答案
                answer = self._generate_answer(rule_components)

                # 创建变种数据
                variation = {
                    'business_object': self.BUSINESS_OBJECT,
                    'rule_id': rule.get('id'),
                    'rule_name': rule.get('name', ''),
                    'question': question,
                    'answer': answer,
                    'rule_components': rule_components,
                    'variation_index': i + 1
                }

                variations.append(variation)

            except Exception as e:
                print(f"生成变种 {i+1} 时出错: {e}")
                continue

        return variations

    def _generate_question(self, rule_components: Dict) -> str:
        """
        根据规则组件生成问题

        Args:
            rule_components: 规则组件字典

        Returns:
            生成的问题字符串
        """
        try:
            # 获取问题组件
            question_parts = []

            # 处理统计操作 (01)
            if '01' in rule_components:
                question_parts.append(rule_components['01'])

            # 处理项目信息 (10)
            if '10' in rule_components:
                question_parts.append(rule_components['10'])

            # 处理供应商信息 (11)
            if '11' in rule_components:
                question_parts.append(rule_components['11'])

            # 处理材料类型 (12-15)
            for material_code in ['12', '13', '14', '15']:
                if material_code in rule_components:
                    question_parts.append(rule_components[material_code])

            # 处理状态信息 (16)
            if '16' in rule_components:
                question_parts.append(rule_components['16'])

            # 处理时间信息 (17-19)
            time_parts = []
            for time_code in ['17', '18', '19']:
                if time_code in rule_components:
                    time_parts.append(rule_components[time_code])
            if time_parts:
                question_parts.extend(time_parts)

            # 处理连接词 (03)
            if '03' in rule_components:
                question_parts.append(rule_components['03'])

            # 处理对象类型 (02)
            if '02' in rule_components:
                question_parts.append(rule_components['02'])

            # 处理统计指标 (05-09)
            metrics = []
            for metric_code in ['05', '06', '07', '08', '09']:
                if metric_code in rule_components:
                    metrics.append(rule_components[metric_code])

            if metrics:
                if len(metrics) > 1:
                    # 多个指标用"和"连接
                    if '04' in rule_components:
                        metrics_text = rule_components['04'].join(metrics[:-1]) + rule_components['04'] + metrics[-1]
                    else:
                        metrics_text = '和'.join(metrics)
                else:
                    metrics_text = metrics[0]
                question_parts.append(metrics_text)

            # 组合问题文本，使用逗号分隔
            question = '，'.join([part for part in question_parts if part])

            return question

        except Exception as e:
            print(f"生成问题时出错: {e}")
            return "统计订单信息"

    def _generate_answer(self, rule_components: Dict, answer_elements: Dict) -> str:
        """
        根据规则组件生成答案

        Args:
            rule_components: 解析后的规则组件
            answer_elements: 回答元素定义

        Returns:
            生成的答案字符串
        """
        try:
            # 订单统计的答案格式
            answer_template = {
                "操作": "统计",
                "对象": "订单预结算审核单",
                "项目": rule_components.get('10', ''),
                "供应商": rule_components.get('11', ''),
                "对象状态": self._normalize_status(rule_components.get('16', '')),
                "对象审核单类型": "",
                "对象提交时间": "",
                "对象审核时间": "",
                "对象发货时间": "",
                "对象下单时间": self._format_time_condition(rule_components),
                "材料状态": "",
                "材料类型": self._get_material_type(rule_components),
                "材料工艺图": "",
                "材料工程属性": "",
                "材料所属订单": "",
                "材料编号": "",
                "对象金额": "",
                "对象附加费用": "",
                "材料AI金额条件": "",
                "对象审核单类型": "",
                "材料是否异型": "",
                "材料是否超长超宽": "",
                "对象单号": "",
                "送货单号": "",
                "运费": "",
                "其他费用": "",
                "其他费用说明": ""
            }

            # 转换为JSON字符串
            return json.dumps(answer_template, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"生成答案时出错: {e}")
            return '{"操作": "统计", "对象": "订单预结算审核单"}'

    def _normalize_status(self, status: str) -> str:
        """
        标准化状态信息
        """
        if not status:
            return "审核通过,待成本审核"
        
        if any(keyword in status for keyword in ["已完成审核", "完成审核", "已结算"]):
            return "审核通过"
        elif any(keyword in status for keyword in ["待审核", "待结算", "还没审核"]):
            return "待成本审核"
        else:
            return "审核通过,待成本审核"

    def _get_material_type(self, rule_components: Dict) -> str:
        """
        获取材料类型
        """
        for code in ['12', '13', '14', '15']:
            if code in rule_components:
                return rule_components[code]
        return ""

    def _format_time_condition(self, rule_components: Dict) -> str:
        """
        格式化时间条件
        """
        time_parts = []
        for code in ['17', '18', '19']:
            if code in rule_components:
                time_parts.append(rule_components[code])
        return ''.join(time_parts) if time_parts else ""

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 summaryPo 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )


# 获取服务实例的便捷函数
def get_summary_po_service():
    return SummaryPoService.get_instance()


# 便捷方法，使用变种生成服务创建
def generate_summary_po_data(business_object: str = SummaryPoService.BUSINESS_OBJECT,
                              total_samples: int = 10,
                              variations_per_rule: int = 2,
                              ruleids: str = None) -> List[Dict]:
    """
    生成订单统计数据
    
    Args:
        business_object: 业务对象名称，默认为summaryPo
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    summary_po_service = get_summary_po_service()

    # 调用生成方法
    return summary_po_service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=ruleids
    )


if __name__ == "__main__":
    # 简单测试
    print("测试订单统计服务...")
    try:
        service = get_summary_po_service()
        print(f"服务创建成功: {service.__class__.__name__}")
        print(f"业务对象: {service.BUSINESS_OBJECT}")
        
        # 生成少量测试数据
        test_data = generate_summary_po_data(total_samples=2, variations_per_rule=1)
        print(f"生成测试数据成功，共 {len(test_data)} 条")
        
        if test_data:
            print("示例数据:")
            print(f"问题: {test_data[0].get('question', 'N/A')}")
            print(f"答案: {test_data[0].get('answer', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"测试失败: {e}")
