#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资料库RAG索引构建脚本
将资料库内容索引到向量数据库供写作时检索
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# 添加脚本目录到路径
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_compat import enable_windows_utf8_stdio
from data_modules.config import DataModulesConfig
from data_modules.rag_adapter import RAGAdapter


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
    """
    将内容分割成适合检索的块
    
    策略：
    1. 按章节标题（##）分割
    2. 每块不超过max_chunk_size字符
    """
    chunks = []
    
    # 按二级标题分割
    sections = content.split("\n## ")
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
            
        # 如果是第一个section，可能包含一级标题
        if i == 0 and section.startswith("# "):
            # 提取一级标题
            lines = section.split("\n")
            title = lines[0].replace("# ", "").strip()
            section_content = "\n".join(lines[1:]).strip()
        else:
            # 提取二级标题
            lines = section.split("\n")
            title = lines[0].strip() if lines else f"段落{i}"
            section_content = section.strip()
        
        # 如果内容太长，进一步分割
        if len(section_content) > max_chunk_size:
            # 按段落分割
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
                        # 单个段落就超长，直接作为一个块
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


def index_ziliaoku():
    """索引资料库内容"""
    print("=" * 60)
    print("📚 资料库RAG索引构建")
    print("=" * 60)
    
    # 初始化配置
    config = DataModulesConfig.from_project_root(PROJECT_ROOT)
    config.ensure_dirs()
    
    # 初始化RAG适配器
    adapter = RAGAdapter(config)
    
    # 检查API连接
    print("\n🔍 检查API连接...")
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            test_result = loop.run_until_complete(adapter.api_client.embed(["测试连接"]))
            if test_result:
                print("  ✅ Embedding API连接成功")
            else:
                print("  ⚠️ Embedding API返回空结果，可能需要检查API密钥")
        finally:
            loop.close()
    except Exception as e:
        print(f"  ❌ API连接失败: {e}")
        print("  提示：请检查.env文件中的EMBED_API_KEY配置")
        return
    
    # 收集所有资料库文件
    all_files = []
    
    # 道德经
    daodejing_dir = ZILIAOKU_ROOT / "道德经"
    if daodejing_dir.exists():
        for f in daodejing_dir.glob("*.md"):
            all_files.append(("道德经", f))
    
    # 心经
    xinjing_dir = ZILIAOKU_ROOT / "心经"
    if xinjing_dir.exists():
        for f in xinjing_dir.glob("*.md"):
            all_files.append(("心经", f))
    
    # 金刚经
    jingangjing_dir = ZILIAOKU_ROOT / "金刚经"
    if jingangjing_dir.exists():
        for f in jingangjing_dir.glob("*.md"):
            all_files.append(("金刚经", f))
    
    # 三体原著
    santi_dir = ZILIAOKU_ROOT / "三体原著"
    if santi_dir.exists():
        for f in santi_dir.glob("*.md"):
            all_files.append(("三体原著", f))
    
    # 简史三部曲
    jianshi_dir = ZILIAOKU_ROOT / "简史三部曲"
    if jianshi_dir.exists():
        for f in jianshi_dir.glob("*.md"):
            all_files.append(("简史三部曲", f))
    
    # AI知识科普
    ai_dir = ZILIAOKU_ROOT / "AI知识科普"
    if ai_dir.exists():
        for f in ai_dir.glob("*.md"):
            all_files.append(("AI知识科普", f))
    
    # StudyMate
    studymate_dir = ZILIAOKU_ROOT / "StudyMate"
    if studymate_dir.exists():
        for f in studymate_dir.glob("*.md"):
            all_files.append(("StudyMate", f))
    
    print(f"\n📚 发现 {len(all_files)} 个资料文件")
    
    # 处理每个文件
    all_chunks = []
    chunk_id_counter = 0
    
    for category, file_path in all_files:
        print(f"\n📄 处理: [{category}] {file_path.name}")
        content = load_markdown_file(file_path)
        
        if not content:
            continue
        
        # 分割成块
        chunks = split_content_into_chunks(content, f"{category}/{file_path.stem}")
        
        for chunk in chunks:
            chunk_id_counter += 1
            all_chunks.append({
                "chunk_id": f"ziliao_{chunk_id_counter:04d}",
                "chapter": 0,  # 资料库用chapter=0标识
                "scene_index": chunk_id_counter,
                "content": f"【{category}】{chunk['title']}\n\n{chunk['content']}",
                "chunk_type": "reference",
                "source_file": chunk['source']
            })
        
        print(f"  ✅ 生成 {len(chunks)} 个检索块")
    
    print(f"\n📊 总计 {len(all_chunks)} 个检索块")
    
    # 存储到向量数据库
    if all_chunks:
        print("\n🔄 正在建立向量索引...")
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                stored = loop.run_until_complete(adapter.store_chunks(all_chunks))
                print(f"  ✅ 成功索引 {stored} 个块")
            finally:
                loop.close()
            
            # 显示统计
            stats = adapter.get_stats()
            print(f"\n📈 索引统计:")
            print(f"  - 向量数: {stats.get('vectors', 0)}")
            print(f"  - 词汇数: {stats.get('terms', 0)}")
            
        except Exception as e:
            print(f"  ❌ 索引失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 资料库索引构建完成！")
    print("=" * 60)


if __name__ == "__main__":
    enable_windows_utf8_stdio(skip_in_pytest=True)
    index_ziliaoku()
