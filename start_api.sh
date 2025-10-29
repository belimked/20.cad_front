#!/bin/bash
# ============================================================================
# DWG Processing API 启动脚本 (Linux/Mac)
# ============================================================================

echo "================================================================================"
echo "DWG Processing API 服务启动"
echo "================================================================================"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")"

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖是否安装
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 缺少FastAPI依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[失败] 依赖安装失败，请手动执行: pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo ""
echo "启动API服务..."
echo "- 主机: 0.0.0.0"
echo "- 端口: 8000"
echo "- API文档: http://localhost:8000/docs"
echo "- ReDoc: http://localhost:8000/redoc"
echo ""
echo "按Ctrl+C停止服务"
echo "================================================================================"
echo ""

# 启动FastAPI服务
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
