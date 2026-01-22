---
name: write-article
description: 多智能体协作的微信公众号文章写作工具。支持「创作」和「仿写」两种模式。当用户说"写一篇文章"、"帮我写公众号"、"生成文章"时使用。
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Task, AskUserQuestion
---

# 微信公众号文章写作助手（多智能体协作版）

## 概述

这是一个多智能体协作的微信公众号文章写作工具，支持两种核心模式：
- **创作模式**：提供主题和内容描述，AI 自主调研并创作
- **仿写模式**：提供参考文章 URL，模仿风格进行创作

## 可用 Agent

| Agent | 职责 | 模型 |
|-------|------|------|
| prompt-optimizer-agent | 基于四块模式优化各 Agent 提示词 | opus |
| research-agent | 搜索、抓取、整理资料 | opus |
| tech-writer-agent | 技术开发者视角写作 | opus |
| pm-writer-agent | AI 产品经理视角写作 | opus |
| ai-news-writer-agent | AI 行业观察者视角写作 | opus |
| tutorial-writer-agent | AI 教程作者视角写作 | opus |
| image-generator-agent | 生成文章配图（封面图、结构图、概念图等），支持 Gemini 和即梦 AI | opus |

## 执行流程

### Step 1: 选择写作模式（核心分支）

**问题 1：写作模式**

```json
{
  "question": "请选择写作模式",
  "header": "写作模式",
  "options": [
    {
      "label": "✨ 创作模式（推荐）",
      "description": "提供主题和内容描述，AI 自主调研并创作原创文章"
    },
    {
      "label": "🔄 仿写模式",
      "description": "提供参考文章 URL，分析风格后模仿创作新内容"
    }
  ],
  "multiSelect": false
}
```

---

## 分支 A：创作模式

当用户选择「创作模式」时，收集以下信息：

### A.1 写作角度

```json
{
  "question": "请选择写作角度",
  "header": "写作角度",
  "options": [
    {
      "label": "🔧 技术开发者",
      "description": "代码实现、技术原理、开发教程，适合技术深度文章"
    },
    {
      "label": "📊 AI 产品经理",
      "description": "产品拆解、场景方案、效率提升，适合产品分析文章"
    },
    {
      "label": "📰 AI 行业观察者",
      "description": "新闻解读、趋势分析、观点评论，适合行业动态文章"
    },
    {
      "label": "📚 AI 教程作者",
      "description": "入门指南、实操教程、最佳实践，适合零基础教学"
    }
  ],
  "multiSelect": false
}
```

### A.2 主题类型

```json
{
  "question": "请选择写作主题类型",
  "header": "主题类型",
  "options": [
    {
      "label": "🤖 AI 大模型",
      "description": "Claude、GPT、Gemini、Llama 等模型介绍/对比/评测"
    },
    {
      "label": "🛠️ AI 开发工具",
      "description": "Claude Code、Cursor、Copilot、Dify、LangChain 等"
    },
    {
      "label": "📱 AI 产品体验",
      "description": "Perplexity、NotebookLM、Midjourney、Suno 等"
    },
    {
      "label": "🔬 AI 技术原理",
      "description": "RAG、Agent、MCP、Prompt Engineering、Fine-tuning"
    },
    {
      "label": "📈 AI 行业动态",
      "description": "融资新闻、产品发布、政策法规、行业趋势分析"
    },
    {
      "label": "💼 AI 应用场景",
      "description": "办公提效、内容创作、代码开发、客服自动化等"
    },
    {
      "label": "🎓 AI 入门教程",
      "description": "零基础入门、工具使用指南、新手快速上手"
    }
  ],
  "multiSelect": false
}
```

### A.3 内容描述（文本输入）

询问用户提供详细的内容描述：

```markdown
请描述您想要创作的文章内容，包括：

1. **文章主题**：您想写什么？
   例如："Claude Code 入门教程"、"Cursor vs Windsurf 对比评测"

2. **核心要点**：文章应该覆盖哪些内容？
   例如："安装配置、基础使用、进阶技巧、常见问题"

3. **目标读者**：这篇文章是写给谁看的？
   例如："有一定编程基础的开发者"、"完全零基础的新手"

4. **特殊要求**（可选）：
   例如："需要包含代码示例"、"重点对比性能差异"、"突出实战案例"

---
示例输入：
"写一篇 Claude Code 的入门教程，面向有 VS Code 使用经验的开发者，
重点介绍安装配置、常用命令、MCP 配置，最好有实际的代码示例"
```

