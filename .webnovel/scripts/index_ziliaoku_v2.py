#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资料库RAG索引构建脚本（同步版本）
将资料库内容索引到向量数据库供写作时检索
"""

import os
import sys
import json
import asyncio
import ssl
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiohttp
import certifi

# 添加脚本目录到路径
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_compat import enable_windows_utf8_stdio
from data_modules.config import DataModulesConfig


# 资料库目录
PROJECT_ROOT = Path("/Volumes/Ken2T/三体外篇/book")
ZILIAOKU_ROOT = PROJECT_ROOT / "资料库"


def load_markdown_file(file_path: Path) -> str:
    """读取Markdown文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"  ⚠️ 读取失败: {file_path.name} - {e}")
        return ""


def split_content_into_chunks(content: str, source_name: str, max_chunk_size: int = 2000) -> List[Dict[str, Any]]:
    """将内容分割成适合检索的块"""
    chunks = []
    sections = content.split("\n## ")
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
            
        if i == 0 and section.startswith("# "):
            lines = section.split("\n")
            title = lines[0].replace("# ", "").strip()
            section_content = "\n".join(lines[1:]).strip()
        else:
            lines = section.split("\n")
            title = lines[0].strip() if lines else f"段落{i}"
            section_content = section.strip()
        
        if len(section_content) > max_chunk_size:
            paragraphs = section_content.split("\n\n")
            current_chunk = ""
            chunk_index = 0
            
            for para in paragraphs:
                if len(current_chunk) + len(para) > max_chunk_size:
                    if current_chunk:
                        chunks.append({
                            "content": current_chunk.strip(),
                            "title": f"{title} (第{chunk_index + 1}部分)",
                            "source": source_name
                        })
                        chunk_index += 1
                        current_chunk = para
                    else:
                        chunks.append({
                            "content": para.strip(),
                            "title": title,
                            "source": source_name
                        })
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
            
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "title": f"{title} (第{chunk_index + 1}部分)" if chunk_index > 0 else title,
                    "source": source_name
                })
        else:
            chunks.append({
                "content": section_content,
                "title": title,
                "source": source_name
            })
    
    return chunks


async def get_embeddings_batch(texts: List[str], config: DataModulesConfig) -> List[Optional[List[float]]]:
    """获取文本的embedding向量"""
    if not texts:
        return []
    
    # 创建SSL上下文
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(limit=64, ssl=ssl_context)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.embed_api_key}"
    }
    
    url = f"{config.embed_base_url.rstrip('/')}/embeddings"
    if not url.endswith("/embeddings"):
        if url.endswith("/v1"):
            url = f"{url}/embeddings"
        else:
            url = f"{url}/v1/embeddings"
    
    all_embeddings: List[Optional[List[float]]] = []
    batch_size = config.embed_batch_size
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            payload = {
                "model": config.embed_model,
                "input": batch
            }
            
            try:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "data" in data:
                            sorted_data = sorted(data["data"], key=lambda x: x.get("index", 0))
                            all_embeddings.extend([item["embedding"] for item in sorted_data])
                            print(f"  ✅ 批次 {i // batch_size + 1}: {len(batch)} 条成功")
                        else:
                            all_embeddings.extend([None] * len(batch))
                            print(f"  ⚠️ 批次 {i // batch_size + 1}: 响应格式错误")
                    else:
                        err_text = await resp.text()
                        all_embeddings.extend([None] * len(batch))
                        print(f"  ❌ 批次 {i // batch_size + 1}: HTTP {resp.status} - {err_text[:200]}")
            except Exception as e:
                all_embeddings.extend([None] * len(batch))
                print(f"  ❌ 批次 {i // batch_size + 1}: {e}")
    
    return all_embeddings


