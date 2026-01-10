# kuku-claude

Claude Code 增强工具集，提供代码审查和文档一致性检查等功能。

## Plugins

### kuku-pr-review-toolkit

综合 PR 代码审查工具，包含 7 个专用 Agent：

| Agent | 功能 |
|-------|------|
| code-reviewer | 通用代码质量审查 |
| comment-analyzer | 代码注释准确性分析 |
| pr-test-analyzer | 测试覆盖率审查 |
| type-design-analyzer | 类型设计质量分析 |
| code-simplifier | 代码简化建议 |
| silent-failure-hunter | 静默失败检测 |
| security-reviewer | 安全漏洞审查 |

**使用方式：**
```bash
# 完整审查（运行所有 Agent）
/kuku-pr-review-toolkit:review-pr

# 单项审查
/kuku-pr-review-toolkit:review-pr quality      # 通用代码质量
/kuku-pr-review-toolkit:review-pr comments     # 注释准确性
/kuku-pr-review-toolkit:review-pr tests        # 测试覆盖率
/kuku-pr-review-toolkit:review-pr types        # 类型设计
/kuku-pr-review-toolkit:review-pr simplify     # 代码简化
/kuku-pr-review-toolkit:review-pr errors       # 静默失败检测
/kuku-pr-review-toolkit:review-pr security     # 安全漏洞

# 组合审查
/kuku-pr-review-toolkit:review-pr tests errors # 测试 + 错误处理
/kuku-pr-review-toolkit:review-pr security quality # 安全 + 质量
```

### kuku-doc-consistency-toolkit

文档与代码一致性检查工具，包含 4 个专用 Agent：

| Agent | 功能 |
|-------|------|
| spec-impl-checker | OpenSpec 与代码实现一致性 |
| design-impl-checker | 详细设计与代码实现一致性 |
| architecture-design-checker | 顶层设计与详细设计一致性 |
| cross-doc-checker | 跨文档一致性检查 |

**使用方式：**
```bash
# 检查 OpenSpec 与代码实现一致性
/kuku-doc-consistency-toolkit:check-consistency spec-impl

# 检查顶层设计与详细设计一致性
/kuku-doc-consistency-toolkit:check-consistency arch-design

# 检查详细设计与代码实现一致性
/kuku-doc-consistency-toolkit:check-consistency design-impl

# 检查跨文档一致性
/kuku-doc-consistency-toolkit:check-consistency cross-doc

# 完整一致性检查（运行所有 Agent）
/kuku-doc-consistency-toolkit:check-consistency full

# 指定模块检查
/kuku-doc-consistency-toolkit:check-consistency spec-impl auth      # 检查 auth 模块
/kuku-doc-consistency-toolkit:check-consistency design-impl payment # 检查 payment 模块
```

## 安装

### 步骤一：添加插件市场

首先需要将本仓库添加为 Claude Code 的插件市场源：

```bash
/plugin marketplace add kuku0922/kuku-claude
```

### 步骤二：安装插件

#### 方式 A：交互式安装（推荐）

```bash
/plugin
```
进入插件管理器后，切换到 **Discover** 标签页，搜索并选择要安装的插件。

#### 方式 B：命令行安装

```bash
# 安装 PR 代码审查工具
/plugin install kuku-pr-review-toolkit@kuku-claude

# 安装文档一致性检查工具
/plugin install kuku-doc-consistency-toolkit@kuku-claude
```

### 安装作用域

安装时可选择作用域：
- `user`（默认）：个人跨项目使用
- `project`：团队共享（提交到版本控制）
- `local`：仅当前项目（gitignore）

> ⚠️ **注意：** 安装前请确保信任该插件。Anthropic 不控制插件中包含的 MCP 服务器、文件或其他软件。

## License

MIT
