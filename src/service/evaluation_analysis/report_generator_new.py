#!/usr/bin/env python3
"""
评估分析报告生成器 - 使用外部HTML模板
"""

import os
import json
import base64
import logging
from io import BytesIO
from typing import Dict, Any
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np

from ...entity.analysis_result import AnalysisResult


def configure_chinese_fonts():
    """配置matplotlib中文字体支持"""
    try:
        # 尝试使用系统中文字体
        available_fonts = [font.name for font in fm.fontManager.ttflist]
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'STHeiti']
        
        selected_font = None
        for font in chinese_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            plt.rcParams['font.sans-serif'] = [selected_font]
            plt.rcParams['axes.unicode_minus'] = False
            return selected_font
        else:
            # 如果没有找到中文字体，使用默认字体
            plt.rcParams['axes.unicode_minus'] = False
            return "Default"
    except Exception as e:
        logging.warning(f"配置中文字体时出错: {e}")
        return "Default"


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        configure_chinese_fonts()

    def generate_html_report(self, analysis_result: AnalysisResult, output_dir: str = "outputs/reports", evaluation_records=None) -> str:
        """生成HTML分析报告"""
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成图表
            charts = self._generate_charts(analysis_result)
            
            # 生成HTML内容
            html_content = self._generate_html_content(analysis_result, charts, evaluation_records)
            
            # 保存HTML文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_analysis_report_{timestamp}.html"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成HTML报告时出错: {e}")
            raise

    def _generate_charts(self, analysis_result: AnalysisResult) -> Dict[str, str]:
        """生成分析图表"""
        charts = {}
        
        try:
            metrics = analysis_result.quality_metrics
            
            # 成功/失败比例饼图
            charts['success_failure_pie'] = self._create_success_failure_pie_chart(metrics)
            
            # 分数分布图
            charts['score_distribution'] = self._create_score_distribution_chart(metrics)
            
            # 业务对象表现图
            charts['business_object_performance'] = self._create_business_object_chart(metrics)
            
            # 性能分析图
            charts['performance_analysis'] = self._create_performance_chart(metrics)
            
        except Exception as e:
            self.logger.error(f"生成图表时出错: {e}")
            # 返回空字符串作为图表占位符
            charts = {key: '' for key in ['success_failure_pie', 'score_distribution', 'business_object_performance', 'performance_analysis']}
        
        return charts

    def _create_success_failure_pie_chart(self, metrics) -> str:
        """创建成功/失败比例饼图"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            success_count = metrics.successful_responses
            failure_count = metrics.failed_responses
            
            labels = ['成功', '失败']
            sizes = [success_count, failure_count]
            colors = ['#2ecc71', '#e74c3c']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            
            ax.set_title('成功/失败比例分析', fontsize=14, pad=20)
            
            # 添加图例
            ax.legend(wedges, [f'{label}: {size}' for label, size in zip(labels, sizes)],
                      title="统计", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            
            return self._fig_to_base64(fig)
        except Exception as e:
            self.logger.error(f"创建成功/失败饼图时出错: {e}")
            return ""

    def _create_score_distribution_chart(self, metrics) -> str:
        """创建分数分布图"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            score_ranges = metrics.score_distribution.score_ranges
            
            # 提取分数范围和计数
            ranges = []
            counts = []
            for range_str, count in score_ranges.items():
                ranges.append(range_str)
                counts.append(count)
            
            # 创建柱状图
            bars = ax.bar(ranges, counts, color='skyblue', alpha=0.7)
            
            # 在柱子上添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            ax.set_title('分数分布分析', fontsize=14, pad=20)
            ax.set_xlabel('分数范围')
            ax.set_ylabel('数量')
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            return self._fig_to_base64(fig)
        except Exception as e:
            self.logger.error(f"创建分数分布图时出错: {e}")
            return ""

    def _create_business_object_chart(self, metrics) -> str:
        """创建业务对象表现对比图"""
        try:
            if not metrics.quality_by_business_object:
                return ""
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            business_objects = []
            success_rates = []
            counts = []
            
            for bo, data in metrics.quality_by_business_object.items():
                # 处理业务对象名称，去除特殊字符
                safe_bo = str(bo).replace('{', '').replace('}', '')
                business_objects.append(safe_bo)
                success_rates.append(data.get('success_rate', 0) * 100)
                counts.append(data.get('count', 0))
            
            # 创建柱状图
            bars = ax.bar(business_objects, success_rates, color='lightcoral', alpha=0.7)
            
            # 在柱子上添加数量标签
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{counts[i]} 条',
                        ha='center', va='bottom', fontsize=9)
                ax.text(bar.get_x() + bar.get_width()/2., height/2,
                        f'{height:.1f}%',
                        ha='center', va='center', fontweight='bold')
            
            ax.set_title('业务对象表现对比', fontsize=14, pad=20)
            ax.set_xlabel('业务对象')
            ax.set_ylabel('成功率 (%)')
            ax.set_ylim(0, 105)
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            return self._fig_to_base64(fig)
        except Exception as e:
            self.logger.error(f"创建业务对象表现图时出错: {e}")
            return ""

    def _create_performance_chart(self, metrics) -> str:
        """创建性能分析图表"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            perf_metrics = metrics.performance_metrics
            
            # 1. 时间分布直方图
            if hasattr(perf_metrics, 'processing_times') and perf_metrics.processing_times:
                ax1.hist(perf_metrics.processing_times, bins=20, color='lightblue', alpha=0.7, edgecolor='black')
                ax1.set_title('处理时间分布')
                ax1.set_xlabel('处理时间 (秒)')
                ax1.set_ylabel('频次')
                ax1.grid(True, alpha=0.3)
            
            # 2. 时间百分位数
            time_percentiles = perf_metrics.time_percentiles
            percentiles = list(time_percentiles.keys())
            values = list(time_percentiles.values())
            
            ax2.plot(percentiles, values, marker='o', color='green', linewidth=2)
            ax2.set_title('时间百分位数')
            ax2.set_xlabel('百分位数')
            ax2.set_ylabel('时间 (秒)')
            ax2.grid(True, alpha=0.3)
            
            # 3. 响应长度统计
            response_data = [
                metrics.min_response_length,
                metrics.average_response_length,
                metrics.max_response_length
            ]
            response_labels = ['最小长度', '平均长度', '最大长度']
            
            bars3 = ax3.bar(response_labels, response_data, color=['lightgreen', 'orange', 'lightcoral'])
            ax3.set_title('响应长度统计')
            ax3.set_ylabel('字符数')
            
            # 在柱子上添加数值
            for bar, value in zip(bars3, response_data):
                ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                         f'{int(value)}',
                         ha='center', va='bottom')
            
            # 4. JSON有效性统计
            json_valid = metrics.json_valid_count
            json_invalid = metrics.total_questions - json_valid
            
            json_labels = ['有效JSON', '无效JSON']
            json_sizes = [json_valid, json_invalid]
            json_colors = ['lightgreen', 'lightcoral']
            
            ax4.pie(json_sizes, labels=json_labels, autopct='%1.1f%%', 
                    colors=json_colors, startangle=90)
            ax4.set_title('JSON有效性')
            
            plt.tight_layout()
            
            return self._fig_to_base64(fig)
        except Exception as e:
            self.logger.error(f"创建性能分析图时出错: {e}")
            return ""

    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图形转换为base64字符串"""
        try:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            plt.close(fig)
            
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            
            return f"data:image/png;base64,{graphic}"
        except Exception as e:
            self.logger.error(f"转换图形为base64时出错: {e}")
            plt.close(fig)
            return ""

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
            safe_bo = str(bo).replace('{', '_').replace('}', '_')
            business_objects[safe_bo] = {
                'success_rate': data.get('success_rate', 0) * 100,
                'count': data.get('count', 0)
            }
        
        business_objects_json = json.dumps(business_objects)
        
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
        
        # 读取HTML模板
        html_template = self._get_html_template()
        
        # 创建替换映射字典
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
            'chart_data_json': json.dumps(chart_data)
        }
        
        # 进行字符串替换
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
            return """<!DOCTYPE html>
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
</html>""".format(template_path=template_path)
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