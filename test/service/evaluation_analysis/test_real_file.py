"""
分析真实评估文件的脚本
"""

import os
import sys
import json

# 添加项目根路径到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.service.evaluation_analysis.evaluation_analyzer import EvaluationAnalyzer


def analyze_real_evaluation_file(file_path: str):
    """分析真实的评估文件"""
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"开始分析真实评估文件: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path) / (1024*1024):.1f} MB")
    
    try:
        # 初始化分析器
        analyzer = EvaluationAnalyzer()
        print("✅ 评估分析器初始化成功")
        
        # 分析文件
        print("🔍 开始分析文件...")
        result = analyzer.analyze_file(file_path)
        print("✅ 文件分析完成")
        
        # 打印详细分析结果
        print(f"\n{'='*60}")
        print(f"📊 评估文件分析报告")
        print(f"{'='*60}")
        
        print(f"\n📁 文件信息:")
        print(f"  路径: {result.file_path}")
        print(f"  分析时间: {result.analysis_timestamp}")
        print(f"  处理耗时: {result.processing_time:.2f} 秒")
        print(f"  文件大小: {result.metadata.file_size_mb:.1f} MB")
        print(f"  源文件数量: {len(result.metadata.source_files)}")
        print(f"  记录总数: {result.metadata.merged_record_count}")
        
        print(f"\n📈 质量指标:")
        metrics = result.quality_metrics
        print(f"  总问题数: {metrics.total_questions:,}")
        print(f"  成功响应数: {metrics.successful_responses:,}")
        print(f"  失败响应数: {metrics.failed_responses:,}")
        print(f"  成功率: {metrics.success_rate:.1%}")
        print(f"  平均分数: {metrics.score_distribution.mean:.1f}")
        print(f"  分数中位数: {metrics.score_distribution.median:.1f}")
        print(f"  分数标准差: {metrics.score_distribution.std_dev:.1f}")
        print(f"  完美分数数量: {metrics.perfect_score_count:,}")
        print(f"  完美分数率: {metrics.perfect_score_rate:.1%}")
        print(f"  JSON有效数量: {metrics.json_valid_count:,}")
        print(f"  JSON有效率: {metrics.json_valid_rate:.1%}")
        print(f"  平均响应长度: {metrics.average_response_length:.0f} 字符")
        
        print(f"\n⏱️ 性能指标:")
        perf = metrics.performance_metrics
        print(f"  总处理时间: {perf.total_processing_time:.1f} 秒")
        print(f"  平均处理时间: {perf.average_time_per_question:.2f} 秒/问题")
        print(f"  最快处理时间: {perf.min_processing_time:.2f} 秒")
        print(f"  最慢处理时间: {perf.max_processing_time:.2f} 秒")
        print(f"  处理时间中位数: {perf.time_percentiles.get('p50', 0):.2f} 秒")
        print(f"  90%分位数: {perf.time_percentiles.get('p90', 0):.2f} 秒")
        
        print(f"\n📊 分数分布:")
        for range_name, count in metrics.score_distribution.score_ranges.items():
            percentage = (count / metrics.successful_responses) * 100 if metrics.successful_responses > 0 else 0
            print(f"  {range_name}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n❌ 失败分析:")
        failure = result.failure_analysis
        print(f"  失败模式数量: {len(failure.patterns)}")
        print(f"  失败率: {failure.failure_rate:.1%}")
        print(f"  最常见失败原因: {failure.most_common_failure}")
        
        if failure.patterns:
            print(f"\n  主要失败模式:")
            for i, pattern in enumerate(failure.patterns[:5]):  # 显示前5个
                print(f"    {i+1}. {pattern.pattern_name}")
                print(f"       数量: {pattern.count:,} ({pattern.percentage:.1f}%)")
                print(f"       严重程度: {pattern.severity.value}")
                print(f"       类型: {pattern.pattern_type.value}")
        
        print(f"\n🏢 按业务对象统计:")
        for obj_name, obj_metrics in metrics.quality_by_business_object.items():
            print(f"  {obj_name}:")
            print(f"    记录数: {obj_metrics['total_records']:,}")
            print(f"    成功率: {obj_metrics['success_rate']:.1%}")
            print(f"    平均分数: {obj_metrics['average_score']:.1f}")
            print(f"    平均处理时间: {obj_metrics['average_processing_time']:.2f}秒")
        
        print(f"\n💡 改进建议:")
        if result.recommendations:
            for i, rec in enumerate(result.recommendations[:8]):  # 显示前8个建议
                print(f"  {i+1}. [{rec.priority.upper()}] {rec.title}")
                print(f"     类别: {rec.category}")
                print(f"     描述: {rec.description}")
                print(f"     预期影响: {rec.expected_impact}")
                print(f"     实施难度: {rec.implementation_effort}")
                print()
        
        print(f"\n🔍 关键洞察:")
        for i, insight in enumerate(result.key_insights):
            print(f"  {i+1}. {insight}")
        
        # 保存分析结果到JSON文件
        output_file = f"analysis_result_{result.analysis_timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 分析结果已保存到: {output_file}")
        print(f"\n✅ 分析完成！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 使用用户提供的评估文件路径
    evaluation_file = "/Users/saul/Desktop/unified_batch_summary_20250619_113039.json"
    
    success = analyze_real_evaluation_file(evaluation_file)
    sys.exit(0 if success else 1) 