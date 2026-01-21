---
name: publish
description: 将已生成的文章发布到微信公众号草稿箱。可指定文件路径或自动查找最近生成的文章。
allowed-tools: Read, Bash, Task, AskUserQuestion, Glob
---

# 微信公众号发布命令

## 概述

独立的发布命令，用于将已生成的文章发布到微信公众号草稿箱。支持：
- 发布指定的 HTML 文件
- 自动查找最近生成的文章
- 批量发布多篇文章

## 使用方式

```bash
# 发布最近生成的文章
/wechat-article-toolkit:publish

# 发布指定文件
/wechat-article-toolkit:publish path/to/article.html

# 发布指定目录下的所有文章
/wechat-article-toolkit:publish --dir path/to/articles/
```

## 执行流程

### Step 1: 确定发布文件

**情况 1：用户指定了文件路径**

直接使用指定的文件。

**情况 2：未指定文件**

使用 AskUserQuestion 询问用户：

```json
{
  "question": "请选择要发布的文章",
  "header": "选择文章",
  "options": [
    {
      "label": "📄 最近生成的文章",
      "description": "自动查找当前目录下最近生成的 HTML 文件"
    },
    {
      "label": "📁 指定文件路径",
      "description": "手动输入要发布的文件路径"
    },
    {
      "label": "📚 批量发布",
      "description": "发布指定目录下的所有 HTML 文件"
    }
  ],
  "multiSelect": false
}
```

### Step 2: 查找文件

**自动查找最近文章**：

```bash
# 使用 Glob 查找当前目录下的 HTML 文件
Glob(pattern: "**/*.html")

# 按修改时间排序，取最近的文件
```

**验证文件**：
- 检查文件是否存在
- 检查文件是否为有效的 HTML
- 检查是否包含必要的文章内容

### Step 3: 确认发布信息

显示即将发布的文章信息：

```markdown
## 发布确认

### 文章信息
- 文件：{file_path}
- 标题：{从 HTML 中提取}
- 大小：{file_size}
- 修改时间：{modified_time}

### 封面图
- 路径：{cover_path}（如存在）

是否确认发布？
```

### Step 4: 调用 Publisher Agent

```
Task(
  subagent_type: "wechat-article-toolkit:publisher-agent",
  prompt: "
    发布文章到微信公众号草稿箱：
    - HTML 文件：{html_path}
    - 封面图：{cover_path}
    - 标题：{title}
  ",
  model: "opus"
)
```

### Step 5: 输出结果

```markdown
## 发布结果

### 状态
- ✅ 发布成功 / ❌ 发布失败

### 详情
- 草稿 ID：{media_id}
- 文章标题：{title}
- 发布时间：{timestamp}

### 下一步
- 登录微信公众号后台查看草稿
- 编辑后可直接发布
- 链接：https://mp.weixin.qq.com/
```

## 批量发布

当选择批量发布时：

```markdown
## 批量发布

### 发现的文章
1. {article1.html} - {title1}
2. {article2.html} - {title2}
3. {article3.html} - {title3}

### 确认
是否发布以上 {count} 篇文章？
```

依次调用 Publisher Agent 发布每篇文章，并汇总结果。

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 文件不存在 | 路径错误 | 检查文件路径 |
| 配置缺失 | 未配置微信 API | 复制 config/settings.example.json |
| Token 失效 | Access Token 过期 | 自动刷新 Token |
| 上传失败 | 网络问题或图片过大 | 重试或压缩图片 |

## 配置要求

确保已配置 `config/settings.json`：

```json
{
  "wechat": {
    "appid": "wx1234567890abcdef",
    "appsecret": "your-appsecret-here",
    "base_url": "https://api.weixin.qq.com/cgi-bin"
  }
}
```

首次使用：
```bash
cp config/settings.example.json config/settings.json
```

## 注意事项

1. **发布前检查**：确保文章内容和格式正确
2. **封面图**：如果同目录下有 cover.png，会自动作为封面图
3. **草稿箱**：发布后文章在草稿箱，需手动发布到公众号
4. **频率限制**：注意微信 API 的调用频率限制
