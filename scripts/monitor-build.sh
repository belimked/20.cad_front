#!/bin/bash
# GitHub Actions 构建状态持续监控脚本
# 每分钟检查一次,直到所有任务完成

REPO="belimked/20.cad_front"
API_URL="https://api.github.com/repos/${REPO}/actions/runs"
CHECK_INTERVAL=60  # 秒

echo "================================================"
echo "开始监控 GitHub Actions 构建状态"
echo "Repository: ${REPO}"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "================================================"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] 检查中..."

    # 获取最近的运行记录
    RESULT=$(curl -s "${API_URL}?per_page=5" | python3 -c "
import sys, json

data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])

queued = 0
in_progress = 0
completed = 0
success = 0
failure = 0

for run in runs:
    status = run['status']
    conclusion = run.get('conclusion')

    if status == 'queued':
        queued += 1
    elif status == 'in_progress':
        in_progress += 1
    elif status == 'completed':
        completed += 1
        if conclusion == 'success':
            success += 1
        elif conclusion == 'failure':
            failure += 1

print(f'{queued},{in_progress},{completed},{success},{failure}')
")

    IFS=',' read -r QUEUED IN_PROGRESS COMPLETED SUCCESS FAILURE <<< "$RESULT"

    echo "  排队中: ${QUEUED} | 进行中: ${IN_PROGRESS} | 已完成: ${COMPLETED} (成功: ${SUCCESS}, 失败: ${FAILURE})"

    # 如果没有排队或进行中的任务,停止监控
    if [ "$QUEUED" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ]; then
        echo ""
        echo "================================================"
        echo "✅ 所有构建任务已完成!"
        echo "成功: ${SUCCESS} | 失败: ${FAILURE}"
        echo "================================================"
        echo ""
        echo "查看详细结果:"
        echo "https://github.com/${REPO}/actions"
        break
    fi

    # 如果有进行中的任务,显示详细信息
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "  🔄 有任务正在构建,详情:"
        curl -s "${API_URL}?per_page=5&status=in_progress" | python3 -c "
import sys, json

data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])

for run in runs:
    if run['status'] == 'in_progress':
        print(f\"     - {run['name']} ({run['head_branch']}) - {run['head_sha'][:7]}\")
" 2>/dev/null || true
    fi

    echo ""
    echo "等待 ${CHECK_INTERVAL} 秒后再次检查..."
    sleep $CHECK_INTERVAL
done

# 最终状态检查
echo ""
echo "执行完整状态检查:"
./scripts/check-build-status.sh
