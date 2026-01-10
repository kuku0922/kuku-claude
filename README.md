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
/kuku-pr-review-toolkit:review-pr              # 完整审查
/kuku-pr-review-toolkit:review-pr tests errors # 指定审查项
/kuku-pr-review-toolkit:review-pr security     # 安全审查
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
/kuku-doc-consistency-toolkit:check-consistency spec-impl    # 规格与实现
/kuku-doc-consistency-toolkit:check-consistency design-impl  # 设计与实现
/kuku-doc-consistency-toolkit:check-consistency full         # 完整检查
```

## 安装

```bash
# 添加 plugin 仓库
claude plugins:add https://github.com/user/kuku-claude

# 或者安装单个 plugin
claude plugins:add https://github.com/user/kuku-claude/kuku-pr-review-toolkit
claude plugins:add https://github.com/user/kuku-claude/kuku-doc-consistency-toolkit
```

## License

MIT
