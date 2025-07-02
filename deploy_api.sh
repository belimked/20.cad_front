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

echo "确保evaluation目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/evaluation"

echo "上传evaluation目录文件..."
$SCP_CMD src/entity/evaluation/*.py $USER@$SERVER:$DIR/src/entity/evaluation/

echo "确保relationship目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/relationship"

echo "上传relationship目录文件..."
$SCP_CMD src/entity/relationship/*.json $USER@$SERVER:$DIR/src/entity/relationship/
$SCP_CMD src/entity/relationship/*.py $USER@$SERVER:$DIR/src/entity/relationship/ 2>/dev/null || echo "没有relationship Python文件"

echo "确保baseElements目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/baseElements"

echo "上传baseElements目录文件..."
$SCP_CMD src/entity/baseElements/*.json $USER@$SERVER:$DIR/src/entity/baseElements/
$SCP_CMD src/entity/baseElements/*.py $USER@$SERVER:$DIR/src/entity/baseElements/ 2>/dev/null || echo "没有baseElements Python文件"

echo "确保connection目录存在..."
$SSH_CMD "mkdir -p $DIR/src/entity/connection"

echo "上传connection目录文件..."
$SCP_CMD src/entity/connection/*.json $USER@$SERVER:$DIR/src/entity/connection/

echo -e "\n===== 上传评估分析相关文件 ====="
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

echo -e "\n===== 上传模板文件 ====="
echo "确保templates目录结构存在..."
$SSH_CMD "mkdir -p $DIR/src/templates/evaluation_analysis"

echo "上传evaluation_analysis模板文件..."
$SCP_CMD src/templates/evaluation_analysis/*.html $USER@$SERVER:$DIR/src/templates/evaluation_analysis/ 2>/dev/null || echo "没有evaluation_analysis模板文件"

echo "上传其他模板文件..."
$SCP_CMD src/templates/*.html $USER@$SERVER:$DIR/src/templates/ 2>/dev/null || echo "没有根目录模板文件"

echo -e "\n===== 上传配置文件 ====="
echo "确保config目录存在..."
$SSH_CMD "mkdir -p $DIR/src/config"

echo "上传配置文件..."
$SCP_CMD src/config/*.yml $USER@$SERVER:$DIR/src/config/
$SCP_CMD src/config/*.py $USER@$SERVER:$DIR/src/config/ 2>/dev/null || echo "没有Python配置文件"

echo -e "\n===== 上传字典文件 ====="
echo "确保dict目录存在..."
$SSH_CMD "mkdir -p $DIR/src/dict"

echo "上传字典文件..."
$SCP_CMD src/dict/*.json $USER@$SERVER:$DIR/src/dict/ 2>/dev/null || echo "没有字典JSON文件"
$SCP_CMD src/dict/*.py $USER@$SERVER:$DIR/src/dict/ 2>/dev/null || echo "没有字典Python文件"

echo -e "\n===== 创建输出目录结构 ====="
echo "创建outputs目录结构..."
$SSH_CMD "mkdir -p $DIR/outputs/data"
$SSH_CMD "mkdir -p $DIR/outputs/temp"
$SSH_CMD "mkdir -p $DIR/outputs/reports"

echo -e "\n===== 检查并安装依赖 ====="
echo "配置pip国内镜像源..."
$SSH_CMD "mkdir -p ~/.pip && cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
EOF"

echo -e "\n===== 安装中文字体支持 ====="
echo "检查系统中的中文字体..."
$SSH_CMD "fc-list :lang=zh 2>/dev/null | wc -l" | grep -q "0" && {
    echo "没有找到中文字体，开始安装..."
    
    # 检测系统类型
    if $SSH_CMD "command -v yum &> /dev/null"; then
        echo "检测到CentOS/RHEL系统，使用yum安装字体..."
        $SSH_CMD "yum install -y wqy-microhei-fonts wqy-zenhei-fonts" || echo "安装字体包失败，尝试替代方案..."
    elif $SSH_CMD "command -v apt-get &> /dev/null"; then
        echo "检测到Debian/Ubuntu系统，使用apt安装字体..."
        $SSH_CMD "apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei" || echo "安装字体包失败，尝试替代方案..."
    fi
    
    # 如果包管理器安装失败，尝试手动安装
    echo "手动下载微软雅黑字体..."
    $SSH_CMD "mkdir -p /usr/share/fonts/chinese/"
    
    # 检查是否已存在字体文件
    if ! $SSH_CMD "test -f /usr/share/fonts/chinese/msyh.ttf"; then
        # 从Gitee下载字体（因为国内访问速度快）
        echo "从镜像站下载中文字体..."
        $SSH_CMD "curl -L -o /usr/share/fonts/chinese/msyh.ttf http://mirrors.cloud.tencent.com/fonts/msyh.ttf || curl -L -o /usr/share/fonts/chinese/msyh.ttf https://gitee.com/mirrors/fonts/raw/master/msyh.ttf"
    fi
    
    # 更新字体缓存
    echo "更新字体缓存..."
    $SSH_CMD "fc-cache -fv"
    
    # 验证字体安装
    echo "验证中文字体安装结果..."
    $SSH_CMD "fc-list :lang=zh | grep -i 'micro\\|msyh'" || echo "注意: 未检测到中文字体，可能会导致图表中文显示异常"
} || echo "系统已安装中文字体"

echo "检查python-multipart是否安装..."
$SSH_CMD "$PYTHON -c 'import multipart' 2>/dev/null" || {
    echo "安装python-multipart..."
    $SSH_CMD "$PYTHON -m pip install python-multipart"
}

echo "检查matplotlib是否安装..."
$SSH_CMD "$PYTHON -c 'import matplotlib' 2>/dev/null" || {
    echo "安装matplotlib..."
    $SSH_CMD "$PYTHON -m pip install 'matplotlib<3.8'"
}

echo "检查pandas是否安装..."
$SSH_CMD "$PYTHON -c 'import pandas' 2>/dev/null" || {
    echo "安装pandas..."
    $SSH_CMD "/root/miniconda3/bin/conda install -y pandas" || $SSH_CMD "$PYTHON -m pip install 'pandas<2.1'"
}

echo "检查seaborn是否安装..."
$SSH_CMD "$PYTHON -c 'import seaborn' 2>/dev/null" || {
    echo "安装seaborn..."
    $SSH_CMD "$PYTHON -m pip install seaborn"
}

echo "检查plotly是否安装..."
$SSH_CMD "$PYTHON -c 'import plotly' 2>/dev/null" || {
    echo "安装plotly..."
    $SSH_CMD "$PYTHON -m pip install plotly"
}

echo -e "\n===== 确保静态文件目录存在 ====="
echo "检查并创建静态文件目录..."
$SSH_CMD "mkdir -p $DIR/src/static/css"
$SSH_CMD "mkdir -p $DIR/src/static/js"
$SSH_CMD "mkdir -p $DIR/src/static/js/utils"

echo -e "\n===== 上传静态文件 ====="
echo "上传HTML文件..."
$SCP_CMD src/static/*.html $USER@$SERVER:$DIR/src/static/
echo "上传CSS文件..."
$SCP_CMD src/static/css/style.css $USER@$SERVER:$DIR/src/static/css/
echo "上传新增的 report.css..."
$SCP_CMD src/static/css/report.css $USER@$SERVER:$DIR/src/static/css/
echo "上传JavaScript文件..."
$SCP_CMD src/static/js/*.js $USER@$SERVER:$DIR/src/static/js/

echo "上传JavaScript工具函数库..."
$SCP_CMD src/static/js/utils/*.js $USER@$SERVER:$DIR/src/static/js/utils/ 2>/dev/null || echo "没有utils工具函数文件"
$SCP_CMD src/static/js/utils/*.md $USER@$SERVER:$DIR/src/static/js/utils/ 2>/dev/null || echo "没有utils文档文件"

echo -e "\n===== 上传评估报告静态资源 ====="
echo "确保evaluation_reports目录存在..."
$SSH_CMD "mkdir -p $DIR/src/static/evaluation_reports"
echo "上传evaluation_reports静态资源..."
$SCP_CMD src/static/evaluation_reports/* $USER@$SERVER:$DIR/src/static/evaluation_reports/ 2>/dev/null || echo "没有evaluation_reports资源文件"

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
echo "- 评估分析系统: http://$SERVER:$PORT/static/evaluation_analysis.html"
echo
echo "评估分析API端点:"
echo "- 文件上传: POST http://$SERVER:$PORT/api/evaluation/upload"
echo "- 分析请求: POST http://$SERVER:$PORT/api/evaluation/analyze"
echo "- 状态查询: GET http://$SERVER:$PORT/api/evaluation/status/{task_id}"
echo "- 结果获取: GET http://$SERVER:$PORT/api/evaluation/result/{task_id}"
echo "- 报告下载: GET http://$SERVER:$PORT/api/evaluation/report/{task_id}"
echo
echo "如需查看日志，请执行："
echo "$SSH_CMD \"tail -f $DIR/api.log\""
echo
echo "如需停止服务，请执行："
echo "$SSH_CMD \"pkill -f 'python -m src.api.app'\"" 
