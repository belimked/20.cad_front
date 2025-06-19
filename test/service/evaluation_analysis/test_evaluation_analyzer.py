"""
评估分析器测试脚本
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# 添加项目根路径到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.service.evaluation_analysis.evaluation_analyzer import EvaluationAnalyzer


def create_test_evaluation_file():
    """创建测试用的评估文件"""
    test_data = {
        "metadata": {
            "generation_time": "2024-12-19T12:30:39.047869",
            "source_files": ["test_file.json"],
            "merged_record_count": 10,
            "processing_type": "test_evaluation"
        },
        "summary": {
            "evaluation_info": {
                "total_questions": 10,
                "successful_count": 6,
                "failed_count": 4,
                "success_rate": 0.6
            }
        },
        "logs": [
            {
                "id": 1,
                "question": "测试问题1",
                "expected_answer": '{"操作": "查询", "对象": "合同"}',
                "actual_answer": '{"操作": "查询", "对象": "合同"}',
                "raw_answer": '{"操作": "查询", "对象": "合同"}',
                "processing_time": 3.5,
                "timestamp": "2024-12-19T12:30:40.000000",
                "status": "success",
                "score": 100,
                "evaluation": {
                    "status": "success",
                    "score": 100,
                    "json_valid": True
                },
                "prompt_info": {"prompt_file": "test.txt"},
                "original_data": {
                    "business_object": "searchContract",
                    "rule_id": 1,
                    "rule_name": "测试规则1"
                }
            },
            {
                "id": 2,
                "question": "测试问题2",
                "expected_answer": '{"操作": "更新", "对象": "人员"}',
                "actual_answer": '{"操作": "更新", "对象": "人员信息"}',
                "raw_answer": '{"操作": "更新", "对象": "人员信息"}',
                "processing_time": 4.2,
                "timestamp": "2024-12-19T12:30:41.000000",
                "status": "success",
                "score": 80,
                "evaluation": {
                    "status": "success",
                    "score": 80,
                    "json_valid": True
                },
                "prompt_info": {"prompt_file": "test.txt"},
                "original_data": {
                    "business_object": "updateStaff",
                    "rule_id": 2,
                    "rule_name": "测试规则2"
                }
            },
            {
                "id": 3,
                "question": "测试问题3",
                "expected_answer": '{"操作": "删除", "对象": "订单"}',
                "actual_answer": '{"操作": "删除"',  # 不完整的JSON
                "raw_answer": '{"操作": "删除"',
                "processing_time": 5.1,
                "timestamp": "2024-12-19T12:30:42.000000",
                "status": "failed",
                "score": 0,
                "evaluation": {
                    "status": "failed",
                    "failure_reason": "JSON格式无效: JSON解析失败",
                    "json_valid": False
                },
                "prompt_info": {"prompt_file": "test.txt"},
                "original_data": {
                    "business_object": "searchPo",
                    "rule_id": 3,
                    "rule_name": "测试规则3"
                }
            },
            {
                "id": 4,
                "question": "测试问题4",
                "expected_answer": '{"操作": "查询", "项目": "项目A"}',
                "actual_answer": '{"操作": "查询", "项目": "项目B"}',
                "raw_answer": '{"操作": "查询", "项目": "项目B"}',
                "processing_time": 3.8,
                "timestamp": "2024-12-19T12:30:43.000000",
                "status": "failed",
                "score": 0,
                "evaluation": {
                    "status": "failed",
                    "failure_reason": "JSON属性不匹配",
                    "json_valid": True
                },
                "prompt_info": {"prompt_file": "test.txt"},
                "original_data": {
                    "business_object": "searchContract",
                    "rule_id": 4,
                    "rule_name": "测试规则4"
                }
            }
        ]
    }
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
    json.dump(test_data, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()
    
    return temp_file.name


def test_evaluation_analyzer():
    """测试评估分析器"""
    print("开始测试评估分析器...")
    
    try:
        # 创建测试数据文件
        test_file = create_test_evaluation_file()
        print(f"创建测试文件: {test_file}")
        
        # 初始化分析器
        analyzer = EvaluationAnalyzer()
        print("评估分析器初始化成功")
        
        # 分析文件
        result = analyzer.analyze_file(test_file)
        print("文件分析完成")
        
        # 打印分析结果
        print(f"\n=== 分析结果概览 ===")
        print(f"文件路径: {result.file_path}")
        print(f"分析时间: {result.analysis_timestamp}")
        print(f"处理耗时: {result.processing_time:.2f} 秒")
        
        print(f"\n=== 质量指标 ===")
        metrics = result.quality_metrics
        print(f"总问题数: {metrics.total_questions}")
        print(f"成功响应数: {metrics.successful_responses}")
        print(f"失败响应数: {metrics.failed_responses}")
        print(f"成功率: {metrics.success_rate:.1%}")
        print(f"平均分数: {metrics.score_distribution.mean:.1f}")
        print(f"完美分数率: {metrics.perfect_score_rate:.1%}")
        print(f"JSON有效率: {metrics.json_valid_rate:.1%}")
        
        print(f"\n=== 失败分析 ===")
        failure = result.failure_analysis
        print(f"失败模式数: {len(failure.patterns)}")
        print(f"最常见失败原因: {failure.most_common_failure}")
        
        for i, pattern in enumerate(failure.patterns):
            print(f"模式 {i+1}: {pattern.pattern_name} (数量: {pattern.count}, 严重程度: {pattern.severity.value})")
        
        print(f"\n=== 改进建议 ===")
        print(f"建议数量: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations):
            print(f"建议 {i+1}: [{rec.priority}] {rec.title}")
            print(f"  类别: {rec.category}")
            print(f"  描述: {rec.description}")
            print(f"  预期影响: {rec.expected_impact}")
        
        print(f"\n=== 关键洞察 ===")
        for i, insight in enumerate(result.key_insights):
            print(f"{i+1}. {insight}")
        
        # 清理测试文件
        os.unlink(test_file)
        print(f"\n清理测试文件: {test_file}")
        
        print("\n✅ 评估分析器测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_evaluation_analyzer()
    sys.exit(0 if success else 1) 