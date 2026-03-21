# 智能体说明 (AGENTS.md)

> 本项目集成 webnovel-writer 长篇写作系统，使用多个智能体协同工作

---

## 🤖 智能体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      写作流程智能体协同                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                               │
│  │ context-agent│ → 搜集上下文，生成创作执行包                  │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  写作流程   │ → 生成章节正文                                 │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    审查智能体群                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │   │
│  │  │consistency- │ │continuity-  │ │  ooc-       │       │   │
│  │  │ checker     │ │ checker     │ │ checker     │       │   │
│  │  │ 一致性检查  │ │ 连贯性检查  │ │ OOC检查     │       │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │   │
│  │  │ pacing-     │ │ high-point- │ │ reader-pull-│       │   │
│  │  │ checker     │ │ checker     │ │ checker     │       │   │
│  │  │ 节奏检查    │ │ 爽点检查    │ │ 追读力检查  │       │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  data-agent │ → 提取实体、场景切片、索引构建                │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 智能体清单

### 核心智能体

| 智能体 | 文件路径 | 功能 |
|-------|---------|------|
| **context-agent** | `.qoder/agents/context-agent.md` | 上下文搜集，生成创作执行包 |
| **data-agent** | `.qoder/agents/data-agent.md` | 数据处理，实体提取，索引构建 |

### 审查智能体

| 智能体 | 文件路径 | 检查内容 |
|-------|---------|---------|
| **consistency-checker** | `.qoder/agents/consistency-checker.md` | 设定一致性检查 |
| **continuity-checker** | `.qoder/agents/continuity-checker.md` | 前后连贯性检查 |
| **ooc-checker** | `.qoder/agents/ooc-checker.md` | 人物OOC检查 |
| **pacing-checker** | `.qoder/agents/pacing-checker.md` | 节奏控制检查 |
| **high-point-checker** | `.qoder/agents/high-point-checker.md` | 爽点密度检查 |
| **reader-pull-checker** | `.qoder/agents/reader-pull-checker.md` | 追读力检查 |

---

## 🔍 智能体详细说明

### context-agent（上下文搜集）

**功能**：在写作前搜集所有必要的上下文信息

**输入**：
- 章节号
- 项目根目录
- 状态文件路径

**输出**：
- 7板块任务书（目标/冲突/承接/角色/场景约束/伏笔/追读力）
- Context Contract（目标/阻力/代价/本章变化/未闭合问题/开头类型/情绪节奏/信息密度/过渡章判定/追读力设计）
- Step 2A可直接消费的"写作执行包"

**调用方式**：
```
Task(subagent_type="context-agent", prompt="chapter=1, project_root=...")
```

---

### consistency-checker（一致性检查）

**功能**：检查章节与设定的一致性

**检查项**：
- 世界观设定是否一致
- 人物设定是否一致
- 技术设定是否一致
- 时间线是否一致

**输出格式**：
```json
{
  "issues": [
    {
      "type": "设定冲突",
      "severity": "critical",
      "description": "问题描述",
      "location": "位置",
      "suggestion": "修复建议"
    }
  ],
  "overall_score": 85
}
```

---

### continuity-checker（连贯性检查）

**功能**：检查章节与前文的连贯性

**检查项**：
- 伏笔回收是否完整
- 情节衔接是否自然
- 人物行为是否合理
- 时间线是否连贯

---

### ooc-checker（OOC检查）

**功能**：检查人物是否OOC（Out of Character）

**检查项**：
- 对话风格是否符合人物性格
- 行为动机是否符合人物设定
- 情感反应是否符合人物特点
- 决策逻辑是否符合人物背景

---

### pacing-checker（节奏检查）

**功能**：检查章节节奏控制

**检查项**：
- 信息密度是否合理
- 情节推进是否流畅
- 高潮节奏是否到位
- 过渡是否自然

---

### high-point-checker（爽点检查）

**功能**：检查爽点密度和分布

**检查项**：
- 爽点数量是否足够
- 爽点分布是否均匀
- 爽点类型是否多样
- 爽点兑现是否完整

**爽点类型**：
- 迪化误解
- 身份掉马
- 打脸反转
- 实力展示
- 智商碾压

---

### reader-pull-checker（追读力检查）

**功能**：检查追读力设计

**检查项**：
- 钩子设计是否有效
- 微兑现是否到位
- 约束分层是否合理
- 债务追踪是否完整

---

### data-agent（数据处理）

**功能**：写作后数据处理

**子步骤**：
- A. 加载上下文
- B. AI实体提取
- C. 实体消歧
- D. 写入state/index
- E. 写入章节摘要
- F. AI场景切片
- G. RAG向量索引
- H. 风格样本评估
- I. 债务利息（默认跳过）

---

## 🎯 智能体调用流程

### 写作流程
```
/webnovel-write 1
  ↓
Step 1: context-agent（上下文搜集）
  ↓
Step 2A: 正文起草
  ↓
Step 2B: 风格适配（可选）
  ↓
Step 3: 审查智能体群（并行）
  ├── consistency-checker
  ├── continuity-checker
  ├── ooc-checker
  ├── pacing-checker（条件）
  ├── high-point-checker（条件）
  └── reader-pull-checker（条件）
  ↓
Step 4: 润色修复
  ↓
Step 5: data-agent（数据回写）
  ↓
Step 6: Git备份
```

---

## ⚙️ 智能体配置

### 模型配置

默认配置：
```yaml
model: inherit
```

表示继承当前Claude会话所用模型。

可配置值：
- `inherit`：继承父会话模型
- `sonnet`：使用Sonnet模型
- `opus`：使用Opus模型
- `haiku`：使用Haiku模型

### 工具配置

```yaml
allowed-tools: Read, Grep, Bash, Task
```

---

## 📝 扩展智能体

如需添加新的检查智能体：

1. 在 `.qoder/agents/` 创建新的 `.md` 文件
2. 添加frontmatter配置：
```yaml
---
name: new-checker
description: 新检查器描述
tools: Read, Grep
model: inherit
---
```
3. 编写检查逻辑
4. 在 `webnovel-write` 的 Step 3 中添加调用

---

**版本**：v1.0
**更新日期**：2026-03-20
