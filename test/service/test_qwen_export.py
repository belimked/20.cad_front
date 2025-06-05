#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.service.qwen_service import generate_qwen_data
import json
import os

def test_export_settlement():
    """
    测试导出结算单场景，确保对象状态正确设置为"审核通过"
    """
    print("开始测试导出结算单场景...")
    
    # 创建一个临时测试数据文件，强制包含一条导出结算单的数据
    test_data = [
        {
            "rule_id": 1,
            "rule_name": "导出结算单",
            "question": {
                "operationType": "导出结算单",
                "supplierInfo": "江苏钢铁有限公司",
                "projectInfo": "上海浦东机场三期项目",
                "cargoNumberWithQuantity": "结算单A12345（5件）"
            },
            "answer": {
                "操作": "导出结算单",
                "对象": "货单信息审核单",
                "项目": "上海浦东机场三期项目",
                "供应商": "江苏钢铁有限公司",
                "对象状态": "\"对比\"/\"审核通过\"时，默认为\"待成本审核\"；\"导出结算单\"时，默认为\"审核通过\"",
                "对象提交时间": "无",
                "对象审核时间": "无",
                "对象发货时间": "无",
                "对象下单时间": "无",
                "材料状态": "无",
                "材料类型": "无",
                "材料工艺图": "无",
                "材料工程属性": "无",
                "材料所属订单": "无",
                "材料编号": "无",
                "对象金额": "无",
                "对象附加费用": "无",
                "材料AI金额条件": "无",
                "对象审核单类型": "无",
                "材料是否异型": "无",
                "材料是否超长超宽": "无",
                "对象单号": "结算单A12345（5件）",
                "送货单号": "无",
                "运费": "无",
                "其他费用": "无",
                "网版费": "无",
                "其他费用说明": "无",
                "人员姓名": "无",
                "人员工号": "无",
                "角色信息": "无",
                "人员项目": "无"
            }
        }
    ]
    
    # 创建临时目录
    os.makedirs("outputs/data/temp", exist_ok=True)
    
    # 保存临时测试数据
    temp_original_file = "outputs/data/temp/export_settlement_test.json"
    with open(temp_original_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"创建临时测试数据: {temp_original_file}")
    
    # 从临时文件生成千问格式数据
    temp_qwen_file = "outputs/data/temp/export_settlement_test.jsonl"
    with open(temp_qwen_file, 'w', encoding='utf-8') as f:
        for item in test_data:
            # 获取问题和答案
            question_data = item.get('question', {})
            answer_data = item.get('answer', {})
            
            # 使用process_answer_fields处理答案字段
            from src.service.qwen_service import process_answer_fields
            processed_answer = process_answer_fields(answer_data)
            
            # 格式化问题
            from src.service.qwen_service import format_question_updateCargo
            formatted_question = format_question_updateCargo(question_data)
            
            # 创建千问格式数据
            qwen_data = {
                "messages": [
                    {
                        "role": "user", 
                        "content": f"### 指令：\n你是一个企业信息检索助手，请根据查询内容，返回包含以下字段的标准JSON响应，缺失字段填\"无\"：\n[操作, 对象, 项目, 供应商, 对象状态, 对象提交时间, 对象审核时间, 对象发货时间, 对象下单时间, 材料状态, 材料类型, 材料工艺图, 材料工程属性, 材料所属订单, 材料编号, 对象金额, 对象附加费用, 材料AI金额条件, 对象审核单类型, 材料是否异型, 材料是否超长超宽, 对象单号, 送货单号, 运费, 其他费用, 其他费用说明, 网版费, 人员姓名, 人员工号, 角色信息, 人员项目]\n\n### 查询问题\n{formatted_question}"
                    },
                    {
                        "role": "assistant", 
                        "content": json.dumps(processed_answer, ensure_ascii=False)
                    }
                ]
            }
            
            # 将数据写入jsonl文件
            f.write(json.dumps(qwen_data, ensure_ascii=False) + '\n')
    
    print(f"生成千问格式数据: {temp_qwen_file}")
    
    # 读取生成的千问格式数据
    try:
        # 读取千问格式数据
        qwen_data = []
        with open(temp_qwen_file, 'r', encoding='utf-8') as f:
            for line in f:
                qwen_data.append(json.loads(line))
        
        # 查看处理后的千问格式数据
        print("\n千问格式数据样例:")
        for item in qwen_data:
            assistant_content = json.loads(item['messages'][1]['content'])
            print(f"问题: {item['messages'][0]['content']}")
            print(f"回答: {assistant_content}")
            print(f"操作: {assistant_content['操作']}")
            print(f"项目: {assistant_content['项目']}")
            print(f"供应商: {assistant_content['供应商']}")
            print(f"对象状态: {assistant_content['对象状态']}")
                
        print("\n测试完成!")
    except Exception as e:
        print(f"处理数据时出错: {e}")

if __name__ == "__main__":
    test_export_settlement() 