# AI图片生成指南

## 概述

AI生成图片可以有效补充技术文章的视觉内容，特别适合创建封面图、概念示意图和场景插画。

**图片生成工具**：
- **Gemini**（Google Nano Banana Pro）- 默认，支持 4K 高清
- **即梦 AI**（火山引擎）- 国内访问稳定

## 重要优化原则

### 1. 图片文字规范
- 文字数量要少，只保留关键信息
- 文字必须清晰可读，**绝对不能出现乱码**
- **禁止在图片上显示色号**（如 #282c34）、技术参数等与主题无关的信息
- **语言选择**：根据图片内容自行判断使用简体中文或英文
- **语言统一**：同一张图片内保持语言风格一致（全中文或全英文），特殊情况可混用

### 2. 只生成真正必要的图片
**必要图片的判断标准**：
- ✅ **封面图**：每篇文章必须有一张吸引眼球的封面图
- ✅ **结构图**：有明确的层次结构、流程步骤时生成
- ✅ **性能对比图**：有明确的数据对比时生成
- ✅ **技术架构图**：涉及复杂技术原理需要可视化时生成
- ❌ **装饰性配图**：不要生成纯装饰性的图片
- ❌ **场景插画**：除非对理解内容有实质帮助，否则不生成

**生成决策流程**：
1. 阅读文章内容
2. 封面图（必需）
3. 判断是否有层次结构/流程 → 是：生成结构图
4. 判断是否有数据对比 → 是：生成对比图
5. 判断是否有复杂技术 → 是：生成架构图
6. 其他图片根据实际需求判断

### 3. 图片数量控制
- 每篇文章图片数量：**最多 6 张**
- 优先级：封面图 > 结构图 > 概念图 > 其他配图
- 宁缺毋滥，质量优于数量

### 4. 图片命名规范
- **按主题命名**：`{主题}_cover.png`、`{主题}_structure.png`
- **或按序号命名**：`{主题}_image_1.png`、`{主题}_image_2.png`
- **避免固定名称**：不要用 `cover.png`、`image.png` 等固定名称，否则多张图片会相互覆盖

---

## 快速开始

### 基本用法

使用 `~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/scripts/generate_image.py` 脚本调用图片生成 API：

```bash
uv run -p 3.14 --no-project \
  --with requests --with google-genai --with pillow \
  ~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/scripts/generate_image.py \
  --prompt "图片描述提示词" \
  --output "./output/images/{主题}_cover.png" \
  --provider "gemini"
```

### 环境配置

**Gemini 配置（推荐）**：

编辑 `.claude/config/settings.json`：
```json
{
  "image_generation": {
    "default_provider": "gemini"
  },
  "gemini": {
    "api_key": "your-gemini-api-key"
  }
}
```

或设置环境变量：`GEMINI_API_KEY`

**即梦 AI 配置**：

```json
{
  "image_generation": {
    "default_provider": "jimeng"
  },
  "jimeng": {
    "access_key_id": "your-access-key-id",
    "secret_access_key": "your-secret-access-key"
  }
}
```

或设置环境变量：`VOLC_ACCESSKEY` 和 `VOLC_SECRETKEY`

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 图片生成提示词（必填） | - |
| `--output` | 输出图片路径（必填） | - |
| `--aspect-ratio` | 图片宽高比 | 16:9 |
| `--provider` | 图片生成服务 | gemini |
| `--image-size` | 图片尺寸 1K/2K/4K（仅 Gemini） | 2K |
| `--no-auto-rename` | 禁用自动重命名 | 否 |

### 支持的宽高比

| 宽高比 | Gemini | 即梦尺寸 | 适用场景 |
|--------|--------|----------|----------|
| 16:9 | ✅ | 2560x1440 | 封面图、横版配图 |
| 1:1 | ✅ | 2048x2048 | 头像、方形配图 |
| 4:3 | ✅ | 2304x1728 | 传统比例 |
| 9:16 | ✅ | 1440x2560 | 竖版配图 |
| 3:2 | - | 2496x1664 | 照片比例（仅即梦） |
| 21:9 | - | 3024x1296 | 超宽横幅（仅即梦） |

---

## 何时使用AI生成图片

### ✅ 适合AI生成的场景

1. **封面图/首图**
   - 吸引读者点击的视觉设计
   - 体现文章主题的创意图
   - 品牌风格的标题图

2. **概念示意图**
   - 抽象技术概念的可视化
   - 工作流程的示意图
   - 系统架构的简化表现

3. **结构图/信息图**
   - 展示文章核心要点
   - 多层次内容的可视化
   - 对比分析的图表化

4. **场景插画**（谨慎使用）
   - 使用场景的情景化展示
   - 问题场景的描绘
   - 解决方案的效果展示

### ❌ 不适合AI生成的场景

1. **实际产品截图**
   - 软件界面必须用真实截图
   - 代码编辑器画面
   - 实际操作步骤

2. **真实数据图表**
   - 性能测试数据（需要准确性）
   - 市场占有率图表
   - GitHub Star趋势图

3. **官方品牌素材**
   - 产品Logo
   - 官方宣传图
   - 品牌标识

---

## 提示词模板

### 1. 封面图模板

```
A cover image for WeChat article about [主题].
[配色] gradient background.
Layout: Split into two distinct zones (left 40%, right 60%).
Left zone: title '[标题]' in bold, subtitle '[副标题]' in Chinese, text aligned left, clear and readable.
Right zone: [视觉元素], 3D style, modern tech aesthetic.
Visual elements should not overlap with text zone.
Clean design, professional look, 2.35:1 aspect ratio.
Text must be in simplified Chinese, accurate and clear, no garbled characters.
```

### 2. 结构图模板

