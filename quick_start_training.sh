#!/bin/bash

# 数据库专家AI快速训练启动脚本
# 基于现有的 first_time_training.py 和数据库专家数据

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助
show_help() {
    cat << EOF
🎯 数据库专家AI快速训练脚本

用法:
    $0 [选项]

训练模式:
    --quick-test        快速测试模式 (10%数据, 1轮训练)
    --full-training     完整训练模式 (全部数据, 3轮训练)
    --custom           自定义模式 (手动设置参数)

训练参数:
    --epochs NUM        训练轮数 (默认: 3)
    --batch-size NUM    批次大小 (默认: 2)
    --learning-rate LR  学习率 (默认: 5e-6)
    --model-path PATH   模型路径 (默认: microsoft/DialoGPT-small)

高级选项:
    --enable-eval       启用评估 (推荐)
    --enable-early-stop 启用早停 (推荐)
    --skip-gpu-check    跳过GPU检查
    --dry-run          只显示命令不执行
    --help, -h         显示帮助

示例:
    # 快速测试
    $0 --quick-test

    # 完整训练
    $0 --full-training --enable-eval --enable-early-stop

    # 自定义训练
    $0 --custom --epochs 5 --batch-size 4 --enable-eval

EOF
}

# 检查数据文件
check_data_file() {
    local data_file="data/4table_training_data_messages_format.json"
    
    if [ ! -f "$data_file" ]; then
        print_error "数据文件不存在: $data_file"
        print_info "请确保数据文件在正确位置"
        exit 1
    fi
    
    print_success "数据文件检查通过: $data_file"
    
    # 检查文件大小
    local file_size=$(wc -c < "$data_file")
    local file_size_mb=$((file_size / 1024 / 1024))
    print_info "数据文件大小: ${file_size_mb}MB"
}

# 检查训练脚本
check_training_script() {
    if [ ! -f "examples/first_time_training.py" ]; then
        print_error "训练脚本不存在: examples/first_time_training.py"
        exit 1
    fi
    
    print_success "训练脚本检查通过"
}

# 检查Python依赖
check_dependencies() {
    print_info "检查Python依赖..."
    
    python3 -c "
import sys
missing = []

try:
    import torch
    print('✅ PyTorch:', torch.__version__)
except ImportError:
    missing.append('torch')
    print('❌ PyTorch: 未安装')

try:
    import transformers
    print('✅ Transformers:', transformers.__version__)
except ImportError:
    missing.append('transformers')
    print('❌ Transformers: 未安装')

try:
    from peft import LoraConfig
    print('✅ PEFT: 已安装')
except ImportError:
    missing.append('peft')
    print('❌ PEFT: 未安装')

try:
    from datasets import Dataset
    print('✅ Datasets: 已安装')
except ImportError:
    missing.append('datasets')
    print('❌ Datasets: 未安装')

if missing:
    print()
    print('缺少依赖:', ', '.join(missing))
    print('安装命令: pip install torch transformers peft datasets accelerate')
    sys.exit(1)
else:
    print()
    print('✅ 所有依赖已安装')
"
    
    if [ $? -ne 0 ]; then
        print_error "依赖检查失败"
        print_info "请先安装依赖: pip install torch transformers peft datasets accelerate"
        exit 1
    fi
}

