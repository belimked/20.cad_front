#!/bin/bash

# API服务部署脚本
# 用于将API服务部署到10.3.19.199并配置网络设置
# 更新：支持评估分析系统部署和JavaScript文件部署

# 安全提示：
# 建议使用SSH密钥认证替代密码认证：
# 1. ssh-keygen -t rsa (生成密钥对)
# 2. ssh-copy-id root@10.3.19.199 (复制公钥到服务器)
# 3. 删除下面的PASSWORD变量并移除sshpass相关命令

# 服务器信息
SERVER="10.3.19.199"
USER="root"
PASSWORD="1"  # 警告：生产环境请使用SSH密钥认证
DIR="/home/100.AI/100.AI.Train.Data"
PORT="9088"
PYTHON="/root/miniconda3/bin/python"

# 创建SSH命令
SSH_CMD="sshpass -p 1 ssh -o StrictHostKeyChecking=no $USER@$SERVER"
SCP_CMD="sshpass -p 1 scp -o StrictHostKeyChecking=no"

echo "===== API服务部署工具 ====="
echo "正在连接到服务器 $SERVER..."

# 检查sshpass是否安装
if ! command -v sshpass &> /dev/null; then
    echo "错误: 需要安装sshpass工具"
    echo "macOS: brew install esolitos/ipa/sshpass"
    echo "Ubuntu: sudo apt-get install sshpass"
    echo "CentOS: sudo yum install sshpass"
    exit 1
fi

# 测试SSH连接
echo "测试SSH连接..."
echo $SSH_CMD
$SSH_CMD "echo '连接成功'" || { echo "SSH连接失败"; exit 1; }



echo -e "\n===== 检查Python环境 ====="
echo "验证Python路径和版本..."
$SSH_CMD "$PYTHON --version" || { echo "指定的Python解释器不存在或无法执行"; exit 1; }

echo -e "\n===== 停止现有服务 ====="
echo "停止现有的API服务..."
$SSH_CMD "pkill -f 'python -m src.api.app' || echo '没有运行中的API服务'"

echo -e "\n===== 上传Python文件 ====="
echo "上传src/api/app.py文件..."
$SCP_CMD src/api/*.py $USER@$SERVER:$DIR/src/api/

echo "确保routes目录存在..."
$SSH_CMD "mkdir -p $DIR/src/api/routes"

echo "上传routes目录文件..."
$SCP_CMD src/api/routes/*.py $USER@$SERVER:$DIR/src/api/routes/

echo "确保evaluation目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/evaluation"

echo "上传evaluation目录文件..."
$SCP_CMD src/entity/evaluation/*.py $USER@$SERVER:$DIR/src/entity/evaluation/

echo "确保relationship目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/relationship"

echo "上传relationship目录文件..."
$SCP_CMD src/entity/relationship/*.py $USER@$SERVER:$DIR/src/entity/relationship/ 2>/dev/null || echo "没有relationship Python文件"

echo "确保baseElements目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/baseElements"

echo "上传baseElements目录文件..."
$SCP_CMD src/entity/baseElements/*.py $USER@$SERVER:$DIR/src/entity/baseElements/ 2>/dev/null || echo "没有baseElements Python文件"

echo "确保evaluation_analysis服务目录存在..."
$SSH_CMD "mkdir -p $DIR/src/service/evaluation_analysis"

echo "上传service服务文件..."
$SCP_CMD src/service/*.py $USER@$SERVER:$DIR/src/service/

echo "上传service/common服务文件..."
$SCP_CMD src/service/common/*.py $USER@$SERVER:$DIR/src/service/common/

echo "上传VPO服务文件..."
$SSH_CMD "mkdir -p $DIR/src/service/vpo"
$SCP_CMD -r src/service/vpo/*.py $USER@$SERVER:$DIR/src/service/vpo/

echo "上传evaluation_analysis服务文件..."
$SCP_CMD src/service/evaluation_analysis/*.py $USER@$SERVER:$DIR/src/service/evaluation_analysis/

echo "上传配置Python文件..."
$SSH_CMD "mkdir -p $DIR/src/config"
$SCP_CMD src/config/*.py $USER@$SERVER:$DIR/src/config/ 2>/dev/null || echo "没有Python配置文件"

echo "上传字典Python文件..."
$SSH_CMD "mkdir -p $DIR/src/dict"
$SCP_CMD src/dict/*.py $USER@$SERVER:$DIR/src/dict/ 2>/dev/null || echo "没有字典Python文件"

echo -e "\n===== 启动API服务 ====="
echo "启动API服务..."
$SSH_CMD "cd $DIR && PYTHONPATH=$DIR nohup $PYTHON -m src.api.app --host $SERVER --port $PORT > api.log 2>&1 &"

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 验证服务是否正常运行
echo -e "\n===== 验证服务状态 ====="
echo "检查进程..."
$SSH_CMD "ps aux | grep '[p]ython -m src.api.app'"

echo "检查端口..."
$SSH_CMD "ss -tulpn | grep $PORT"

echo "测试本地API访问..."
$SSH_CMD "curl -s http://127.0.0.1:$PORT/docs | head -5"

echo -e "\n===== 部署完成 ====="
echo "API服务已部署到 http://$SERVER:$PORT"
echo
echo "主要访问地址:"
echo "- API文档: http://$SERVER:$PORT/docs"
echo
echo "如需查看日志，请执行："
echo "$SSH_CMD \"tail -f $DIR/api.log\""
echo
echo "如需停止服务，请执行："
echo "$SSH_CMD \"pkill -f 'python -m src.api.app'\""