### A.4 创作模式执行计划

```markdown
## Execution Plan (创作模式)

### 输入信息
- 写作模式: 创作
- 写作角度: {角度}
- 主题类型: {类型}
- 内容描述: {用户输入的描述}

### Agent 调度（完全串行）
Step 1: prompt-optimizer → research-agent (调研)
    ↓
Step 2: prompt-optimizer → [writer-agent] (写作)
    ↓
Step 3: 分析文章内容，确定需要的图片（最多 6 张）
    ↓
Step 4: 按需生成图片（每张图片前都调用 prompt-optimizer）
    - 封面图、结构图、概念图、场景图等
    - 根据文章实际需求智能判断
    - 按优先级串行生成，总数不超过 6 张
    - 默认使用 Gemini，可配置使用即梦 AI
    ↓
Step 5: 输出 Markdown 文件
```

---

## 分支 B：仿写模式

当用户选择「仿写模式」时，收集以下信息：

### B.1 参考文章 URL（必填）

```markdown
请提供参考文章的 URL：

系统将分析该文章的：
- 写作风格（语气、人称、句式）
- 内容结构（章节安排、逻辑顺序）
- 表达特点（专业程度、案例使用方式）

---
支持的来源：
- 微信公众号文章
- 技术博客（掘金、CSDN、Medium 等）
- 知乎专栏/回答
- 其他可访问的网页

示例：
https://mp.weixin.qq.com/s/xxxxxx
```

### B.2 仿写任务类型

```json
{
  "question": "请选择仿写任务类型",
  "header": "仿写类型",
  "options": [
    {
      "label": "📝 模仿风格写新主题",
      "description": "保留参考文章的风格，但写一个全新的主题"
    },
    {
      "label": "🔄 改写/重写",
      "description": "用自己的话重新表达参考文章的内容"
    },
    {
      "label": "🌐 翻译+本土化",
      "description": "翻译外文文章并进行本土化适配"
    },
    {
      "label": "📈 扩展/深化",
      "description": "在参考文章基础上扩展内容或深入分析"
    }
  ],
  "multiSelect": false
}
```

### B.3 仿写内容描述

根据仿写类型，询问不同的信息：

**类型 1：模仿风格写新主题**
```markdown
请描述您想写的新主题：

1. **新文章主题**：您想写什么？
2. **保留哪些风格特点**：
   - 语气风格（专业/轻松/幽默）
   - 内容结构（章节安排）
   - 表达方式（案例类型、代码示例风格）

示例："模仿这篇文章的风格，写一篇关于 Cursor 的入门教程"
```

**类型 2：改写/重写**
```markdown
请说明改写要求：

1. **改写目标**：为什么要改写？
   - 简化内容，降低阅读门槛
   - 调整风格，更适合特定读者
   - 更新信息，补充最新内容

2. **改写重点**：需要重点调整什么？

示例："这篇文章太技术化了，帮我改写成面向产品经理的版本"
```

**类型 3：翻译+本土化**
```markdown
请说明翻译要求：

1. **目标语言**：翻译成什么语言？（默认：中文）
2. **本土化要求**：
   - 替换不适合国内的工具/服务
   - 添加国内相关的案例
   - 调整表达方式适合国内读者

示例："翻译这篇英文教程，把 GitHub Copilot 的例子换成 Claude Code"
```

**类型 4：扩展/深化**
```markdown
请说明扩展要求：

1. **扩展方向**：想要补充什么内容？
   - 添加更多案例
   - 深入技术原理
   - 补充实战经验
   - 添加对比分析

2. **扩展篇幅**：预期增加多少内容？

示例："这篇文章只介绍了基础用法，帮我扩展进阶技巧和实战案例"
```

### B.4 仿写模式执行计划

