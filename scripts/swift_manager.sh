#!/bin/bash

# Swift 模型部署管理脚本
# 作者: Claude 4.0 sonnet
# 版本: 1.0
# 日期: 2025-09-03

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/swift_service.pid"
LOG_FILE="$LOG_DIR/swift_service.log"

# 默认配置
DEFAULT_MODEL_PATH="/root/lanyun-tmp/modelscope_cache/qwen/Qwen2___5-3B"
DEFAULT_ADAPTER_PATH="./outputs/4table_training_20250903_105534"
DEFAULT_PORT=8000
DEFAULT_HOST="0.0.0.0"

# 创建必要目录
mkdir -p "$LOG_DIR"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖环境..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查 Swift
    if ! python3 -c "import swift" &> /dev/null; then
        log_error "Swift 未安装，请运行: pip install ms-swift[llm]"
        exit 1
    fi
    
    # 检查 CUDA (可选)
    if command -v nvidia-smi &> /dev/null; then
        log_info "检测到 CUDA 环境"
        nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits | while read line; do
            log_debug "GPU: $line"
        done
    else
        log_warn "未检测到 CUDA 环境，将使用 CPU 推理"
    fi
    
    log_info "依赖检查完成"
}

# 检查服务状态
check_service_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # 服务运行中
        else
            rm -f "$PID_FILE"
            return 1  # PID文件存在但进程不存在
        fi
    else
        return 1  # PID文件不存在
    fi
}

# 启动服务
start_service() {
    local model_path="${1:-$DEFAULT_MODEL_PATH}"
    local adapter_path="${2:-$DEFAULT_ADAPTER_PATH}"
    local port="${3:-$DEFAULT_PORT}"
    local host="${4:-$DEFAULT_HOST}"
    
    log_info "启动 Swift 服务..."
    log_debug "模型路径: $model_path"
    log_debug "适配器路径: $adapter_path"
    log_debug "端口: $port"
    log_debug "主机: $host"
    
    if check_service_status; then
        log_warn "服务已在运行中 (PID: $(cat "$PID_FILE"))"
        return 0
    fi
    
    # 检查模型路径
    if [ ! -d "$model_path" ]; then
        log_error "模型路径不存在: $model_path"
        exit 1
    fi
    
    # 检查适配器路径（可选）
    local adapter_args=""
    if [ -d "$adapter_path" ]; then
        adapter_args="--adapters_id_or_path $adapter_path"
        log_info "使用 LoRA 适配器: $adapter_path"
    else
        log_warn "适配器路径不存在，使用基础模型: $adapter_path"
    fi
    
    # 启动命令
    local cmd="swift deploy \
        --model_type qwen2_5-3b-instruct \
        --model_id_or_path $model_path \
        $adapter_args \
        --port $port \
        --host $host \
        --api_mode openai \
        --max_length 2048 \
        --temperature 0.1 \
        --top_p 0.8 \
        --use_flash_attn true"
    
    log_debug "执行命令: $cmd"
    
    # 后台启动服务
    nohup $cmd > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
    
    if check_service_status; then
        log_info "Swift 服务启动成功 (PID: $pid, Port: $port)"
        
        # 测试服务
        if test_service "$port"; then
            log_info "服务测试通过"
        else
            log_warn "服务测试失败，请检查日志"
        fi
    else
        log_error "Swift 服务启动失败"
        exit 1
    fi
}

# 停止服务
stop_service() {
    log_info "停止 Swift 服务..."
    
    if check_service_status; then
        local pid=$(cat "$PID_FILE")
        log_debug "终止进程: $pid"
        
        # 优雅停止
        kill -TERM "$pid" 2>/dev/null || true
        
        # 等待进程结束
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 30 ]; do
            sleep 1
            ((count++))
        done
        
        # 强制停止
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warn "优雅停止失败，强制终止进程"
            kill -KILL "$pid" 2>/dev/null || true
        fi
        
        rm -f "$PID_FILE"
        log_info "Swift 服务已停止"
    else
        log_warn "服务未运行"
    fi
    
    # 清理相关进程
    pkill -f "swift deploy" 2>/dev/null || true
}

