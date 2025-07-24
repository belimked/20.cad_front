#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试千问服务功能
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime

# --- 修正后的服务导入 ---
from src.service.cargo_update_service import CargoUpdateService
from src.service.cargo_search_service import CargoSearchService
from src.service.staffing_update_service import StaffingUpdateService
from src.service.staffing_service import StaffingService
from src.service.contract_search_service import ContractSearchService
from src.service.search_po_service import SearchPOService
from src.service.submitvpopo_service import SubmitVpopoService
from src.service.submitvposent_service import SubmitVposentService
from src.service.vpocontractclone_service import VpoContractCloneService
from src.service.searchvpopo_service import SearchvpopoService
from src.service.searchvposent_service import SearchVposentService
from src.service.vpo.searchvpopofrom_service import SearchvpopofromService
from src.service.vpo.searchvposentfrom_service import SearchvposentfromService
from src.service.searchvpocontract_service import SearchVPOContractService

# --- 旧的 generate_* 函数导入（保留以兼容旧的测试函数） ---
from src.service.cargo_update_service import generate_cargo_update_data
from src.service.cargo_search_service import generate_search_cargo_data
from src.service.staffing_update_service import generate_update_staffing_data
from src.service.staffing_service import generate_staffing_data
from src.service.contract_search_service import generate_search_contract_data
from src.service.search_po_service import generate_search_order_data
from src.service.submitvpopo_service import generate_submitvpopo_data
from src.service.submitvposent_service import generate_submitvposent_data
from src.service.vpocontractclone_service import generate_vpocontractclone_data
from src.service.searchvpopo_service import generate_searchvpopo_data
from src.service.searchvpocontract_service import generate_searchvpocontract_data

from src.service.common.generation_service_factory import get_generation_service
from src.service.common.tools import load_index_file
from src.service.rule_logic import get_rule_components, get_sorted_rules, format_question_by_codebase, \
    format_answer_to_cn


def format_question(question_data):
    """
    将问题数据格式化为自然语言
    """
    if 'personName' in question_data and 'personProjectQuery' in question_data:
        return f"{question_data['personName']}{question_data['personProjectQuery']}"
    elif 'projectName' in question_data and 'projectPersonQuery' in question_data:
        return f"{question_data['projectName']}{question_data['projectPersonQuery']}"
    elif 'projectStatusQuery' in question_data:
        return question_data['projectStatusQuery']
    else:
        # 如果没有匹配的模式，则返回原始格式
        return str(question_data)


def get_rule_codebase(business_object, data):
    """
    根据数据中的rule_id找到对应的规则codebase
    """
    sorted_rules = get_sorted_rules(business_object)

    # 直接通过rule_id匹配对应的规则
    if 'rule_id' in data:
        for rule in sorted_rules:
            if rule.get('id') == data['rule_id']:
                return rule.get('codebase', '')

    # 如果没有找到匹配的规则，返回空字符串
    return ""


