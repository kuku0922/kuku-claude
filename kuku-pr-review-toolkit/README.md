# PR Review Toolkit

A comprehensive collection of specialized agents for thorough pull request review, covering code comments, test coverage, error handling, type design, code quality, security vulnerabilities, architectural impact, and code simplification.

## Overview

This plugin bundles 8 expert review agents that each focus on a specific aspect of code quality. Use them individually for targeted reviews or together for comprehensive PR analysis. All agents support multiple programming languages and leverage LSP and Serena symbolic tools for precise code analysis.

## Code Analysis Tools

All agents have access to powerful code analysis tools.

> **使用优先级**：符号级代码检索时，LSP > Serena > Grep

### LSP Tools
- `find_definition` - Find symbol definitions
- `find_references` - Find all references to a symbol
- `get_diagnostics` - Get language diagnostics (errors, warnings)

### Serena Symbolic Tools
- `get_symbols_overview` - Get file symbols overview
- `find_symbol` - Find specific symbol with body
- `find_referencing_symbols` - Find symbols that reference a symbol
- `search_for_pattern` - Search patterns in code

## Supported Languages

Most agents support the following languages:
- Python
- Go
- Java
- Rust
- TypeScript/JavaScript
- C/C++
- Ruby
- Swift
- PHP (security-reviewer)

## Agents

### 1. comment-analyzer
**Focus**: Code comment accuracy and maintainability

**Analyzes:**
- Comment accuracy vs actual code
- Documentation completeness
- Comment rot and technical debt
- Misleading or outdated comments

**When to use:**
- After adding documentation
- Before finalizing PRs with comment changes
- When reviewing existing comments

**Triggers:**
```
"Check if the comments are accurate"
"Review the documentation I added"
"Analyze comments for technical debt"
```

### 2. pr-test-analyzer
**Focus**: Test coverage quality and completeness

**Analyzes:**
- Behavioral vs line coverage
- Critical gaps in test coverage
- Test quality and resilience
- Edge cases and error conditions

**When to use:**
- After creating a PR
- When adding new functionality
- To verify test thoroughness

**Triggers:**
```
"Check if the tests are thorough"
"Review test coverage for this PR"
"Are there any critical test gaps?"
```

### 3. silent-failure-hunter
**Focus**: Error handling and silent failures (Multi-language)

**Analyzes:**
- Silent failures in error handlers
- Inadequate error handling patterns
- Inappropriate fallback behavior
- Missing error logging
- Language-specific anti-patterns

**Language-specific patterns:**
- Python: bare `except:`, `pass` in except blocks
- Go: `_ = someFunc()` ignoring errors, empty `if err != nil`
- Java: empty catch blocks, swallowing `InterruptedException`
- Rust: excessive `.unwrap()`, ignoring `Result`
- JS/TS: empty catch blocks, unhandled Promise rejections
- C++: catching `...` without re-throwing
- Swift: force unwrapping `!`, `try!` in production

**When to use:**
- After implementing error handling
- When reviewing error handling code
- Before finalizing PRs with error handling

**Triggers:**
```
"Review the error handling"
"Check for silent failures"
"Analyze catch blocks in this PR"
```

### 4. type-design-analyzer
**Focus**: Type design quality and invariants

**Analyzes:**
- Type encapsulation (rated 1-10)
- Invariant expression (rated 1-10)
- Type usefulness (rated 1-10)
- Invariant enforcement (rated 1-10)

**When to use:**
- When introducing new types
- During PR creation with data models
- When refactoring type designs

**Triggers:**
```
"Review the UserAccount type design"
"Analyze type design in this PR"
"Check if this type has strong invariants"
```

### 5. code-reviewer
**Focus**: General code review for project guidelines

**Analyzes:**
- CLAUDE.md compliance
- Style violations
- Bug detection
- Code quality issues

**When to use:**
- After writing or modifying code
- Before committing changes
- Before creating pull requests

**Triggers:**
```
"Review my recent changes"
"Check if everything looks good"
"Review this code before I commit"
```

### 6. security-reviewer
**Focus**: Security vulnerabilities and attack vectors (Multi-language)

