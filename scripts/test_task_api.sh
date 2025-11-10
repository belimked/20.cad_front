#!/bin/bash

# CAD任务API测试脚本
# 用于诊断任务状态更新问题

set -e

# 配置
API_URL="${API_URL:-http://localhost:8000}"
TASK_ID="${1:-task_202}"

echo "========================================"
echo "CAD 任务 API 测试"
echo "========================================"
echo "API URL: $API_URL"
echo "任务 ID: $TASK_ID"
echo ""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试1: 查询任务详情
echo -e "${YELLOW}[测试 1] 查询任务详情${NC}"
echo "GET $API_URL/api/v1/tasks/$TASK_ID"
echo ""

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/api/v1/tasks/$TASK_ID")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ HTTP 200 OK${NC}"
    echo ""
    echo "响应体:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    echo ""

    # 提取关键字段
    echo -e "${YELLOW}关键字段检查:${NC}"

    # 检查是否是新格式 (带 ApiResponse 包装)
    CODE=$(echo "$BODY" | jq -r '.code' 2>/dev/null)
    if [ "$CODE" != "null" ] && [ "$CODE" != "" ]; then
        echo "✓ 检测到新格式 (ApiResponse)"
        echo "  - code: $CODE"
        echo "  - message: $(echo "$BODY" | jq -r '.message')"

        STATUS=$(echo "$BODY" | jq -r '.data.status')
        PROGRESS=$(echo "$BODY" | jq -r '.data.progress')
        CURRENT_STEP=$(echo "$BODY" | jq -r '.data.current_step')
        MESSAGE=$(echo "$BODY" | jq -r '.data.message')
        FILE_SIZE=$(echo "$BODY" | jq -r '.data.file_size')
        DWG_FILENAME=$(echo "$BODY" | jq -r '.data.dwg_filename')
    else
        echo "✓ 检测到旧格式 (直接返回数据)"

        STATUS=$(echo "$BODY" | jq -r '.status')
        PROGRESS=$(echo "$BODY" | jq -r '.progress')
        CURRENT_STEP=$(echo "$BODY" | jq -r '.current_step')
        MESSAGE=$(echo "$BODY" | jq -r '.message')
        FILE_SIZE=$(echo "$BODY" | jq -r '.file_size')
        DWG_FILENAME=$(echo "$BODY" | jq -r '.dwg_filename')
    fi

    echo ""
    echo "任务状态:"
    echo "  - status: ${STATUS:-未提供}"
    echo "  - progress: ${PROGRESS:-未提供}%"
    echo "  - current_step: ${CURRENT_STEP:-未提供}"
    echo "  - message: ${MESSAGE:-未提供}"
    echo "  - file_size: ${FILE_SIZE:-未提供} bytes"
    echo "  - dwg_filename: ${DWG_FILENAME:-未提供}"
    echo ""

    # 检查必需字段
    MISSING_FIELDS=""
    [ "$STATUS" == "null" ] || [ -z "$STATUS" ] && MISSING_FIELDS="$MISSING_FIELDS status"
    [ "$PROGRESS" == "null" ] || [ -z "$PROGRESS" ] && MISSING_FIELDS="$MISSING_FIELDS progress"

    if [ -n "$MISSING_FIELDS" ]; then
        echo -e "${RED}✗ 缺少必需字段:$MISSING_FIELDS${NC}"
    else
        echo -e "${GREEN}✓ 所有必需字段都存在${NC}"
    fi

    # 检查可选字段
    echo ""
    echo "可选字段:"
    [ "$CURRENT_STEP" != "null" ] && [ -n "$CURRENT_STEP" ] && echo -e "  ${GREEN}✓${NC} current_step" || echo -e "  ${YELLOW}✗${NC} current_step (可选)"
    [ "$MESSAGE" != "null" ] && [ -n "$MESSAGE" ] && echo -e "  ${GREEN}✓${NC} message" || echo -e "  ${YELLOW}✗${NC} message (可选)"
    [ "$FILE_SIZE" != "null" ] && [ -n "$FILE_SIZE" ] && echo -e "  ${GREEN}✓${NC} file_size" || echo -e "  ${YELLOW}✗${NC} file_size (可选)"
    [ "$DWG_FILENAME" != "null" ] && [ -n "$DWG_FILENAME" ] && echo -e "  ${GREEN}✓${NC} dwg_filename" || echo -e "  ${GREEN}✓${NC} dwg_filename (可选)"

else
    echo -e "${RED}✗ HTTP $HTTP_STATUS${NC}"
    echo "错误响应:"
    echo "$BODY"
fi

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"
echo ""
echo "诊断建议:"
echo ""
if [ "$HTTP_STATUS" != "200" ]; then
    echo "1. 检查 API 服务是否正在运行"
    echo "2. 检查任务 ID 是否存在: $TASK_ID"
    echo "3. 检查 API URL 是否正确: $API_URL"
elif [ "$PROGRESS" == "null" ] || [ -z "$PROGRESS" ]; then
    echo "1. 后端未返回 progress 字段,检查后端代码"
    echo "2. 任务可能还未开始处理"
elif [ "$FILE_SIZE" == "null" ] || [ -z "$FILE_SIZE" ]; then
    echo "1. 后端未返回 file_size,前端会显示 '0 Bytes'"
    echo "2. 检查后端是否在下载后更新了文件大小"
elif [ "$CURRENT_STEP" == "null" ] && [ "$MESSAGE" == "null" ]; then
    echo "1. current_step 和 message 都未返回"
    echo "2. 前端将显示状态名称作为消息"
else
    echo -e "${GREEN}所有关键字段都正常!${NC}"
    echo "如果前端仍然没有更新,请检查:"
    echo "1. 浏览器控制台是否有错误"
    echo "2. 调试日志中是否有轮询记录"
    echo "3. 任务 store 是否正确更新"
fi
