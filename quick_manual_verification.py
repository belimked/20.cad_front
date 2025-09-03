#!/usr/bin/env python3
"""
快速手动验证脚本 - 展示所有测试结果供人工评估
"""

import requests
import json
import time

class QuickVerifier:
    def __init__(self, base_url: str = "http://ai.devtest.belimked.com"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.model_name = "4table_training_20250903_100554"
    
    def query_model(self, prompt: str, max_tokens: int = 150) -> tuple:
        """查询模型 - 限制输出长度"""
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
    
    def evaluate_response(self, response: str, expected: str, evaluation_points: list) -> dict:
        """简单的自动评估"""
        score = 0
        total_points = len(evaluation_points)
        
        # 简单的关键词匹配评估
        response_lower = response.lower()
        expected_lower = expected.lower()
        
        # 检查是否包含期望答案中的关键词
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        
        # 计算词汇重叠度
        overlap = len(expected_words.intersection(response_words))
        word_score = overlap / len(expected_words) if expected_words else 0
        
        # 长度评估 (简洁性)
        length_score = 1.0 if len(response) <= len(expected) * 2 else 0.5
        
        # 综合评分
        final_score = (word_score * 0.7 + length_score * 0.3)
        
        return {
            "score": final_score,
            "word_overlap": overlap,
            "total_expected_words": len(expected_words),
            "length_ratio": len(response) / len(expected) if expected else 0
        }
    
    def run_all_tests(self):
        """运行所有测试并显示结果"""
        print("🧪 快速手动验证测试")
        print("=" * 80)
        
        test_cases = [
            {
                "id": 1,
                "name": "基础关系查询",
                "prompt": """表 mstb_project_materials 通过 pro_id 字段与 mstb_project 关联。

问题: mstb_project_materials通过什么字段与mstb_project关联？""",
                "expected": "pro_id字段",
                "evaluation_points": ["识别关联字段", "简洁回答"]
            },
            {
                "id": 2,
                "name": "关系类型判断",
                "prompt": """表结构:
- mstb_project (pro_id 主键)
- mstb_project_materials (mpm_id 主键, pro_id 外键)

问题: 这两个表是什么关系？""",
                "expected": "一对多关系",
                "evaluation_points": ["正确识别关系类型", "简洁表达"]
            },
            {
                "id": 3,
                "name": "主键识别",
                "prompt": """表 mstb_pms_purchase_order_material:
- mpom_id (int, 主键)
- mpom_o_id (外键)

问题: 这个表的主键是什么？""",
                "expected": "mpom_id",
                "evaluation_points": ["正确识别主键", "避免冗余信息"]
            },
            {
                "id": 4,
                "name": "简单SQL生成",
                "prompt": """表结构:
- mstb_project (pro_id, pro_name)
- mstb_project_materials (mpm_id, pro_id, psam_name)

问题: 查询项目ID为1的所有材料名称的SQL？""",
                "expected": "SELECT psam_name FROM mstb_project_materials WHERE pro_id = 1",
                "evaluation_points": ["SQL语法正确", "查询逻辑正确"]
            },
            {
                "id": 5,
                "name": "外键关系",
                "prompt": """表 mstb_pms_purchase_order_material 的 mpom_o_id 字段引用 mstb_pms_purchase_order_main 的 o_id。

问题: mpom_o_id是什么类型的字段？""",
                "expected": "外键字段",
                "evaluation_points": ["识别外键概念", "简洁回答"]
            }
        ]
        
        results = []
        total_score = 0
        
        for case in test_cases:
            print(f"\n📝 测试 {case['id']}: {case['name']}")
            print("-" * 50)
            print(f"❓ 问题: {case['prompt'].split('问题:')[-1].strip()}")
            print(f"🎯 期望: {case['expected']}")
            
            # 查询模型
            response, response_time = self.query_model(case['prompt'])
            
            print(f"🤖 回答: {response}")
            print(f"⏱️  时间: {response_time:.2f}秒")
            
            # 评估
            evaluation = self.evaluate_response(response, case['expected'], case['evaluation_points'])
            
            print(f"📊 评分: {evaluation['score']:.1%}")
            print(f"🔍 词汇匹配: {evaluation['word_overlap']}/{evaluation['total_expected_words']}")
            print(f"📏 长度比: {evaluation['length_ratio']:.1f}x")
            
            # 人工评估提示
            if evaluation['score'] >= 0.8:
                status = "✅ 优秀"
            elif evaluation['score'] >= 0.6:
                status = "👍 良好"
            elif evaluation['score'] >= 0.4:
                status = "⚠️ 一般"
            else:
                status = "❌ 需改进"
            
            print(f"🏆 状态: {status}")
            
            results.append({
                "case": case,
                "response": response,
                "response_time": response_time,
                "evaluation": evaluation,
                "status": status
            })
            
            total_score += evaluation['score']
        
        # 总结
        print("\n" + "=" * 80)
        print("📋 验证总结")
        print("=" * 80)
        
        avg_score = total_score / len(test_cases)
        avg_time = sum(r['response_time'] for r in results) / len(results)
        
        print(f"🎯 总体评分: {avg_score:.1%}")
        print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
        print(f"🧪 测试数量: {len(test_cases)}")
        
        print(f"\n📈 详细结果:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['case']['name']}: {result['evaluation']['score']:.1%} {result['status']}")
        
        # 分析和建议
        print(f"\n💡 分析:")
        if avg_score >= 0.8:
            print("  ✅ 模型表现优秀，可以投入使用")
        elif avg_score >= 0.6:
            print("  👍 模型表现良好，建议微调优化")
        elif avg_score >= 0.4:
            print("  ⚠️ 模型需要改进，建议调整训练参数")
        else:
            print("  ❌ 模型表现不佳，需要重新训练")
        
        # 具体建议
        long_responses = [r for r in results if r['evaluation']['length_ratio'] > 2]
        if long_responses:
            print(f"  📝 发现 {len(long_responses)} 个回答过长，建议降低 max_tokens")
        
        low_overlap = [r for r in results if r['evaluation']['word_overlap'] < 2]
        if low_overlap:
            print(f"  🎯 发现 {len(low_overlap)} 个回答偏离期望，建议增加相关训练样本")

def main():
    print("🧠 ERD模型快速验证")
    print("模型: 4table_training_20250903_100554")
    print("目标: 评估模型在实际ERD问题上的表现")
    
    verifier = QuickVerifier()
    verifier.run_all_tests()
    
    print(f"\n🎉 验证完成！")

if __name__ == "__main__":
    main()