def test_service_dynamically(businessObject, service_class, totalSamples: int = 100, variations_per_rule: int = 5,
                             collect_data=False, keyword=None, ruleids: str = None):
    """
    动态测试单个服务的功能，使用服务工厂。
    """
    print(f"--- 开始动态测试服务: {businessObject} ---")
    collected_dialogs = []
    collected_raw_data = []
    filtered_count = 0
    keyword_stats = {}

    try:
        print(
            f"正在为业务对象 '{businessObject}' 生成 {totalSamples} 个样本，每个规则 {variations_per_rule} 个变种...")

        if ruleids:
            print(f"使用规则ID过滤: {ruleids}")

        # --- Core Change: Use the service factory ---
        service = get_generation_service(businessObject, service_class)
        if not service:
            raise ValueError(f"无法为业务对象 '{businessObject}' 找到或创建服务实例")

        generated_data = service.generate_data(
            total_samples=totalSamples,
            variations_per_rule=variations_per_rule,
            rule_ids=ruleids
        )
        # --- End of Core Change ---

        print(f"\n生成数据成功！总共生成了 {len(generated_data)} 个数据")

        keywords = [k.strip() for k in keyword.split(',') if k.strip()] if keyword else []
        for k in keywords:
            keyword_stats[k] = 0

        if generated_data:
            for i, data in enumerate(generated_data):
                codebase = get_rule_codebase(businessObject, data)
                codevalue = data.get('combo_value', f"{businessObject}_{data.get('rule_id', '')}")
                formatted_question = format_question_by_codebase(data['question'], codevalue, businessObject)
                formatted_answer = format_answer_to_cn(data['answer'], businessObject)

                dialog_json = {"messages": [{"role": "user", "content": formatted_question},
                                            {"role": "assistant", "content": formatted_answer}]}

                should_collect = not keywords or any(k.lower() in formatted_question.lower() for k in keywords)

                if collect_data and should_collect:
                    if keywords:
                        for k in keywords:
                            if k.lower() in formatted_question.lower():
                                keyword_stats[k] += 1
                    collected_dialogs.append(dialog_json)
                    collected_raw_data.append({
                        "business_object": businessObject, "rule_id": data.get('rule_id', ''),
                        "rule_name": data.get('rule_name', ''),
                        "question": data['question'], "answer": data['answer'], "codebase": codebase,
                        "formatted_question": formatted_question, "formatted_answer": formatted_answer,
                        "combo_value": codevalue
                    })
                elif not should_collect:
                    filtered_count += 1

                if i < 100:  # Limit print output
                    print(f"\n样本 {i + 1}: ... (output ommitted for brevity)")

        if keywords:
            print(f"\n关键字过滤: 过滤掉 {filtered_count} 个样本, 保留 {len(collected_dialogs)} 个。")

        print(f"\n--- 动态测试服务 {businessObject} 完成，功能正常！ ---")

        if collect_data:
            return collected_dialogs, collected_raw_data
        return True

    except Exception as e:
        import traceback
        print(f"\n测试 '{businessObject}' 过程中发生错误: {e}")
        traceback.print_exc()
        if collect_data:
            return [], []
        return False


