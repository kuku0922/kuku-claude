# Document Consistency Toolkit

A comprehensive collection of specialized agents for verifying consistency between design documents and code implementation. Supports OpenSpec specifications, top-level architecture design, detailed design documents, and code implementation.

## Overview

This toolkit bundles 4 expert consistency-checking agents that each focus on a specific aspect of document-code alignment. Use them individually for targeted checks or together for comprehensive consistency analysis. All agents leverage LSP and Serena symbolic tools for precise code analysis.

## Code Analysis Tools

All agents have access to powerful code analysis tools:

### LSP Tools
- `find_definition` - Find symbol definitions
- `find_references` - Find all references to a symbol
- `get_diagnostics` - Get language diagnostics (errors, warnings)

### Serena Symbolic Tools
- `get_symbols_overview` - Get file symbols overview
- `find_symbol` - Find specific symbol with body
- `find_referencing_symbols` - Find symbols that reference a symbol
- `search_for_pattern` - Search patterns in code

## Document Hierarchy

```
┌─────────────────────────────────────┐
│     Top-Level Design (Architecture)  │  Strategic decisions, patterns, constraints
├─────────────────────────────────────┤
│     Detailed Design (Key Design)     │  Module-specific implementation details
├─────────────────────────────────────┤
│     OpenSpec (Specifications)        │  GIVEN-WHEN-THEN behavioral requirements
├─────────────────────────────────────┤
│     Implementation (Code)            │  Actual code
└─────────────────────────────────────┘
```

## Supported Document Types

### Top-Level Design (Architecture)
- System architecture overview
- Technology stack decisions
- Cross-cutting concerns (security, logging, monitoring)
- Integration patterns and protocols
- Design principles and constraints

Common locations: `docs/top-level-design/`, `docs/architecture/`, `design/architecture/`

### Detailed Design (Key Design)
- Module-specific implementation details
- API contracts and data models
- Database schemas
- Algorithm specifications
- Security implementation details

Common locations: `docs/key-design/`, `docs/detailed-design/`, `design/modules/`

### OpenSpec (Specifications)
- GIVEN-WHEN-THEN behavioral specifications
- SHALL/SHOULD/MAY requirements
- Acceptance criteria
- Edge cases and error scenarios

Common locations: `openspec/specs/`, `specs/`, `*.spec.md`

## Agents

### 1. spec-impl-checker
**Focus**: OpenSpec vs Code Implementation

**Analyzes:**
- GIVEN-WHEN-THEN scenario compliance
- SHALL/SHOULD/MAY requirement implementation
- Behavioral correctness
- Edge case coverage

**When to use:**
- After implementing a feature
- Before marking a spec as complete
- During code review

**Triggers:**
```
"Check if the auth implementation matches the openspec"
"Does my code comply with the spec?"
"Verify spec implementation"
```

### 2. architecture-design-checker
**Focus**: Top-Level Design vs Detailed Design

**Analyzes:**
- Technology stack compliance
- Architectural pattern adherence
- Cross-cutting concern alignment
- Interface contract consistency

**When to use:**
- After creating a detailed design
- Before implementing a module
- When updating architecture

**Triggers:**
```
"Does the auth detailed design align with the architecture?"
"Check architecture compliance"
"Verify design follows architecture"
```

### 3. design-impl-checker
**Focus**: Detailed Design vs Code Implementation

**Analyzes:**
- API endpoint compliance
- Database schema alignment
- Configuration consistency
- Architectural pattern implementation

**When to use:**
- After implementing a module
- During code review
- Before deployment

**Triggers:**
```
"Check if the auth module matches its detailed design"
"Verify implementation follows design"
"Does the code match the design?"
```

### 4. cross-doc-checker
**Focus**: Cross-Document Consistency

**Analyzes:**
- Document hierarchy alignment
- Cross-reference validity
- Conflict detection
- Orphaned document identification

**When to use:**
- Periodic documentation health check
- After major architecture changes
- Before release

**Triggers:**
```
"Check if all design docs are consistent"
"What docs need updating after this change?"
"Verify documentation consistency"
```

## Usage Patterns

### Individual Agent Usage

Simply ask questions that match an agent's focus area:

```
"Does my implementation match the OpenSpec?"
→ Triggers spec-impl-checker

"Is the detailed design aligned with architecture?"
→ Triggers architecture-design-checker

"Does the code follow the detailed design?"
→ Triggers design-impl-checker
```

