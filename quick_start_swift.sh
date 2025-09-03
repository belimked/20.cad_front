#!/bin/bash

# Swift 快速启动脚本
# 作者: Claude 4.0 sonnet
# 版本: 1.0
# 日期: 2025-09-03

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Swift 模型部署快速启动${NC}"
echo "=================================="

# 项目根目录
PROJECT_ROOT="$(pwd)"

echo -e "${GREEN}📁 项目目录:${NC} $PROJECT_ROOT"
echo ""

# 1. 检查Swift安装
echo -e "${YELLOW}1. 检查Swift环境...${NC}"
if python3 -c "import swift" 2>/dev/null; then
    echo "✅ Swift 已安装"
else
    echo "❌ Swift 未安装，正在安装..."
    pip install ms-swift[llm]
fi

# 2. 检查模型文件
echo -e "${YELLOW}2. 检查模型文件...${NC}"
if [ -d "./outputs/4table_training_20250903_105534" ]; then
    echo "✅ 找到训练好的LoRA模型"
    ADAPTER_PATH="./outputs/4table_training_20250903_105534"
else
    echo "⚠️  未找到LoRA模型，将使用基础模型"
    ADAPTER_PATH=""
fi

# 3. 启动服务
echo -e "${YELLOW}3. 启动Swift服务...${NC}"
echo "使用管理脚本启动服务..."

if [ -f "./scripts/swift_manager.sh" ]; then
    ./scripts/swift_manager.sh start
else
    echo "❌ 管理脚本不存在，请先运行 git_push_swift.sh"
    exit 1
fi

# 4. 显示使用说明
echo ""
echo -e "${GREEN}🎉 Swift服务启动完成！${NC}"
echo ""
echo "📋 使用说明:"
echo "  • 服务地址: http://localhost:8000"
echo "  • API文档: http://localhost:8000/docs"
echo "  • 管理命令: ./scripts/swift_manager.sh [start|stop|status|test]"
echo ""
echo "🧪 测试命令:"
echo "  ./scripts/swift_manager.sh test"
echo ""
echo "📊 查看状态:"
echo "  ./scripts/swift_manager.sh status"
echo ""
echo "📝 查看日志:"
echo "  ./scripts/swift_manager.sh logs"
echo ""
echo "🔄 Git推送Swift信息:"
echo "  ./scripts/git_push_swift.sh"
echo ""
echo -e "${BLUE}Happy coding! 🐾${NC}"
