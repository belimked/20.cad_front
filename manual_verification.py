#!/usr/bin/env python3
"""
手动验证脚本 - 提供具体示例进行人工评估
"""

import requests
import json
import time

class ManualVerifier:
    def __init__(self, base_url: str = "http://ai.devtest.belimked.com"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.model_name = "4table_training_20250903_100554"
    
    def query_model(self, prompt: str, max_tokens: int = 200) -> tuple:
        """查询模型"""
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "top_p": 0.8
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"], response_time
            else:
                return f"HTTP错误: {response.status_code}", response_time
        except Exception as e:
            response_time = time.time() - start_time
            return f"请求失败: {str(e)}", response_time
    
    def run_manual_tests(self):
        """运行手动验证测试"""
        print("🧪 手动验证测试")
        print("=" * 60)
        print("我们将测试几个具体的ERD问题，请人工评估模型回答的质量")
        print()
        
        # 测试用例
        test_cases = [
            {
                "id": 1,
                "name": "基础关系查询",
                "prompt": """数据库结构:
表 mstb_project:
  - pro_id (int, 主键) - 项目序号
  - pro_name (varchar(128)) - 项目名称

表 mstb_project_materials:
  - mpm_id (int, 主键) - 材料序号
  - pro_id (外键 -> mstb_project.pro_id) - 项目序号
  - psam_name (varchar(512)) - 材料名称

问题: mstb_project_materials通过什么字段与mstb_project关联？""",
                "expected": "mstb_project_materials通过pro_id字段与mstb_project的pro_id字段关联，关系类型为多对一。",
                "evaluation_points": [
                    "是否正确识别了关联字段 pro_id",
                    "是否说明了关系类型（多对一）",
                    "回答是否简洁明了"
                ]
            },
            {
                "id": 2,
                "name": "复杂关系分析",
                "prompt": """数据库结构:
表 mstb_pms_purchase_order_main:
  - o_id (int, 主键) - 采购订单序号
  - o_proId (外键 -> mstb_project.pro_id) - 项目ID

表 mstb_pms_purchase_order_material:
  - mpom_id (int, 主键) - 采购订单材料序号
  - mpom_o_id (外键 -> mstb_pms_purchase_order_main.o_id) - 采购订单ID
  - mpom_proId (外键 -> mstb_project.pro_id) - 工程项目ID

问题: 如何查询某个项目的所有采购订单及其材料信息？""",
                "expected": "需要关联三个表：mstb_project、mstb_pms_purchase_order_main、mstb_pms_purchase_order_material。通过project.pro_id = order_main.o_proId 和 order_main.o_id = order_material.mpom_o_id 进行关联。",
                "evaluation_points": [
                    "是否识别需要关联的三个表",
                    "是否正确说明关联条件",
                    "是否提供了合理的SQL思路"
                ]
            },
            {
                "id": 3,
                "name": "SQL生成测试",
                "prompt": """数据库结构:
表 mstb_project:
  - pro_id (int, 主键) - 项目序号
  - pro_name (varchar(128)) - 项目名称

表 mstb_project_materials:
  - mpm_id (int, 主键) - 材料序号
  - pro_id (外键 -> mstb_project.pro_id) - 项目序号
  - psam_name (varchar(512)) - 材料名称

问题: 生成SQL查询某个项目的所有材料名称。""",
                "expected": "SELECT m.psam_name FROM mstb_project p JOIN mstb_project_materials m ON p.pro_id = m.pro_id WHERE p.pro_id = ?",
                "evaluation_points": [
                    "SQL语法是否正确",
                    "是否使用了正确的JOIN条件",
                    "是否包含了WHERE条件"
                ]
            },
            {
                "id": 4,
                "name": "关系类型判断",
                "prompt": """数据库结构:
表 mstb_project:
  - pro_id (int, 主键) - 项目序号

表 mstb_pms_purchase_order_main:
  - o_id (int, 主键) - 采购订单序号
  - o_proId (外键 -> mstb_project.pro_id) - 项目ID

问题: mstb_project和mstb_pms_purchase_order_main是什么关系？""",
                "expected": "一对多关系。一个项目可以有多个采购订单，但每个采购订单只属于一个项目。",
                "evaluation_points": [
                    "是否正确识别为一对多关系",
                    "是否解释了关系的业务含义",
                    "回答是否清晰易懂"
                ]
            },
            {
                "id": 5,
                "name": "简单字段查询",
                "prompt": """数据库结构:
表 mstb_pms_purchase_order_material:
  - mpom_id (int, 主键) - 采购订单材料序号
  - mpom_o_id (外键 -> mstb_pms_purchase_order_main.o_id) - 采购订单ID

问题: mstb_pms_purchase_order_material的主键是什么？""",
                "expected": "mpom_id",
                "evaluation_points": [
                    "是否正确识别主键字段",
                    "回答是否简洁",
                    "是否避免了不必要的解释"
                ]
            }
        ]
        
        for case in test_cases:
            print(f"📝 测试 {case['id']}: {case['name']}")
            print("-" * 40)
            print(f"❓ 问题:")
            print(case['prompt'])
            print()
            print(f"🎯 期望答案:")
            print(case['expected'])
            print()
            
            # 查询模型
            response, response_time = self.query_model(case['prompt'])
            
            print(f"🤖 模型回答:")
            print(response)
            print()
            print(f"⏱️  响应时间: {response_time:.2f}秒")
            print()
            print(f"📋 评估要点:")
            for i, point in enumerate(case['evaluation_points'], 1):
                print(f"  {i}. {point}")
            print()
            print("🔍 请人工评估:")
            print("  ✅ 正确  ⚠️ 部分正确  ❌ 错误")
            print("  📝 评估理由: ________________")
            print()
            print("=" * 60)
            print()
            
            # 暂停让用户评估
            input("按回车键继续下一个测试...")
            print()

def main():
    print("🧠 ERD模型手动验证")
    print("模型: 4table_training_20250903_100554")
    print("=" * 60)
    print()
    
    verifier = ManualVerifier()
    verifier.run_manual_tests()
    
    print("🎉 手动验证完成！")
    print()
    print("📊 总结建议:")
    print("1. 记录每个测试的评估结果")
    print("2. 分析模型的优势和不足")
    print("3. 确定是否需要进一步优化")

if __name__ == "__main__":
    main()
