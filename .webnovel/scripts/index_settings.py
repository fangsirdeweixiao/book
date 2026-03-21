#!/usr/bin/env python3
"""索引核心设定集到RAG数据库"""

import os
import sys
import json
import sqlite3
import requests
from pathlib import Path

# 添加脚本目录到路径
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_compat import enable_windows_utf8_stdio
from data_modules.config import DataModulesConfig, _load_dotenv

# 加载.env配置
_load_dotenv()

def get_embeddings(texts, config):
    """获取向量嵌入"""
    headers = {
        "Authorization": f"Bearer {config.embed_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": config.embed_model,
        "input": texts,
        "task": "retrieval.passage"
    }
    
    resp = requests.post(
        f"{config.embed_base_url}/embeddings",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if resp.status_code != 200:
        raise Exception(f"API错误: {resp.status_code} - {resp.text}")
    
    result = resp.json()
    return [d["embedding"] for d in result["data"]]

def main():
    print("=" * 60)
    print("📚 核心设定集RAG索引构建")
    print("=" * 60)
    
    # 加载配置
    config = DataModulesConfig.from_project_root(Path("/Volumes/Ken2T/三体外篇/book"))
    
    if not config.embed_api_key:
        print("❌ 未配置EMBED_API_KEY，请检查.env文件")
        return
    
    # 项目根目录
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent  # scripts的上一级
    settings_file = project_root / "核心设定集.md"
    db_path = project_root / "index.db"
    
    if not os.path.exists(settings_file):
        print(f"❌ 找不到设定文件: {settings_file}")
        return
    
    # 读取设定文件
    with open(settings_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 分块
    lines = content.split("\n")
    chunks = []
    current_chunk = []
    current_title = "引言"
    
    for line in lines:
        if line.startswith("## "):
            if current_chunk:
                chunks.append({
                    "title": current_title,
                    "content": "\n".join(current_chunk)
                })
            current_title = line[3:].strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    if current_chunk:
        chunks.append({
            "title": current_title,
            "content": "\n".join(current_chunk)
        })
    
    print(f"\n📄 发现 {len(chunks)} 个设定区块")
    
    # 获取嵌入
    print("\n🔄 正在获取向量嵌入...")
    texts = [c["content"] for c in chunks]
    embeddings = get_embeddings(texts, config)
    print(f"  ✅ 获取 {len(embeddings)} 个嵌入")
    
    # 存储到数据库
    print("\n💾 正在存储到数据库...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 清空旧数据
    cursor.execute("DELETE FROM settings_index")
    
    # 插入新数据
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        cursor.execute(
            "INSERT INTO settings_index (title, content, embedding) VALUES (?, ?, ?)",
            (chunk["title"], chunk["content"], json.dumps(embedding))
        )
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 索引完成! 存储 {len(chunks)} 条设定")
    print("=" * 60)

if __name__ == "__main__":
    main()
