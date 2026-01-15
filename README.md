# kuku-claude

Claude Code 增强工具集，提供多维度代码审查和文档一致性检查功能。

## Plugins

### kuku-pr-review-toolkit

PR 级别代码审查工具，基于 `git diff` 审查变更代码，包含 8 个专用 Agent：

| Agent | 功能 |
|-------|------|
| code-reviewer | 通用代码质量审查（含跨文件一致性检查） |
| comment-analyzer | 代码注释准确性分析 |
| pr-test-analyzer | 测试覆盖率审查 |
| type-design-analyzer | 类型设计质量分析 |
| code-simplifier | 代码简化建议 |
| silent-failure-hunter | 静默失败检测 |
| security-reviewer | 安全漏洞审查 |
| architecture-impact-analyzer | 架构影响分析（层边界、依赖方向、循环依赖） |

**使用方式：**
```bash
# 完整审查（运行所有 Agent）
/kuku-pr-review-toolkit:review-pr

# 单项审查
/kuku-pr-review-toolkit:review-pr code        # 通用代码质量
/kuku-pr-review-toolkit:review-pr comments    # 注释准确性
/kuku-pr-review-toolkit:review-pr tests       # 测试覆盖率
/kuku-pr-review-toolkit:review-pr types       # 类型设计
/kuku-pr-review-toolkit:review-pr simplify    # 代码简化
/kuku-pr-review-toolkit:review-pr errors      # 静默失败检测
/kuku-pr-review-toolkit:review-pr security    # 安全漏洞
/kuku-pr-review-toolkit:review-pr architecture # 架构影响分析

# 组合审查
/kuku-pr-review-toolkit:review-pr tests errors    # 测试 + 错误处理
/kuku-pr-review-toolkit:review-pr security code   # 安全 + 质量

# 并行审查（最多 3 个 Agent 同时运行）
/kuku-pr-review-toolkit:review-pr all parallel
```

---

### kuku-feature-review-toolkit

功能级别代码审查工具，基于功能边界发现审查完整功能实现（前端+后端），包含 8 个专用 Agent：

| Agent | 功能 |
|-------|------|
| feature-code-reviewer | 跨文件代码质量审查 |
| feature-error-handler | 错误流追踪（后端→前端） |
| feature-security-reviewer | 功能攻击面安全审查 |
| feature-type-analyzer | 前后端类型一致性分析 |
| feature-test-analyzer | 功能测试覆盖率审查 |
| feature-architecture-reviewer | 架构层级与依赖分析 |
| feature-comment-analyzer | 跨文件文档一致性分析 |
| feature-code-simplifier | 功能级代码简化建议 |

**与 PR Review 的区别：**

| 维度 | PR Review | Feature Review |
|------|-----------|----------------|
| 审查范围 | `git diff` 变更文件 | 完整功能边界 |
| 入口点 | 变更的文件 | 功能入口点（函数/类/目录） |
| 覆盖 | 仅修改的代码 | 功能相关的所有代码 |
| 前后端 | 分别审查 | 联合审查 + API 契约检查 |
| 使用场景 | 提交前/PR 前 | 功能审计、架构审查 |

**使用方式：**
```bash
# 单入口审查
/kuku-feature-review-toolkit:review-feature AuthController.login

# 前端入口
/kuku-feature-review-toolkit:review-feature LoginForm

# 目录入口
/kuku-feature-review-toolkit:review-feature src/features/payment/

# 前后端联合入口
/kuku-feature-review-toolkit:review-feature LoginForm,AuthController.login

# 快速检查（3 个 Agent）
/kuku-feature-review-toolkit:review-feature UserService.register quick

# 深度审查（8 个 Agent，用于关键功能）
/kuku-feature-review-toolkit:review-feature PaymentProcessor.process deep
```

**深度级别：**

| 深度 | Agent 数量 | 适用场景 |
|------|-----------|----------|
| quick | 3 | 快速健全性检查 |
| standard | 5-6 | 常规功能审查 |
| deep | 8 | 关键功能（认证、支付） |

---

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

---

## 推荐工作流

```
开发流程：

1. 编写代码
2. /kuku-pr-review-toolkit:review-pr              ← PR 级审查（git diff）
3. /kuku-feature-review-toolkit:review-feature    ← 功能级审查（完整边界）
4. /kuku-doc-consistency-toolkit:check-consistency ← 文档对齐检查
5. 创建 PR
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

# 安装功能级代码审查工具
/plugin install kuku-feature-review-toolkit@kuku-claude

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