### Comprehensive Consistency Check

For thorough consistency analysis:

```
"I'm ready to release this feature. Please:
1. Check spec-implementation consistency
2. Verify design-implementation alignment
3. Check cross-document consistency"
```

### Command Usage

```bash
# Check OpenSpec vs Implementation
/kuku-doc-consistency-toolkit:check-consistency spec-impl

# Check Architecture vs Detailed Design
/kuku-doc-consistency-toolkit:check-consistency arch-design

# Check Detailed Design vs Implementation
/kuku-doc-consistency-toolkit:check-consistency design-impl

# Check all documents for consistency
/kuku-doc-consistency-toolkit:check-consistency cross-doc

# Full consistency check (max 3 agents concurrent)
/kuku-doc-consistency-toolkit:check-consistency full

# Focus on specific module
/kuku-doc-consistency-toolkit:check-consistency design-impl auth
```

**Concurrency Rule**: Before launching agents, output an Execution Plan:
```
## Execution Plan
- Check type: [type]
- Total agents: [count]
- Batching required: [Yes/No]
- Batch 1: [agent1, agent2, agent3]
- Batch 2: [agent4, ...]
```

Then execute EXACTLY as planned:
- 4 agents → Batch 1 (3) → wait → Batch 2 (1)
- 7 agents → Batch 1 (3) → wait → Batch 2 (3) → wait → Batch 3 (1)

## Output Format

All agents provide structured, actionable output:

```markdown
## Consistency Report

### Fully Compliant ✅
- [REQ-001] Requirement name - Implemented correctly

### Partial Compliance ⚠️
| Item | Status | Gap | Location |
|------|--------|-----|----------|
| [REQ-002] | 70% | Missing X | file:line |

### Non-Compliant ❌
| Item | Issue | Expected | Actual | Location |
|------|-------|----------|--------|----------|
| [REQ-003] | Incorrect | A | B | file:line |

### Recommendations
1. Priority fixes
2. Document updates needed
```

## Severity Classification

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | Security/data integrity at risk, core requirement missing |
| **HIGH** | API contract broken, schema mismatch, pattern violated |
| **MEDIUM** | Partial implementation, config differs, edge case missing |
| **LOW** | Minor inconsistency, documentation gap |
| **INFO** | Document needs update to reflect valid implementation |

## Best Practices

### Development Workflow Integration

**Before implementing a feature:**
```
1. Write/update OpenSpec
2. Run: /kuku-doc-consistency-toolkit:check-consistency arch-design
3. Ensure spec aligns with architecture
```

**After implementing a feature:**
```
1. Run: /kuku-doc-consistency-toolkit:check-consistency spec-impl
2. Verify implementation matches spec
3. Update spec if implementation differs intentionally
```

**During code review:**
```
1. Run: /kuku-doc-consistency-toolkit:check-consistency design-impl
2. Ensure code matches detailed design
3. Flag any undocumented changes
```

**Periodic maintenance:**
```
1. Run: /kuku-doc-consistency-toolkit:check-consistency full
2. Address all critical and high issues
3. Update stale references
```

### Tips

- **Start with cross-doc**: Get overview of document health first
- **Focus on modules**: Check specific modules for detailed analysis
- **Run after changes**: Verify consistency after updating docs or code
- **Update both sides**: Fix code OR update docs based on findings
- **Track over time**: Run periodically to catch drift

## Configuration

### Custom Document Paths

If your project uses non-standard paths, specify them in the command:

```
/kuku-doc-consistency-toolkit:check-consistency spec-impl \
  --spec-path=my-specs/ \
  --impl-path=src/
```

### Project-Specific Patterns

The toolkit automatically detects common document patterns:
- OpenSpec: `spec.md`, `*.spec.md`, `specs/`
- Architecture: `*-architecture.md`, `architecture-*.md`
- Detailed Design: `detailed-design.md`, `*-design.md`

## Integration with PR Review Toolkit

This toolkit complements the PR Review Toolkit:

```
1. Write code → pr-review-toolkit (code quality)
2. Check consistency → doc-consistency-toolkit (design alignment)
3. Create PR
```

## Contributing

Found issues or have suggestions? These agents are maintained in:
- User agents: `~/.claude/agents/`
- Project agents: `.claude/agents/`

## License

MIT

## Author

Community contributions

---

**Quick Start**: Just ask about document-code consistency and the right agent will trigger automatically!
