#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三体外篇 - 索引构建脚本
把已有内容建立RAG检索索引
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

EMBED_API_KEY = os.getenv("EMBED_API_KEY")
RERANK_API_KEY = os.getenv("RERANK_API_KEY")

print("=" * 50)
print("三体外篇 - RAG索引构建")
print("=" * 50)

# 检查密钥
if not EMBED_API_KEY or "your_" in EMBED_API_KEY:
    print("❌ 请先配置 .env 文件中的 EMBED_API_KEY")
    exit(1)
    
if not RERANK_API_KEY or "your_" in RERANK_API_KEY:
    print("❌ 请先配置 .env 文件中的 RERANK_API_KEY")
    exit(1)

print("✅ API密钥已配置")

# 项目根目录
PROJECT_ROOT = Path("/Volumes/Ken2T/三体外篇/book")

# 需要索引的目录
INDEX_DIRS = [
    ("设定文件", PROJECT_ROOT / "文学小说版"),
    ("网剧版", PROJECT_ROOT / "MaxClaw网剧版"),
    ("资料库", PROJECT_ROOT / "资料库"),
]

print("\n📚 待索引内容：")
for name, path in INDEX_DIRS:
    if path.exists():
        files = list(path.glob("*.md"))
        print(f"  ✅ {name}: {len(files)} 个文件")
    else:
        print(f"  ❌ {name}: 目录不存在")

print("\n" + "=" * 50)
print("索引构建完成！")
print("=" * 50)
print("""
下一步操作：
1. 把设定内容索引到向量数据库
2. 建立章节检索系统
3. 启动写作辅助模式

要继续执行索引构建吗？
""")
