#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_draw_id, normalize_staff_id, normalize_project_name, \
    normalize_vendor_name
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.rule_logic import get_rule_components
from src.service.common.variation_generation_service import VariationGenerationService
import os
import json

# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')


class ContractSearchService(BaseGenerationService):
    """
    人员安排服务类，用于根据规则生成人员安排的问题和答案
    继承自BaseGenerationService基础类
    """

    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'searchContract'

    def __init__(self):
        """
        初始化人员安排服务
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

        # 提取规则的codeList
        code_list = self._extract_code_list(rule)

        # 提前格式化数据，减少重复代码
        base_elements_dict = base_elements
        if isinstance(base_elements, str):
            _, base_elements_dict, _ = get_rule_components(base_elements)

        answer_elements_dict = answer_elements
        if isinstance(answer_elements, str):
            _, _, answer_elements_dict = get_rule_components(answer_elements)

        for _ in range(num_variations):
            # 生成问题数据
            question_data = self.generate_question(rule, base_elements)

            # 生成答案数据
            answer_data = self.generate_answer(question_data, answer_elements, base_elements)

            # 设置object字段为固定值
            answer_data['object'] = "合同信息审核单"
            answer_data['operation'] = "查询"

            # 特殊处理：确保personName字段映射
            if 'personName' in question_data:
                answer_data['personName'] = question_data['personName']

            # 特殊处理：确保projectName字段映射到personProject
            if 'projectName' in question_data and '05' in code_list:
                # 使用工具函数标准化项目名称
                project_value = normalize_project_name(question_data['projectName'])
                answer_data['personProject'] = project_value

            # 特殊处理：如果有staffId字段，确保映射到personJobNumber
            if 'staffId' in question_data:
                # 使用工具函数标准化工号
                staff_id = normalize_staff_id(question_data['staffId'])
                answer_data['personJobNumber'] = staff_id

            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', ''),
                'code_list': code_list  # 添加codeList，便于后续处理
            })

        return variations

    def _extract_code_list(self, rule):
        """从rule中提取codeList并处理成列表格式"""
        if not rule:
            return []

        code_list_value = rule.get('codeList', [])
        # 如果codeList是字符串，拆分成列表
        if isinstance(code_list_value, str):
            # 如果包含分号，则按分号拆分
            if ';' in code_list_value:
                code_list = []
                for code_item in code_list_value.split(';'):
                    code_list.append(code_item)
                return code_list
            # 否则直接作为单个元素的列表返回
            return [code_list_value]

        # 如果已经是列表，检查每个元素是否需要进一步拆分
        result = []
        for item in code_list_value:
            if ';' in item:
                result.extend(item.split(';'))
            else:
                result.append(item)

        return result

    def _get_rule_by_id(self, rule_id):
        """根据规则ID获取规则信息"""
        if not hasattr(self, '_rules_cache'):
            # 初始化规则缓存
            self._rules_cache = {}
            try:
                # 从searchStaffRules.json加载规则
                rules_file_path = os.path.join(ENTITY_DIR, 'relationship', 'searchContract.json')
                with open(rules_file_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)

                # 缓存规则，以rule_id为键
                for rule in rules_data:
                    rule_id_value = rule.get('rule_id')
                    if rule_id_value:
                        self._rules_cache[rule_id_value] = rule
            except Exception as e:
                print(f"加载规则时出错: {e}")
                return None

        # 从缓存中获取规则
        return self._rules_cache.get(rule_id)

    def post_process_data(self, data, answer_elements):
        """后处理生成的数据，确保规则和字段关联正确"""
        # 获取回答元素定义（如果answer_elements是字符串）
        if isinstance(answer_elements, str):
            _, _, answer_elements_dict = get_rule_components(answer_elements)
            answer_elements = answer_elements_dict

        for item in data:
            # 先从item中获取code_list
            code_list = item.get('code_list', [])
            rule_id = item.get('rule_id')

            # 如果code_list为空，尝试从rule中提取
            if not code_list:
                rule = self._get_rule_by_id(rule_id)
                if rule:
                    code_list = self._extract_code_list(rule)
                    # 将code_list保存回item中，以便后续处理
                    item['code_list'] = code_list

            # print(f"处理数据, rule_id: {rule_id}, code_list: {code_list}")

            # 设置基础操作和对象
            item['answer']['object'] = "合同信息审核单"
            item['answer']['operation'] = "查询"

            if 'supplierInfo' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['supplier'] = normalize_vendor_name(item['question']['supplierInfo'])
            if 'timeRange' in item['question'] and (
                    'submitDate' in item['question'] or 'submitStatus' in item['question']):
                # 使用工具函数标准化工号
                item['answer']['objectSubmitTime'] = item['question']['timeRange']
            if 'auditStatus' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['objectStatus'] = item['question']['auditStatus']
            if 'projectInfo' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['project'] = normalize_project_name(item['question']['projectInfo'])

            if 'priceChangeType' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['reviewType'] = item['question']['priceChangeType']

            if 'processDrawing' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['materialProcessDrawing'] =normalize_draw_id(item['question']['processDrawing'])

            if 'engineeringProperties' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['materialEngineeringProperties'] = item['question']['engineeringProperties']

            if 'materialType' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['materialType'] = item['question']['materialType']
            if 'priceChangeType' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['reviewType'] = item['question']['priceChangeType']
            if 'priceRule' in item['question']:
                # 使用工具函数标准化工号
                item['answer']['reviewType'] = item['question']['priceRule']

            # 处理关联字段
            # 移除临时的code_list字段，保持数据干净
            if 'code_list' in item:
                del item['code_list']

        return data

    def generate_search_contract_data(self, business_object: str = BUSINESS_OBJECT,
                                      total_samples: int = 200,
                                      variations_per_rule: int = 2,
                                      variation_service=None,
                                      ruleids: str = None) -> List[Dict]:
        """
        生成合同查询数据
        
        Args:
            business_object: 业务对象名称，默认为searchContract
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
            
        Returns:
            生成的数据列表
        """
        # 调用基类的通用方法
        return self.generate_business_data(business_object, total_samples, variations_per_rule, variation_service, ruleids)

    # 获取服务实例的便捷函数


def get_search_contract_service():
    return ContractSearchService.get_instance()


# 便捷方法，使用变种生成服务创建
def generate_search_contract_data(business_object: str = ContractSearchService.BUSINESS_OBJECT,
                                  total_samples: int = 10,
                                  variations_per_rule: int = 2,
                                  ruleids: str = None) -> List[Dict]:
    """
    生成合同查询数据
    
    Args:
        business_object: 业务对象名称，默认为searchContract
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    variation_service = GenerationServiceFactory.create_variation_service()
    search_contract_service = get_search_contract_service()

    # 调用生成方法，传递变种服务实例
    return search_contract_service.generate_search_contract_data(
        business_object,
        total_samples,
        variations_per_rule,
        variation_service,  # 传递变种服务实例
        ruleids             # 传递规则ID过滤字符串
    )


# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的人员安排数据
        staffing_data = generate_search_contract_data(total_samples=10, variations_per_rule=2)
        print(f"\n生成的数据数量: {len(staffing_data)}")

        # 打印第一条数据
        if staffing_data:
            print("\n示例数据:")
            print(f"问题: {staffing_data[0]['question']}")
            print(f"答案: {staffing_data[0]['answer']}")
    except Exception as e:
        import traceback

        print(f"\n发生错误: {e}")
        traceback.print_exc()
