#!/usr/bin/env python3
"""
vLLM + S-LoRA ERD模型验证脚本
验证刚训练的 4table_training_20250903_100554 模型
"""

import requests
import json
import time
from typing import Dict, List, Tuple

class ERDModelVerifier:
    def __init__(self, base_url: str = "http://ai.devtest.belimked.com"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.model_name = "4table_training_20250903_100554"
    
    def test_model_availability(self) -> bool:
        """测试模型是否可用"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json()["data"]
                available_models = [model["id"] for model in models]
                print(f"🔍 可用模型: {available_models}")
                return self.model_name in available_models
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def query_model(self, prompt: str, max_tokens: int = 512) -> Tuple[str, float]:
        """查询模型并返回响应和响应时间"""
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
    
    def test_erd_understanding(self) -> Dict:
        """测试ERD理解能力"""
        print("\n🧠 ERD理解能力测试")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "基础关系识别",
                "prompt": """根据以下ERD信息，回答问题：

表结构：
- users (id, name, email, created_at)
- orders (id, user_id, total_amount, order_date)
- order_items (id, order_id, product_id, quantity, price)
- products (id, name, price, category_id)

问题：users表和orders表之间是什么关系？通过哪个字段关联？""",
                "expected_keywords": ["一对多", "user_id", "外键"]
            },
            {
                "name": "复杂关系推理",
                "prompt": """根据ERD结构分析：

表结构：
- customers (customer_id, name, email)
- orders (order_id, customer_id, order_date)
- order_details (detail_id, order_id, product_id, quantity)
- products (product_id, product_name, price)

问题：如何查询某个客户购买的所有产品信息？需要关联哪些表？""",
                "expected_keywords": ["JOIN", "customers", "orders", "order_details", "products"]
            },
            {
                "name": "SQL生成能力",
                "prompt": """基于以下ERD结构，生成SQL查询：

表结构：
- employees (emp_id, name, department_id, salary)
- departments (dept_id, dept_name, manager_id)

需求：查询每个部门的平均工资，包含部门名称。

请生成SQL语句：""",
                "expected_keywords": ["SELECT", "AVG", "JOIN", "GROUP BY"]
            }
        ]
        
        results = []
        total_response_time = 0
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {case['name']}")
            print(f"❓ 问题: {case['prompt'][:100]}...")
            
            response, response_time = self.query_model(case['prompt'])
            total_response_time += response_time
            
            print(f"🤖 回答: {response}")
            print(f"⏱️  响应时间: {response_time:.2f}秒")
            
            # 检查关键词
            keywords_found = sum(1 for keyword in case['expected_keywords'] 
                               if keyword.lower() in response.lower())
            accuracy = keywords_found / len(case['expected_keywords'])
            
            print(f"🎯 关键词匹配: {keywords_found}/{len(case['expected_keywords'])} ({accuracy:.1%})")
            
            results.append({
                "name": case['name'],
                "response": response,
                "response_time": response_time,
                "accuracy": accuracy,
                "keywords_found": keywords_found,
                "total_keywords": len(case['expected_keywords'])
            })
            print("-" * 50)
        
        # 计算总体指标
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        avg_response_time = total_response_time / len(results)
        
        return {
            "results": results,
            "avg_accuracy": avg_accuracy,
            "avg_response_time": avg_response_time,
            "total_tests": len(results)
        }
    
    def test_loss_correlation(self) -> None:
        """测试损失值与实际效果的关联"""
        print("\n📊 损失值与效果关联分析")
        print("=" * 50)
        
        simple_prompt = """简单问题：users表的主键是什么？

表结构：users (id, name, email)"""
        
        response, response_time = self.query_model(simple_prompt, max_tokens=50)
        
        print(f"🔍 简单测试问题: {simple_prompt}")
        print(f"🤖 模型回答: {response}")
        print(f"⏱️  响应时间: {response_time:.2f}秒")
        
        # 分析回答质量
        if "id" in response.lower() and ("主键" in response or "primary" in response.lower()):
            print("✅ 基础理解正确")
        else:
            print("❌ 基础理解有问题")
    
    def generate_report(self, test_results: Dict) -> None:
        """生成验证报告"""
        print("\n📋 验证报告总结")
        print("=" * 50)
        
        print(f"🎯 模型: {self.model_name}")
        print(f"📊 总体准确率: {test_results['avg_accuracy']:.1%}")
        print(f"⏱️  平均响应时间: {test_results['avg_response_time']:.2f}秒")
        print(f"🧪 测试用例数: {test_results['total_tests']}")
        
        print(f"\n📈 详细结果:")
        for result in test_results['results']:
            status = "✅" if result['accuracy'] >= 0.6 else "❌"
            print(f"  {status} {result['name']}: {result['accuracy']:.1%} "
                  f"({result['response_time']:.2f}s)")
        
        # 评估等级
        if test_results['avg_accuracy'] >= 0.8:
            grade = "优秀 🌟"
            recommendation = "模型表现优秀，可以部署使用"
        elif test_results['avg_accuracy'] >= 0.6:
            grade = "良好 👍"
            recommendation = "模型基本可用，建议进一步优化"
        elif test_results['avg_accuracy'] >= 0.4:
            grade = "一般 ⚠️"
            recommendation = "模型需要改进，建议重新训练"
        else:
            grade = "较差 ❌"
            recommendation = "模型效果不佳，需要检查训练数据和配置"
        
        print(f"\n🏆 综合评级: {grade}")
        print(f"💡 建议: {recommendation}")
        
        # 与损失值的关联分析
        print(f"\n🔗 损失值关联分析:")
        print(f"  训练损失: 0.9346 (偏高)")
        print(f"  验证损失: 0.8409 (偏高)")
        print(f"  实际准确率: {test_results['avg_accuracy']:.1%}")
        
        if test_results['avg_accuracy'] > 0.6 and test_results['avg_accuracy'] < 0.8:
            print("  📝 分析: 损失值偏高但实际效果尚可，可能存在过拟合")
        elif test_results['avg_accuracy'] < 0.5:
            print("  📝 分析: 损失值和实际效果都不理想，需要优化训练")
        else:
            print("  📝 分析: 效果超出损失值预期，模型可用")

def main():
    print("🧠 ERD模型验证 - vLLM + S-LoRA")
    print("模型: 4table_training_20250903_100554")
    print("=" * 50)
    
    verifier = ERDModelVerifier()
    
    # 检查模型可用性
    print("🔍 检查模型可用性...")
    if not verifier.test_model_availability():
        print("❌ 模型不可用，请检查vLLM服务")
        return
    
    print("✅ 模型可用，开始验证...")
    
    # 执行ERD理解测试
    test_results = verifier.test_erd_understanding()
    
    # 执行简单关联测试
    verifier.test_loss_correlation()
    
    # 生成报告
    verifier.generate_report(test_results)
    
    print(f"\n🎉 验证完成！")

if __name__ == "__main__":
    main()