```markdown
## Execution Plan (仿写模式)

### 输入信息
- 写作模式: 仿写
- 参考 URL: {url}
- 仿写类型: {类型}
- 仿写描述: {用户输入的描述}

### Agent 调度（完全串行）
Step 1: prompt-optimizer → research-agent (抓取并分析参考文章)
    ↓ 输出：风格分析报告 + 原文内容
Step 2: prompt-optimizer → [writer-agent] (写作)
    ↓ 输入：风格报告 + 仿写要求
Step 3: 分析文章内容，确定需要的图片（最多 6 张）
    ↓
Step 4: 按需生成图片（每张图片前都调用 prompt-optimizer）
    - 封面图、结构图、概念图、场景图等
    - 根据文章实际需求智能判断
    - 按优先级串行生成，总数不超过 6 张
    - 默认使用 Gemini，可配置使用即梦 AI
    ↓
Step 5: 输出 Markdown 文件
```

---

## Step 2: 执行 Agent 调度（完全串行）

**核心原则**：所有 Agent 串行执行，每个 Agent 执行前都先调用 prompt-optimizer-agent 进行提示词优化。

### 创作模式调度

```
Step 1: prompt-optimizer-agent → research-agent
    ↓ (等待完成，获取调研结果)
Step 2: prompt-optimizer-agent → [writer-agent]
    ↓ (等待完成，获取文章内容)
Step 3: 分析文章，确定需要的图片（最多 6 张）
    ↓
Step 4: 串行生成图片（每张图片前都优化提示词）
    按优先级逐张生成：
    - prompt-optimizer-agent → image-generator-agent (图片 1)
        ↓ (等待完成)
    - prompt-optimizer-agent → image-generator-agent (图片 2)
        ↓ (等待完成)
    - ... (根据需求列表继续，最多 6 张)
    ↓
Step 5: 输出 Markdown 文件
```

### 仿写模式调度

```
Step 1: prompt-optimizer-agent → research-agent
    ↓ (等待完成，获取风格分析 + 原文内容)
Step 2: prompt-optimizer-agent → [writer-agent]
    ↓ (等待完成，获取文章内容)
Step 3: 分析文章，确定需要的图片（最多 6 张）
    ↓
Step 4: 串行生成图片（每张图片前都优化提示词）
    按优先级逐张生成：
    - prompt-optimizer-agent → image-generator-agent (图片 1)
        ↓ (等待完成)
    - prompt-optimizer-agent → image-generator-agent (图片 2)
        ↓ (等待完成)
    - ... (根据需求列表继续，最多 6 张)
    ↓
Step 5: 输出 Markdown 文件
```

### Writer Agent 选择

| 写作角度 | Writer Agent |
|----------|--------------|
| 技术开发者 | tech-writer-agent |
| AI 产品经理 | pm-writer-agent |
| AI 行业观察者 | ai-news-writer-agent |
| AI 教程作者 | tutorial-writer-agent |

**仿写模式特殊处理**：如果用户未选择写作角度，则根据参考文章的风格自动推断合适的 Writer Agent。

### Step 3: 分析文章确定图片需求

写作完成后，分析文章内容确定需要哪些图片：

**图片数量限制**：一篇文章最多生成 **6 张图片**

