#!/usr/bin/env python3
"""
Semantic Scholar Search Script
使用 Semantic Scholar API 进行学术文献检索的 Python 脚本
"""

import requests
import json
import time
import sys
from typing import List, Dict, Optional

# Semantic Scholar API 基础URL
BASE_URL = "https://api.semanticscholar.org/graph/v1"

def search_papers(query: str, limit: int = 10, fields: List[str] = None) -> List[Dict]:
    """
    搜索论文
    
    Args:
        query: 搜索关键词
        limit: 返回结果数量限制
        fields: 需要返回的字段列表
    
    Returns:
        论文列表
    """
    if fields is None:
        fields = ["title", "venue", "year", "authors", "abstract", "citationCount", "url"]
    
    # 构建请求参数
    params = {
        "query": query,
        "limit": limit,
        "fields": ",".join(fields)
    }
    
    # 发送请求
    response = requests.get(f"{BASE_URL}/paper/search", params=params)
    
    if response.status_code != 200:
        print(f"错误: API请求失败，状态码 {response.status_code}")
        print(response.text)
        return []
    
    data = response.json()
    return data.get("data", [])

def get_paper_details(paper_id: str, fields: List[str] = None) -> Optional[Dict]:
    """
    获取单篇论文的详细信息
    
    Args:
        paper_id: 论文ID（Semantic Scholar ID或DOI等）
        fields: 需要返回的字段列表
    
    Returns:
        论文详情或None
    """
    if fields is None:
        fields = ["title", "venue", "year", "authors", "abstract", "citationCount", 
                  "references", "citations", "url", "doi", "publicationTypes"]
    
    response = requests.get(f"{BASE_URL}/paper/{paper_id}", params={"fields": ",".join(fields)})
    
    if response.status_code != 200:
        print(f"错误: 获取论文详情失败，状态码 {response.status_code}")
        return None
    
    return response.json()

def format_results(papers: List[Dict]) -> None:
    """
    格式化输出搜索结果
    
    Args:
        papers: 论文列表
    """
    if not papers:
        print("未找到相关论文")
        return
    
    print(f"找到 {len(papers)} 篇相关论文:\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.get('title', '无标题')}")
        
        # 作者信息
        authors = paper.get('authors', [])
        if authors:
            author_names = [author.get('name', '') for author in authors if author.get('name')]
            print(f"   作者: {', '.join(author_names[:3])}{'等' if len(author_names) > 3 else ''}")
        
        # 发表信息
        venue = paper.get('venue', '未知期刊/会议')
        year = paper.get('year', '未知年份')
        print(f"   发表: {venue} ({year})")
        
        # 引用次数
        citations = paper.get('citationCount', 0)
        print(f"   引用次数: {citations}")
        
        # 摘要（截断显示）
        abstract = paper.get('abstract', '')
        if abstract:
            abstract_preview = abstract[:200] + ('...' if len(abstract) > 200 else '')
            print(f"   摘要: {abstract_preview}")
        
        # URL和DOI
        url = paper.get('url', '')
        doi = paper.get('doi', '')
        if url:
            print(f"   链接: {url}")
        if doi:
            print(f"   DOI: {doi}")
        
        print()

def save_to_json(papers: List[Dict], filename: str) -> None:
    """
    保存结果为JSON文件
    
    Args:
        papers: 论文列表
        filename: 文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python semantic_scholar_search.py <搜索关键词> [结果数量]")
        print("示例: python semantic_scholar_search.py \"machine learning medical imaging\" 20")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"正在使用Semantic Scholar API搜索: '{query}'")
    print(f"请求返回前 {limit} 条结果...\n")
    
    papers = search_papers(query, limit=limit)
    format_results(papers)
    
    # 可选：保存结果
    save_option = input("是否保存结果到JSON文件？(y/n): ").lower().strip()
    if save_option == 'y':
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"semantic_scholar_results_{timestamp}.json"
        save_to_json(papers, filename)

if __name__ == "__main__":
    main()