def store_chunks_to_db(chunks: List[Dict], embeddings: List[Optional[List[float]]], db_path: Path) -> int:
    """存储chunks和embeddings到数据库"""
    import sqlite3
    import struct
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 确保表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            chunk_id TEXT PRIMARY KEY,
            chapter INTEGER,
            scene_index INTEGER,
            content TEXT,
            embedding BLOB,
            parent_chunk_id TEXT,
            chunk_type TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    stored = 0
    skipped = 0
    
    for chunk, embedding in zip(chunks, embeddings):
        chunk_id = chunk.get("chunk_id")
        
        if embedding is None:
            skipped += 1
            continue
        
        embedding_bytes = struct.pack(f"{len(embedding)}f", *embedding)
        
        cursor.execute("""
            INSERT OR REPLACE INTO vectors
            (chunk_id, chapter, scene_index, content, embedding, parent_chunk_id, chunk_type, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk_id,
            chunk["chapter"],
            chunk.get("scene_index", 0),
            chunk.get("content", ""),
            embedding_bytes,
            chunk.get("parent_chunk_id"),
            chunk.get("chunk_type", "reference"),
            chunk.get("source_file", ""),
        ))
        stored += 1
    
    conn.commit()
    conn.close()
    
    return stored, skipped


def index_ziliaoku():
    """索引资料库内容"""
    print("=" * 60)
    print("📚 资料库RAG索引构建（同步版本）")
    print("=" * 60)
    
    # 初始化配置
    config = DataModulesConfig.from_project_root(PROJECT_ROOT)
    config.ensure_dirs()
    
    # 检查API密钥
    if not config.embed_api_key:
        print("❌ 未配置EMBED_API_KEY，请检查.env文件")
        return
    
    print(f"\n🔧 API配置:")
    print(f"  - Base URL: {config.embed_base_url}")
    print(f"  - Model: {config.embed_model}")
    
    # 收集所有资料库文件
    all_files = []
    
    categories = ["道德经", "心经", "金刚经", "三体原著", "简史三部曲", "AI知识科普", "StudyMate"]
    for category in categories:
        cat_dir = ZILIAOKU_ROOT / category
        if cat_dir.exists():
            for f in cat_dir.glob("*.md"):
                all_files.append((category, f))
    
    print(f"\n📚 发现 {len(all_files)} 个资料文件")
    
    # 处理每个文件
    all_chunks = []
    chunk_id_counter = 0
    
    for category, file_path in all_files:
        print(f"\n📄 处理: [{category}] {file_path.name}")
        content = load_markdown_file(file_path)
        
        if not content:
            continue
        
        chunks = split_content_into_chunks(content, f"{category}/{file_path.stem}")
        
        for chunk in chunks:
            chunk_id_counter += 1
            all_chunks.append({
                "chunk_id": f"ziliao_{chunk_id_counter:04d}",
                "chapter": 0,
                "scene_index": chunk_id_counter,
                "content": f"【{category}】{chunk['title']}\n\n{chunk['content']}",
                "chunk_type": "reference",
                "source_file": chunk['source']
            })
        
        print(f"  ✅ 生成 {len(chunks)} 个检索块")
    
    print(f"\n📊 总计 {len(all_chunks)} 个检索块")
    
    if not all_chunks:
        print("❌ 没有内容需要索引")
        return
    
    # 获取embeddings
    print("\n🔄 正在获取向量嵌入...")
    contents = [c.get("content", "") for c in all_chunks]
    
    embeddings = asyncio.run(get_embeddings_batch(contents, config))
    
    # 统计成功数量
    success_count = sum(1 for e in embeddings if e is not None)
    print(f"\n📈 嵌入统计: {success_count}/{len(embeddings)} 成功")
    
    # 存储到数据库
    print("\n💾 正在存储到数据库...")
    db_path = config.webnovel_dir / "vectors.db"
    stored, skipped = store_chunks_to_db(all_chunks, embeddings, db_path)
    
    print(f"\n✅ 索引完成!")
    print(f"  - 存储: {stored} 条")
    print(f"  - 跳过: {skipped} 条")
    
    # 验证
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vectors")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"  - 数据库总记录: {count} 条")
    
    print("\n" + "=" * 60)
    print("✅ 资料库索引构建完成！")
    print("=" * 60)


if __name__ == "__main__":
    enable_windows_utf8_stdio(skip_in_pytest=True)
    index_ziliaoku()
