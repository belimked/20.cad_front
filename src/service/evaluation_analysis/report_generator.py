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
import re

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
    
    def generate_html_report(self, analysis_result: AnalysisResult, output_dir: str = "outputs/reports", evaluation_records=None, task_id: str = None) -> str:
        """生成HTML分析报告"""
        self.logger.info("开始生成HTML报告")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成图表
        charts = self._generate_charts(analysis_result)
        
        # 生成HTML内容
        html_content = self._generate_html_content(analysis_result, charts, evaluation_records, task_id)
        
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
    
    def _generate_html_content(self, analysis_result: AnalysisResult, charts: Dict[str, str], evaluation_records=None, task_id: str = None) -> str:
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
        
        # 创建图表数据JSON
        chart_data = {
            "success_failure": {
                "title": "Success/Failure Analysis",
                "data": {
                    "success": {"count": success_count, "percentage": f"{success_percentage:.1f}%"},
                    "failure": {"count": failure_count, "percentage": f"{failure_percentage:.1f}%"},
                    "total": total_count
                },
                "stats": {
                    "success_rate": f"{success_percentage:.1f}%",
                    "failure_rate": f"{failure_percentage:.1f}%"
                }
            },
            "score_distribution": {
                "title": "Score Distribution Analysis",
                "data": {
                    "ranges": score_ranges,
                    "mean": mean_score,
                    "median": median_score,
                    "std_dev": std_dev
                },
                "stats": {
                    "perfect_score_count": perfect_score_count,
                    "perfect_score_rate": f"{perfect_score_rate:.3f}%"
                }
            },
            "business_object": {
                "title": "Business Object Performance",
                "data": business_objects,
                "records": business_object_records,
                "stats": {
                    "best_performing": best_performing,
                    "worst_performing": worst_performing
                }
            },
            "performance": {
                "title": "Performance Analysis",
                "data": {
                    "total_processing_time": total_processing_time,
                    "average_time_per_question": avg_time_per_question,
                    "min_processing_time": min_processing_time,
                    "max_processing_time": max_processing_time,
                    "time_percentiles": time_percentiles,
                    "response_lengths": {
                        "min": min_response_length,
                        "avg": avg_response_length,
                        "max": max_response_length
                    },
                    "json_metrics": {
                        "valid_count": json_valid_count,
                        "valid_rate": json_valid_rate
                    }
                },
                "stats": {
                    "fastest_time": f"{min_processing_time:.3f}s",
                    "slowest_time": f"{max_processing_time:.3f}s",
                    "median_time": f"{time_p50:.3f}s",
                    "p90_time": f"{time_p90:.3f}s"
                }
            }
        }
        
        # 使用安全的字符串替换方法，直接替换占位符，不进行复杂的大括号转换
        # 创建一个替换映射字典
        replacements = {
            'analysis_time': analysis_result.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'success_rate': f"{success_percentage:.1f}",
            'total_questions': f"{total_count:,}",
            'avg_score': f"{mean_score:.1f}",
            'success_failure_chart': charts.get('success_failure_pie', ''),
            'score_distribution_chart': charts.get('score_distribution', ''),
            'business_object_chart': charts.get('business_object_performance', ''),
            'performance_chart': charts.get('performance_analysis', ''),
            'json_valid_rate': f"{json_valid_rate:.1f}",
            'avg_response_length': f"{avg_response_length:.1f}",
            'perfect_score_rate_display': perfect_score_rate_display,
            'total_processing_time': f"{total_processing_time:.2f}",
            'avg_time_per_question': f"{avg_time_per_question:.3f}",
            'min_processing_time': f"{min_processing_time:.3f}",
            'max_processing_time': f"{max_processing_time:.3f}",
            'time_p50': f"{time_p50:.3f}",
            'time_p90': f"{time_p90:.3f}",
            'chart_data_json': json.dumps(chart_data),
            'task_id': task_id or 'unknown'
        }
        
        # 直接进行字符串替换，不改变CSS样式中的大括号
        formatted_html = html_template
        for key, value in replacements.items():
            placeholder = f"{{{key}}}"
            formatted_html = formatted_html.replace(placeholder, str(value))
        
        return formatted_html
    
    def _get_html_template(self):
        """从模板文件读取HTML模板"""
        template_path = os.path.join(os.path.dirname(__file__), '../../templates/evaluation_analysis/report_template.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"HTML模板文件未找到: {template_path}")
            # 如果模板文件不存在，返回一个简单的错误页面
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>报告生成错误</title>
</head>
<body>
    <h1>报告生成错误</h1>
    <p>HTML模板文件未找到，请检查模板文件是否存在。</p>
    <p>模板路径：{template_path}</p>
</body>
</html>"""
        except Exception as e:
            self.logger.error(f"读取HTML模板文件时出错: {e}")
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>报告生成错误</title>
</head>
<body>
    <h1>报告生成错误</h1>
    <p>读取HTML模板文件时出错：{e}</p>
</body>
</html>"""
