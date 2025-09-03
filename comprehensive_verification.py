#!/usr/bin/env python3
"""
全面验证脚本 - 测试新训练模型的实际效果
模型: 4table_training_20250903_105534 (最终验证损失: 0.934226)
"""

import requests
import json
import time
from typing import Dict, List, Tuple

class ComprehensiveVerifier:
    def __init__(self, base_url: str = "http://ai.devtest.belimked.com"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        # 使用新训练的模型
        self.model_name = "4table_training_20250903_105534"
    
    def query_model(self, prompt: str, max_tokens: int = 100) -> Tuple[str, float]:
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
    
    def run_comprehensive_tests(self):
        """运行全面验证测试"""
        print("🧪 新训练模型全面验证")
        print("=" * 80)
        print(f"模型: {self.model_name}")
        print(f"最终验证损失: 0.934226")
        print(f"训练时长: 46分钟 (620步)")
        print("=" * 80)
        
        # 测试用例分类
        test_categories = [
            {
                "name": "🔍 基础关系识别",
                "tests": [
                    {
                        "question": "mstb_project_materials通过什么字段与mstb_project关联？",
                        "expected": "pro_id",
                        "max_tokens": 30
                    },
                    {
                        "question": "mstb_pms_purchase_order_material的主键是什么？",
                        "expected": "mpom_id",
                        "max_tokens": 20
                    },
                    {
                        "question": "mstb_project和mstb_project_materials是什么关系？",
                        "expected": "一对多关系",
                        "max_tokens": 25
                    }
                ]
            },
            {
                "name": "🔗 复杂关系分析",
                "tests": [
                    {
                        "question": "mstb_pms_purchase_order_material和mstb_pms_purchase_order_main怎么关联？",
                        "expected": "通过mpom_o_id与o_id关联",
                        "max_tokens": 40
                    },
                    {
                        "question": "如何查询某个项目的所有采购订单材料？需要关联哪些表？",
                        "expected": "需要关联mstb_project、mstb_pms_purchase_order_main、mstb_pms_purchase_order_material三个表",
                        "max_tokens": 60
                    }
                ]
            },
            {
                "name": "💻 SQL生成能力",
                "tests": [
                    {
                        "question": "生成SQL：查询项目ID为1的所有材料名称",
                        "expected": "SELECT psam_name FROM mstb_project_materials WHERE pro_id = 1",
                        "max_tokens": 50
                    },
                    {
                        "question": "写SQL查询某个项目的采购订单数量",
                        "expected": "SELECT COUNT(*) FROM mstb_pms_purchase_order_main WHERE o_proId = ?",
                        "max_tokens": 50
                    }
                ]
            },
            {
                "name": "🎯 简洁性测试",
                "tests": [
                    {
                        "question": "外键是什么？",
                        "expected": "外键是引用其他表主键的字段",
                        "max_tokens": 20
                    },
                    {
                        "question": "主键的作用？",
                        "expected": "唯一标识表中每一行记录",
                        "max_tokens": 20
                    }
                ]
            },
            {
                "name": "🧠 业务理解测试",
                "tests": [
                    {
                        "question": "一个项目可以有多个采购订单吗？",
                        "expected": "可以，一对多关系",
                        "max_tokens": 25
                    },
                    {
                        "question": "采购订单材料表的作用是什么？",
                        "expected": "记录每个采购订单包含的具体材料信息",
                        "max_tokens": 30
                    }
                ]
            }
        ]
        
        total_tests = 0
        total_score = 0
        category_results = []
        
        for category in test_categories:
            print(f"\n{category['name']}")
            print("-" * 60)
            
            category_score = 0
            category_tests = len(category['tests'])
            
            for i, test in enumerate(category['tests'], 1):
                print(f"\n📝 测试 {i}: {test['question']}")
                print(f"🎯 期望: {test['expected']}")
                
                # 查询模型
                response, response_time = self.query_model(
                    test['question'], 
                    test['max_tokens']
                )
                
                print(f"🤖 回答: {response}")
                print(f"⏱️  时间: {response_time:.2f}秒")
                
                # 简单评分 (关键词匹配)
                score = self.evaluate_response(response, test['expected'])
                category_score += score
                total_score += score
                
                status = "✅" if score >= 0.6 else "⚠️" if score >= 0.3 else "❌"
                print(f"📊 评分: {score:.1%} {status}")
                
                total_tests += 1
            
            category_avg = category_score / category_tests
            category_results.append({
                "name": category['name'],
                "score": category_avg,
                "tests": category_tests
            })
            
            print(f"\n📈 {category['name']} 平均分: {category_avg:.1%}")
        
        # 总结报告
        self.generate_final_report(total_score, total_tests, category_results)
    
    def evaluate_response(self, response: str, expected: str) -> float:
        """简单的响应评估"""
        response_lower = response.lower()
        expected_lower = expected.lower()
        
        # 关键词匹配
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        
        if not expected_words:
            return 0.0
        
        # 计算重叠度
        overlap = len(expected_words.intersection(response_words))
        keyword_score = overlap / len(expected_words)
        
        # 长度惩罚 (鼓励简洁)
        length_ratio = len(response) / len(expected) if expected else 1
        length_penalty = 1.0 if length_ratio <= 2 else 0.8 if length_ratio <= 3 else 0.6
        
        # 综合评分
        final_score = keyword_score * length_penalty
        return min(final_score, 1.0)
    
    def generate_final_report(self, total_score: float, total_tests: int, category_results: List[Dict]):
        """生成最终报告"""
        print("\n" + "=" * 80)
        print("📋 全面验证报告")
        print("=" * 80)
        
        overall_score = total_score / total_tests
        
        print(f"🎯 模型: {self.model_name}")
        print(f"📊 总体评分: {overall_score:.1%}")
        print(f"🧪 测试数量: {total_tests}")
        print(f"⏱️  训练损失: 0.934226")
        
        print(f"\n📈 分类详情:")
        for result in category_results:
            status = "🌟" if result['score'] >= 0.8 else "👍" if result['score'] >= 0.6 else "⚠️" if result['score'] >= 0.4 else "❌"
            print(f"  {status} {result['name']}: {result['score']:.1%} ({result['tests']}项测试)")
        
        # 与之前对比
        print(f"\n🔄 与之前对比:")
        print(f"  上次验证: 30.2% (学习率4e-06)")
        print(f"  这次验证: {overall_score:.1%} (学习率1e-06)")
        
        if overall_score > 0.302:
            improvement = (overall_score - 0.302) / 0.302 * 100
            print(f"  📈 改善: +{improvement:.1f}%")
        else:
            decline = (0.302 - overall_score) / 0.302 * 100
            print(f"  📉 下降: -{decline:.1f}%")
        
        # 评级和建议
        if overall_score >= 0.8:
            grade = "优秀 🌟"
            recommendation = "模型表现优秀，可以部署使用！"
        elif overall_score >= 0.6:
            grade = "良好 👍"
            recommendation = "模型表现良好，建议进一步优化"
        elif overall_score >= 0.4:
            grade = "一般 ⚠️"
            recommendation = "模型需要改进，考虑调整训练参数"
        else:
            grade = "需要改进 ❌"
            recommendation = "模型效果不理想，需要重新训练"
        
        print(f"\n🏆 综合评级: {grade}")
        print(f"💡 建议: {recommendation}")
        
        # 训练配置总结
        print(f"\n🔧 成功的训练配置:")
        print(f"  学习率: 1e-06 (稳定收敛)")
        print(f"  训练轮数: 20轮 (充分训练)")
        print(f"  LoRA配置: r=16, alpha=16")
        print(f"  Early Stopping: 耐心值2, 阈值0.0005")

def main():
    print("🧠 新训练模型全面验证")
    print("训练完成时间: 2025-09-03 11:42:16")
    print("最终验证损失: 0.934226")
    print("=" * 80)
    
    verifier = ComprehensiveVerifier()
    
    # 检查模型可用性
    print("🔍 检查模型可用性...")
    try:
        response = requests.get(f"{verifier.base_url}/v1/models", timeout=10)
        if response.status_code == 200:
            models = response.json()["data"]
            available_models = [model["id"] for model in models]
            if verifier.model_name in available_models:
                print("✅ 新训练模型可用")
            else:
                print("❌ 新训练模型不可用")
                print(f"可用模型: {available_models}")
                return
        else:
            print("❌ 无法连接到vLLM服务")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    # 运行全面测试
    verifier.run_comprehensive_tests()
    
    print(f"\n🎉 验证完成！")

if __name__ == "__main__":
    main()
