#!/usr/bin/env python3
"""
Bplot API 测试脚本

使用方法:
1. 先启动 API 服务: start_api.ps1
2. 运行此脚本: python test_bplot_api.py
"""

import requests
import json
import time

# API 配置
API_URL = "http://localhost:8000/api/dwg/process"

# 测试参数
test_payload = {
    "dwg_url": "F:/cad/caddd/PCX20.01 主体钢结构（20230301）.dwg",
    "config_name": "bplot"
}

def test_bplot_workflow():
    """测试 Bplot 工作流"""
    print("=" * 80)
    print("Bplot API 测试")
    print("=" * 80)
    print(f"API 地址: {API_URL}")
    print(f"配置名称: {test_payload['config_name']}")
    print(f"DWG 文件: {test_payload['dwg_url']}")
    print("=" * 80)

    try:
        print("\n📤 发送请求...")
        response = requests.post(
            API_URL,
            json=test_payload,
            timeout=300  # 5分钟超时
        )

        # 检查响应状态
        print(f"✅ 响应状态: {response.status_code}")

        # 解析响应
        result = response.json()

        # 显示结果
        print("\n" + "=" * 80)
        print("📊 执行结果")
        print("=" * 80)

        print(f"\n任务ID: {result.get('task_id', 'N/A')}")
        print(f"状态: {result.get('status', 'N/A')}")

        # 显示提取的数据
        if 'extracted_data' in result:
            print("\n✅ 提取的数据:")
            for key, value in result['extracted_data'].items():
                print(f"  {key}: {value}")

        # 显示 OCR 日志
        if 'ocr_logs' in result and result['ocr_logs']:
            print("\n📋 OCR 识别日志:")
            for i, log in enumerate(result['ocr_logs'], 1):
                print(f"\n  [{i}] OCR 识别")
                print(f"      ID: {log.get('id', 'N/A')}")
                print(f"      目标模式: {log.get('target_text', 'N/A')}")
                print(f"      是否找到: {'✅' if log.get('found') else '❌'}")
                if log.get('found'):
                    print(f"      匹配文本: {log.get('matched_text', 'N/A')}")
                    print(f"      置信度: {log.get('confidence', 0):.2f}")
                    print(f"      匹配版本: {log.get('matched_version', 'N/A')}")
                print(f"      总耗时: {log.get('total_time', 0):.3f}秒")

        # 显示完整响应（调试用）
        print("\n" + "=" * 80)
        print("📝 完整响应 (JSON)")
        print("=" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return result

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到 API 服务")
        print("   请确保已启动 API 服务: start_api.ps1")
        return None

    except requests.exceptions.Timeout:
        print("❌ 请求超时: 执行时间超过5分钟")
        return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_bplot_workflow()

    if result:
        print("\n" + "=" * 80)
        print("✅ 测试完成")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 测试失败")
        print("=" * 80)
