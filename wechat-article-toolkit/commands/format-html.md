---
name: format-html
description: 将 Markdown 文章转换为微信公众号适配的精美 HTML。可单独调用，用于修改 MD 后重新生成 HTML。
allowed-tools: Read, Bash, AskUserQuestion, Glob
---

# Markdown 转 HTML 命令

## 概述

独立的 HTML 格式化命令，用于将 Markdown 文章转换为微信公众号适配的精美 HTML。

**使用场景**：
- 修改生成的 Markdown 后，重新生成 HTML
- 将已有的 Markdown 文章格式化为微信公众号风格
- 更换 HTML 模板风格

## 使用方式

```bash
# 格式化最近的 Markdown 文件
/wechat-article-toolkit:format-html

# 格式化指定文件
/wechat-article-toolkit:format-html path/to/article.md

# 指定模板风格
/wechat-article-toolkit:format-html --template 极客暗黑风
```

## 执行流程

### Step 1: 确定输入文件

**情况 1：用户指定了文件路径**

直接使用指定的 Markdown 文件。

**情况 2：未指定文件**

使用 Glob 查找当前目录下的 Markdown 文件，让用户选择：

```bash
# 查找 Markdown 文件
Glob(pattern: "**/*.md")
```

如果只找到一个 `.md` 文件，直接使用；如果有多个，列出让用户选择。

### Step 2: 选择 HTML 模板风格

使用 AskUserQuestion 询问用户：

```json
{
  "question": "请选择 HTML 模板风格",
  "header": "模板风格",
  "options": [
    {
      "label": "🖥️ 极客暗黑风（推荐）",
      "description": "适合技术文章、代码教程，暗色背景突出代码"
    },
    {
      "label": "💙 VSCode 蓝色科技风",
      "description": "适合开发工具介绍，专业技术感"
    },
    {
      "label": "🌙 终端极客·暗夜测评风",
      "description": "适合技术评测、对比分析"
    },
    {
      "label": "📊 产品经理高级模板",
      "description": "适合产品分析、商业文章"
    }
  ],
  "multiSelect": false
}
```

**第二组选项**（如果用户选择"其他"）：

```json
{
  "question": "请选择其他模板风格",
  "header": "更多模板",
  "options": [
    {
      "label": "🏆 高端商务·黑金咨询风",
      "description": "适合商业分析、行业报告"
    },
    {
      "label": "⚔️ 红蓝对决·深度测评模板",
      "description": "适合对比评测文章"
    },
    {
      "label": "✨ 未来科技·弥散光感风",
      "description": "适合 AI/科技前沿话题"
    },
    {
      "label": "📝 现代极简风",
      "description": "适合通用文章，简洁清爽"
    }
  ],
  "multiSelect": false
}
```

**第三组选项**：

```json
{
  "question": "请选择其他模板风格",
  "header": "更多模板",
  "options": [
    {
      "label": "🎨 新潮杂志·孟菲斯风",
      "description": "适合新闻资讯、潮流话题"
    },
    {
      "label": "🌸 治愈系·暖色手账风",
      "description": "适合入门教程、生活方式"
    }
  ],
  "multiSelect": false
}
```

### 模板风格 → 主题映射

| 模板风格 | 主题参数 | 参考示例文件 |
|----------|----------|--------------|
| 极客暗黑风 | tech | 极客暗黑风.html |
| VSCode 蓝色科技风 | tech | VSCode 蓝色科技风.html |
| 终端极客·暗夜测评风 | tech | 终端极客·暗夜测评风.html |
| 产品经理高级模板 | business | 产品经理高级模板.html |
| 高端商务·黑金咨询风 | business | 高端商务·黑金咨询风.html |
| 红蓝对决·深度测评模板 | tech | 红蓝对决·深度测评模板.html |
| 未来科技·弥散光感风 | tech | 未来科技·弥散光感风.html |
| 现代极简风 | minimal | 现代极简风.html |
| 新潮杂志·孟菲斯风 | minimal | 新潮杂志·孟菲斯风.html |
| 治愈系·暖色手账风 | minimal | 治愈系·暖色手账风.html |