```
┌─────────────────────────────────────────────────────────────────┐
│  图片需求分析                                                    │
│                                                                 │
│  根据文章实际内容，智能判断需要哪些图片：                        │
│                                                                 │
│  1. 封面图（通常必需）                                          │
│     - 根据文章标题和主题确定封面风格                            │
│                                                                 │
│  2. 结构图/流程图（根据内容判断）                               │
│     - 如果文章有清晰的层次结构、对比分析、流程步骤              │
│     - 适合用图表展示的内容                                      │
│                                                                 │
│  3. 概念图/示意图（根据内容判断）                               │
│     - 解释抽象概念时需要可视化辅助                              │
│     - 技术原理需要图解                                          │
│                                                                 │
│  4. 场景图/配图（根据内容判断）                                 │
│     - 文章中描述的应用场景                                      │
│     - 产品截图无法获取时的替代                                  │
│     - 增强阅读体验的装饰性配图                                  │
│                                                                 │
│  5. 扫描文章中的 <!-- IMAGE_NEEDED: xxx --> 标记                │
│     - 作者在写作时明确标注需要配图的位置                        │
│                                                                 │
│  判断原则：                                                      │
│  - 图片应有实际价值，不是为了配图而配图                         │
│  - 优先级：封面 > 核心概念图 > 结构图 > 场景配图                │
│  - 总数不超过 6 张                                              │
│                                                                 │
│  输出：图片需求列表（按优先级排序，最多 6 张）                  │
│  [                                                               │
│    { "type": "cover", "priority": 1, "context": "..." },        │
│    { "type": "concept", "priority": 2, "position": "...", ... },│
│    { "type": "structure", "priority": 3, "context": "..." },    │
│    ...                                                           │
│  ]                                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 图片生成降级策略

**核心原则**：图片生成失败不阻断整体流程

**图片生成工具**：默认使用 Gemini（Google Nano Banana Pro），可配置使用即梦 AI（火山引擎）

当图片生成 Agent 执行失败时：

```
┌─────────────────────────────────────────────────────────────────┐
│  图片生成失败降级处理                                            │
│                                                                 │
│  1. 记录失败原因（API 错误、超时、配额不足等）                  │
│  2. 在文章对应位置插入图片生成提示词占位：                       │
│                                                                 │
│     <!-- IMAGE_PLACEHOLDER                                      │
│     类型: 封面图/结构图/内容配图                                │
│     提示词: {生成该图片的完整 prompt}                           │
│     -->                                                         │
│                                                                 │
│  3. 继续执行下一张图片的生成                                    │
│  4. 在最终报告中汇总提示用户手动生成失败的图片                  │
└─────────────────────────────────────────────────────────────────┘
```

**占位符格式示例**：

```markdown
<!-- COVER_IMAGE_PLACEHOLDER
提示词: 生成一张微信公众号封面图，主题是"Claude Code 入门教程"，
风格：科技感、蓝紫渐变、简洁现代，尺寸 900x383px，
包含元素：代码编辑器图标、AI 助手符号、渐变背景
-->
```

```markdown
<!-- STRUCTURE_IMAGE_PLACEHOLDER
提示词: 生成一张信息结构图，展示 Claude Code 的核心功能：
1. 智能代码补全
2. 多文件编辑
3. MCP 扩展
4. 终端集成
风格：流程图/思维导图，配色与文章主题一致
-->
```

## Step 4: 即时提示词优化（核心机制）

**原则：每个 Agent 执行前，先调用 prompt-optimizer-agent 进行针对性优化**

这样做的好处：
1. **上下文完整**：可以获取前置 Agent 的输出作为上下文
2. **针对性强**：根据当前任务状态生成最精准的提示词
3. **动态适应**：根据实际调研结果调整写作策略

### 执行模式

```
┌─────────────────────────────────────────────────────────┐
│  对于每个即将执行的 Agent：                              │
│                                                         │
│  1. 调用 prompt-optimizer-agent                         │
│     输入：目标 Agent + 当前上下文 + 前置输出             │
│     输出：优化后的提示词                                 │
│                                                         │
│  2. 使用优化后的提示词调用目标 Agent                     │
│     输入：优化后的提示词                                 │
│     输出：Agent 执行结果                                 │
│                                                         │
│  3. 保存输出，作为下一个 Agent 的上下文                  │
│                                                         │
│  4. 等待完成后，再执行下一个 Agent                       │
└─────────────────────────────────────────────────────────┘
```

### 示例：创作模式完整流程

```
Step 1: 优化 research-agent 提示词
┌──────────────────────────────────────┐
│ prompt-optimizer-agent               │
│ 输入：                               │
│   - 目标 Agent: research-agent       │
│   - 写作模式: 创作                   │
│   - 写作角度: 技术开发者             │
│   - 内容描述: {用户输入}             │
│   - 前置输出: 无                     │
│ 输出：优化后的调研提示词             │
└──────────────────────────────────────┘
    ↓
Step 2: 执行 research-agent
┌──────────────────────────────────────┐
│ research-agent                       │
│ 输入：优化后的调研提示词             │
│ 输出：调研报告（作为下一步上下文）   │
└──────────────────────────────────────┘
    ↓