# 重启服务
restart_service() {
    log_info "重启 Swift 服务..."
    stop_service
    sleep 2
    start_service "$@"
}

# 查看服务状态
status_service() {
    echo "=== Swift 服务状态 ==="
    
    if check_service_status; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}状态: 运行中${NC}"
        echo "PID: $pid"
        
        # 获取进程信息
        if ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null; then
            echo ""
        fi
        
        # 检查端口
        local port=$(netstat -tlnp 2>/dev/null | grep ":$DEFAULT_PORT " | awk '{print $4}' | cut -d: -f2)
        if [ -n "$port" ]; then
            echo "监听端口: $port"
        fi
        
        # 内存使用
        local mem=$(ps -p "$pid" -o rss --no-headers 2>/dev/null | awk '{print $1/1024}')
        if [ -n "$mem" ]; then
            echo "内存使用: ${mem} MB"
        fi
        
    else
        echo -e "${RED}状态: 未运行${NC}"
    fi
    
    echo ""
    echo "=== GPU 状态 ==="
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
    else
        echo "未检测到 GPU"
    fi
}

# 测试服务
test_service() {
    local port="${1:-$DEFAULT_PORT}"
    local host="${2:-localhost}"
    
    log_info "测试 Swift 服务..."
    
    # 测试模型列表接口
    local models_response=$(curl -s "http://$host:$port/v1/models" 2>/dev/null)
    if [ $? -eq 0 ] && echo "$models_response" | grep -q "qwen"; then
        log_info "模型列表接口测试通过"
    else
        log_error "模型列表接口测试失败"
        return 1
    fi
    
    # 测试聊天接口
    local chat_response=$(curl -s -X POST "http://$host:$port/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "qwen2_5-3b-instruct",
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 10
        }' 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$chat_response" | grep -q "choices"; then
        log_info "聊天接口测试通过"
        return 0
    else
        log_error "聊天接口测试失败"
        return 1
    fi
}

# 查看日志
view_logs() {
    local lines="${1:-50}"
    
    if [ -f "$LOG_FILE" ]; then
        echo "=== Swift 服务日志 (最近 $lines 行) ==="
        tail -n "$lines" "$LOG_FILE"
    else
        log_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 清理日志
clean_logs() {
    log_info "清理日志文件..."
    
    if [ -f "$LOG_FILE" ]; then
        > "$LOG_FILE"
        log_info "日志文件已清理"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
Swift 模型部署管理脚本

用法: $0 <命令> [参数]

命令:
    start [model_path] [adapter_path] [port] [host]
                        启动 Swift 服务
    stop                停止 Swift 服务
    restart [参数]      重启 Swift 服务
    status              查看服务状态
    test [port] [host]  测试服务接口
    logs [lines]        查看日志 (默认50行)
    clean-logs          清理日志文件
    check               检查依赖环境
    help                显示此帮助信息

示例:
    $0 start                                    # 使用默认配置启动
    $0 start /path/to/model /path/to/adapter    # 指定模型和适配器路径
    $0 restart                                  # 重启服务
    $0 status                                   # 查看状态
    $0 test 8000 localhost                      # 测试服务
    $0 logs 100                                 # 查看最近100行日志

默认配置:
    模型路径: $DEFAULT_MODEL_PATH
    适配器路径: $DEFAULT_ADAPTER_PATH
    端口: $DEFAULT_PORT
    主机: $DEFAULT_HOST

EOF
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            check_dependencies
            start_service "$2" "$3" "$4" "$5"
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_dependencies
            restart_service "$2" "$3" "$4" "$5"
            ;;
        status)
            status_service
            ;;
        test)
            test_service "$2" "$3"
            ;;
        logs)
            view_logs "$2"
            ;;
        clean-logs)
            clean_logs
            ;;
        check)
            check_dependencies
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