**Analyzes:**
- OWASP Top 10 vulnerabilities
- Injection attacks (SQL, command, template)
- Authentication and authorization flaws
- Cryptographic failures
- Insecure deserialization
- SSRF and path traversal
- Language-specific security anti-patterns

**Language-specific patterns:**
- Python: `eval()`, `pickle.loads()`, `yaml.load()` without SafeLoader
- Go: SQL string formatting, unchecked errors in security code
- Java: XXE, JNDI injection, insecure deserialization
- Rust: unsafe blocks, `.unwrap()` on user input
- JS/TS: `eval()`, DOM XSS, prototype pollution
- C/C++: buffer overflows, format strings, use-after-free
- PHP: `eval()`, file inclusion, `unserialize()`
- Swift: insecure data storage, missing certificate pinning

**Severity scoring:** 0-100 (only reports ≥50 by default)

**When to use:**
- When implementing authentication/authorization
- When handling user input
- When working with cryptography
- Before deploying security-sensitive code

**Triggers:**
```
"Check for security vulnerabilities"
"Review the authentication code for security"
"Audit this API endpoint for injection attacks"
```

### 7. code-simplifier
**Focus**: Code simplification and refactoring (Multi-language)

**Analyzes:**
- Code clarity and readability
- Unnecessary complexity and nesting
- Redundant code and abstractions
- Consistency with project standards
- Overly compact or clever code

**Language-specific guidelines:**
- Python: PEP 8, comprehensions, type hints
- Go: Effective Go, error handling, defer
- Java: streams, Optional, composition over inheritance
- Rust: iterators, pattern matching, clippy suggestions
- JS/TS: async/await, const preference, named exports
- C/C++: RAII, smart pointers, const correctness
- Ruby: blocks, iterators, short methods
- Swift: optionals, guard clauses, protocol-oriented design

**When to use:**
- After writing or modifying code
- After passing code review
- When code works but feels complex

**Triggers:**
```
"Simplify this code"
"Make this clearer"
"Refine this implementation"
```

**Note**: This agent preserves functionality while improving code structure and maintainability.

### 8. architecture-impact-analyzer
**Focus**: Architectural impact of code changes

**Analyzes:**
- Layer boundary compliance (Controller → Service → Repository)
- Dependency direction and circular dependencies
- New dependencies introduced by changes
- Pattern compliance with existing codebase
- Module boundary impact (cohesion, coupling)

**When to use:**
- When changes touch multiple modules
- When introducing new patterns or dependencies
- When modifying core infrastructure
- When changes span multiple architectural layers

**Triggers:**
```
"Check the architectural impact"
"Does this fit our architecture?"
"Review layer boundaries in these changes"
"Check for circular dependencies"
```

**Output includes:**
- Layer boundary analysis with violations
- Dependency graph changes visualization
- Pattern compliance assessment
- Recommendations prioritized by severity

## Usage Patterns

### Individual Agent Usage

Simply ask questions that match an agent's focus area, and Claude will automatically trigger the appropriate agent:

```
"Can you check if the tests cover all edge cases?"
→ Triggers pr-test-analyzer

"Review the error handling in the API client"
→ Triggers silent-failure-hunter

"I've added documentation - is it accurate?"
→ Triggers comment-analyzer

"Check this code for security vulnerabilities"
→ Triggers security-reviewer
```

### Comprehensive PR Review

For thorough PR review, ask for multiple aspects:

```
"I'm ready to create this PR. Please:
1. Review test coverage
2. Check for silent failures
3. Verify code comments are accurate
4. Review any new types
5. Security audit
6. General code review"
```

This will trigger all relevant agents to analyze different aspects of your PR.

### Proactive Review

Claude may proactively use these agents based on context:

- **After writing code** → code-reviewer
- **After adding docs** → comment-analyzer
- **Before creating PR** → Multiple agents as appropriate
- **After adding types** → type-design-analyzer
- **After auth/crypto code** → security-reviewer

## Installation

Install from your personal marketplace:

```bash
/plugins
# Find "kuku-pr-review-toolkit"
# Install
```

Or add manually to settings if needed.

## Agent Details

### Confidence Scoring

