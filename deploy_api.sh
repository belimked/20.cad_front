#!/bin/bash

# API服务部署脚本
# 用于将API服务部署到10.3.19.199并配置网络设置

# 服务器信息
SERVER="10.3.19.199"
USER="root"
PASSWORD="1"
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

echo -e "\n===== 上传修改后的代码 ====="
echo "上传src/api/app.py文件..."
$SCP_CMD src/api/*.py $USER@$SERVER:$DIR/src/api/

echo "确保routes目录存在..."
$SSH_CMD "mkdir -p $DIR/src/api/routes"

echo "上传routes目录文件..."
$SCP_CMD src/api/routes/*.py $USER@$SERVER:$DIR/src/api/routes/

echo -e "\n===== 上传回答元素数据 ====="
echo "确保answerElements目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/answerElements"

echo "上传answerElements目录文件..."
$SCP_CMD src/entity/answerElements/*.json $USER@$SERVER:$DIR/src/entity/answerElements/

echo -e "\n===== 确保静态文件目录存在 ====="
echo "检查并创建静态文件目录..."
$SSH_CMD "mkdir -p $DIR/src/static/css"

echo -e "\n===== 上传静态文件 ====="
echo "上传HTML文件..."
$SCP_CMD src/static/*.html $USER@$SERVER:$DIR/src/static/
echo "上传CSS文件..."
$SCP_CMD src/static/css/style.css $USER@$SERVER:$DIR/src/static/css/

echo -e "\n===== 配置网络和防火墙 ====="
echo "检查防火墙状态..."
$SSH_CMD "systemctl status firewalld | grep Active || echo '防火墙未运行'"

# 配置iptables以允许外部访问
echo "配置iptables规则..."
$SSH_CMD "iptables -I INPUT -p tcp --dport $PORT -j ACCEPT"
$SSH_CMD "iptables-save > /etc/sysconfig/iptables"

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
echo "访问地址:"
echo "- API首页: http://$SERVER:$PORT/"
echo "- API文档: http://$SERVER:$PORT/docs"
echo "- 静态页面: http://$SERVER:$PORT/static/index.html"
echo "- 数据字典: http://$SERVER:$PORT/static/dictionary.html"
echo "- 规则字典: http://$SERVER:$PORT/static/rule_dictionary.html"
echo "- 回答元素字典: http://$SERVER:$PORT/static/answer_dictionary.html"
echo
echo "如需查看日志，请执行："
echo "$SSH_CMD \"tail -f $DIR/api.log\""
echo
echo "如需停止服务，请执行："
echo "$SSH_CMD \"pkill -f 'python -m src.api.app'\"" 