```
A content structure infographic for [主题].
Design: modern card-based layout with [数量] main sections.
Style: professional infographic with hierarchy.
Cards arranged in [grid/flow] layout, each containing:
- Section icon (simple, modern)
- Chinese title in bold
- 2-3 bullet points in Chinese
Color scheme: [配色方案].
Background: clean gradient, not distracting.
All text in simplified Chinese, clear and readable.
16:9 aspect ratio, high quality infographic.
```

### 3. 技术架构图模板

```
A modern technical architecture diagram for [系统名称].
Design: layered architecture with 3-4 tiers, connected by arrows showing data flow.
Style: clean, professional, developer-oriented.
Layers from top to bottom:
- [层级1]: [组件名称]
- [层级2]: [组件名称]
- [层级3]: [组件名称]
Visual elements:
- Arrows showing data flow direction (with Chinese labels)
- Color coding: each layer has a distinct color
- Icons: subtle tech icons for each component
Style: flat design with subtle shadows, modern and clean.
All text in simplified Chinese, clear labels.
16:9 aspect ratio, high quality.
```

### 4. 对比图模板

```
A clear comparison image showing [概念A] vs [概念B].
Layout: split screen design, left side for [概念A], right side for [概念B].
Design:
- Left side: cooler tones (blue-gray) representing traditional/old
- Right side: warmer/brighter tones (green-blue) representing modern/new
- Center: "VS" or arrow showing transformation
Text labels in Chinese.
Style: clean, modern, infographic-style, easy to understand.
All text in simplified Chinese, clear and readable.
16:9 aspect ratio.
```

---

## 配色建议

### 根据文章类型选择配色

| 文章类型 | 推荐配色 | 色彩代码 |
|----------|----------|----------|
| AI/大模型 | 蓝紫渐变 | #1a1f5c → #7c3aed |
| 开发工具 | 绿橙渐变 | #10b981 → #f97316 |
| 产品体验 | 粉紫渐变 | #ec4899 → #a855f7 |
| 技术原理 | 蓝绿渐变 | #0891b2 → #06b6d4 |
| 行业动态 | 橙红渐变 | #f97316 → #ef4444 |
| 入门教程 | 青绿渐变 | #14b8a6 → #22c55e |

### 颜色语义

- **蓝色**：稳定、可靠、专业（适合主导产品）
- **绿色**：增长、正面、环保（适合性能提升）
- **紫色**：创新、高端、未来（适合新技术）
- **橙色**：警示、次要、中性（适合对比项）

---

## 工作流集成

### 完整生成流程

```bash
# 1. 生成封面图
uv run -p 3.14 --no-project \
  --with requests --with google-genai --with pillow \
  ~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/scripts/generate_image.py \
  --prompt "A cover image for WeChat article about Claude Code. Blue-purple gradient background..." \
  --output "./output/images/claude_code_cover.png"

# 2. 生成结构图（如需要）
uv run -p 3.14 --no-project \
  --with requests --with google-genai --with pillow \
  ~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/scripts/generate_image.py \
  --prompt "A content structure infographic for Claude Code tutorial..." \
  --output "./output/images/claude_code_structure.png"

# 3. 生成其他配图（如需要）
uv run -p 3.14 --no-project \
  --with requests --with google-genai --with pillow \
  ~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/scripts/generate_image.py \
  --prompt "A comparison image showing traditional coding vs AI-assisted coding..." \
  --output "./output/images/claude_code_image_1.png"
```

### 在文章中嵌入图片

```markdown
# Claude Code 入门教程

![封面图](./images/claude_code_cover.png)

## 核心功能

Claude Code 拥有强大的多模态理解能力：

![内容结构图](./images/claude_code_structure.png)

如上图所示，Claude Code 的核心功能包括...
```

---

## 提示词优化技巧

### 1. 具体而非抽象

❌ "A nice tech image"
✅ "A clean infographic showing data flow with blue arrows on white background"

### 2. 明确构图

❌ "Some icons"
✅ "Three icons arranged horizontally in the center, equal spacing, on gradient background"

### 3. 控制复杂度

❌ "Complex system architecture"
✅ "Simplified 3-tier architecture with 3 main components and connecting arrows"

### 4. 强调中文要求

在每个提示词中包含：
```
Text must be in simplified Chinese, accurate and clear, no garbled characters.
All Chinese characters must be readable and correct.
```

---

## 常见问题

### Q: 生成的图片中文乱码？

**解决方案**：在提示词中多次强调中文要求：
```
IMPORTANT: All text must be in simplified Chinese (简体中文).
Chinese characters must be clear, readable, and accurate - NO garbled text.
```

### Q: 图片太复杂了？

**解决方案**：在提示词中强调简洁：
- "minimalist"
- "simple"
- "clean design"
- "maximum 5 elements"

### Q: 文字与图片重叠？

**解决方案**：在提示词中明确分区：
```
Layout: Split into two distinct zones.
Visual elements should not overlap with text zone.
```

### Q: 生成失败？

**排查步骤**：
1. 检查 API 凭证是否正确配置
2. 检查网络连接
3. 简化提示词重试
4. 查看错误信息确定具体原因

---

## 最佳实践总结

1. ✅ **每篇文章必须有封面图**
2. ✅ **图片按主题命名，避免覆盖**
3. ✅ **提前规划需要的图片类型和数量**
4. ✅ **强调中文要求，避免乱码**
5. ✅ **简约优先，技术文章配图宜简不宜繁**
6. ✅ **最多 6 张图片，质量优于数量**
7. ✅ **生成后检查清晰度和相关性**

通过合理使用即梦 AI 生成图片，可以让技术文章更加生动专业，同时保持高效的创作流程！
