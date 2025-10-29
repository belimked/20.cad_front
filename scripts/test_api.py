"""
API功能测试脚本

老王我写的测试脚本，艹！用来验证API功能是否正常
"""

import requests
import time
import json


API_BASE = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("\n" + "=" * 80)
    print("测试1: 健康检查")
    print("=" * 80)

    response = requests.get(f"{API_BASE}/health")
    result = response.json()

    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    assert result['code'] == 200
    assert result['data']['status'] == 'ok'

    print("✅ 健康检查通过")


def test_create_task():
    """测试创建任务"""
    print("\n" + "=" * 80)
    print("测试2: 创建任务")
    print("=" * 80)

    # 准备测试数据
    task_data = {
        "dwg_url": "https://httpbin.org/image/png",  # 测试URL
        "config_name": "default"
    }

    print(f"请求数据: {json.dumps(task_data, indent=2, ensure_ascii=False)}")

    response = requests.post(
        f"{API_BASE}/api/v1/tasks/print",
        json=task_data
    )

    result = response.json()
    print(f"\n响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    assert result['code'] == 200
    assert 'task_id' in result['data']

    task_id = result['data']['task_id']
    print(f"\n✅ 任务创建成功: {task_id}")

    return task_id


def test_get_task(task_id):
    """测试查询任务详情"""
    print("\n" + "=" * 80)
    print("测试3: 查询任务详情")
    print("=" * 80)

    response = requests.get(f"{API_BASE}/api/v1/tasks/{task_id}")
    result = response.json()

    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    assert result['code'] == 200
    assert result['data']['task_id'] == task_id

    print(f"✅ 任务查询成功")
    print(f"   状态: {result['data']['status']}")
    print(f"   进度: {result['data']['progress']}%")
    print(f"   步骤: {result['data']['current_step']}")


def test_list_tasks():
    """测试查询任务列表"""
    print("\n" + "=" * 80)
    print("测试4: 查询任务列表")
    print("=" * 80)

    response = requests.get(f"{API_BASE}/api/v1/tasks?page=1&size=10")
    result = response.json()

    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    assert result['code'] == 200
    assert 'items' in result['data']

    print(f"✅ 列表查询成功")
    print(f"   总数: {result['data']['total']}")
    print(f"   当前页: {result['data']['page']}")
    print(f"   本页条数: {len(result['data']['items'])}")


def test_task_polling(task_id, max_wait=60):
    """测试任务轮询"""
    print("\n" + "=" * 80)
    print("测试5: 任务状态轮询")
    print("=" * 80)

    print(f"轮询任务: {task_id}")
    print(f"最大等待: {max_wait} 秒")

    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(f"{API_BASE}/api/v1/tasks/{task_id}")
        result = response.json()

        task = result['data']
        elapsed = int(time.time() - start_time)

        print(f"\r[{elapsed}s] 状态: {task['status']:12s} | 进度: {task['progress']:3d}% | 步骤: {task['current_step'] or 'N/A':30s}", end='')

        if task['status'] in ['completed', 'failed']:
            print()  # 换行
            print(f"\n✅ 任务已完成")
            print(f"   最终状态: {task['status']}")
            print(f"   总耗时: {elapsed} 秒")

            # 显示步骤日志
            if task['steps']:
                print(f"\n步骤日志:")
                for step in task['steps']:
                    status_icon = '✅' if step['status'] == 'completed' else '❌' if step['status'] == 'failed' else '🔄'
                    duration = f"{step['duration_seconds']:.2f}s" if step['duration_seconds'] else 'N/A'
                    print(f"   {status_icon} [{step['step_order']}] {step['step_name']} ({duration})")
                    if step['message']:
                        print(f"      ℹ️  {step['message']}")
                    if step['error_message']:
                        print(f"      ❌ {step['error_message']}")

            return task['status'] == 'completed'

        time.sleep(2)

    print(f"\n⚠️ 轮询超时（{max_wait}秒）")
    return False


def main():
    """主测试流程"""
    print("=" * 80)
    print("DWG Processing API 功能测试")
    print("=" * 80)

    try:
        # 测试1: 健康检查
        test_health()

        # 测试2: 创建任务
        task_id = test_create_task()

        # 等待一会儿，让任务开始处理
        time.sleep(2)

        # 测试3: 查询任务详情
        test_get_task(task_id)

        # 测试4: 查询任务列表
        test_list_tasks()

        # 测试5: 任务状态轮询
        success = test_task_polling(task_id, max_wait=120)

        print("\n" + "=" * 80)
        if success:
            print("✅ 所有测试通过！")
        else:
            print("⚠️ 部分测试未完成")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：API服务未启动")
        print("   请先运行: start_api.bat (Windows) 或 ./start_api.sh (Linux/Mac)")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
