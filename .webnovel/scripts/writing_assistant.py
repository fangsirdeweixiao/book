#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三体外篇 - AI写作助手
在写作时检索相关设定，保证内容一致性
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API配置
EMBED_API_KEY = os.getenv("EMBED_API_KEY")
RERANK_API_KEY = os.getenv("RERANK_API_KEY")
EMBED_URL = "https://api.jina.ai/v1/embeddings"
RERANK_URL = "https://api.jina.ai/v1/rerank"

PROJECT_ROOT = Path("/Volumes/Ken2T/三体外篇/book")

def get_embedding(text: str) -> list:
    """获取文本向量"""
    response = requests.post(
        EMBED_URL,
        headers={"Authorization": f"Bearer {EMBED_API_KEY}"},
        json={"model": "jina-embeddings-v3", "input": [text]}
    )
    return response.json()["data"][0]["embedding"]

def rerank(query: str, documents: list) -> list:
    """重排检索结果"""
    response = requests.post(
        RERANK_URL,
        headers={"Authorization": f"Bearer {RERANK_API_KEY}"},
        json={
            "model": "jina-reranker-v3",
            "query": query,
            "documents": documents,
            "top_n": 5
        }
    )
    return response.json()["results"]

def search_context(query: str, max_results: int = 5) -> list:
    """检索相关设定和章节"""
    # 获取查询向量
    query_embedding = get_embedding(query)
    
    # 读取所有设定文件
    results = []
    for md_file in PROJECT_ROOT.glob("文学小说版/*.md"):
        if md_file.name.startswith("00-"):
            continue  # 跳过大纲
        
        content = md_file.read_text(encoding="utf-8")
        # 提取前500字作为摘要
        summary = content[:500].replace("\n", " ")
        
        results.append({
            "file": md_file.name,
            "summary": summary,
            "content": content
        })
    
    # 用重排模型排序
    docs = [r["summary"] for r in results]
    reranked = rerank(query, docs)
    
    # 返回排序后的结果
    sorted_results = []
    for r in reranked[:max_results]:
        idx = r["index"]
        sorted_results.append({
            "file": results[idx]["file"],
            "score": r["relevance_score"],
            "summary": results[idx]["summary"][:200]
        })
    
    return sorted_results

def main():
    print("""
╔══════════════════════════════════════════════════════╗
║     三体外篇 - AI写作助手                            ║
║     《智脑纪元：暗子降临》创作支持系统               ║
╚══════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📝 请输入你想查询的内容（输入 q 退出）：")
        query = input("> ").strip()
        
        if query.lower() == "q":
            print("\n👋 再见！祝你创作愉快！")
            break
        
        if not query:
            continue
        
        print("\n🔍 正在检索相关设定...")
        results = search_context(query)
        
        print(f"\n📚 找到 {len(results)} 个相关结果：\n")
        for i, r in enumerate(results, 1):
            print(f"【{i}】{r['file']}")
            print(f"    相关度: {r['score']:.2f}")
            print(f"    摘要: {r['summary']}...")
            print()

if __name__ == "__main__":
    main()