# 构建训练命令
build_training_command() {
    local mode="$1"
    local data_file="data/4table_training_data_messages_format.json"
    local timestamp=$(date +"%Y%m%d_%H%M")
    local output_dir="./outputs/db_expert_${mode}_${timestamp}"
    
    # 基础命令
    local cmd="python examples/first_time_training.py"
    cmd="$cmd --data_path $data_file"
    cmd="$cmd --output_dir $output_dir"
    
    # 根据模式设置参数
    case $mode in
        "quick_test")
            cmd="$cmd --test_mode"
            cmd="$cmd --num_epochs 1"
            cmd="$cmd --per_device_train_batch_size 1"
            cmd="$cmd --gradient_accumulation_steps 4"
            cmd="$cmd --learning_rate 5e-6"
            ;;
        "full_training")
            cmd="$cmd --num_epochs ${EPOCHS:-3}"
            cmd="$cmd --per_device_train_batch_size ${BATCH_SIZE:-2}"
            cmd="$cmd --gradient_accumulation_steps 8"
            cmd="$cmd --learning_rate ${LEARNING_RATE:-5e-6}"
            ;;
        "custom")
            cmd="$cmd --num_epochs ${EPOCHS:-3}"
            cmd="$cmd --per_device_train_batch_size ${BATCH_SIZE:-2}"
            cmd="$cmd --learning_rate ${LEARNING_RATE:-5e-6}"
            ;;
    esac
    
    # 模型路径
    if [ -n "$MODEL_PATH" ]; then
        cmd="$cmd --model_path $MODEL_PATH"
    fi
    
    # LoRA参数
    cmd="$cmd --lora_r 16 --lora_alpha 16"
    
    # 可选功能
    if [ "$ENABLE_EVAL" = true ]; then
        cmd="$cmd --enable_evaluation"
        cmd="$cmd --eval_split_ratio 0.1"
        cmd="$cmd --eval_steps 50"
    fi
    
    if [ "$ENABLE_EARLY_STOP" = true ]; then
        cmd="$cmd --enable_early_stopping"
        cmd="$cmd --early_stopping_patience 3"
        cmd="$cmd --early_stopping_threshold 0.0001"
        cmd="$cmd --early_stopping_metric dual_loss"
    fi
    
    if [ "$SKIP_GPU_CHECK" = true ]; then
        cmd="$cmd --skip_gpu_check"
    fi
    
    echo "$cmd"
}

# 默认参数
MODE=""
EPOCHS=""
BATCH_SIZE=""
LEARNING_RATE=""
MODEL_PATH=""
ENABLE_EVAL=false
ENABLE_EARLY_STOP=false
SKIP_GPU_CHECK=false
DRY_RUN=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --quick-test)
            MODE="quick_test"
            shift
            ;;
        --full-training)
            MODE="full_training"
            shift
            ;;
        --custom)
            MODE="custom"
            shift
            ;;
        --epochs)
            EPOCHS="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --learning-rate)
            LEARNING_RATE="$2"
            shift 2
            ;;
        --model-path)
            MODEL_PATH="$2"
            shift 2
            ;;
        --enable-eval)
            ENABLE_EVAL=true
            shift
            ;;
        --enable-early-stop)
            ENABLE_EARLY_STOP=true
            shift
            ;;
        --skip-gpu-check)
            SKIP_GPU_CHECK=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            print_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 如果没有指定模式，默认为快速测试
if [ -z "$MODE" ]; then
    print_warning "未指定训练模式，使用快速测试模式"
    MODE="quick_test"
fi

print_info "🎯 数据库专家AI训练启动"
echo "=================================="

# 执行检查
print_info "执行预检查..."
check_data_file
check_training_script
check_dependencies

# 显示配置
print_info "训练配置:"
echo "  模式: $MODE"
echo "  轮数: ${EPOCHS:-'默认'}"
echo "  批次大小: ${BATCH_SIZE:-'默认'}"
echo "  学习率: ${LEARNING_RATE:-'默认'}"
echo "  模型路径: ${MODEL_PATH:-'默认'}"
echo "  启用评估: $ENABLE_EVAL"
echo "  启用早停: $ENABLE_EARLY_STOP"
echo "  跳过GPU检查: $SKIP_GPU_CHECK"

# 构建命令
print_info "构建训练命令..."
TRAIN_CMD=$(build_training_command "$MODE")

print_info "训练命令:"
echo "$TRAIN_CMD"

if [ "$DRY_RUN" = true ]; then
    print_warning "干运行模式，不执行训练"
    exit 0
fi

# 确认执行
echo ""
read -p "是否开始训练? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "训练已取消"
    exit 0
fi

# 执行训练
print_success "开始数据库专家AI训练..."
echo "=================================="

eval $TRAIN_CMD

print_success "训练完成！"