### Step 3: 执行转换

调用 formatter-agent 执行转换：

```
Task(
  subagent_type: "wechat-article-toolkit:formatter-agent",
  prompt: "
    将 Markdown 转换为 HTML：
    - 输入文件：{markdown_path}
    - 输出目录：{output_dir}
    - 主题：{theme}
    - 参考示例：{PLUGIN_DIR}/examples/{template_file}
  ",
  model: "opus"
)
```

**或者直接执行命令**（更快）：

```bash
# 定位插件目录
PLUGIN_DIR=$(find ~/.claude -name "wechat-article-toolkit" -type d 2>/dev/null | head -1)

# 执行转换
uv run -p 3.14 --no-project \
  --with markdown \
  --with beautifulsoup4 \
  --with cssutils \
  ${PLUGIN_DIR}/scripts/markdown_to_html.py \
  --input "{MARKDOWN_FILE}" \
  --output "{OUTPUT_DIR}/{ARTICLE_NAME}.html" \
  --theme {THEME}
```

### Step 4: 代码块转换（条件执行）

如果文章包含代码块，执行代码块转换：

```bash
uv run -p 3.14 --no-project \
  ${PLUGIN_DIR}/scripts/convert-code-blocks.py \
  "{INPUT_HTML}" "{OUTPUT_HTML}"
```

### Step 5: 输出结果

```markdown
## 格式化完成

### 输出文件
- 📄 HTML：{output_path}
- 🎨 使用模板：{template_name}
- 🔧 主题参数：{theme}

### 使用说明
1. 打开生成的 HTML 文件
2. 在浏览器中 Ctrl+A（全选）→ Ctrl+C（复制）
3. 粘贴到微信公众号编辑器

### 下一步
如需发布到微信公众号草稿箱：
/wechat-article-toolkit:publish
```

## 快速参考

### 可用模板一览

| 模板 | 风格 | 适用场景 |
|------|------|----------|
| 🖥️ 极客暗黑风 | tech | 技术文章、代码教程 |
| 💙 VSCode 蓝色科技风 | tech | 开发工具介绍 |
| 🌙 终端极客·暗夜测评风 | tech | 技术评测 |
| 📊 产品经理高级模板 | business | 产品分析 |
| 🏆 高端商务·黑金咨询风 | business | 行业报告 |
| ⚔️ 红蓝对决·深度测评模板 | tech | 对比评测 |
| ✨ 未来科技·弥散光感风 | tech | AI/科技前沿 |
| 📝 现代极简风 | minimal | 通用文章 |
| 🎨 新潮杂志·孟菲斯风 | minimal | 新闻资讯 |
| 🌸 治愈系·暖色手账风 | minimal | 入门教程 |

### 命令参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `{file}` | 指定 Markdown 文件 | `/format-html output/article.md` |
| `--template` | 指定模板名称 | `--template 极客暗黑风` |
| `--theme` | 指定主题参数 | `--theme tech` |
| `--output` | 指定输出路径 | `--output ./my-article.html` |

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 找不到 Markdown 文件 | 路径错误 | 检查文件路径 |
| uv 命令不存在 | uv 未安装 | 安装 uv：`curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| HTML 乱码 | 编码问题 | 确保 Markdown 文件为 UTF-8 编码 |

## 与 write-article 的关系

```
/write-article
    ↓
  写作流程（包含 HTML 转换）
    ↓
  输出 .md + .html
    ↓
  用户修改 .md
    ↓
/format-html  ← 单独重新生成 HTML
    ↓
  输出新的 .html
```

**设计理念**：
- `write-article`：完整写作流程，自动包含 HTML 转换
- `format-html`：独立命令，用于重新格式化已有的 Markdown
