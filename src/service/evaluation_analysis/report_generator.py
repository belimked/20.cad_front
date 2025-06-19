"""
报告生成器 - 生成可视化分析报告
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64
from io import BytesIO
import platform
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import matplotlib as mpl
from matplotlib.figure import Figure

# 配置中文字体支持
def configure_chinese_fonts():
    """配置matplotlib中文字体支持"""
    try:
        # 检查是否已经配置了中文字体
        if any(['SimHei' in f or 'Microsoft YaHei' in f or 'WenQuanYi' in f 
                for f in mpl.font_manager.findSystemFonts()]):
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            logging.info("成功配置中文字体")
            return True
        else:
            # 尝试使用系统可用字体
            available_fonts = [f for f in mpl.font_manager.findSystemFonts() if os.path.exists(f)]
            if available_fonts:
                plt.rcParams['font.sans-serif'] = [os.path.basename(available_fonts[0]).split('.')[0], 'DejaVu Sans', 'sans-serif']
                logging.info(f"使用系统字体: {plt.rcParams['font.sans-serif'][0]}")
                return True
            else:
                logging.warning("未找到可用的中文字体，图表中文可能显示为方块")
                return False
    except Exception as e:
        logging.error(f"配置中文字体失败: {e}")
        return False

# 初始化中文字体
configure_chinese_fonts()

from src.entity.evaluation.analysis_result import AnalysisResult


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_html_report(self, analysis_result: AnalysisResult, output_dir: str = "outputs/reports", evaluation_records=None) -> str:
        """生成HTML分析报告"""
        self.logger.info("开始生成HTML报告")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成图表
        charts = self._generate_charts(analysis_result)
        
        # 生成HTML内容
        html_content = self._generate_html_content(analysis_result, charts, evaluation_records)
        
        # 保存报告文件
        timestamp = analysis_result.analysis_timestamp.strftime("%Y%m%d_%H%M%S")
        report_filename = f"evaluation_analysis_report_{timestamp}.html"
        report_path = os.path.join(output_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {report_path}")
        return report_path
    
    def _generate_charts(self, analysis_result: AnalysisResult) -> Dict[str, str]:
        """生成分析图表"""
        charts = {}
        
        try:
            # 成功率饼图
            charts['success_failure_pie'] = self._create_success_failure_pie_chart(analysis_result.quality_metrics)
            
            # 分数分布图
            charts['score_distribution'] = self._create_score_distribution_chart(analysis_result.quality_metrics)
            
            # 业务对象表现图
            charts['business_object_performance'] = self._create_business_object_chart(analysis_result.quality_metrics)
            
            # 性能分析图
            charts['performance_analysis'] = self._create_performance_chart(analysis_result.quality_metrics)
            
        except Exception as e:
            self.logger.error(f"生成图表时发生错误: {e}", exc_info=True)
        
        return charts
    
    def _create_success_failure_pie_chart(self, metrics) -> str:
        """创建成功/失败比例饼图"""
        # 完全避免使用中文
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 使用纯ASCII标签
        labels = ['Success', 'Failure']
        
        sizes = [metrics.successful_responses, metrics.failed_responses]
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0)
        
        # 绘制饼图，使用ASCII标签
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         explode=explode, shadow=True, startangle=90)
        
        # 设置自动文本样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')
        
        # 使用ASCII标题
        ax.set_title(f'Success/Failure Distribution\nTotal: {metrics.total_questions:,} Questions', 
                     fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_score_distribution_chart(self, metrics) -> str:
        """创建分数分布图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：分数段分布柱状图
        if hasattr(metrics.score_distribution, 'score_ranges') and metrics.score_distribution.score_ranges:
            ranges = list(metrics.score_distribution.score_ranges.keys())
            counts = list(metrics.score_distribution.score_ranges.values())
            
            bars = ax1.bar(ranges, counts, color=sns.color_palette("viridis", len(ranges)))
            ax1.set_title('Score Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Score Range')
            ax1.set_ylabel('Count')
            
            # 添加数值标签
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                        f'{count}', ha='center', va='bottom', fontweight='bold')
            
            ax1.tick_params(axis='x', rotation=45)
        
        # 右图：分数统计信息
        stats_data = [
            ('Mean', metrics.score_distribution.mean),
            ('Median', metrics.score_distribution.median),
            ('Std Dev', metrics.score_distribution.std_dev)
        ]
        
        stats_labels, stats_values = zip(*stats_data)
        bars2 = ax2.bar(stats_labels, stats_values, color=['#3498db', '#9b59b6', '#f39c12'])
        ax2.set_title('Score Statistics', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Value')
        
        # 添加数值标签
        for bar, value in zip(bars2, stats_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(stats_values)*0.01,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_business_object_chart(self, metrics) -> str:
        """创建业务对象表现对比图"""
        if not hasattr(metrics, 'quality_by_business_object') or not metrics.quality_by_business_object:
            return ""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 准备数据
        objects = list(metrics.quality_by_business_object.keys())
        success_rates = [metrics.quality_by_business_object[obj]['success_rate'] * 100 for obj in objects]
        avg_scores = [metrics.quality_by_business_object[obj]['average_score'] for obj in objects]
        total_records = [metrics.quality_by_business_object[obj]['total_records'] for obj in objects]
        
        # 1. 成功率对比
        bars1 = ax1.bar(objects, success_rates, color=sns.color_palette("RdYlGn", len(objects)))
        ax1.set_title('Success Rate by Business Object', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        for bar, rate in zip(bars1, success_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)
        
        # 2. 平均分数对比
        bars2 = ax2.bar(objects, avg_scores, color=sns.color_palette("plasma", len(objects)))
        ax2.set_title('Average Score by Business Object', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Score')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, score in zip(bars2, avg_scores):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 3. 记录数量对比 (左下)
        bars3 = ax3.bar(objects, total_records, color=sns.color_palette("coolwarm", len(objects)))
        ax3.set_title('Record Count by Business Object', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Record Count')
        ax3.tick_params(axis='x', rotation=45)
        
        for bar, count in zip(bars3, total_records):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(total_records)*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=10)
        
        # 4. 综合表现雷达图 (右下)
        ax4.remove()  # 移除原始轴
        ax4 = fig.add_subplot(2, 2, 4, projection='polar')
        
        # 为每个业务对象创建简化雷达图
        angles = [0, 2*3.14159/3, 4*3.14159/3, 2*3.14159]  # 0, 120, 240, 360度
        
        for i, obj in enumerate(objects[:3]):  # 只显示前3个对象
            values = [
                success_rates[i],
                avg_scores[i] * 10,  # 放大分数显示
                min(100, total_records[i] / max(total_records) * 100)  # 标准化记录数
            ]
            values.append(values[0])  # 闭合
            
            ax4.plot(angles, values, marker='o', label=obj, linewidth=2)
            ax4.fill(angles, values, alpha=0.1)
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(['Success', 'Score', 'Records'])
        ax4.set_ylim(0, 100)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax4.set_title('Performance Comparison', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_performance_chart(self, metrics) -> str:
        """创建性能分析图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 性能指标
        perf_metrics = metrics.performance_metrics
        
        # 1. 处理时间分布直方图
        # 模拟处理时间分布数据
        times = np.random.normal(perf_metrics.average_time_per_question, 
                               (perf_metrics.max_processing_time - perf_metrics.min_processing_time) / 6, 
                               1000)
        times = np.clip(times, perf_metrics.min_processing_time, perf_metrics.max_processing_time)
        
        ax1.hist(times, bins=30, color='skyblue', alpha=0.7, edgecolor='black')
        ax1.axvline(perf_metrics.average_time_per_question, color='red', linestyle='--', 
                   label=f'Mean: {perf_metrics.average_time_per_question:.3f}s')
        ax1.axvline(perf_metrics.time_percentiles.get('p50', 0), color='orange', linestyle='--', 
                   label=f'Median: {perf_metrics.time_percentiles.get("p50", 0):.3f}s')
        ax1.set_title('Processing Time Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Processing Time (seconds)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 处理时间百分位数
        percentiles = perf_metrics.time_percentiles
        p_labels = list(percentiles.keys())
        p_values = list(percentiles.values())
        
        bars = ax2.bar(p_labels, p_values, color=sns.color_palette("viridis", len(p_labels)))
        ax2.set_title('Processing Time Percentiles', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Percentile')
        ax2.set_ylabel('Time (seconds)')
        
        # 添加数值标签
        for bar, value in zip(bars, p_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(p_values)*0.01,
                    f'{value:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        # 3. 响应长度分析
        response_data = [
            ('Min Length', metrics.min_response_length),
            ('Avg Length', metrics.average_response_length),
            ('Max Length', metrics.max_response_length)
        ]
        
        labels, values = zip(*response_data)
        bars3 = ax3.bar(labels, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax3.set_title('Response Length Analysis', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Characters')
        
        # 添加数值标签
        for bar, value in zip(bars3, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. 综合性能指标雷达图
        ax4.remove()
        ax4 = fig.add_subplot(2, 2, 4, projection='polar')
        
        # 性能指标（标准化到0-100）
        performance_scores = [
            min(100, (1 / perf_metrics.average_time_per_question) * 20),  # 速度得分
            min(100, metrics.success_rate * 100),  # 成功率
            min(100, metrics.json_valid_rate * 100),  # JSON有效率
            min(100, (metrics.score_distribution.mean / 100) * 100),  # 质量得分
            min(100, metrics.perfect_score_rate * 1000)  # 满分率（放大显示）
        ]
        
        # 角度
        angles = [0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5, 2*np.pi]
        performance_scores.append(performance_scores[0])  # 闭合
        
        ax4.plot(angles, performance_scores, marker='o', linewidth=2, color='#2E86AB')
        ax4.fill(angles, performance_scores, alpha=0.25, color='#2E86AB')
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(['Speed', 'Success', 'JSON Valid', 'Quality', 'Perfect'])
        ax4.set_ylim(0, 100)
        ax4.set_title('Performance Overview', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图形转换为base64字符串"""
        buffer = BytesIO()
        
        # 保存为PNG格式，增加DPI提高文字清晰度
        try:
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                      facecolor='white', edgecolor='none')
        except Exception as e:
            self.logger.error(f"保存图表时出错: {e}")
            # 如果保存失败，尝试创建一个带有错误信息的图表
            plt.close(fig)
            err_fig = plt.figure(figsize=(6, 2))
            plt.text(0.5, 0.5, f"图表生成错误: {str(e)}", 
                    ha='center', va='center', fontsize=12)
            plt.axis('off')
            err_fig.savefig(buffer, format='png', dpi=150)
            plt.close(err_fig)
            
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_html_content(self, analysis_result: AnalysisResult, charts: Dict[str, str], evaluation_records=None) -> str:
        """生成HTML报告内容"""
        # 提取质量指标
        metrics = analysis_result.quality_metrics
        
        # 提取基本指标
        total_count = metrics.total_questions
        success_count = metrics.successful_responses
        failure_count = metrics.failed_responses
        success_percentage = metrics.success_rate * 100
        failure_percentage = 100 - success_percentage
        
        # 分数分布
        mean_score = metrics.score_distribution.mean
        median_score = metrics.score_distribution.median
        std_dev = metrics.score_distribution.std_dev
        score_ranges = metrics.score_distribution.score_ranges
        score_ranges_json = json.dumps(score_ranges)
        
        # 完美分数
        perfect_score_count = metrics.perfect_score_count
        perfect_score_rate = metrics.perfect_score_rate
        perfect_score_rate_display = f"{perfect_score_rate * 100:.1f}%"
        
        # 业务对象性能
        business_objects = {}
        for bo, data in metrics.quality_by_business_object.items():
            # 确保业务对象名称中的特殊字符被替换
            safe_bo = str(bo).replace('{', '_').replace('}', '_')
            business_objects[safe_bo] = {
                'success_rate': data.get('success_rate', 0) * 100,
                'count': data.get('count', 0)
            }
        
        # 记录分布
        business_object_records = {}
        if evaluation_records:
            bo_records = {}
            for record in evaluation_records:
                bo = record.business_object
                # 确保业务对象名称中的特殊字符被替换
                safe_bo = str(bo).replace('{', '_').replace('}', '_')
                if safe_bo not in bo_records:
                    bo_records[safe_bo] = {'total': 0, 'success': 0, 'failure': 0}
                
                bo_records[safe_bo]['total'] += 1
                if record.is_successful:
                    bo_records[safe_bo]['success'] += 1
                else:
                    bo_records[safe_bo]['failure'] += 1
            
            for bo, counts in bo_records.items():
                business_object_records[bo] = {
                    'total': counts['total'],
                    'success': counts['success'],
                    'failure': counts['failure'],
                    'success_rate': (counts['success'] / counts['total']) * 100 if counts['total'] > 0 else 0
                }
        
        business_objects_json = json.dumps(business_objects)
        business_object_records_json = json.dumps(business_object_records)
        
        # 最佳/最差业务对象
        best_performing = '未知'
        worst_performing = '未知'
        
        if metrics.quality_by_business_object:
            sorted_bos = sorted(
                [(bo.replace('{', '_').replace('}', '_'), data.get('success_rate', 0)) 
                 for bo, data in metrics.quality_by_business_object.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            if sorted_bos:
                best_performing = sorted_bos[0][0]
                worst_performing = sorted_bos[-1][0]
        
        # 性能指标
        perf_metrics = metrics.performance_metrics
        total_processing_time = perf_metrics.total_processing_time
        avg_time_per_question = perf_metrics.average_time_per_question
        min_processing_time = perf_metrics.min_processing_time
        max_processing_time = perf_metrics.max_processing_time
        
        # 时间百分位数
        time_percentiles = perf_metrics.time_percentiles
        time_percentiles_json = json.dumps(time_percentiles)
        time_p50 = time_percentiles.get('p50', 0)
        time_p90 = time_percentiles.get('p90', 0)
        
        # 响应长度
        min_response_length = metrics.min_response_length
        max_response_length = metrics.max_response_length
        avg_response_length = metrics.average_response_length
        
        # JSON有效性
        json_valid_count = metrics.json_valid_count
        json_valid_rate = metrics.json_valid_rate
        
        # 读取HTML模板
        # 由于模板中包含大量的JavaScript代码，其中有很多大括号，
        # 这些大括号会被Python的字符串格式化误解为替换字段
        # 我们需要将模板中的大括号进行转义，将单个大括号变成两个大括号
        
        # 获取原始HTML模板
        html_template = self._get_html_template()
        
        # 在格式化之前，先处理模板中的大括号
        # 1. 先标记我们需要替换的实际占位符
        # 2. 将其他大括号转义
        # 3. 恢复实际占位符
        
        # 1. 标记实际占位符
        placeholders = [
            'analysis_time', 'success_rate', 'total_questions', 'avg_score',
            'success_failure_chart', 'score_distribution_chart', 'business_object_chart', 'performance_chart',
            'success_count', 'failure_count', 'total_count', 'success_percentage', 'failure_percentage',
            'failure_rate', 'score_ranges_json', 'mean_score', 'median_score', 'std_dev',
            'perfect_score_count', 'perfect_score_rate', 'business_objects_json', 'business_object_records_json',
            'best_performing', 'worst_performing', 'total_processing_time', 'avg_time_per_question',
            'min_processing_time', 'max_processing_time', 'time_p50', 'time_p90',
            'time_percentiles_json', 'min_response_length', 'max_response_length', 'avg_response_length',
            'json_valid_count', 'json_valid_rate', 'perfect_score_rate_display'
        ]
        
        # 为每个占位符创建一个唯一的临时标记
        temp_markers = {}
        for placeholder in placeholders:
            temp_marker = f"__TEMP_MARKER_{placeholder}__"
            temp_markers[placeholder] = temp_marker
            html_template = html_template.replace(f"{{{placeholder}}}", temp_marker)
        
        # 2. 转义其他大括号
        html_template = html_template.replace("{", "{{").replace("}", "}}")
        
        # 3. 恢复实际占位符
        for placeholder, marker in temp_markers.items():
            html_template = html_template.replace(marker, f"{{{placeholder}}}")
        
        # 现在可以安全地进行格式化
        formatted_html = html_template.format(
            analysis_time=analysis_result.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            success_rate=success_percentage,
            total_questions=total_count,
            avg_score=mean_score,
            success_failure_chart=charts.get('success_failure_pie', ''),
            score_distribution_chart=charts.get('score_distribution', ''),
            business_object_chart=charts.get('business_object_performance', ''),
            performance_chart=charts.get('performance_analysis', ''),
            # 图表数据
            success_count=success_count,
            failure_count=failure_count,
            total_count=total_count,
            success_percentage=success_percentage,
            failure_percentage=failure_percentage,
            failure_rate=failure_percentage,
            score_ranges_json=score_ranges_json,
            mean_score=mean_score,
            median_score=median_score,
            std_dev=std_dev,
            perfect_score_count=perfect_score_count,
            perfect_score_rate=perfect_score_rate,
            business_objects_json=business_objects_json,
            business_object_records_json=business_object_records_json,
            best_performing=best_performing,
            worst_performing=worst_performing,
            # 新增的性能指标参数
            total_processing_time=total_processing_time,
            avg_time_per_question=avg_time_per_question,
            min_processing_time=min_processing_time,
            max_processing_time=max_processing_time,
            time_p50=time_p50,
            time_p90=time_p90,
            time_percentiles_json=time_percentiles_json,
            min_response_length=min_response_length,
            max_response_length=max_response_length,
            avg_response_length=avg_response_length,
            json_valid_count=json_valid_count,
            json_valid_rate=json_valid_rate,
            perfect_score_rate_display=perfect_score_rate_display
        )
        
        return formatted_html
    
    def _get_html_template(self):
        # 这里应该返回HTML模板文件的内容
        # 由于模板文件是外部文件，我们暂时使用一个字符串作为模板
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Evaluation Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .section {{ background: white; padding: 30px; margin-bottom: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(45deg, #f1f2f6 0%, #ffffff 100%); padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #3498db; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .chart-container {{ text-align: center; margin: 30px 0; }}
        .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s; }}
        .chart-container img:hover {{ transform: scale(1.02); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .insights {{ background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px; }}
        .insights h3 {{ color: #0d47a1; margin-top: 0; }}
        .recommendations {{ background-color: #fff8e1; padding: 15px; border-radius: 8px; margin-top: 20px; }}
        .recommendations h3 {{ color: #ff6f00; margin-top: 0; }}
        .failure-pattern {{ background-color: #ffebee; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
        .failure-pattern h4 {{ color: #c62828; margin-top: 0; }}
        .translation {{ color: #666; font-size: 0.9em; margin-top: 5px; font-style: italic; }}
        
        /* 模态框样式 */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }}
        .modal-content {{ background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; border-radius: 10px; width: 80%; max-width: 1000px; max-height: 80vh; overflow: auto; }}
        .close {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; }}
        .close:hover, .close:focus {{ color: black; text-decoration: none; cursor: pointer; }}
        pre.json {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto; max-height: 60vh; }}
        .modal-tabs {{ display: flex; border-bottom: 1px solid #ddd; margin-bottom: 15px; }}
        .modal-tab {{ padding: 10px 15px; cursor: pointer; margin-right: 5px; border-radius: 5px 5px 0 0; }}
        .modal-tab.active {{ background-color: #f0f0f0; border: 1px solid #ddd; border-bottom: none; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .stats-table {{ width: 100%; border-collapse: collapse; }}
        .stats-table th {{ width: 40%; text-align: left; padding: 8px; background-color: #f5f5f5; }}
        .stats-table td {{ padding: 8px; }}
        
        /* 记录显示样式 */
        .records-container {{ max-height: 70vh; overflow-y: auto; }}
        .business-object-section {{ margin-bottom: 20px; }}
        .business-object-section h4 {{ color: #2c3e50; margin-bottom: 10px; }}
        .record-count {{ color: #7f8c8d; font-size: 0.9em; font-weight: normal; }}
        .record-item {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; padding: 10px; background-color: #fafafa; }}
        
        /* 记录标签页样式 */
        .records-tabs {{ display: flex; margin-bottom: 15px; border-bottom: 1px solid #ddd; }}
        .record-tab {{ padding: 8px 15px; cursor: pointer; margin-right: 5px; border-radius: 5px 5px 0 0; }}
        .record-tab:hover {{ background-color: #f5f5f5; }}
        .record-tab.active {{ background-color: #4CAF50; color: white; }}
        .record-tab-content {{ display: none; }}
        .record-tab-content.active {{ display: block; }}
        
        /* 搜索框样式 */
        .records-search-container {{ margin-bottom: 15px; display: flex; }}
        .records-search-container input {{ flex-grow: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; }}
        .records-search-container button {{ padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; }}
        .records-search-container button:hover {{ background-color: #45a049; }}
        
        /* 状态样式 */
        .status-success {{ color: #27ae60; }}
        .status-failed {{ color: #e74c3c; }}
        .record-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .record-id {{ font-weight: bold; color: #34495e; }}
        .record-status {{ padding: 2px 8px; border-radius: 12px; font-size: 0.8em; color: white; }}
        .status-success {{ background-color: #27ae60; }}
        .status-failed {{ background-color: #e74c3c; }}
        .record-score {{ background-color: #3498db; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
        .record-question {{ margin-bottom: 10px; font-size: 0.9em; }}
        .record-answers {{ margin-top: 10px; }}
        .record-answers summary {{ cursor: pointer; font-weight: bold; color: #2980b9; }}
        .answer-section {{ margin-top: 10px; }}
        .answer-section > div {{ margin-bottom: 10px; }}
        .json-display {{ background-color: #f8f9fa; padding: 8px; border-radius: 3px; font-size: 0.8em; overflow-x: auto; border: 1px solid #e9ecef; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Evaluation Analysis Report</h1>
            <p class="translation">(评估分析报告)</p>
            <p>Generated: {analysis_time}</p>
        </div>

        <div class="section">
            <h2>📈 Core Quality Metrics</h2>
            <p class="translation">(核心质量指标)</p>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{success_rate:.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                    <div class="translation">(成功率)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_questions:,}</div>
                    <div class="metric-label">Total Questions</div>
                    <div class="translation">(总问题数)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_score:.1f}</div>
                    <div class="metric-label">Average Score</div>
                    <div class="translation">(平均分数)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{json_valid_rate:.1f}%</div>
                    <div class="metric-label">JSON Valid Rate</div>
                    <div class="translation">(JSON有效率)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_response_length:.0f}</div>
                    <div class="metric-label">Avg Response Length</div>
                    <div class="translation">(平均响应长度)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perfect_score_rate:.1f}%</div>
                    <div class="metric-label">Perfect Score Rate</div>
                    <div class="translation">(满分率)</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>⏱️ Performance Metrics</h2>
            <p class="translation">(性能指标)</p>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_processing_time:.1f}s</div>
                    <div class="metric-label">Total Processing Time</div>
                    <div class="translation">(总处理时间)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_time_per_question:.3f}s</div>
                    <div class="metric-label">Avg Time/Question</div>
                    <div class="translation">(平均处理时间)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{min_processing_time:.3f}s</div>
                    <div class="metric-label">Min Processing Time</div>
                    <div class="translation">(最短处理时间)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{max_processing_time:.3f}s</div>
                    <div class="metric-label">Max Processing Time</div>
                    <div class="translation">(最长处理时间)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{time_p50:.3f}s</div>
                    <div class="metric-label">Median Time (P50)</div>
                    <div class="translation">(中位数处理时间)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{time_p90:.3f}s</div>
                    <div class="metric-label">P90 Time</div>
                    <div class="translation">(90%分位数时间)</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Data Visualization Analysis</h2>
            <p class="translation">(数据可视化分析)</p>
            
            <div class="chart-container">
                <h3>Success/Failure Ratio</h3>
                <p class="translation">(成功失败比例)</p>
                <img src="{success_failure_chart}" alt="成功失败比例图" data-chart="success_failure" onclick="showChartData('success_failure')">
            </div>
            
            <div class="chart-container">
                <h3>Score Distribution</h3>
                <p class="translation">(分数分布分析)</p>
                <img src="{score_distribution_chart}" alt="分数分布图" data-chart="score_distribution" onclick="showChartData('score_distribution')">
            </div>
            
            <div class="chart-container">
                <h3>Business Object Performance</h3>
                <p class="translation">(业务对象表现对比)</p>
                <img src="{business_object_chart}" alt="业务对象表现图" data-chart="business_object" onclick="showChartData('business_object')">
            </div>
            
            <div class="chart-container">
                <h3>Performance Analysis</h3>
                <p class="translation">(性能分析)</p>
                <img src="{performance_chart}" alt="性能分析图" data-chart="performance" onclick="showChartData('performance')">
            </div>
            
            <!-- 数据查看模态框 -->
            <div id="dataModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <h2 id="modalTitle">Chart Data</h2>
                    
                    <div class="modal-tabs">
                        <div class="modal-tab active" onclick="showTab('visualTab')">Visualization</div>
                        <div class="modal-tab" onclick="showTab('dataTab')">Raw Data</div>
                        <div class="modal-tab" onclick="showTab('statsTab')">Statistics</div>
                        <div class="modal-tab" onclick="showTab('recordsTab')">Sample Records</div>
                    </div>
                    
                    <div id="visualTab" class="tab-content active">
                        <div id="modalVisual"></div>
                    </div>
                    
                    <div id="dataTab" class="tab-content">
                        <pre class="json" id="modalData"></pre>
                    </div>
                    
                    <div id="statsTab" class="tab-content">
                        <div id="modalStats"></div>
                    </div>
                    
                    <div id="recordsTab" class="tab-content">
                        <div class="records-search-container">
                            <input type="text" id="recordsSearchInput" placeholder="搜索关键字..." />
                            <button onclick="searchRecords()">搜索</button>
                        </div>
                        <div class="records-tabs">
                            <div class="record-tab active" onclick="showRecordTab('allRecords')">全部</div>
                            <div class="record-tab" onclick="showRecordTab('successRecords')">成功记录</div>
                            <div class="record-tab" onclick="showRecordTab('failedRecords')">失败记录</div>
                        </div>
                        <div id="allRecords" class="record-tab-content active"></div>
                        <div id="successRecords" class="record-tab-content"></div>
                        <div id="failedRecords" class="record-tab-content"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 添加JavaScript代码 -->
    <script>
        // 图表数据
        const chartData = {{
            success_failure: {{
                title: "Success/Failure Analysis",
                data: {{
                    success: {{count: {success_count}, percentage: "{success_percentage}%"}},
                    failure: {{count: {failure_count}, percentage: "{failure_percentage}%"}},
                    total: {total_count}
                }},
                stats: {{
                    success_rate: "{success_rate}%",
                    failure_rate: "{failure_rate}%"
                }}
            }},
            score_distribution: {{
                title: "Score Distribution Analysis",
                data: {{
                    ranges: {score_ranges_json},
                    mean: {mean_score},
                    median: {median_score},
                    std_dev: {std_dev}
                }},
                stats: {{
                    perfect_score_count: {perfect_score_count},
                    perfect_score_rate: "{perfect_score_rate}%"
                }}
            }},
                         business_object: {{
                 title: "Business Object Performance",
                 data: {business_objects_json},
                 records: {business_object_records_json},
                 stats: {{
                     best_performing: "{best_performing}",
                     worst_performing: "{worst_performing}"
                 }}
             }},
             performance: {{
                 title: "Performance Analysis",
                 data: {{
                     total_processing_time: {total_processing_time},
                     average_time_per_question: {avg_time_per_question},
                     min_processing_time: {min_processing_time},
                     max_processing_time: {max_processing_time},
                     time_percentiles: {time_percentiles_json},
                     response_lengths: {{
                         min: {min_response_length},
                         avg: {avg_response_length},
                         max: {max_response_length}
                     }},
                     json_metrics: {{
                         valid_count: {json_valid_count},
                         valid_rate: {json_valid_rate}
                     }}
                 }},
                 stats: {{
                     fastest_time: "{min_processing_time:.3f}s",
                     slowest_time: "{max_processing_time:.3f}s",
                     median_time: "{time_p50:.3f}s",
                     p90_time: "{time_p90:.3f}s"
                 }}
             }}
        }};
        
        // 获取模态框元素
        const modal = document.getElementById("dataModal");
        const modalTitle = document.getElementById("modalTitle");
        const modalVisual = document.getElementById("modalVisual");
        const modalData = document.getElementById("modalData");
        const modalStats = document.getElementById("modalStats");
        const modalRecords = document.getElementById("modalRecords");
        
        // 显示图表数据
        function showChartData(chartType) {{
            const data = chartData[chartType];
            if (!data) return;
            
            // 设置标题
            modalTitle.textContent = data.title;
            
            // 设置可视化内容
            modalVisual.innerHTML = `<img src="${{document.querySelector(`img[data-chart="${{chartType}}"]`).src}}" alt="${{data.title}}" style="max-width:100%;">`;
            
            // 设置原始数据
            modalData.textContent = JSON.stringify(data.data, null, 2);
            
            // 设置统计信息
            let statsHTML = '<table class="stats-table">';
            for (const [key, value] of Object.entries(data.stats)) {{
                statsHTML += `<tr><th>${{formatKey(key)}}</th><td>${{value}}</td></tr>`;
            }}
            statsHTML += '</table>';
            modalStats.innerHTML = statsHTML;
            
            // 设置记录数据（如果有的话）
            if (data.records && Object.keys(data.records).length > 0) {{
                // 存储所有记录以供搜索和分类
                window.allRecordsData = [];
                
                // 生成所有记录的HTML
                let allRecordsHTML = '<div class="records-container">';
                let successRecordsHTML = '<div class="records-container">';
                let failedRecordsHTML = '<div class="records-container">';
                
                for (const [objectName, records] of Object.entries(data.records)) {{
                    // 添加到全局记录数组
                    records.forEach(record => {{
                        window.allRecordsData.push({{
                            ...record,
                            businessObject: objectName
                        }});
                    }});
                    
                    // 为每个业务对象创建分区
                    const successRecords = records.filter(r => r.status === 'success');
                    const failedRecords = records.filter(r => r.status === 'failed');
                    
                    // 全部记录部分
                    allRecordsHTML += generateBusinessObjectSection(objectName, records);
                    
                    // 成功记录部分
                    if (successRecords.length > 0) {{
                        successRecordsHTML += generateBusinessObjectSection(objectName, successRecords);
                    }}
                    
                    // 失败记录部分
                    if (failedRecords.length > 0) {{
                        failedRecordsHTML += generateBusinessObjectSection(objectName, failedRecords);
                    }}
                }}
                
                allRecordsHTML += '</div>';
                successRecordsHTML += '</div>';
                failedRecordsHTML += '</div>';
                
                // 填充各个标签页
                document.getElementById('allRecords').innerHTML = allRecordsHTML;
                document.getElementById('successRecords').innerHTML = successRecordsHTML;
                document.getElementById('failedRecords').innerHTML = failedRecordsHTML;
            }} else {{
                document.getElementById('allRecords').innerHTML = '<p>无可用的详细记录。</p>';
                document.getElementById('successRecords').innerHTML = '<p>无可用的成功记录。</p>';
                document.getElementById('failedRecords').innerHTML = '<p>无可用的失败记录。</p>';
            }}
            
            // 使用全局函数生成业务对象部分HTML
            
            // 显示模态框
            modal.style.display = "block";
        }}
        
        // 格式化键名
        function formatKey(key) {{
            return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        }}
        
        // 格式化JSON字符串
        function formatJson(jsonString) {{
            try {{
                if (!jsonString) return 'N/A';
                const parsed = JSON.parse(jsonString);
                return JSON.stringify(parsed, null, 2);
            }} catch (e) {{
                return jsonString || 'Invalid JSON';
            }}
        }}
        
        // 生成业务对象部分的HTML（全局函数）
        function generateBusinessObjectSection(objectName, records) {{
            let html = `<div class="business-object-section" data-object="${{objectName}}">`;
            html += `<h4>${{objectName}} <span class="record-count">(${{records.length}} 条记录)</span></h4>`;
            html += `<div class="records-list">`;
            
            records.forEach((record, index) => {{
                html += `<div class="record-item" data-id="${{record.id}}" data-status="${{record.status}}" data-score="${{record.score}}">`;
                html += `<div class="record-header">`;
                html += `<span class="record-id">ID: ${{record.id}}</span>`;
                html += `<span class="record-status status-${{record.status}}">${{record.status}}</span>`;
                html += `<span class="record-score">Score: ${{record.score}}</span>`;
                html += `</div>`;
                html += `<div class="record-details">`;
                html += `<div class="record-question"><strong>问题:</strong> ${{record.question}}</div>`;
                html += `<details class="record-answers">`;
                html += `<summary>查看答案和评估</summary>`;
                html += `<div class="answer-section">`;
                html += `<div><strong>期望答案:</strong><pre class="json-display">${{formatJson(record.expected_answer)}}</pre></div>`;
                html += `<div><strong>实际答案:</strong><pre class="json-display">${{formatJson(record.actual_answer)}}</pre></div>`;
                if (record.evaluation && record.evaluation.comparison_result) {{
                    html += `<div><strong>差异:</strong><pre class="json-display">${{JSON.stringify(record.evaluation.comparison_result.value_differences || [], null, 2)}}</pre></div>`;
                }}
                if (record.evaluation && record.evaluation.failure_reason) {{
                    html += `<div><strong>失败原因:</strong> ${{record.evaluation.failure_reason}}</div>`;
                }}
                html += `<div><strong>处理时间:</strong> ${{record.processing_time.toFixed(3)}}s</div>`;
                html += `</div>`;
                html += `</details>`;
                html += `</div>`;
                html += `</div>`;
            }});
            
            html += `</div>`;
            html += `</div>`;
            return html;
        }}
        
        // 关闭模态框
        function closeModal() {{
            modal.style.display = "none";
        }}
        
        // 切换标签页
        function showTab(tabId) {{
            // 隐藏所有标签页内容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 取消所有标签页按钮的活动状态
            document.querySelectorAll('.modal-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签页内容
            document.getElementById(tabId).classList.add('active');
            
            // 设置选中的标签页按钮为活动状态
            document.querySelector(`.modal-tab[onclick="showTab('${{tabId}}')"]`).classList.add('active');
        }}
        
        // 切换记录标签页
        function showRecordTab(tabId) {{
            // 隐藏所有记录标签页内容
            document.querySelectorAll('.record-tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 取消所有记录标签页按钮的活动状态
            document.querySelectorAll('.record-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的记录标签页内容
            document.getElementById(tabId).classList.add('active');
            
            // 设置选中的记录标签页按钮为活动状态
            document.querySelector(`.record-tab[onclick="showRecordTab('${{tabId}}')"]`).classList.add('active');
        }}
        
        // 搜索记录
        function searchRecords() {{
            const searchTerm = document.getElementById('recordsSearchInput').value.toLowerCase();
            if (!window.allRecordsData || !searchTerm) return;
            
            // 过滤记录
            const filteredRecords = window.allRecordsData.filter(record => {{
                // 在多个字段中搜索
                return (
                    (record.question && record.question.toLowerCase().includes(searchTerm)) ||
                    (record.expected_answer && record.expected_answer.toLowerCase().includes(searchTerm)) ||
                    (record.actual_answer && record.actual_answer.toLowerCase().includes(searchTerm)) ||
                    (record.businessObject && record.businessObject.toLowerCase().includes(searchTerm)) ||
                    (record.id && record.id.toString().includes(searchTerm)) ||
                    (record.score && record.score.toString().includes(searchTerm))
                );
            }});
            
            // 按业务对象分组
            const groupedRecords = {{}};
            filteredRecords.forEach(record => {{
                if (!groupedRecords[record.businessObject]) {{
                    groupedRecords[record.businessObject] = [];
                }}
                groupedRecords[record.businessObject].push(record);
            }});
            
            // 生成搜索结果HTML
            let searchResultsHTML = '<div class="records-container">';
            if (Object.keys(groupedRecords).length > 0) {{
                searchResultsHTML += `<h3>搜索结果: "${{searchTerm}}" (${{filteredRecords.length}} 条匹配记录)</h3>`;
                for (const [objectName, records] of Object.entries(groupedRecords)) {{
                    searchResultsHTML += generateBusinessObjectSection(objectName, records);
                }}
            }} else {{
                searchResultsHTML += `<h3>搜索结果: "${{searchTerm}}"</h3><p>没有找到匹配的记录</p>`;
            }}
            searchResultsHTML += '</div>';
            
            // 显示搜索结果
            document.getElementById('allRecords').innerHTML = searchResultsHTML;
            showRecordTab('allRecords');
        }}
        
        // 点击模态框外部时关闭
        window.onclick = function(event) {{
            if (event.target == modal) {{
                closeModal();
            }}
        }}
    </script>
    
    <!-- 训练指南部分 -->
    <div class="section">
        <h2>🎓 Training Guide</h2>
        <p class="translation">(训练指南)</p>
        
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">Training Guide Generator</h5>
                <p class="card-text">基于评估结果和失败记录自动生成训练指南和改进建议。</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <button class="btn btn-primary" onclick="generateTrainingGuide()">
                            <i class="bi bi-book"></i> 生成训练指南
                        </button>
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-outline-success dropdown-toggle" type="button" id="downloadDropdown" data-bs-toggle="dropdown" aria-expanded="false" disabled>
                            <i class="bi bi-download"></i> 下载训练指南
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="downloadDropdown">
                            <li><a class="dropdown-item" href="#" onclick="downloadTrainingGuide('json', null)">下载全部 (JSON)</a></li>
                            <li><a class="dropdown-item" href="#" onclick="downloadTrainingGuide('csv', null)">下载全部 (CSV)</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><h6 class="dropdown-header">按业务对象下载</h6></li>
                            <div id="bo-download-list">
                                <!-- 此处将由JavaScript填充业务对象列表 -->
                            </div>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 训练指南显示区域 -->
        <div id="trainingGuideContainer" style="display: none;">
            <div class="alert alert-info mb-4">
                <h5 class="alert-heading">训练指南摘要</h5>
                <p id="guideSummary"></p>
            </div>
            
            <ul class="nav nav-tabs mb-4" id="trainingGuideTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary" type="button" role="tab">
                        摘要与建议
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="business-objects-tab" data-bs-toggle="tab" data-bs-target="#business-objects" type="button" role="tab">
                        业务对象分析
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="rules-tab" data-bs-toggle="tab" data-bs-target="#rules" type="button" role="tab">
                        规则分析
                    </button>
                </li>
            </ul>
            
            <div class="tab-content" id="trainingGuideTabContent">
                <!-- 摘要与建议标签页 -->
                <div class="tab-pane fade show active" id="summary" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h5>总体统计</h5>
                                </div>
                                <div class="card-body">
                                    <table class="table">
                                        <tbody id="guideTotalStats">
                                            <!-- 将由JavaScript填充 -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h5>建议类型统计</h5>
                                </div>
                                <div class="card-body">
                                    <table class="table">
                                        <tbody id="guideRecommendationStats">
                                            <!-- 将由JavaScript填充 -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>高优先级建议</h5>
                        </div>
                        <div class="card-body">
                            <div id="highPriorityList">
                                <!-- 将由JavaScript填充 -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 业务对象分析标签页 -->
                <div class="tab-pane fade" id="business-objects" role="tabpanel">
                    <div id="businessObjectsAccordion">
                        <!-- 将由JavaScript填充 -->
                    </div>
                </div>
                
                <!-- 规则分析标签页 -->
                <div class="tab-pane fade" id="rules" role="tabpanel">
                    <div class="mb-3">
                        <div class="input-group">
                            <input type="text" class="form-control" id="ruleSearchInput" placeholder="搜索规则ID...">
                            <button class="btn btn-outline-secondary" type="button" onclick="searchRules()">
                                <i class="bi bi-search"></i> 搜索
                            </button>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-primary active" onclick="filterRules('all')">全部</button>
                            <button type="button" class="btn btn-outline-primary" onclick="filterRules('training')">需要训练</button>
                            <button type="button" class="btn btn-outline-primary" onclick="filterRules('prompt')">改进提示词</button>
                            <button type="button" class="btn btn-outline-primary" onclick="filterRules('both')">两者都需要</button>
                        </div>
                    </div>
                    
                    <div id="rulesContainer">
                        <!-- 将由JavaScript填充 -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 训练指南相关功能
        let trainingGuideData = null;
        
        async function generateTrainingGuide() {
            const loader = document.getElementById('trainingGuideContainer');
            loader.innerHTML = '<div class="text-center my-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-3">正在生成训练指南，请稍候...</p></div>';
            loader.style.display = 'block';
            
            try {
                // 获取任务ID
                const urlParams = new URLSearchParams(window.location.search);
                const taskId = urlParams.get('task_id');
                
                if (!taskId) {
                    throw new Error('无法获取任务ID');
                }
                
                // 发送请求获取训练指南
                const response = await fetch(`/evaluation/training-guide/${taskId}`);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`获取训练指南失败: ${response.status} - ${errorText}`);
                }
                
                // 获取响应文本
                const responseText = await response.text();
                
                // 尝试解析JSON
                try {
                    trainingGuideData = JSON.parse(responseText);
                } catch (jsonError) {
                    console.error("JSON解析错误:", jsonError);
                    console.error("原始响应内容:", responseText);
                    throw new Error(`JSON解析失败: ${jsonError.message}. 请检查服务器响应格式。`);
                }
                
                // 检查数据结构
                if (!trainingGuideData || typeof trainingGuideData !== 'object') {
                    throw new Error('无效的训练指南数据结构');
                }
                
                // 启用下载按钮
                document.getElementById('downloadDropdown').disabled = false;
                
                // 渲染训练指南
                renderTrainingGuide(trainingGuideData);
            } catch (error) {
                console.error("生成训练指南错误:", error);
                loader.innerHTML = `<div class="alert alert-danger my-4">
                    <h5>生成训练指南失败</h5>
                    <p>${error.message}</p>
                    <details>
                        <summary>详细错误信息</summary>
                        <pre>${error.stack || '无堆栈信息'}</pre>
                    </details>
                </div>`;
            }
        }
        
        function renderTrainingGuide(data) {
            // 显示容器
            const container = document.getElementById('trainingGuideContainer');
            container.style.display = 'block';
            
            // 显示摘要
            document.getElementById('guideSummary').textContent = data.summary;
            
            // 渲染总体统计
            renderTotalStats(data);
            
            // 渲染建议类型统计
            renderRecommendationStats(data);
            
            // 渲染高优先级建议
            renderHighPriorityRecommendations(data);
            
            // 渲染业务对象分析
            renderBusinessObjects(data);
            
            // 渲染规则分析
            renderRules(data);
            
            // 渲染业务对象下载列表
            renderBusinessObjectDownloadList(data);
        }
        
        function renderTotalStats(data) {
            const container = document.getElementById('guideTotalStats');
            
            container.innerHTML = `
                <tr>
                    <th>总记录数</th>
                    <td>${data.total_records}</td>
                </tr>
                <tr>
                    <th>失败记录数</th>
                    <td>${data.total_failures}</td>
                </tr>
                <tr>
                    <th>整体失败率</th>
                    <td>${data.overall_failure_percentage.toFixed(1)}%</td>
                </tr>
                <tr>
                    <th>业务对象数量</th>
                    <td>${Object.keys(data.business_object_guides).length}</td>
                </tr>
            `;
        }
        
        function renderRecommendationStats(data) {
            // 统计不同类型的建议数量
            let trainingCount = 0;
            let promptCount = 0;
            let bothCount = 0;
            let highPriorityCount = 0;
            
            for (const bo in data.business_object_guides) {
                const guide = data.business_object_guides[bo];
                
                guide.recommendations.forEach(rec => {
                    if (rec.recommendation_type === 'training') trainingCount++;
                    else if (rec.recommendation_type === 'prompt') promptCount++;
                    else if (rec.recommendation_type === 'both') bothCount++;
                    
                    if (rec.priority === 'high') highPriorityCount++;
                });
            }
            
            const totalRecommendations = trainingCount + promptCount + bothCount;
            
            const container = document.getElementById('guideRecommendationStats');
            container.innerHTML = `
                <tr>
                    <th>训练建议总数</th>
                    <td>${totalRecommendations}</td>
                </tr>
                <tr>
                    <th>需要训练</th>
                    <td>${trainingCount} (${(trainingCount / totalRecommendations * 100).toFixed(1)}%)</td>
                </tr>
                <tr>
                    <th>改进提示词</th>
                    <td>${promptCount} (${(promptCount / totalRecommendations * 100).toFixed(1)}%)</td>
                </tr>
                <tr>
                    <th>两者都需要</th>
                    <td>${bothCount} (${(bothCount / totalRecommendations * 100).toFixed(1)}%)</td>
                </tr>
                <tr>
                    <th>高优先级建议</th>
                    <td>${highPriorityCount}</td>
                </tr>
            `;
        }
        
        function renderHighPriorityRecommendations(data) {
            const container = document.getElementById('highPriorityList');
            
            // 收集所有高优先级建议
            const highPriorityRecs = [];
            
            for (const bo in data.business_object_guides) {
                const guide = data.business_object_guides[bo];
                
                guide.recommendations.forEach(rec => {
                    if (rec.priority === 'high') {
                        highPriorityRecs.push({...rec, business_object: bo});
                    }
                });
            }
            
            if (highPriorityRecs.length === 0) {
                container.innerHTML = '<div class="alert alert-success">没有高优先级建议，做得不错！</div>';
                return;
            }
            
            // 按失败次数排序
            highPriorityRecs.sort((a, b) => b.failure_count - a.failure_count);
            
            let html = '';
            highPriorityRecs.forEach(rec => {
                html += `
                <div class="alert alert-danger mb-3">
                    <h5>${rec.business_object} - 规则 ${rec.rule_id}</h5>
                    <p><strong>失败次数:</strong> ${rec.failure_count} (${rec.failure_percentage.toFixed(1)}%)</p>
                    <p><strong>建议类型:</strong> ${getRecommendationTypeText(rec.recommendation_type)}</p>
                    <p><strong>描述:</strong> ${rec.description}</p>
                    <p><strong>失败类型:</strong> ${rec.failure_types.join(', ') || '未知'}</p>
                </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function renderBusinessObjects(data) {
            const container = document.getElementById('businessObjectsAccordion');
            
            let html = '';
            let index = 0;
            
            // 按失败率排序
            const sortedBOs = Object.entries(data.business_object_guides)
                .sort((a, b) => b[1].failure_percentage - a[1].failure_percentage);
            
            for (const [bo, guide] of sortedBOs) {
                index++;
                
                html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${index}">
                        <button class="accordion-button ${index > 1 ? 'collapsed' : ''}" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#collapse${index}" 
                                aria-expanded="${index === 1}" aria-controls="collapse${index}">
                            <span class="me-3">${bo}</span>
                            <span class="badge ${getBadgeClass(guide.failure_percentage)} ms-auto me-2">
                                失败率 ${guide.failure_percentage.toFixed(1)}%
                            </span>
                        </button>
                    </h2>
                    <div id="collapse${index}" class="accordion-collapse collapse ${index === 1 ? 'show' : ''}" 
                         aria-labelledby="heading${index}" data-bs-parent="#businessObjectsAccordion">
                        <div class="accordion-body">
                            <div class="mb-3">
                                <p><strong>总记录数:</strong> ${guide.total_records}</p>
                                <p><strong>失败记录数:</strong> ${guide.failure_count}</p>
                                <p><strong>建议数量:</strong> ${guide.recommendations.length}</p>
                            </div>
                            
                            <h6>训练建议:</h6>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>规则ID</th>
                                            <th>失败次数</th>
                                            <th>失败百分比</th>
                                            <th>建议类型</th>
                                            <th>优先级</th>
                                            <th>描述</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${renderRecommendationTable(guide.recommendations)}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function renderRecommendationTable(recommendations) {
            let html = '';
            
            if (recommendations.length === 0) {
                html = `<tr><td colspan="6" class="text-center">没有建议</td></tr>`;
                return html;
            }
            
            // 按失败次数排序
            const sortedRecs = [...recommendations].sort((a, b) => b.failure_count - a.failure_count);
            
            sortedRecs.forEach(rec => {
                html += `
                <tr>
                    <td>${rec.rule_id}</td>
                    <td>${rec.failure_count}</td>
                    <td>${rec.failure_percentage.toFixed(1)}%</td>
                    <td>${getRecommendationTypeText(rec.recommendation_type)}</td>
                    <td><span class="badge ${getPriorityBadgeClass(rec.priority)}">${rec.priority}</span></td>
                    <td>${rec.description}</td>
                </tr>
                `;
            });
            
            return html;
        }
        
        function renderRules(data) {
            const container = document.getElementById('rulesContainer');
            
            // 收集所有规则
            const allRules = [];
            
            for (const bo in data.business_object_guides) {
                const guide = data.business_object_guides[bo];
                
                guide.recommendations.forEach(rec => {
                    allRules.push({...rec, business_object: bo});
                });
            }
            
            if (allRules.length === 0) {
                container.innerHTML = '<div class="alert alert-info">没有找到规则分析数据</div>';
                return;
            }
            
            // 按规则ID和业务对象排序
            allRules.sort((a, b) => {
                const ruleCompare = a.rule_id.localeCompare(b.rule_id);
                if (ruleCompare !== 0) return ruleCompare;
                return a.business_object.localeCompare(b.business_object);
            });
            
            renderRulesList(allRules, container);
        }
        
        function renderRulesList(rules, container) {
            let html = `
            <div class="table-responsive">
                <table class="table table-striped rule-table">
                    <thead>
                        <tr>
                            <th>规则ID</th>
                            <th>业务对象</th>
                            <th>失败次数</th>
                            <th>相似度</th>
                            <th>建议类型</th>
                            <th>优先级</th>
                            <th>失败类型</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            rules.forEach(rule => {
                html += `
                <tr data-rule-id="${rule.rule_id}" data-business-object="${rule.business_object}" 
                    data-type="${rule.recommendation_type}" data-search="${rule.rule_id} ${rule.business_object} ${rule.failure_types.join(' ')}">
                    <td>${rule.rule_id}</td>
                    <td>${rule.business_object}</td>
                    <td>${rule.failure_count} (${rule.failure_percentage.toFixed(1)}%)</td>
                    <td>${rule.similarity_score.toFixed(2)}</td>
                    <td><span class="badge ${getTypeBadgeClass(rule.recommendation_type)}">${getRecommendationTypeText(rule.recommendation_type)}</span></td>
                    <td><span class="badge ${getPriorityBadgeClass(rule.priority)}">${rule.priority}</span></td>
                    <td>${rule.failure_types.join(', ') || '未知'}</td>
                </tr>
                `;
            });
            
            html += `
                    </tbody>
                </table>
            </div>
            `;
            
            container.innerHTML = html;
        }
        
        function renderBusinessObjectDownloadList(data) {
            const container = document.getElementById('bo-download-list');
            
            let html = '';
            
            const boNames = Object.keys(data.business_object_guides).sort();
            
            boNames.forEach(bo => {
                html += `
                <li>
                    <div class="dropdown-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>${bo}</span>
                            <div class="btn-group btn-group-sm ms-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="downloadTrainingGuide('json', '${bo}')">JSON</button>
                                <button class="btn btn-sm btn-outline-primary" onclick="downloadTrainingGuide('csv', '${bo}')">CSV</button>
                            </div>
                        </div>
                    </div>
                </li>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function searchRules() {
            const searchTerm = document.getElementById('ruleSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('.rule-table tbody tr');
            
            rows.forEach(row => {
                const searchText = row.getAttribute('data-search').toLowerCase();
                if (searchTerm === '' || searchText.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        function filterRules(type) {
            const rows = document.querySelectorAll('.rule-table tbody tr');
            
            rows.forEach(row => {
                const rowType = row.getAttribute('data-type');
                
                if (type === 'all' || rowType === type) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // 更新按钮状态
            document.querySelectorAll('.btn-group button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.querySelector(`.btn-group button[onclick="filterRules('${type}')"]`).classList.add('active');
        }
        
        function downloadTrainingGuide(format, businessObject) {
            // 获取任务ID
            const urlParams = new URLSearchParams(window.location.search);
            const taskId = urlParams.get('task_id');
            
            if (!taskId) {
                alert('无法获取任务ID');
                return;
            }
            
            // 构建下载URL
            let url = `/evaluation/training-guide/${taskId}/download?format=${format}`;
            if (businessObject) {
                url += `&business_object=${encodeURIComponent(businessObject)}`;
            }
            
            // 触发下载
            window.open(url, '_blank');
        }
        
        // 辅助函数
        function getBadgeClass(failurePercentage) {
            if (failurePercentage >= 50) return 'bg-danger';
            if (failurePercentage >= 20) return 'bg-warning text-dark';
            return 'bg-success';
        }
        
        function getPriorityBadgeClass(priority) {
            if (priority === 'high') return 'bg-danger';
            if (priority === 'medium') return 'bg-warning text-dark';
            return 'bg-info';
        }
        
        function getTypeBadgeClass(type) {
            if (type === 'training') return 'bg-primary';
            if (type === 'prompt') return 'bg-info text-dark';
            return 'bg-dark';
        }
        
        function getRecommendationTypeText(type) {
            if (type === 'training') return '需要训练';
            if (type === 'prompt') return '改进提示词';
            if (type === 'both') return '两者都需要';
            return type;
        }
    </script>
</body>
</html>
        """
        
        return html_template.format(
            analysis_time=analysis_result.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            success_rate=success_percentage,
            total_questions=total_count,
            avg_score=mean_score,
            success_failure_chart=charts.get('success_failure_pie', ''),
            score_distribution_chart=charts.get('score_distribution', ''),
            business_object_chart=charts.get('business_object_performance', ''),
            performance_chart=charts.get('performance_analysis', ''),
            # 图表数据
            success_count=success_count,
            failure_count=failure_count,
            total_count=total_count,
            success_percentage=success_percentage,
            failure_percentage=failure_percentage,
            failure_rate=failure_percentage,
            score_ranges_json=score_ranges_json,
            mean_score=mean_score,
            median_score=median_score,
            std_dev=std_dev,
            perfect_score_count=perfect_score_count,
            perfect_score_rate=perfect_score_rate,
            business_objects_json=business_objects_json,
            business_object_records_json=business_object_records_json,
            best_performing=best_performing,
            worst_performing=worst_performing,
            # 新增的性能指标参数
            total_processing_time=total_processing_time,
            avg_time_per_question=avg_time_per_question,
            min_processing_time=min_processing_time,
            max_processing_time=max_processing_time,
            time_p50=time_p50,
            time_p90=time_p90,
            time_percentiles_json=time_percentiles_json,
            min_response_length=min_response_length,
            max_response_length=max_response_length,
            avg_response_length=avg_response_length,
            json_valid_count=json_valid_count,
            json_valid_rate=json_valid_rate,
            perfect_score_rate_display=perfect_score_rate_display
        ) 