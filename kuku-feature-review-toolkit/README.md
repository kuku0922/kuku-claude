# Feature Review Toolkit

A feature-level code review toolkit with boundary discovery and multi-agent orchestration. Unlike diff-based reviews, this toolkit traces complete feature boundaries across frontend and backend, then coordinates specialized review agents for comprehensive analysis.

## Overview

This plugin provides:
1. **Feature Boundary Discovery** - Traces call chains from entry points to discover all related code
2. **Multi-Agent Review** - Coordinates 8 specialized review agents
3. **Frontend-Backend Coverage** - Automatically includes both layers when detected
4. **Concurrent Execution** - Manages agent concurrency (max 3 parallel)

## Key Difference from PR Review

| Aspect | PR Review (kuku-pr-review-toolkit) | Feature Review (this toolkit) |
|--------|-----------------------------------|-------------------------------|
| Scope | `git diff` changes | Complete feature boundary |
| Entry Point | Changed files | Feature entry point(s) |
| Coverage | Only modified code | All code related to the feature |
| Use Case | Before commit/PR | Feature audit, architecture review |

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

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Boundary Discovery (Command executes directly)     │
│  - Parse entry points                                        │
│  - Trace call chains using LSP/Serena                        │
│  - Detect frontend/backend boundaries                        │
│  - Build feature boundary map                                │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: Execution Planning                                 │
│  - Determine applicable agents based on depth                │
│  - Generate execution plan with batching                     │
│  - Output plan BEFORE launching agents                       │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: Multi-Agent Review                                 │
│  - Batch 1: Up to 3 agents in parallel                       │
│  - Wait for completion                                       │
│  - Batch 2: Remaining agents                                 │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: Results Aggregation                                │
│  - Collect all agent findings                                │
│  - Organize by severity                                      │
│  - Provide cross-cutting observations                        │
└─────────────────────────────────────────────────────────────┘
```

## Agents (8 Total)

### 1. feature-code-reviewer
**Focus**: Code quality across feature boundary

- CLAUDE.md compliance
- Cross-file naming consistency
- Code style alignment (frontend ↔ backend)
- Bug detection

### 2. feature-error-handler
**Focus**: Error flow from backend to frontend

- Silent failure detection
- Error propagation tracing
- User-facing error message quality
- Language-specific anti-patterns

### 3. feature-security-reviewer
**Focus**: Security across complete attack surface

- OWASP Top 10 vulnerabilities
- Data flow from frontend to backend
- Trust boundary validation
- Language-specific security patterns

### 4. feature-type-analyzer
**Focus**: Type consistency and design

- Frontend-backend type alignment
- API contract type consistency
- Type design quality (encapsulation, invariants)
- Naming consistency across layers

### 5. feature-test-analyzer
**Focus**: Test coverage across feature

- Behavioral coverage (not just line coverage)
- Frontend and backend test balance
- Critical path test gaps
- Integration test presence

### 6. feature-architecture-reviewer
**Focus**: Structural integrity

- Layer separation (controller → service → repository)
- Dependency direction (no circular dependencies)
- API contract consistency
- Feature boundary clarity

### 7. feature-comment-analyzer
**Focus**: Documentation accuracy and consistency

- Comment accuracy vs actual code
- Cross-file documentation consistency
- Comment rot and technical debt
- API documentation alignment (frontend ↔ backend)

### 8. feature-code-simplifier
**Focus**: Code clarity and simplification

- Complexity hotspot identification
- Cross-file pattern consolidation
- Refactoring opportunities
- Clarity over brevity

## Agent Concurrency

**Before launching ANY agents, an Execution Plan is required:**

```
## Execution Plan
- Feature: [name]
- Entry Points: [list]
- Files Discovered: [count] (Frontend: X, Backend: X, Shared: X)
- Depth: [quick|standard|deep]
- Total Agents: [count]
- Batching Required: [Yes/No]
- Batch 1: [agent1, agent2, agent3]
- Batch 2: [agent4, agent5, agent6]
```

| Total Agents | Batching Strategy |
|--------------|-------------------|
| 1-3 | Single batch, launch together |
| 4-6 | Batch 1 (3) → wait → Batch 2 (remaining) |
| 7+ | Batch 1 (3) → wait → Batch 2 (3) → wait → Batch 3 |

## Depth Levels

| Depth | Agents | Use Case |
|-------|--------|----------|
| quick | 3 (code-reviewer, error-handler, architecture) | Quick sanity check |
| standard | 5-6 (+ security, type, comment) | Normal feature review |
| deep | 8 (all agents including test, simplifier) | Critical features (auth, payment) |

## Usage

### Basic Usage

```bash
# Review a backend entry point
/kuku-feature-review-toolkit:review-feature AuthController.login

# Review a frontend component
/kuku-feature-review-toolkit:review-feature LoginForm

# Review a directory
/kuku-feature-review-toolkit:review-feature src/features/payment/
```

### Multiple Entry Points (Full-Stack Feature)

```bash
# Include both frontend and backend entry points
/kuku-feature-review-toolkit:review-feature LoginForm,AuthController.login
```

### Depth Control

```bash
# Quick check
/kuku-feature-review-toolkit:review-feature UserService.register quick

# Deep review for critical features
/kuku-feature-review-toolkit:review-feature PaymentProcessor.process deep
```

## Output Format

```markdown
# Feature Review: [Name]

## Overview
- Entry Points: [list]
- Files: [count] (Frontend: X, Backend: X, Shared: X)
- Depth: [depth]
- Agents: [list]

## Feature Boundary
[Visualization of call chain]

## Critical Issues (Must Fix)
| # | Category | Location | Issue | Agent |
|---|----------|----------|-------|-------|

## Important Issues (Should Fix)
| # | Category | Location | Issue | Agent |
|---|----------|----------|-------|-------|

## Suggestions
| # | Category | Location | Suggestion | Agent |
|---|----------|----------|------------|-------|

## Cross-Cutting Observations
- Frontend-Backend Consistency
- Error Flow
- API Contract

## Summary
- Health Score: X/100
- Priority Actions
- Recommendation
```

## Best Practices

### When to Use Feature Review

- **Feature audit** before release
- **Architecture review** for complex features
- **Onboarding** to understand a feature
- **After major refactoring** to verify integrity

### Tips

1. **Be specific with entry points** - Better discovery with clear entry points
2. **Use multiple entry points** for full-stack features
3. **Use `deep` for critical features** - Payment, auth, security-sensitive
4. **Verify boundary first** - Check discovered files before reviewing findings
5. **Focus on cross-cutting issues** - Feature-level reviews excel here

## Integration with Other Toolkits

```
Development Workflow:

1. Write code
2. /kuku-pr-review-toolkit:review-pr        ← PR-level review (git diff)
3. /kuku-feature-review-toolkit:review-feature ← Feature-level review (boundary)
4. /kuku-doc-consistency-toolkit:check-consistency ← Doc alignment
5. Create PR
```

## Supported Languages

### Frontend
- TypeScript/JavaScript (React, Vue, Angular, Svelte)

### Backend
- Go (Gin, Echo, Fiber)
- Python (Django, FastAPI, Flask)
- Java (Spring Boot, Quarkus)
- Rust (Actix, Axum)
- Node.js (Express, NestJS)

## Installation

```bash
/plugins
# Find "kuku-feature-review-toolkit"
# Install
```

## License

MIT

## Author

Community
