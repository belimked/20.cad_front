#!/bin/bash
# SQL查询生成模型训练脚本 (修正版本)
# 作者: Claude 4.0 sonnet
# 基于错误日志修正参数格式

set -e

# =============================================================================
# 配置区域
# =============================================================================

# 模型路径配置
export MODEL_PATH="/root/lanyun-tmp/modelscope_cache/qwen/Qwen2___5-3B"
export SWIFT_UI_LANG=zh

# 模型类型自动检测
if [[ "$MODEL_PATH" == *"Instruct"* ]]; then
    MODEL_TYPE="qwen2_5-3b-instruct"
else
    MODEL_TYPE="qwen2_5-3b"
fi

# 双卡分布式配置
export CUDA_VISIBLE_DEVICES=0,1
export NPROC_PER_NODE=2
export MASTER_PORT=29500

# 训练配置
DATASET_PATH="./data/query_condition_training_messages_format.jsonl"
OUTPUT_BASE_DIR="./outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE_DIR}/sql_query_training_fixed_${TIMESTAMP}"
LOG_DIR="./logs"
LOG_FILE="${LOG_DIR}/sql_training_fixed_${TIMESTAMP}.log"
PID_FILE="${LOG_DIR}/sql_training_fixed_${TIMESTAMP}.pid"

# =============================================================================
# 函数定义
# =============================================================================

print_info() {
    echo -e "\033[36m[INFO]\033[0m $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1" | tee -a "$LOG_FILE"
}

# 创建必要目录
create_directories() {
    print_info "创建输出目录..."
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$LOG_DIR"
    print_success "目录创建完成"
}

# 显示训练配置
show_config() {
    print_info "=== 修正版训练配置 ==="
    echo "训练模式: 双卡分布式 (torchrun)" | tee -a "$LOG_FILE"
    echo "GPU设置: CUDA_VISIBLE_DEVICES=0,1" | tee -a "$LOG_FILE"
    echo "进程数量: nproc_per_node=2" | tee -a "$LOG_FILE"
    echo "主端口: master_port=29500" | tee -a "$LOG_FILE"
    echo "模型类型: $MODEL_TYPE" | tee -a "$LOG_FILE"
    echo "模型路径: $MODEL_PATH" | tee -a "$LOG_FILE"
    echo "数据集: $DATASET_PATH" | tee -a "$LOG_FILE"
    echo "输出目录: $OUTPUT_DIR" | tee -a "$LOG_FILE"
    echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "PID文件: $PID_FILE" | tee -a "$LOG_FILE"
    echo "有效批次大小: 4×2×2=16 (batch_size×gpu×grad_accum)" | tee -a "$LOG_FILE"
    echo "早停机制: 启用 (patience=3, threshold=0.005)" | tee -a "$LOG_FILE"
    echo "评估策略: 每30步评估一次" | tee -a "$LOG_FILE"
    echo "最大训练轮数: 10轮 (可能提前停止)" | tee -a "$LOG_FILE"
    echo "===================" | tee -a "$LOG_FILE"
}

# 启动训练
start_training() {
    print_info "🚀 开始后台训练 SQL 查询生成模型 (修正版)..."
    
    # 构建修正的分布式训练命令
    # 基于错误信息，使用 --model 而不是 --model_id_or_path
    TRAIN_CMD="torchrun --nproc_per_node=2 --master_port=29500 \
        /root/miniconda/bin/swift sft \
        --model_type $MODEL_TYPE \
        --model $MODEL_PATH \
        --dataset $DATASET_PATH \
        --train_dataset_sample -1 \
        --num_train_epochs 10 \
        --max_length 2048 \
        --check_dataset_strategy warning \
        --lora_rank 32 \
        --lora_alpha 64 \
        --lora_dropout_p 0.1 \
        --lora_target_modules ALL \
        --gradient_checkpointing true \
        --batch_size 4 \
        --weight_decay 0.01 \
        --learning_rate 5e-5 \
        --gradient_accumulation_steps 2 \
        --max_grad_norm 0.5 \
        --warmup_ratio 0.1 \
        --eval_steps 30 \
        --save_steps 50 \
        --save_total_limit 3 \
        --logging_steps 10 \
        --use_flash_attn true \
        --evaluation_strategy steps \
        --load_best_model_at_end true \
        --metric_for_best_model eval_loss \
        --greater_is_better false \
        --early_stopping_patience 3 \
        --early_stopping_threshold 0.005 \
        --output_dir $OUTPUT_DIR"
    
    # 记录训练命令
    echo "修正版双卡分布式训练命令:" | tee -a "$LOG_FILE"
    echo "CUDA_VISIBLE_DEVICES=0,1" | tee -a "$LOG_FILE"
    echo "$TRAIN_CMD" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 后台启动分布式训练
    nohup bash -c "export CUDA_VISIBLE_DEVICES=0,1; $TRAIN_CMD" >> "$LOG_FILE" 2>&1 &
    
    # 记录进程ID
    TRAIN_PID=$!
    echo $TRAIN_PID > "$PID_FILE"
    
    print_success "修正版训练已在后台启动"
    print_info "进程ID: $TRAIN_PID"
    print_info "日志文件: $LOG_FILE"
    print_info "PID文件: $PID_FILE"
}

# 显示监控信息
show_monitoring_info() {
    print_info "=== 监控命令 ==="
    echo "查看实时日志: tail -f $LOG_FILE"
    echo "查看进程状态: ps aux | grep $TRAIN_PID"
    echo "查看GPU使用: nvidia-smi"
    echo "停止训练: kill $TRAIN_PID"
    echo "使用监控脚本: ./scripts/monitor_training.sh --follow"
    echo "==================="
}

# 清理函数
cleanup() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            print_warning "检测到训练进程仍在运行 (PID: $PID)"
            read -p "是否要停止训练? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill $PID
                print_info "训练进程已停止"
            fi
        fi
    fi
}

# =============================================================================
# 主程序
# =============================================================================

main() {
    # 设置信号处理
    trap cleanup EXIT
    
    print_info "=== SQL查询生成模型修正版后台训练脚本 ==="
    print_info "启动时间: $(date)"
    print_info "修正内容: 使用 --model 参数替代 --model_id_or_path"
    
    # 执行检查和准备
    create_directories
    show_config
    
    # 启动训练
    start_training
    
    # 显示监控信息
    show_monitoring_info
    
    print_success "修正版脚本执行完成！训练正在后台进行..."
    print_info "使用 'tail -f $LOG_FILE' 查看训练进度"
    print_info "或使用 './scripts/monitor_training.sh --follow' 监控"
}

# 检查是否直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