Agents provide confidence scores for their findings:

**comment-analyzer**: Identifies issues with high confidence in accuracy checks

**pr-test-analyzer**: Rates test gaps 1-10 (10 = critical, must add)

**silent-failure-hunter**: Flags severity (CRITICAL/HIGH/MEDIUM) with language context

**type-design-analyzer**: Rates 4 dimensions on 1-10 scale

**code-reviewer**: Scores issues 0-100 (91-100 = critical)

**security-reviewer**: Scores 0-100 with OWASP category (reports ≥50 by default)

**code-simplifier**: Identifies complexity with language-specific suggestions

**architecture-impact-analyzer**: Rates layer violations and dependency issues by severity (CRITICAL/HIGH/MEDIUM/LOW)

### Output Formats

All agents provide structured, actionable output:
- Clear issue identification
- Specific file and line references
- Explanation of why it's a problem
- Suggestions for improvement
- Prioritized by severity
- Language-specific remediation examples

## Best Practices

### When to Use Each Agent

**Before Committing:**
- code-reviewer (general quality)
- silent-failure-hunter (if changed error handling)
- security-reviewer (if security-sensitive code)

**Before Creating PR:**
- pr-test-analyzer (test coverage check)
- comment-analyzer (if added/modified comments)
- type-design-analyzer (if added/modified types)
- security-reviewer (for auth, crypto, input handling)
- architecture-impact-analyzer (if changes span multiple modules)
- code-reviewer (final sweep)

**After Passing Review:**
- code-simplifier (improve clarity and maintainability)

**During PR Review:**
- Any agent for specific concerns raised
- Targeted re-review after fixes

### Running Multiple Agents

You can request multiple agents to run in parallel or sequentially:

**Parallel** (faster, max 3 concurrent):
```
"Run pr-test-analyzer and comment-analyzer in parallel"
```

**Concurrency Rule**: Before launching agents, output an Execution Plan:
```
## Execution Plan
- Review scope: [scope]
- Total agents: [count]
- Batching required: [Yes/No]
- Batch 1: [agent1, agent2, agent3]
- Batch 2: [agent4, ...]
```

Then execute EXACTLY as planned:
- 4 agents → Batch 1 (3) → wait → Batch 2 (1)
- 8 agents → Batch 1 (3) → wait → Batch 2 (3) → wait → Batch 3 (2)

**Sequential** (when one informs the other):
```
"First review test coverage, then check code quality"
```

## Tips

- **Be specific**: Target specific agents for focused review
- **Use proactively**: Run before creating PRs, not after
- **Address critical issues first**: Agents prioritize findings
- **Iterate**: Run again after fixes to verify
- **Don't over-use**: Focus on changed code, not entire codebase
- **Security first**: Always run security review for sensitive code

## Troubleshooting

### Agent Not Triggering

**Issue**: Asked for review but agent didn't run

**Solution**:
- Be more specific in your request
- Mention the agent type explicitly
- Reference the specific concern (e.g., "test coverage", "security")

### Agent Analyzing Wrong Files

**Issue**: Agent reviewing too much or wrong files

**Solution**:
- Specify which files to focus on
- Reference the PR number or branch
- Mention "recent changes" or "git diff"

## Integration with Workflow

This plugin works great with:
- **build-validator**: Run build/tests before review
- **Project-specific agents**: Combine with your custom agents

**Recommended workflow:**
1. Write code → **code-reviewer**
2. Fix issues → **silent-failure-hunter** (if error handling)
3. Security check → **security-reviewer** (if sensitive code)
4. Architecture check → **architecture-impact-analyzer** (if multi-module changes)
5. Add tests → **pr-test-analyzer**
6. Document → **comment-analyzer**
7. Review passes → **code-simplifier** (polish)
8. Create PR

## Contributing

Found issues or have suggestions? These agents are maintained in:
- User agents: `~/.claude/agents/`
- Project agents: `.claude/agents/` in claude-cli-internal

## License

MIT

## Author

Original: Daisy (daisy@anthropic.com)
Multi-language enhancements: Community contributions

---

**Quick Start**: Just ask for review and the right agent will trigger automatically!
