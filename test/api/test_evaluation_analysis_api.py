#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
评估分析API接口测试脚本

测试评估分析相关的API功能
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# API基础URL
BASE_URL = "http://localhost:8000/api"


class EvaluationAnalysisAPITester:
    """评估分析API测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """测试健康检查接口"""
        print("🔍 测试健康检查接口...")
        
        try:
            response = self.session.get(f"{self.base_url}/evaluation/health")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 健康检查成功")
                print(f"   服务状态: {result.get('status')}")
                print(f"   服务版本: {result.get('version')}")
                print(f"   活跃任务: {result.get('active_tasks')}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_upload_file(self, file_path: str):
        """测试文件上传接口"""
        print(f"📁 测试文件上传接口: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ 测试文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/json')}
                response = self.session.post(f"{self.base_url}/evaluation/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文件上传成功")
                print(f"   文件ID: {result.get('file_id')}")
                print(f"   文件名: {result.get('filename')}")
                print(f"   文件大小: {result.get('file_size')} bytes")
                return result
            else:
                print(f"❌ 文件上传失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 文件上传异常: {e}")
            return None
    
    def test_analyze_file(self, file_path: str, generate_report: bool = True):
        """测试文件分析接口"""
        print(f"🔬 测试文件分析接口: {file_path}")
        
        try:
            payload = {
                "file_path": file_path,
                "generate_report": generate_report
            }
            
            response = self.session.post(
                f"{self.base_url}/evaluation/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 分析任务创建成功")
                print(f"   任务ID: {result.get('task_id')}")
                print(f"   估计时间: {result.get('estimated_time')}")
                return result.get('task_id')
            else:
                print(f"❌ 分析任务创建失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 分析任务创建异常: {e}")
            return None
    
    def test_get_status(self, task_id: str):
        """测试获取任务状态接口"""
        print(f"📊 查询任务状态: {task_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/evaluation/status/{task_id}")
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                progress = result.get('progress', 0.0)
                message = result.get('message', '')
                
                print(f"   状态: {status}")
                print(f"   进度: {progress:.1%}")
                print(f"   消息: {message}")
                
                return result
            else:
                print(f"❌ 查询状态失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 查询状态异常: {e}")
            return None
    
    def wait_for_completion(self, task_id: str, timeout: int = 300):
        """等待任务完成"""
        print(f"⏳ 等待任务完成: {task_id}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_info = self.test_get_status(task_id)
            
            if not status_info:
                return False
            
            status = status_info.get('status')
            
            if status == 'completed':
                print(f"✅ 任务完成!")
                return True
            elif status == 'failed':
                print(f"❌ 任务失败: {status_info.get('message')}")
                return False
            elif status in ['pending', 'running']:
                print(f"   等待中... ({status})")
                time.sleep(5)  # 等待5秒再检查
            else:
                print(f"❓ 未知状态: {status}")
                return False
        
        print(f"❌ 任务超时")
        return False
    
    def test_get_result(self, task_id: str, format: str = "summary"):
        """测试获取分析结果接口"""
        print(f"📋 获取分析结果: {task_id} (格式: {format})")
        
        try:
            response = self.session.get(
                f"{self.base_url}/evaluation/result/{task_id}",
                params={"format": format}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取结果成功")
                
                if format == "summary":
                    print(f"   整体质量等级: {result.get('overall_quality_grade')}")
                    print(f"   成功率: {result.get('success_rate', 0) * 100:.1f}%")
                    print(f"   总问题数: {result.get('total_questions', 0):,}")
                    print(f"   平均分数: {result.get('average_score', 0):.1f}")
                    print(f"   主要失败原因: {result.get('main_failure_reason')}")
                    print(f"   严重问题数: {result.get('critical_issues_count', 0)}")
                    print(f"   高优先级建议数: {result.get('high_priority_recommendations', 0)}")
                
                return result
            else:
                print(f"❌ 获取结果失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 获取结果异常: {e}")
            return None
    
    def test_get_report(self, task_id: str):
        """测试获取HTML报告接口"""
        print(f"📄 获取HTML报告: {task_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/evaluation/report/{task_id}")
            
            if response.status_code == 200:
                print(f"✅ 获取报告成功")
                print(f"   内容类型: {response.headers.get('content-type')}")
                print(f"   文件大小: {len(response.content)} bytes")
                
                # 保存报告到本地进行验证
                report_path = f"test_report_{task_id}.html"
                with open(report_path, 'wb') as f:
                    f.write(response.content)
                print(f"   报告已保存到: {report_path}")
                
                return True
            else:
                print(f"❌ 获取报告失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取报告异常: {e}")
            return False
    
    def test_list_tasks(self):
        """测试获取任务列表接口"""
        print(f"📋 获取任务列表")
        
        try:
            response = self.session.get(f"{self.base_url}/evaluation/tasks")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取任务列表成功")
                print(f"   总任务数: {result.get('total_tasks', 0)}")
                
                tasks = result.get('tasks', [])
                for i, task in enumerate(tasks[:3]):  # 显示前3个任务
                    print(f"   任务{i+1}: {task.get('task_id')} - {task.get('status')}")
                
                return result
            else:
                print(f"❌ 获取任务列表失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取任务列表异常: {e}")
            return None
    
    def run_full_test(self, test_file_path: str):
        """运行完整测试流程"""
        print("🚀 开始评估分析API完整测试")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_health_check():
            print("❌ 健康检查失败，停止测试")
            return False
        
        print("\n" + "-" * 30 + "\n")
        
        # 2. 文件上传
        upload_result = self.test_upload_file(test_file_path)
        if not upload_result:
            print("❌ 文件上传失败，停止测试")
            return False
        
        file_path = upload_result['file_path']
        
        print("\n" + "-" * 30 + "\n")
        
        # 3. 开始分析
        task_id = self.test_analyze_file(file_path, generate_report=True)
        if not task_id:
            print("❌ 分析任务创建失败，停止测试")
            return False
        
        print("\n" + "-" * 30 + "\n")
        
        # 4. 等待完成
        if not self.wait_for_completion(task_id):
            print("❌ 任务未能完成，停止测试")
            return False
        
        print("\n" + "-" * 30 + "\n")
        
        # 5. 获取摘要结果
        summary_result = self.test_get_result(task_id, format="summary")
        if not summary_result:
            print("❌ 获取摘要结果失败")
        
        print("\n" + "-" * 30 + "\n")
        
        # 6. 获取HTML报告
        if not self.test_get_report(task_id):
            print("❌ 获取HTML报告失败")
        
        print("\n" + "-" * 30 + "\n")
        
        # 7. 获取任务列表
        if not self.test_list_tasks():
            print("❌ 获取任务列表失败")
        
        print("\n" + "=" * 50)
        print("🎉 评估分析API测试完成!")
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
        print("请确保API服务已启动，或指定正确的测试文件路径")
        print("用法: python test_evaluation_analysis_api.py [测试文件路径]")
        return
    
    print(f"📁 使用测试文件: {test_file}")
    print(f"🌐 API地址: {BASE_URL}")
    
    # 创建测试器并运行测试
    tester = EvaluationAnalysisAPITester()
    success = tester.run_full_test(test_file)
    
    if success:
        print("✅ 所有测试通过!")
        sys.exit(0)
    else:
        print("❌ 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main() 