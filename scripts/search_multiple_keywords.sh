#!/bin/bash
# search_multiple_keywords.sh
# 批量关键词检索脚本
# 使用方式: ./search_multiple_keywords.sh <关键词文件> [结果数量/关键词] [输出目录]
# 例如: ./search_multiple_keywords.sh keywords.txt 10 results/

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "用法: $0 <关键词文件> [结果数量/关键词] [输出目录]"
    echo "示例: $0 keywords.txt 10 results/"
    echo "关键词文件应为每行一个关键词的纯文本文件"
    exit 1
fi

KEYWORDS_FILE="$1"
RESULTS_PER_KEYWORD="${2:-10}"
OUTPUT_DIR="${3:-./results}"

if [[ ! -f "$KEYWORDS_FILE" ]]; then
    echo "错误: 关键词文件 '$KEYWORDS_FILE' 不存在"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 读取关键词并逐个处理
KEYWORD_COUNT=0
TOTAL_RESULTS=0

echo "开始批量关键词检索..."
echo "关键词文件: $KEYWORDS_FILE"
echo "每个关键词返回结果数: $RESULTS_PER_KEYWORD"
echo "输出目录: $OUTPUT_DIR"
echo "----------------------------------------"

while IFS= read -r keyword || [[ -n "$keyword" ]]; do
    # 跳过空行和注释行
    [[ -z "$keyword" || "$keyword" =~ ^[[:space:]]*# ]] && continue
    
    KEYWORD_COUNT=$((KEYWORD_COUNT + 1))
    
    # 清理关键词用于文件名
    SAFE_KEYWORD=$(echo "$keyword" | tr ' ' '_' | tr -cd '[:alnum:]_-')
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT_FILE="$OUTPUT_DIR/${SAFE_KEYWORD}_${TIMESTAMP}.json"
    
    echo "[$KEYWORD_COUNT] 正在搜索: \"$keyword\""
    
    # 调用 Semantic Scholar 搜索脚本（假设它在同目录下）
    if [[ -x "./semantic_scholar_search.py" ]]; then
        python3 ./semantic_scholar_search.py "$keyword" "$RESULTS_PER_KEYWORD" > "$OUTPUT_FILE"
        RESULT_COUNT=$(jq 'length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        TOTAL_RESULTS=$((TOTAL_RESULTS + RESULT_COUNT))
        echo "    -> 找到 $RESULT_COUNT 条结果，保存到 $OUTPUT_FILE"
    else
        echo "    警告: 未找到 semantic_scholar_search.py 脚本，跳过此关键词"
    fi
    
    # 礼貌性延迟，避免请求过于频繁
    sleep 2
done < "$KEYWORDS_FILE"

echo "----------------------------------------"
echo "批量检索完成!"
echo "  处理关键词数: $KEYWORD_COUNT"
echo "  总结果数: $TOTAL_RESULTS"
echo "  结果保存在目录: $OUTPUT_DIR"