Step 3: 优化 writer-agent 提示词
┌──────────────────────────────────────┐
│ prompt-optimizer-agent               │
│ 输入：                               │
│   - 目标 Agent: tech-writer-agent    │
│   - 写作模式: 创作                   │
│   - 内容描述: {用户输入}             │
│   - 前置输出: 调研报告 ← 关键！      │
│ 输出：优化后的写作提示词             │
└──────────────────────────────────────┘
    ↓
Step 4: 执行 writer-agent
┌──────────────────────────────────────┐
│ tech-writer-agent                    │
│ 输入：优化后的写作提示词             │
│ 输出：文章 Markdown                  │
└──────────────────────────────────────┘
    ↓
Step 5: 分析文章，确定图片需求（最多 6 张）
┌──────────────────────────────────────┐
│ 分析文章内容                         │
│ 根据实际需要确定：                   │
│   - 封面图（通常必需）               │
│   - 结构图（如有层次/流程）          │
│   - 概念图（如有抽象概念需图解）     │
│   - 场景图（如有应用场景描述）       │
│   - 其他配图（根据 IMAGE_NEEDED 标记）│
│ 按优先级排序，总数不超过 6 张        │
└──────────────────────────────────────┘
    ↓
Step 6-N: 串行生成每张图片
┌──────────────────────────────────────┐
│ 对于每张需要的图片：                 │
│                                      │
│ 1. prompt-optimizer-agent            │
│    输入：图片类型 + 文章上下文       │
│    输出：优化后的图片生成提示词      │
│                                      │
│ 2. image-generator-agent             │
│    输入：优化后的提示词              │
│    输出：图片文件                    │
│                                      │
│ 3. 等待完成后，继续下一张图片        │
└──────────────────────────────────────┘
    ↓
Step N+1: 输出 Markdown 文件
```

### 示例：仿写模式完整流程

```
Step 1-3: 同创作模式（调研 → 写作 → 分析图片需求）
    ↓
Step 4-N: 串行生成每张图片（最多 6 张）
    ↓
Step N+1: 输出 Markdown 文件
```

## Step 5: 提示词优化调用模板

```
Task(
  subagent_type: "wechat-article-toolkit:prompt-optimizer-agent",
  prompt: "
    ## 优化请求

    ### 目标 Agent
    {target_agent_name}

    ### 当前上下文
    - 写作模式: {创作/仿写}
    - 写作角度: {writing_perspective}
    - 主题类型: {topic_category}
    - 内容描述/仿写要求: {user_input}

    ### 前置 Agent 输出
    {previous_agent_output}

    ### 任务
    请为 {target_agent_name} 生成优化后的提示词，
    基于四块模式（INSTRUCTIONS/CONTEXT/TASK/OUTPUT FORMAT），
    确保充分利用前置输出中的信息。
  ",
  model: "opus"
)
```

## Step 6: 执行 Agent

使用 Task 工具启动 Agent：

**启动 Agent 示例**：

```
Task(
  subagent_type: "wechat-article-toolkit:research-agent",
  prompt: "{优化后的提示词}",
  model: "opus"
)
```

**串行执行规则**：
1. 每个 Agent 执行前都先调用 prompt-optimizer-agent
2. 等待当前 Agent 完成后再启动下一个 Agent
3. 收集每个 Agent 的输出，传递给后续 Agent 作为上下文
4. 图片生成按需求列表顺序逐张生成

## Step 7: 聚合结果

收集所有 Agent 的输出：

```markdown
## 写作完成报告

### 写作模式
- 模式：{创作/仿写}
- 参考 URL：{仿写模式时显示}

### 生成的文件
- 📄 文章：articles/{topic}.md
- 🖼️ 封面图：articles/images/{topic}-cover.png
- 📊 结构图：articles/images/{topic}-structure.png（如有）
- 🖼️ 其他配图：articles/images/{topic}-image-1.png、{topic}-image-2.png...
- 📋 调研报告：articles/research/{topic}-research-report.md

