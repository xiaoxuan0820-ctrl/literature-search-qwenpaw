#!/bin/bash
# filter_by_year.sh
# 按发表年份过滤 Semantic Scholar 搜索结果的脚本
# 使用方式: ./filter_by_year.sh <输入JSON文件> <输出JSON文件> [最小年份] [最大年份]
# 例如: ./filter_by_year.sh results.json filtered.json 2020 2023

set -euo pipefail

if [[ $# -lt 3 ]]; then
    echo "用法: $0 <输入JSON文件> <输出JSON文件> <最小年份> [最大年份]"
    echo "示例: $0 results.json filtered.json 2020 2023"
    echo "如果只提供最小年份，则过滤出年份 >= 最小年份的论文"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"
MIN_YEAR="$3"
MAX_YEAR="${4:-}"  # 可选参数

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "错误: 输入文件 '$INPUT_FILE' 不存在"
    exit 1
fi

# 使用 jq 进行过滤（需要 jq 工具）
if ! command -v jq &> /dev/null; then
    echo "错误: 需要安装 jq 工具来处理 JSON 数据"
    echo "在 macOS 上可以使用: brew install jq"
    echo "在 Ubuntu/Debian 上可以使用: sudo apt-get install jq"
    exit 1
fi

# 构建 jq 过滤条件
if [[ -n "$MAX_YEAR" ]]; then
    # 区间过滤：MIN_YEAR <= year <= MAX_YEAR
    FILTER="[.[] | select(.year | tonumber >= $MIN_YEAR and tonumber <= $MAX_YEAR)]"
else
    # 下限过滤：year >= MIN_YEAR
    FILTER="[.[] | select(.year | tonumber >= $MIN_YEAR)]"
fi

# 执行过滤
jq "$FILTER" "$INPUT_FILE" > "$OUTPUT_FILE"

# 输出统计信息
ORIGINAL_COUNT=$(jq 'length' "$INPUT_FILE" 2>/dev/null || echo "0")
FILTERED_COUNT=$(jq 'length' "$OUTPUT_FILE" 2>/dev/null || echo "0")

echo "过滤完成:"
echo "  原始记录数: $ORIGINAL_COUNT"
echo "  过滤后记录数: $FILTERED_COUNT"
echo "  过滤条件: 年份 >= $MIN_YEAR${MAX_YEAR:+ 和 <= $MAX_YEAR}"
echo "  结果已保存到: $OUTPUT_FILE"