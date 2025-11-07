#!/bin/bash
# GitHub Actions 构建状态监控脚本

REPO="belimked/20.cad_front"
API_URL="https://api.github.com/repos/${REPO}/actions/runs"

echo "================================================"
echo "GitHub Actions 构建状态监控"
echo "Repository: ${REPO}"
echo "================================================"
echo ""

# 获取最近 5 次运行记录
curl -s "${API_URL}?per_page=5" | python3 << 'EOF'
import sys, json

try:
    data = json.load(sys.stdin)
    runs = data.get('workflow_runs', [])

    if not runs:
        print('❌ 无法获取构建信息')
        sys.exit(1)

    print(f'最近 {len(runs)} 次运行记录:\n')

    for i, run in enumerate(runs, 1):
        name = run['name']
        status = run['status']
        conclusion = run.get('conclusion')
        branch = run['head_branch']
        sha = run['head_sha'][:7]
        created = run['created_at'].replace('T', ' ').replace('Z', '')

        # 状态图标
        if conclusion == 'success':
            icon = '✅'
            result_text = 'success'
        elif conclusion == 'failure':
            icon = '❌'
            result_text = 'failure'
        elif conclusion == 'cancelled':
            icon = '🚫'
            result_text = 'cancelled'
        elif status == 'queued':
            icon = '⏳'
            result_text = '排队中'
        elif status == 'in_progress':
            icon = '🔄'
            result_text = '进行中'
        else:
            icon = '❓'
            result_text = 'unknown'

        print(f'{i}. {icon} {name}')
        print(f'   状态: {status}', end='')
        if conclusion:
            print(f' / 结果: {conclusion}')
        else:
            print(f' / {result_text}')
        print(f'   分支: {branch}')
        print(f'   提交: {sha}')
        print(f'   时间: {created}')
        print()
except Exception as e:
    print(f'❌ 解析失败: {e}')
    sys.exit(1)
EOF

echo "================================================"
echo "查看详细信息:"
echo "https://github.com/${REPO}/actions"
echo "================================================"