def test_generate_staffing_data(businessObject, totalSamples: int = 100, variations_per_rule: int = 5,
                                collect_data=False, keyword=None, ruleids: str = None):
    """
    测试生成人员安排数据功能
    
    Args:
        businessObject: 业务对象名称
        totalSamples: 总样本数
        variations_per_rule: 每个规则的变种数
        collect_data: 是否收集数据
        keyword: 关键字过滤，只收集包含该关键字的对话，多个关键字用逗号分隔
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        如果collect_data为True，返回收集的对话数据和原始数据的元组；否则返回True/False表示成功/失败
    """
    print("开始测试StaffingService服务...")
    collected_dialogs = []
    collected_raw_data = []  # 添加原始数据收集列表
    filtered_count = 0
    keyword_stats = {}  # 记录每个关键字匹配到的数量

    try:
        # 生成人员安排数据
        business_object = businessObject
        total_samples = totalSamples
        variations_per_rule = variations_per_rule

        print(
            f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")

        if ruleids:
            print(f"使用规则ID过滤: {ruleids}")

        if businessObject == 'searchContract':
            staffing_data = generate_search_contract_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'updateStaff':
            staffing_data = generate_update_staffing_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'updateCargo':
            staffing_data = generate_cargo_update_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'searchStaff':
            staffing_data = generate_staffing_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'searchCargo':
            staffing_data = generate_search_cargo_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'searchPo':
            staffing_data = generate_search_order_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'submitvpopo':
            staffing_data = generate_submitvpopo_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'submitvposent':
            staffing_data = generate_submitvposent_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'vpocontractclone':
            staffing_data = generate_vpocontractclone_data(business_object, total_samples, variations_per_rule, ruleids)
        elif businessObject == 'searchvpopo':
            staffing_data = generate_searchvpopo_data(business_object, total_samples, variations_per_rule, ruleids)
        else:
            raise ValueError(f"不支持的业务对象 '{business_object}'")

        # 打印生成的数据统计
        print(f"\n生成数据成功！总共生成了 {len(staffing_data)} 个数据")

        # 问题前缀说明文本
        # prefix_text = "请根据以下查询返回完整的JSON格式响应，确保包含以下所有字段（即使值为\"无\"）：\n\n操作, 对象, 项目, 供应商, 对象状态, 对象提交时间, 对象审核时间, 对象发货时间, 对象下单时间, 材料状态, 材料类型, 材料工艺图, 材料工程属性, 材料所属订单, 材料编号, 对象金额, 对象附加费用, 材料AI金额条件, 对象审核单类型, 材料是否异型, 材料是否超长超宽, 对象单号, 送货单号, 运费, 其他费用, 其他费用说明, 网版费, 人员姓名, 人员工号, 角色信息, 人员项目\n\n"
        prefix_text = ""

        # 处理关键字列表
        keywords = []
        if keyword and isinstance(keyword, str):
            keywords = [k.strip() for k in keyword.split(',') if k.strip()]
            for k in keywords:
                keyword_stats[k] = 0

        # 打印所有样本数据
        if staffing_data:
            print("\n所有样本数据示例:")
            for i, data in enumerate(staffing_data):
                # 获取该样本对应的规则codebase
                codebase = get_rule_codebase(business_object, data)

                # 使用新方法格式化问题
                formatted_question = format_question_by_codebase(data['question'], codebase, business_object)

                # 使用新方法格式化答案（转换为中文字段名）
                formatted_answer = format_answer_to_cn(data['answer'], business_object)

                # 创建包含问题和答案的JSON对象
                dialog_json = {
                    "messages": [
                        {
                            "role": "user",
                            "content": formatted_question
                        },
                        {
                            "role": "assistant",
                            "content": formatted_answer
                        }
                    ]
                }

                # 如果需要收集数据，并且满足关键字过滤条件，添加到列表中
                should_collect = True
                if keywords:
                    # 任一关键字匹配即可保留
                    matched = False
                    for k in keywords:
                        if k.lower() in formatted_question.lower():
                            matched = True
                            keyword_stats[k] += 1

                    if not matched:
                        should_collect = False
                        filtered_count += 1

                if collect_data and should_collect:
                    collected_dialogs.append(dialog_json)
                    # 保存原始数据，与千问数据一一对应
                    collected_raw_data.append({
                        "business_object": business_object,
                        "rule_id": data.get('rule_id', ''),
                        "rule_name": data.get('rule_name', ''),
                        "question": data['question'],
                        "answer": data['answer'],
                        "codebase": codebase,
                        "formatted_question": formatted_question,  # 添加格式化后的千问问题
                        "formatted_answer": formatted_answer,  # 添加格式化后的千问答案
                        "combo_value": data.get('combo_value', f"{business_object}_{data.get('rule_id', '')}")
                        # 优先使用data中的combo_value，若不存在则构造
                    })

                # 只打印前10个样本，避免输出过多
                if i < 100:
                    print(f"\n样本 {i + 1}:")
                    print(f"原始问题: {data['question']}")
                    print(f"问题: {formatted_question}")
                    print(f"原始答案: {data['answer']}")
                    print(f"格式化答案: {formatted_answer}")
                    print(f"codebase: \"{codebase}\"")
                    print(f"对话JSON: {json.dumps(dialog_json, ensure_ascii=False)}")

        # 分析数据结构
        question_keys = set()
        answer_keys = set()

        for data in staffing_data:
            question_keys.update(data['question'].keys())
            answer_keys.update(data['answer'].keys())

        if keywords:
            print(f"\n关键字过滤情况: 使用关键字 '{keyword}' 过滤掉了 {filtered_count} 个不匹配的样本")
            print(f"保留了 {len(collected_dialogs)} 个包含关键字的样本")
            print("每个关键字匹配情况:")
            for k, count in keyword_stats.items():
                print(f"  - '{k}': {count} 个样本")

        print("\nStaffingService服务测试完成，功能正常！")

        if collect_data:
            return collected_dialogs, collected_raw_data  # 返回一个包含对话数据和原始数据的元组
        return True

    except Exception as e:
        import traceback
        print(f"\n测试过程中发生错误: {e}")
        traceback.print_exc()
        if collect_data:
            return collected_dialogs, collected_raw_data  # 出错时依然返回已收集的数据
        return False


def save_to_jsonl(data, output_dir, filename=None):
    """
    将数据保存为JSONL格式
    
    Args:
        data: 要保存的数据列表
        output_dir: 输出目录路径
        filename: 文件名，如果为None，则自动生成
    """
    # 使用绝对路径确保输出到正确的目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    absolute_output_dir = os.path.join(project_root, output_dir)

    # 确保输出目录存在
    os.makedirs(absolute_output_dir, exist_ok=True)

    # 如果没有指定文件名，则使用当前时间生成
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qwen_data_{timestamp}.jsonl"

    # 完整的文件路径
    file_path = os.path.join(absolute_output_dir, filename)

    # 将数据写入JSONL文件
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"数据已保存到: {file_path}")
    return file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试数据生成服务。")
    parser.add_argument('service_name', nargs='?', default='searchvpocontract',
                        help="要测试的单个服务的名称 (例如 'searchvposent')。如果未提供，则测试所有服务。")
    parser.add_argument('--samples', type=int, default=2, help="生成的总样本数。")
    parser.add_argument('--vars', type=int, default=10, help="每个规则的变种数。")
    args = parser.parse_args()

    # --- 服务类映射 ---
    # 创建一个从 business_object 名称到服务类的映射
    SERVICE_CLASS_MAP = {
        'updateCargo': CargoUpdateService,
        'searchCargo': CargoSearchService,  # 修正: SearchCargoService -> CargoSearchService
        'updateStaff': StaffingUpdateService,  # 修正
        'searchStaff': StaffingService,
        'searchContract': ContractSearchService,  # 修正
        'searchPo': SearchPOService,  # 修正
        'submitvpopo': SubmitVpopoService,
        'submitvposent': SubmitVposentService,
        'vpocontractclone': VpoContractCloneService,  # 修正
        'searchvpopo': SearchvpopoService,
        'searchvposent': SearchVposentService,
        'searchvpopofrom': SearchvpopofromService,
        'searchvpocontract': SearchVPOContractService,
        'searchvposentfrom': SearchvposentfromService,
    }

    all_dialogs = []
    all_raw_data = []

    if args.service_name:
        print(f"模式: 单独测试服务 '{args.service_name}'")
        service_class_to_test = SERVICE_CLASS_MAP.get(args.service_name)
        if service_class_to_test:
            dialogs, raw_data = test_service_dynamically(
                args.service_name,
                service_class_to_test,  # 将找到的服务类传入
                totalSamples=args.samples,
                variations_per_rule=args.vars,
                # ruleids='49',
                collect_data=True
            )
            all_dialogs.extend(dialogs)
            all_raw_data.extend(raw_data)
        else:
            print(f"错误: 未在 SERVICE_CLASS_MAP 中找到服务 '{args.service_name}'。请检查服务名称和映射。")
            sys.exit(1)
    else:
        # 旧版兼容模式
        print("模式: 测试所有已注册的服务 (旧版兼容模式)")
        all_service_names = list(SERVICE_CLASS_MAP.keys())

        for service_name in all_service_names:
            print(f"\n>>> 正在使用动态方法收集 {service_name} 数据...")
            service_class_to_test = SERVICE_CLASS_MAP.get(service_name)
            dialogs, raw_data = test_service_dynamically(
                service_name,
                service_class_to_test,
                totalSamples=args.samples,
                variations_per_rule=args.vars,
                ruleids='8',
                collect_data=True
            )
            all_dialogs.extend(dialogs)
            all_raw_data.extend(raw_data)

    # --- 数据处理和保存逻辑 ---
    print(f"\n总共收集了 {len(all_dialogs)} 条对话数据")
    if not all_dialogs:
        print("没有收集到任何数据，程序退出。")
        sys.exit(0)

    assert len(all_dialogs) == len(all_raw_data), "对话数据和原始数据数量不一致"

    print("正在打乱数据顺序...")
    combined = list(zip(all_dialogs, all_raw_data))
    random.shuffle(combined)
    all_dialogs, all_raw_data = zip(*combined) if combined else ([], [])
    all_dialogs = list(all_dialogs)
    all_raw_data = list(all_raw_data)

    # 生成相同的时间戳用于两个文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存对话数据到JSONL文件
    output_dir = "outputs/data"
    qwen_filename = f"qwen_data_{timestamp}.jsonl"
    raw_filename = f"raw_data_{timestamp}.jsonl"

    # 保存千问对话数据
    qwen_file = save_to_jsonl(all_dialogs, output_dir, qwen_filename)

    # 保存原始数据
    raw_file = save_to_jsonl(all_raw_data, output_dir, raw_filename)

    # 输出文件信息
    qwen_file_size_bytes = os.path.getsize(qwen_file)
    qwen_file_size_mb = qwen_file_size_bytes / (1024 * 1024)
    raw_file_size_bytes = os.path.getsize(raw_file)
    raw_file_size_mb = raw_file_size_bytes / (1024 * 1024)

    print(f"\n输出文件信息:")
    print(f"- 千问数据文件:")
    print(f"  - 路径: {qwen_file}")
    print(f"  - 大小: {qwen_file_size_mb:.2f} MB ({qwen_file_size_bytes:,} 字节)")
    print(f"  - 记录数: {len(all_dialogs)} 条")

    print(f"- 原始数据文件:")
    print(f"  - 路径: {raw_file}")
    print(f"  - 大小: {raw_file_size_mb:.2f} MB ({raw_file_size_bytes:,} 字节)")
    print(f"  - 记录数: {len(all_raw_data)} 条")
