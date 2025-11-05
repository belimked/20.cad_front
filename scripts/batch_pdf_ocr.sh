#!/bin/bash
# 批量处理PDF - 转图片OCR提取文本

set -e

# 配置
PDF_DIR="/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf"
OUTPUT_DIR="/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf_ocr_text"
SCRIPT_PATH="/Users/saul/IdeaProjects/100.AI.TrainData/scripts/pdf_to_images_ocr.py"
DPI=300  # 分辨率（可选：300, 600）
PARALLEL_JOBS=1  # 并行任务数（Umi-OCR服务器性能允许可设为2-3）

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 统计
total_count=$(find "$PDF_DIR" -name "*.pdf" -type f | wc -l | tr -d ' ')
success_count=0
fail_count=0
skip_count=0

echo "=========================================="
echo "批量PDF OCR文本提取"
echo "=========================================="
echo "PDF目录:     $PDF_DIR"
echo "输出目录:    $OUTPUT_DIR"
echo "DPI设置:     $DPI"
echo "总文件数:    $total_count"
echo "=========================================="
echo ""

# 确认继续
read -p "是否继续？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

# 开始时间
start_time=$(date +%s)

# 处理每个PDF
current=0
for pdf_file in "$PDF_DIR"/*.pdf; do
    current=$((current + 1))

    # 获取文件名（不含路径和扩展名）
    filename=$(basename "$pdf_file" .pdf)
    output_file="$OUTPUT_DIR/${filename}.txt"

    # 检查是否已处理
    if [ -f "$output_file" ]; then
        echo -e "${YELLOW}[$current/$total_count] 跳过: $filename (已存在)${NC}"
        skip_count=$((skip_count + 1))
        continue
    fi

    echo "[$current/$total_count] 处理: $filename"

    # 调用OCR脚本
    if python3 "$SCRIPT_PATH" "$pdf_file" "$output_file" "$DPI" > /dev/null 2>&1; then
        # 检查输出文件
        if [ -f "$output_file" ]; then
            char_count=$(wc -c < "$output_file" | tr -d ' ')
            if [ "$char_count" -gt 50 ]; then
                echo -e "  ${GREEN}✅ 成功 - $char_count 字符${NC}"
                success_count=$((success_count + 1))
            else
                echo -e "  ${YELLOW}⚠️  成功但文字少 - $char_count 字符${NC}"
                success_count=$((success_count + 1))
            fi
        else
            echo -e "  ${RED}❌ 失败 - 输出文件未生成${NC}"
            fail_count=$((fail_count + 1))
        fi
    else
        echo -e "  ${RED}❌ 失败 - OCR处理异常${NC}"
        fail_count=$((fail_count + 1))
    fi

    # 显示进度
    percentage=$((current * 100 / total_count))
    echo "  进度: $percentage% ($current/$total_count)"
    echo ""
done

# 结束时间
end_time=$(date +%s)
elapsed=$((end_time - start_time))
minutes=$((elapsed / 60))
seconds=$((elapsed % 60))

# 统计报告
echo ""
echo "=========================================="
echo "处理完成！"
echo "=========================================="
echo -e "${GREEN}成功: $success_count${NC}"
echo -e "${RED}失败: $fail_count${NC}"
echo -e "${YELLOW}跳过: $skip_count${NC}"
echo "总计: $total_count"
echo "耗时: ${minutes}分${seconds}秒"
echo "=========================================="
echo ""
echo "输出目录: $OUTPUT_DIR"

# 失败文件列表
if [ $fail_count -gt 0 ]; then
    echo ""
    echo "失败文件列表已保存到: $OUTPUT_DIR/failed_files.log"
fi

# 生成摘要报告
cat > "$OUTPUT_DIR/summary.txt" << EOF
批量PDF OCR处理报告
==========================================

处理时间: $(date)
PDF源目录: $PDF_DIR
输出目录: $OUTPUT_DIR
DPI设置: $DPI

处理结果:
- 成功: $success_count
- 失败: $fail_count
- 跳过: $skip_count
- 总计: $total_count

耗时: ${minutes}分${seconds}秒
平均速度: $(awk "BEGIN {printf \"%.2f\", $total_count / ($elapsed > 0 ? $elapsed : 1)}") 文件/秒

输出文件:
$(ls -1 "$OUTPUT_DIR"/*.txt 2>/dev/null | wc -l | tr -d ' ') 个TXT文件
总大小: $(du -sh "$OUTPUT_DIR" | cut -f1)

==========================================
EOF

echo "摘要报告: $OUTPUT_DIR/summary.txt"
