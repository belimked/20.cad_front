#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SummaryPoService 使用示例

这个示例展示了如何使用新创建的 SummaryPoService 来生成订单统计相关的训练数据。
基于 rules/po/summaryPo.txt 中定义的规则，生成各种订单预结算审核单统计问题。
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.service.summary_po_service import generate_summary_po_data, get_summary_po_service


def main():
    """
    主函数，演示 SummaryPoService 的各种用法
    """
    print("=" * 60)
    print("SummaryPoService 使用示例")
    print("订单预结算审核单统计数据生成")
    print("=" * 60)
    
    # 示例1：生成少量数据用于测试
    print("\n1. 生成少量测试数据（5个样本）")
    print("-" * 40)
    try:
        test_data = generate_summary_po_data(
            total_samples=5,
            variations_per_rule=1
        )
        print(f"✅ 成功生成 {len(test_data)} 个样本")
        
        # 显示第一个样本
        if test_data:
            sample = test_data[0]
            print(f"📋 样本示例:")
            print(f"   业务对象: {sample.get('business_object')}")
            print(f"   规则ID: {sample.get('rule_id')}")
            print(f"   规则名称: {sample.get('rule_name')}")
            print(f"   问题: {sample.get('question')}")
            print(f"   答案预览: {sample.get('answer', '')[:150]}...")
            
    except Exception as e:
        print(f"❌ 生成测试数据失败: {e}")
    
    # 示例2：生成特定规则的数据
    print("\n2. 生成特定规则的数据（规则ID=1）")
    print("-" * 40)
    try:
        specific_data = generate_summary_po_data(
            total_samples=3,
            variations_per_rule=1,
            ruleids="1"
        )
        print(f"✅ 成功生成 {len(specific_data)} 个样本")
        
        # 显示所有样本的问题
        for i, sample in enumerate(specific_data[:3], 1):
            print(f"   样本{i}: {sample.get('question')}")
            
    except Exception as e:
        print(f"❌ 生成特定规则数据失败: {e}")
    
    # 示例3：使用服务实例直接调用
    print("\n3. 使用服务实例直接调用")
    print("-" * 40)
    try:
        service = get_summary_po_service()
        print(f"✅ 获取服务实例成功: {service.__class__.__name__}")
        print(f"   业务对象: {service.BUSINESS_OBJECT}")
        
        # 生成数据
        instance_data = service.generate_data(
            total_samples=2,
            variations_per_rule=1
        )
        print(f"✅ 通过服务实例生成 {len(instance_data)} 个样本")
        
    except Exception as e:
        print(f"❌ 使用服务实例失败: {e}")
    
    # 示例4：保存生成的数据到文件
    print("\n4. 保存数据到文件")
    print("-" * 40)
    try:
        # 生成一些数据
        export_data = generate_summary_po_data(
            total_samples=10,
            variations_per_rule=1
        )
        
        # 保存到JSON文件
        output_file = "summary_po_samples.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功保存 {len(export_data)} 个样本到 {output_file}")
        
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
