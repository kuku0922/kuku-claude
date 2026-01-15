---
description: "Feature-level code review with boundary discovery and multi-agent orchestration"
argument-hint: "[entry-point(s)] [depth:quick|standard|deep]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "mcp__cclsp__find_definition", "mcp__cclsp__find_references", "mcp__cclsp__get_diagnostics", "mcp__serena__get_symbols_overview", "mcp__serena__find_symbol", "mcp__serena__find_referencing_symbols", "mcp__serena__search_for_pattern", "mcp__serena__list_dir", "mcp__serena__find_file"]
---

# Feature-Level Code Review

Perform comprehensive feature-level code review by discovering feature boundaries and coordinating multiple specialized review agents.

**User Input**: "$ARGUMENTS"

---

## ⚠️ CRITICAL: Agent Concurrency Limit (Max 3)

**Before launching ANY agents, you MUST output an Execution Plan:**

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

**Then execute EXACTLY as planned.**

| Total Agents | Batching Strategy |
|--------------|-------------------|
| 1-3 | Single batch, launch all together |
| 4-6 | Batch 1 (3) → **wait for completion** → Batch 2 (remaining) |
| 7+ | Batch 1 (3) → **wait** → Batch 2 (3) → **wait** → Batch 3 (remaining) |

---

## Workflow Overview

### Phase 1: Boundary Discovery (Command executes directly - NOT an agent)
### Phase 2: Generate Execution Plan
### Phase 3: Launch Review Agents in Batches
### Phase 4: Aggregate Results

---

## Phase 1: Feature Boundary Discovery

**DO NOT skip this phase. Boundary discovery is the foundation of feature-level review.**

### 1.1 Parse User Input

Extract from "$ARGUMENTS":
- **Entry Point(s)**: Function, class, component, or directory (comma-separated for multiple)
- **Depth** (optional, default: standard): `quick`, `standard`, `deep`

### 1.2 Tools for Boundary Discovery

> **使用优先级**：符号级代码检索时，LSP > Serena > Grep

**LSP Tools** (Preferred):
```
mcp__cclsp__find_definition(file_path, symbol_name)   # Find symbol definition
mcp__cclsp__find_references(file_path, symbol_name)   # Find all usages
```

**Serena Tools**:
```
mcp__serena__get_symbols_overview(relative_path)      # File structure
mcp__serena__find_symbol(name_path, include_body)     # Symbol with code
mcp__serena__find_referencing_symbols(name_path, path) # References
mcp__serena__search_for_pattern(pattern, path)        # Pattern search
```

### 1.3 Trace Call Chain

From each entry point, discover ALL related code:

```
[FRONTEND]                          [BACKEND]
Component/Page                      Controller/Handler
    └── Hook/Composable                 └── Service
        └── API Client                      └── Repository
            │                                   └── Database
            └── HTTP Request ──────────────────►
```

**Frontend indicators**: `.tsx`, `.jsx`, `.vue`, `components/`, `hooks/`, `stores/`
**Backend indicators**: `controllers/`, `services/`, `repositories/`, `*Handler.*`
**Shared**: Type definitions, validation schemas, constants

### 1.4 Output Feature Boundary

```markdown
## Feature Boundary: [Name]

### Entry Points
- [file:line] SymbolName (frontend/backend)

### Files Discovered ([X] total)

**Frontend** ([X] files)
- path/Component.tsx - UI Component
- path/useHook.ts - State Hook
- path/api.ts - API Client

**Backend** ([X] files)
- path/controller.go - API Handler
- path/service.go - Business Logic
- path/repository.go - Data Access

**Shared** ([X] files)
- path/types.ts - Type definitions

### Call Chain
[Entry] → Controller.method()
         ├── Service.logic()
         │   └── Repository.query()
         └── Response → Frontend
```

---

## Phase 2: Determine Agents and Generate Plan

### 2.1 Available Review Agents (8 Total)

