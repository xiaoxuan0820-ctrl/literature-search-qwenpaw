#!/usr/bin/env python3
"""
Export RIS Format Script
将检索结果导出为 RIS 格式的脚本
"""

import json
import sys
import os

def parse_arguments():
    """解析命令行参数"""
    if len(sys.argv) < 3:
        print("用法: python export_ris.py <输入JSON文件> <输出RIS文件>")
        print("示例: python export_ris.py results.json output.ris")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    return input_file, output_file

def load_json_data(input_file):
    """加载JSON数据"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"错误: 无法解析JSON文件 '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件 '{input_file}' 时出错: {e}")
        sys.exit(1)

def format_authors(authors):
    """格式化作者信息为RIS格式"""
    if not authors:
        return []
    
    ris_authors = []
    for author in authors:
        if isinstance(author, dict):
            # 处理Semantic Scholar作者格式
            name = author.get('name', '')
            if name:
                # RIS作者格式: 姓氏 名中首字母
                parts = name.split()
                if len(parts) >= 2:
                    last_name = parts[-1]
                    first_initials = ' '.join([p[0] + '.' for p in parts[:-1]])
                    ris_authors.append(f"{last_name} {first_initials}")
                else:
                    ris_authors.append(name)
        elif isinstance(author, str):
            # 处理纯字符串作者
            parts = author.split()
            if len(parts) >= 2:
                last_name = parts[-1]
                first_initials = ' '.join([p[0] + '.' for p in parts[:-1]])
                ris_authors.append(f"{last_name} {first_initials}")
            else:
                ris_authors.append(author)
    
    return ris_authors

def convert_to_ris_entry(paper):
    """将单篇论文转换为RIS条目"""
    ris_lines = []
    
    # 确定文献类型
    # 根据出版物类型判断
    pub_types = paper.get('publicationTypes', [])
    if any('Journal' in pt for pt in pub_types):
        ris_lines.append("TY  - JOUR")  # Journal Article
    elif any('Conference' in pt for pt in pub_types):
        ris_lines.append("TY  - CONF")  # Conference Paper
    else:
        ris_lines.append("TY  - GEN")   # Generic
    
    # 作者
    authors = paper.get('authors', [])
    ris_authors = format_authors(authors)
    for author in ris_authors:
        ris_lines.append(f"AU  - {author}")
    
    # 年份
    year = paper.get('year')
    if year:
        ris_lines.append(f"PY  - {year}")
    
    # 标题
    title = paper.get('title')
    if title:
        ris_lines.append(f"TI  - {title}")
    
    # 期刊/会议名称
    venue = paper.get('venue')
    if venue:
        # 尝试判断是期刊还是会议
        if any('Journal' in pt for pt in pub_types):
            ris_lines.append(f"JO  - {venue}")
        elif any('Conference' in pt for pt in pub_types):
            ris_lines.append(f"C2  - {venue}")  # Conference name
        else:
            ris_lines.append(f"JA  - {venue}")  # Alternate journal name
    
    # 卷号、期号、页码（Semantic Scholar API可能不提供这些详细信息）
    # 这里留空或尝试从其他字段获取
    
    # 摘要
    abstract = paper.get('abstract')
    if abstract:
        ris_lines.append(f"AB  - {abstract}")
    
    # DOI
    doi = paper.get('doi')
    if doi:
        ris_lines.append(f"DO  - {doi}")
    
    # URL
    url = paper.get('url')
    if url:
        ris_lines.append(f"UR  - {url}")
    
    # 标记记录结束
    ris_lines.append("ER  -")
    
    return '\n'.join(ris_lines)

def export_to_ris(papers, output_file):
    """将论文列表导出为RIS文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, paper in enumerate(papers):
                ris_entry = convert_to_ris_entry(paper)
                f.write(ris_entry)
                if i < len(papers) - 1:  # 不是最后一条记录添加空行
                    f.write('\n\n')
        print(f"成功导出 {len(papers)} 条记录到 '{output_file}'")
    except Exception as e:
        print(f"错误: 写入RIS文件时出错: {e}")
        sys.exit(1)

def main():
    """主函数"""
    input_file, output_file = parse_arguments()
    
    # 加载数据
    data = load_json_data(input_file)
    
    # 处理不同的数据结构
    papers = []
    if isinstance(data, list):
        papers = data
    elif isinstance(data, dict):
        # 可能是带有data字段的API响应
        papers = data.get('data', [])
        if not papers:
            # 或者直接是单篇论文
            papers = [data]
    else:
        print("错误: 不支持的数据格式")
        sys.exit(1)
    
    if not papers:
        print("警告: 没有找到可导出的论文数据")
        # 仍然创建空文件
        open(output_file, 'w').close()
        return
    
    # 导出为RIS
    export_to_ris(papers, output_file)

if __name__ == "__main__":
    main()