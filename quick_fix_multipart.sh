#!/bin/bash

# 快速修复脚本 - 只安装缺失的python-multipart包

SERVER="10.3.19.199"
USER="root"
PASSWORD="1"
PYTHON="/root/miniconda3/bin/python"

SSH_CMD="sshpass -p 1 ssh -o StrictHostKeyChecking=no $USER@$SERVER"

echo "===== 快速修复：安装python-multipart ====="

# 安装缺失的包
echo "安装python-multipart（FastAPI文件上传必需）..."
$SSH_CMD "$PYTHON -m pip install python-multipart -i https://mirrors.aliyun.com/pypi/simple/"

# 验证安装
echo -e "\n验证安装..."
$SSH_CMD "$PYTHON -c 'import multipart; print(\"✓ python-multipart安装成功\")'" || echo "✗ python-multipart安装失败"

# 重启API服务
echo -e "\n重启API服务..."
$SSH_CMD "pkill -f 'python -m src.api.app' || echo '没有运行中的API服务'"

echo "启动服务..."
$SSH_CMD "cd /home/100.AI/100.AI.Train.Data && PYTHONPATH=/home/100.AI/100.AI.Train.Data nohup $PYTHON -m src.api.app --host $SERVER --port 9088 > api.log 2>&1 &"

sleep 3

# 验证服务状态
echo -e "\n验证服务状态..."
$SSH_CMD "ps aux | grep '[p]ython -m src.api.app'" && {
    echo "✓ 服务进程运行正常"
    
    echo -e "\n检查API响应..."
    $SSH_CMD "curl -s http://127.0.0.1:9088/api/evaluation/health" && echo -e "\n✓ 评估分析API响应正常" || echo "✗ API响应异常"
    
} || {
    echo "✗ 服务启动失败"
    echo -e "\n查看错误日志："
    $SSH_CMD "tail -n 10 /home/100.AI/100.AI.Train.Data/api.log"
}

echo -e "\n===== 快速修复完成 ====="
echo "访问地址: http://$SERVER:9088/docs" 