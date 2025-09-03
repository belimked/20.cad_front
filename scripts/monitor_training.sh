#!/bin/bash
# 训练监控脚本
# 作者: Claude 4.0 sonnet

set -e

# =============================================================================
# 配置
# =============================================================================

LOG_DIR="./logs"
OUTPUTS_DIR="./outputs"

# =============================================================================
# 函数定义
# =============================================================================

print_info() {
    echo -e "\033[36m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
训练监控脚本使用说明:

用法: $0 [选项]

选项:
    -s, --status        显示训练状态
    -l, --logs          显示最新日志
    -f, --follow        实时跟踪日志
    -g, --gpu           显示GPU使用情况
    -k, --kill          停止所有训练进程
    -c, --cleanup       清理旧的日志和输出
    -h, --help          显示此帮助信息

示例:
    $0 --status         # 查看训练状态
    $0 --follow         # 实时查看日志
    $0 --gpu            # 查看GPU状态
    $0 --kill           # 停止训练

EOF
}

# 显示训练状态
show_status() {
    print_info "=== 训练状态检查 ==="
    
    # 检查PID文件
    if ls "$LOG_DIR"/*.pid 1> /dev/null 2>&1; then
        for pid_file in "$LOG_DIR"/*.pid; do
            if [ -f "$pid_file" ]; then
                PID=$(cat "$pid_file")
                BASENAME=$(basename "$pid_file" .pid)
                
                if ps -p $PID > /dev/null 2>&1; then
                    print_success "训练进程运行中: $BASENAME (PID: $PID)"
                    
                    # 显示进程信息
                    echo "  进程详情: $(ps -p $PID -o pid,ppid,cmd --no-headers)"
                    
                    # 显示运行时间
                    START_TIME=$(ps -p $PID -o lstart --no-headers)
                    echo "  启动时间: $START_TIME"
                    
                    # 显示CPU和内存使用
                    CPU_MEM=$(ps -p $PID -o %cpu,%mem --no-headers)
                    echo "  CPU/内存: $CPU_MEM"
                    
                else
                    print_warning "训练进程已停止: $BASENAME (PID: $PID)"
                fi
                echo ""
            fi
        done
    else
        print_info "没有找到运行中的训练进程"
    fi
    
    # 显示输出目录
    if [ -d "$OUTPUTS_DIR" ]; then
        print_info "=== 输出目录 ==="
        ls -la "$OUTPUTS_DIR" | tail -5
    fi
}

# 显示最新日志
show_logs() {
    print_info "=== 最新训练日志 ==="
    
    if ls "$LOG_DIR"/*.log 1> /dev/null 2>&1; then
        LATEST_LOG=$(ls -t "$LOG_DIR"/*.log | head -1)
        print_info "显示最新日志: $LATEST_LOG"
        echo ""
        tail -50 "$LATEST_LOG"
    else
        print_warning "没有找到日志文件"
    fi
}

# 实时跟踪日志
follow_logs() {
    if ls "$LOG_DIR"/*.log 1> /dev/null 2>&1; then
        LATEST_LOG=$(ls -t "$LOG_DIR"/*.log | head -1)
        print_info "实时跟踪日志: $LATEST_LOG"
        print_info "按 Ctrl+C 退出"
        echo ""
        tail -f "$LATEST_LOG"
    else
        print_error "没有找到日志文件"
        exit 1
    fi
}

# 显示GPU状态
show_gpu() {
    print_info "=== GPU 使用情况 ==="
    
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi
        echo ""
        print_info "=== GPU 进程详情 ==="
        nvidia-smi pmon -c 1
    else
        print_warning "nvidia-smi 不可用"
    fi
}

# 停止训练进程
kill_training() {
    print_warning "=== 停止训练进程 ==="
    
    if ls "$LOG_DIR"/*.pid 1> /dev/null 2>&1; then
        for pid_file in "$LOG_DIR"/*.pid; do
            if [ -f "$pid_file" ]; then
                PID=$(cat "$pid_file")
                BASENAME=$(basename "$pid_file" .pid)
                
                if ps -p $PID > /dev/null 2>&1; then
                    print_info "停止进程: $BASENAME (PID: $PID)"
                    kill $PID
                    
                    # 等待进程结束
                    sleep 2
                    if ps -p $PID > /dev/null 2>&1; then
                        print_warning "强制停止进程: $PID"
                        kill -9 $PID
                    fi
                    
                    print_success "进程已停止: $BASENAME"
                else
                    print_info "进程已经停止: $BASENAME"
                fi
                
                # 删除PID文件
                rm -f "$pid_file"
            fi
        done
    else
        print_info "没有找到运行中的训练进程"
    fi
}

# 清理旧文件
cleanup_old() {
    print_info "=== 清理旧文件 ==="
    
    read -p "确定要清理旧的日志和输出文件吗? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 清理7天前的日志
        find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
        find "$LOG_DIR" -name "*.pid" -mtime +7 -delete 2>/dev/null || true
        
        # 清理旧的输出目录（保留最新3个）
        if [ -d "$OUTPUTS_DIR" ]; then
            ls -t "$OUTPUTS_DIR" | tail -n +4 | xargs -I {} rm -rf "$OUTPUTS_DIR/{}" 2>/dev/null || true
        fi
        
        print_success "清理完成"
    else
        print_info "取消清理"
    fi
}

# =============================================================================
# 主程序
# =============================================================================

main() {
    case "${1:-}" in
        -s|--status)
            show_status
            ;;
        -l|--logs)
            show_logs
            ;;
        -f|--follow)
            follow_logs
            ;;
        -g|--gpu)
            show_gpu
            ;;
        -k|--kill)
            kill_training
            ;;
        -c|--cleanup)
            cleanup_old
            ;;
        -h|--help|"")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 检查是否直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
