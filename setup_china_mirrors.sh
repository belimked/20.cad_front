#!/bin/bash

# 配置国内镜像源脚本
# 为conda和pip配置国内高速镜像

SERVER="10.3.19.199"
USER="root"
PASSWORD="1"
CONDA="/root/miniconda3/bin/conda"

SSH_CMD="sshpass -p 1 ssh -o StrictHostKeyChecking=no $USER@$SERVER"

echo "===== 配置国内镜像源 ====="

# 1. 配置conda镜像源（多个备选）
echo -e "\n1. 配置conda镜像源"
echo "配置清华大学镜像源..."
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
$SSH_CMD "$CONDA config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/"

echo "配置中科大镜像源（备选）..."
$SSH_CMD "$CONDA config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/"
$SSH_CMD "$CONDA config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/"
$SSH_CMD "$CONDA config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/"

$SSH_CMD "$CONDA config --set show_channel_urls yes"

# 2. 配置pip镜像源
echo -e "\n2. 配置pip镜像源"
$SSH_CMD "mkdir -p ~/.pip"

# 创建pip配置文件，包含多个镜像源
$SSH_CMD "cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = 
    https://mirrors.tuna.tsinghua.edu.cn/pypi/simple/
    https://mirrors.ustc.edu.cn/pypi/simple/
    https://pypi.douban.com/simple/
trusted-host = 
    mirrors.aliyun.com
    mirrors.tuna.tsinghua.edu.cn
    mirrors.ustc.edu.cn
    pypi.douban.com
timeout = 120
retries = 3
EOF"

# 3. 显示配置结果
echo -e "\n3. 验证配置"
echo "Conda channels："
$SSH_CMD "$CONDA config --show channels"

echo -e "\nPip configuration："
$SSH_CMD "cat ~/.pip/pip.conf"

# 4. 测试镜像源速度
echo -e "\n4. 测试镜像源连接速度"
echo "测试conda镜像..."
$SSH_CMD "time $CONDA search numpy | head -5"

echo -e "\n测试pip镜像..."
$SSH_CMD "time /root/miniconda3/bin/pip search --index-url https://mirrors.aliyun.com/pypi/simple/ requests | head -5" || echo "pip search功能可能被禁用，但镜像配置正常"

echo -e "\n===== 镜像源配置完成 ====="
echo "已配置的镜像源："
echo ""
echo "Conda镜像源："
echo "- 清华大学: https://mirrors.tuna.tsinghua.edu.cn/anaconda/"
echo "- 中科大: https://mirrors.ustc.edu.cn/anaconda/"
echo ""
echo "Pip镜像源："
echo "- 阿里云（主）: https://mirrors.aliyun.com/pypi/simple/"
echo "- 清华大学: https://mirrors.tuna.tsinghua.edu.cn/pypi/simple/"
echo "- 中科大: https://mirrors.ustc.edu.cn/pypi/simple/"
echo "- 豆瓣: https://pypi.douban.com/simple/"
echo ""
echo "现在可以运行快速安装脚本："
echo "./fix_dependencies_v2_china.sh" 