| Agent | Focus | When to Include |
|-------|-------|-----------------|
| feature-code-reviewer | Code quality, CLAUDE.md compliance | Always |
| feature-error-handler | Error handling, silent failures | Always |
| feature-security-reviewer | Security vulnerabilities, OWASP | auth/payment or standard+ |
| feature-type-analyzer | Type design, API contract types | If types found |
| feature-test-analyzer | Test coverage quality | If tests exist or deep |
| feature-architecture-reviewer | Layer separation, dependencies | Always |
| feature-comment-analyzer | Comment accuracy, documentation | standard+ |
| feature-code-simplifier | Code clarity, simplification | deep only |

### 2.2 Depth-Based Agent Selection

| Depth | Agents | Description |
|-------|--------|-------------|
| quick | 3 | code-reviewer, error-handler, architecture-reviewer |
| standard | 5-6 | + security-reviewer, type-analyzer, comment-analyzer |
| deep | 8 | All agents including test-analyzer, code-simplifier |

### 2.3 Generate Execution Plan (MANDATORY)

**Output this BEFORE launching any agents:**

```markdown
## Execution Plan
- Feature: [name]
- Entry Points: [list]
- Files Discovered: [count] (Frontend: X, Backend: X, Shared: X)
- Depth: [depth]
- Total Agents: [count]
- Batching Required: [Yes/No]
- Batch 1: [agent1, agent2, agent3]
- Batch 2: [agent4, ...]
```

---

## Phase 3: Launch Review Agents

### 3.1 Prepare Boundary Data for Agents

Each agent receives:

```markdown
## Feature Boundary Data

[Paste boundary from Phase 1]

## Instructions
1. ONLY review files in the boundary above
2. Focus on feature-level issues (cross-file, call chain)
3. Check frontend-backend consistency at API boundaries
4. Provide findings with file:line references
```

### 3.2 Execute Batches

**Example for deep review (8 agents):**

**Batch 1**: Launch up to 3 agents in parallel using Task tool
```
[Task: feature-code-reviewer]
[Task: feature-error-handler]
[Task: feature-security-reviewer]
```

**Wait for Batch 1 to complete**

**Batch 2**: Launch next 3 agents
```
[Task: feature-architecture-reviewer]
[Task: feature-type-analyzer]
[Task: feature-comment-analyzer]
```

**Wait for Batch 2 to complete**

**Batch 3**: Launch remaining agents
```
[Task: feature-test-analyzer]
[Task: feature-code-simplifier]
```

**NEVER launch more than 3 agents simultaneously.**

---

## Phase 4: Aggregate Results

### 4.1 Collect and Merge Findings

After all agents complete, organize by severity:

```markdown
# Feature Review: [Name]

## Overview
- Entry Points: [list]
- Files: [count] (Frontend: X, Backend: X, Shared: X)
- Depth: [depth]
- Agents: [list]

## Feature Boundary
[Boundary visualization]

---

## Critical Issues (Must Fix)
| # | Category | Location | Issue | Agent |
|---|----------|----------|-------|-------|

## Important Issues (Should Fix)
| # | Category | Location | Issue | Agent |
|---|----------|----------|-------|-------|

## Suggestions
| # | Category | Location | Suggestion | Agent |
|---|----------|----------|------------|-------|

---

## Cross-Cutting Observations
- **Frontend-Backend Consistency**: [assessment]
- **Error Flow**: [assessment]
- **API Contract**: [assessment]

---

## Summary
**Health Score**: X/100
**Recommendation**: [Ready / Needs fixes / Major refactoring]

**Priority Actions**:
1. [Most critical]
2. [Second]
3. [Third]
```

---

## Usage Examples

**Standard review**:
```
/kuku-feature-review-toolkit:review-feature AuthController.login
```

**Frontend + Backend entry points**:
```
/kuku-feature-review-toolkit:review-feature LoginForm,AuthController.login
```

**Directory entry**:
```
/kuku-feature-review-toolkit:review-feature src/features/payment/
```

**Quick check**:
```
/kuku-feature-review-toolkit:review-feature UserService.register quick
```

**Deep review**:
```
/kuku-feature-review-toolkit:review-feature PaymentProcessor.process deep
```

---

## Notes

- This is NOT a git-diff review - it reviews complete feature implementation
- Boundary discovery is mandatory before agent launch
- Frontend code is automatically included when detected
- Use `deep` for security-critical features (auth, payment)
- Always verify boundary before reviewing findings
