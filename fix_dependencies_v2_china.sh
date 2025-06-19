#!/bin/bash

# 完整修复服务器依赖问题的脚本（国内镜像优化版）
# 使用国内镜像源加速下载

SERVER="10.3.19.199"
USER="root"
PASSWORD="1"
PYTHON="/root/miniconda3/bin/python"
CONDA="/root/miniconda3/bin/conda"

# 创建SSH命令
SSH_CMD="sshpass -p 1 ssh -o StrictHostKeyChecking=no $USER@$SERVER"

echo "===== 完整修复依赖问题（国内镜像优化版） ====="
echo "配置国内镜像源以加速下载..."

# 配置conda国内镜像源
echo -e "\n1. 配置conda镜像源（清华大学源）"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
$SSH_CMD "$CONDA config --set show_channel_urls yes"

# 配置pip国内镜像源
echo -e "\n2. 配置pip镜像源（阿里云源）"
$SSH_CMD "mkdir -p ~/.pip"
$SSH_CMD "cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
EOF"

# 显示当前配置
echo -e "\n3. 验证镜像源配置"
$SSH_CMD "$CONDA config --show channels"

# 使用conda安装pandas（使用国内镜像）
echo -e "\n4. 使用conda安装pandas（清华镜像）"
$SSH_CMD "$CONDA install -y pandas=2.0.3" || {
    echo "尝试安装最新版本..."
    $SSH_CMD "$CONDA install -y pandas"
}

# 安装matplotlib依赖（如果需要更新）
echo -e "\n5. 确保matplotlib版本兼容"
$SSH_CMD "$CONDA install -y matplotlib=3.7.2" || {
    echo "使用pip安装matplotlib..."
    $SSH_CMD "$PYTHON -m pip install matplotlib==3.7.2"
}

# 安装seaborn（使用阿里云pip镜像）
echo -e "\n6. 安装seaborn（阿里云镜像）"
$SSH_CMD "$PYTHON -m pip install seaborn==0.12.2"

# 安装plotly
echo -e "\n7. 安装plotly（阿里云镜像）"
$SSH_CMD "$PYTHON -m pip install plotly==5.15.0"

# 安装其他可能需要的依赖
echo -e "\n8. 安装其他可能需要的依赖"
$SSH_CMD "$PYTHON -m pip install python-multipart==0.0.6"  # FastAPI文件上传支持
$SSH_CMD "$PYTHON -m pip install kaleido==0.2.1"  # plotly静态图导出
$SSH_CMD "$PYTHON -m pip install openpyxl==3.1.2"  # Excel文件支持

# 检查所有依赖
echo -e "\n9. 检查所有依赖"
echo "已安装的关键包版本："
$SSH_CMD "$PYTHON -m pip list | grep -E 'pandas|matplotlib|numpy|seaborn|fastapi|uvicorn|plotly|kaleido|openpyxl|multipart'"

# 测试所有导入
echo -e "\n10. 测试所有导入"
echo "测试核心依赖导入..."
$SSH_CMD "$PYTHON -c '
import sys
print(\"Python版本:\", sys.version)

# 测试导入
modules = [
    (\"numpy\", \"numpy\"),
    (\"pandas\", \"pandas\"), 
    (\"matplotlib\", \"matplotlib\"),
    (\"seaborn\", \"seaborn\"),
    (\"plotly\", \"plotly\"),
    (\"kaleido\", \"kaleido\"),
    (\"openpyxl\", \"openpyxl\"),
    (\"python-multipart\", \"multipart\")
]

for name, module in modules:
    try:
        mod = __import__(module)
        version = getattr(mod, \"__version__\", \"未知\")
        print(f\"✓ {name}导入成功, 版本: {version}\")
    except Exception as e:
        print(f\"✗ {name}导入失败: {e}\")
'"

# 测试评估分析模块导入
echo -e "\n11. 测试评估分析模块导入"
$SSH_CMD "cd /home/100.AI/100.AI.Train.Data && PYTHONPATH=/home/100.AI/100.AI.Train.Data $PYTHON -c '
try:
    from src.service.evaluation_analysis.report_generator import ReportGenerator
    print(\"✓ ReportGenerator导入成功\")
except Exception as e:
    print(f\"✗ ReportGenerator导入失败: {e}\")

try:
    from src.service.evaluation_analysis import EvaluationAnalyzer
    print(\"✓ EvaluationAnalyzer导入成功\")
except Exception as e:
    print(f\"✗ EvaluationAnalyzer导入失败: {e}\")
'"

# 重启API服务
echo -e "\n12. 重启API服务"
echo "停止现有服务..."
$SSH_CMD "pkill -f 'python -m src.api.app' || echo '没有运行中的API服务'"

echo "清理日志..."
$SSH_CMD "cd /home/100.AI/100.AI.Train.Data && rm -f api.log"

echo "启动服务..."
$SSH_CMD "cd /home/100.AI/100.AI.Train.Data && PYTHONPATH=/home/100.AI/100.AI.Train.Data nohup $PYTHON -m src.api.app --host $SERVER --port 9088 > api.log 2>&1 &"

sleep 5

# 验证服务状态
echo -e "\n13. 验证服务状态"
$SSH_CMD "ps aux | grep '[p]ython -m src.api.app'" && {
    echo "✓ 服务进程运行正常"
    
    echo -e "\n检查API响应..."
    $SSH_CMD "curl -s http://127.0.0.1:9088/api/evaluation/health" && echo -e "\n✓ 评估分析API响应正常" || echo "✗ API响应异常"
    
    echo -e "\n检查API文档..."
    $SSH_CMD "curl -s http://127.0.0.1:9088/docs | grep -i evaluation" && echo "✓ API文档包含评估分析功能" || echo "✗ API文档异常"
    
} || {
    echo "✗ 服务启动失败"
    echo -e "\n查看错误日志："
    $SSH_CMD "tail -n 30 /home/100.AI/100.AI.Train.Data/api.log"
}

echo -e "\n===== 修复完成 ====="
echo "使用的镜像源："
echo "- conda: 清华大学镜像"
echo "- pip: 阿里云镜像"
echo
echo "访问地址:"
echo "- API文档: http://$SERVER:9088/docs"
echo "- 健康检查: http://$SERVER:9088/api/evaluation/health"
echo "- 评估分析API: http://$SERVER:9088/api/evaluation/*" 