### 文章信息
- 标题：{标题}
- 字数：{字数}
- 写作角度：{角度}

### 后续步骤
生成的 Markdown 文件可直接复制到微信公众号编辑器，或使用第三方工具（如 Mdnice、墨滴等）转换为公众号格式。
```

## 快速参考

### 写作角度 → Writer Agent 映射

| 角度 | Agent | 模型 | 特点 |
|------|-------|------|------|
| 🔧 技术开发者 | tech-writer-agent | opus | 代码示例、技术深度 |
| 📊 AI 产品经理 | pm-writer-agent | opus | 产品思维、场景导向 |
| 📰 AI 行业观察者 | ai-news-writer-agent | opus | 新闻解读、观点鲜明 |
| 📚 AI 教程作者 | tutorial-writer-agent | opus | 零基础友好、步骤详细 |

### 主题类型 → 配色方案

| 主题类型 | 配色 |
|----------|------|
| 🤖 AI 大模型 | 深蓝渐变 |
| 🛠️ AI 开发工具 | 蓝紫渐变 |
| 📱 AI 产品体验 | 粉紫渐变 |
| 🔬 AI 技术原理 | 蓝绿渐变 |
| 📈 AI 行业动态 | 橙红渐变 |
| 💼 AI 应用场景 | 绿橙渐变 |
| 🎓 AI 入门教程 | 青绿渐变 |

### 典型工作流示例

**示例 1：技术文章**

```
用户：帮我写一篇 Claude Code 的入门教程

选项收集：
- 写作角度：📚 AI 教程作者
- 写作方式：📝 给主题写
- 主题类型：🛠️ AI 开发工具
- 具体主题：Claude Code 入门教程
- 自动发布：否

执行计划（串行）：
- Step 1: prompt-optimizer → research-agent
- Step 2: prompt-optimizer → tutorial-writer-agent
- Step 3: 分析文章，确定图片需求（如需要 3 张图片）
- Step 4: prompt-optimizer → 封面图（Gemini）
- Step 5: prompt-optimizer → 结构图（Gemini）
- Step 6: prompt-optimizer → 概念图（Gemini）
- Step 7: 输出 Markdown 文件

输出：
- articles/claude-code-guide.md
- articles/images/claude-code-cover.png
- articles/images/claude-code-structure.png
- articles/images/claude-code-image-1.png
- articles/research/claude-code-research-report.md
```

**示例 2：产品分析**

```
用户：分析一下 Cursor 这个产品

选项收集：
- 写作角度：📊 AI 产品经理
- 写作方式：📝 给主题写
- 主题类型：🛠️ AI 开发工具
- 具体主题：Cursor 产品拆解

执行计划（串行）：
- Step 1: prompt-optimizer → research-agent
- Step 2: prompt-optimizer → pm-writer-agent
- Step 3: 分析文章，确定图片需求（如需要 4 张图片）
- Step 4-7: 串行生成 4 张图片（Gemini）
- Step 8: 输出 Markdown 文件

输出：
- articles/cursor-product-analysis.md
- articles/images/cursor-cover.png + 其他配图
- articles/research/cursor-research-report.md
```

## 错误处理

### Agent 执行失败

如果某个 Agent 执行失败：
1. 记录错误信息
2. 尝试重试（最多 2 次）
3. 如果仍然失败，跳过该 Agent 并通知用户

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 调研失败 | 网络问题或搜索无结果 | 重试或让用户提供参考资料 |
| 图片生成失败 | API 配置问题 | 检查 Gemini API Key 或即梦 API 密钥 |

## 注意事项

1. **串行执行**：每个 Agent 完成后再启动下一个 Agent
2. **提示词优化**：每个 Agent 执行前都先调用 prompt-optimizer-agent
3. **图片数量限制**：一篇文章最多生成 6 张图片
4. **图片生成工具**：默认使用 Gemini（Google Nano Banana Pro），可配置使用即梦 AI
5. **结果传递**：确保上一个 Agent 的输出正确传递给下一个 Agent 作为上下文
6. **错误处理**：任何 Agent 失败都要有降级方案（特别是图片生成 Agent）
7. **用户反馈**：每个关键步骤完成后向用户报告进度
