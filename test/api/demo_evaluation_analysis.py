#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
评估分析API功能演示脚本

演示评估分析系统的核心功能，模拟API调用流程
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.service.evaluation_analysis import EvaluationAnalyzer, ReportGenerator
from src.config.config_loader import load_evaluation_analysis_config


class EvaluationAnalysisDemo:
    """评估分析API功能演示"""
    
    def __init__(self):
        """初始化演示"""
        self.config = load_evaluation_analysis_config()
        self.analyzer = EvaluationAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # 创建输出目录
        self.temp_dir = "outputs/temp"
        self.reports_dir = "outputs/reports"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def simulate_file_upload(self, file_path: str):
        """模拟文件上传API"""
        print("🔄 模拟API调用: POST /api/evaluation/upload")
        
        if not os.path.exists(file_path):
            return {
                "status_code": 404,
                "detail": "文件不存在"
            }
        
        # 模拟文件验证
        if not file_path.endswith('.json'):
            return {
                "status_code": 400,
                "detail": "仅支持JSON格式的评估文件"
            }
        
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            return {
                "status_code": 400,
                "detail": "文件大小不能超过100MB"
            }
        
        # 生成文件ID
        file_id = str(uuid.uuid4())
        filename = f"evaluation_{file_id}_{os.path.basename(file_path)}"
        
        return {
            "status_code": 200,
            "data": {
                "file_id": file_id,
                "filename": filename,
                "file_path": file_path,  # 实际环境中会是复制后的路径
                "file_size": file_size,
                "upload_time": datetime.now().isoformat(),
                "message": "文件上传成功"
            }
        }
    
    def simulate_analyze_request(self, file_path: str, generate_report: bool = True):
        """模拟分析请求API"""
        print("🔄 模拟API调用: POST /api/evaluation/analyze")
        
        if not os.path.exists(file_path):
            return {
                "status_code": 404,
                "detail": "指定的文件不存在"
            }
        
        task_id = str(uuid.uuid4())
        
        return {
            "status_code": 200,
            "data": {
                "task_id": task_id,
                "status": "pending",
                "message": "分析任务已创建，请使用task_id查询进度",
                "estimated_time": "1-5分钟"
            }
        }
    
    def simulate_analysis_execution(self, file_path: str, task_id: str):
        """模拟分析执行过程"""
        print("🔄 模拟后台分析任务执行...")
        
        # 模拟状态更新
        status_updates = [
            {"progress": 0.1, "message": "开始分析评估文件..."},
            {"progress": 0.3, "message": "解析评估文件..."},
            {"progress": 0.6, "message": "执行质量分析..."},
            {"progress": 0.8, "message": "生成分析报告..."},
            {"progress": 1.0, "message": "分析完成"}
        ]
        
        for update in status_updates:
            print(f"   状态更新: {update['message']} ({update['progress']:.1%})")
        
        try:
            # 执行实际分析
            print("📊 执行真实分析...")
            analysis_result = self.analyzer.analyze_file(file_path)
            
            # 生成结果数据
            result_data = {
                "analysis_result": analysis_result.to_dict(),
                "executive_summary": analysis_result.get_executive_summary(),
                "actionable_items": analysis_result.get_actionable_items()
            }
            
            # 保存分析结果
            result_filename = f"analysis_result_{task_id}.json"
            result_path = os.path.join(self.temp_dir, result_filename)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 生成HTML报告
            print("📄 生成HTML报告...")
            evaluation_records = getattr(analysis_result, '_evaluation_records', None)
            report_path = self.report_generator.generate_html_report(analysis_result, self.reports_dir, evaluation_records)
            
            return {
                "status": "completed",
                "result_path": result_path,
                "report_path": report_path,
                "analysis_result": analysis_result
            }
        
        except Exception as e:
            print(f"❌ 分析执行失败: {e}")
            return {
                "status": "failed",
                "message": f"分析失败: {str(e)}"
            }
    
    def simulate_get_status(self, task_id: str, execution_result: dict):
        """模拟获取状态API"""
        print(f"🔄 模拟API调用: GET /api/evaluation/status/{task_id}")
        
        if execution_result["status"] == "completed":
            return {
                "status_code": 200,
                "data": {
                    "task_id": task_id,
                    "status": "completed",
                    "progress": 1.0,
                    "message": "分析完成",
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "result_path": execution_result["result_path"],
                    "report_path": execution_result["report_path"]
                }
            }
        else:
            return {
                "status_code": 200,
                "data": {
                    "task_id": task_id,
                    "status": "failed",
                    "progress": 0.0,
                    "message": execution_result.get("message", "分析失败"),
                    "end_time": datetime.now().isoformat()
                }
            }
    
    def simulate_get_result(self, task_id: str, execution_result: dict, format: str = "summary"):
        """模拟获取结果API"""
        print(f"🔄 模拟API调用: GET /api/evaluation/result/{task_id}?format={format}")
        
        if execution_result["status"] != "completed":
            return {
                "status_code": 400,
                "detail": f"任务未完成，当前状态: {execution_result['status']}"
            }
        
        result_path = execution_result["result_path"]
        if not os.path.exists(result_path):
            return {
                "status_code": 404,
                "detail": "分析结果文件不存在"
            }
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        if format == "summary":
            return {
                "status_code": 200,
                "data": result_data.get("executive_summary", {})
            }
        elif format == "actionable":
            return {
                "status_code": 200,
                "data": result_data.get("actionable_items", [])
            }
        else:
            return {
                "status_code": 200,
                "data": result_data
            }
    
    def simulate_get_report(self, task_id: str, execution_result: dict):
        """模拟获取报告API"""
        print(f"🔄 模拟API调用: GET /api/evaluation/report/{task_id}")
        
        if execution_result["status"] != "completed":
            return {
                "status_code": 400,
                "detail": f"任务未完成，当前状态: {execution_result['status']}"
            }
        
        report_path = execution_result["report_path"]
        if not os.path.exists(report_path):
            return {
                "status_code": 404,
                "detail": "分析报告文件不存在"
            }
        
        return {
            "status_code": 200,
            "data": {
                "message": "报告文件已准备就绪",
                "report_path": report_path,
                "content_type": "text/html",
                "file_size": os.path.getsize(report_path)
            }
        }
    
    def run_complete_demo(self, test_file_path: str):
        """运行完整的API功能演示"""
        print("🚀 评估分析API功能演示")
        print("=" * 60)
        print(f"📁 测试文件: {test_file_path}")
        print()
        
        # 1. 文件上传演示
        print("1️⃣  文件上传功能演示")
        upload_result = self.simulate_file_upload(test_file_path)
        if upload_result["status_code"] == 200:
            print("✅ 文件上传成功")
            print(f"   文件ID: {upload_result['data']['file_id']}")
            print(f"   文件大小: {upload_result['data']['file_size']:,} bytes")
        else:
            print(f"❌ 文件上传失败: {upload_result['detail']}")
            return
        
        print("\n" + "-" * 40 + "\n")
        
        # 2. 分析请求演示
        print("2️⃣  分析请求功能演示")
        analyze_result = self.simulate_analyze_request(test_file_path)
        if analyze_result["status_code"] == 200:
            print("✅ 分析任务创建成功")
            task_id = analyze_result['data']['task_id']
            print(f"   任务ID: {task_id}")
        else:
            print(f"❌ 分析任务创建失败: {analyze_result['detail']}")
            return
        
        print("\n" + "-" * 40 + "\n")
        
        # 3. 分析执行演示
        print("3️⃣  分析执行功能演示")
        execution_result = self.simulate_analysis_execution(test_file_path, task_id)
        if execution_result["status"] == "completed":
            print("✅ 分析执行成功")
        else:
            print(f"❌ 分析执行失败: {execution_result.get('message')}")
            return
        
        print("\n" + "-" * 40 + "\n")
        
        # 4. 状态查询演示
        print("4️⃣  状态查询功能演示")
        status_result = self.simulate_get_status(task_id, execution_result)
        if status_result["status_code"] == 200:
            print("✅ 状态查询成功")
            print(f"   任务状态: {status_result['data']['status']}")
            print(f"   完成进度: {status_result['data']['progress']:.1%}")
        
        print("\n" + "-" * 40 + "\n")
        
        # 5. 结果获取演示
        print("5️⃣  结果获取功能演示")
        result_summary = self.simulate_get_result(task_id, execution_result, format="summary")
        if result_summary["status_code"] == 200:
            print("✅ 执行摘要获取成功")
            summary = result_summary['data']
            print(f"   整体质量等级: {summary.get('overall_quality_grade')}")
            print(f"   成功率: {summary.get('success_rate', 0) * 100:.1f}%")
            print(f"   总问题数: {summary.get('total_questions', 0):,}")
            print(f"   平均分数: {summary.get('average_score', 0):.1f}")
            print(f"   主要失败原因: {summary.get('main_failure_reason')}")
        
        print("\n" + "-" * 40 + "\n")
        
        # 6. 报告获取演示
        print("6️⃣  报告获取功能演示")
        report_result = self.simulate_get_report(task_id, execution_result)
        if report_result["status_code"] == 200:
            print("✅ HTML报告获取成功")
            print(f"   报告路径: {report_result['data']['report_path']}")
            print(f"   文件大小: {report_result['data']['file_size']:,} bytes")
            print(f"   内容类型: {report_result['data']['content_type']}")
        
        print("\n" + "=" * 60)
        print("🎉 API功能演示完成!")
        
        # 显示关键洞察
        if execution_result["status"] == "completed":
            analysis_result = execution_result["analysis_result"]
            print("\n📋 关键分析洞察:")
            for i, insight in enumerate(analysis_result.key_insights[:3], 1):
                print(f"   {i}. {insight}")
        
        return True


def main():
    """主函数"""
    # 默认测试文件路径
    default_test_file = "/Users/saul/Desktop/unified_batch_summary_20250619_113039.json"
    
    # 从命令行参数获取测试文件路径
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        test_file = default_test_file
    
    # 检查测试文件
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        print("用法: python demo_evaluation_analysis.py [测试文件路径]")
        return
    
    try:
        # 创建演示器并运行演示
        demo = EvaluationAnalysisDemo()
        success = demo.run_complete_demo(test_file)
        
        if success:
            print("\n✅ API功能演示成功完成!")
        else:
            print("\n❌ API功能演示失败!")
            
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 