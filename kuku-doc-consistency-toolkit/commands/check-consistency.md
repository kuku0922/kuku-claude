---
description: "Check consistency between design documents and implementation"
argument-hint: "[check-type] [scope]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Document Consistency Check

Run consistency checks between design documents (top-level design, detailed design, OpenSpec) and code implementation.

**Arguments (optional):** "$ARGUMENTS"

## Check Types

Available consistency check types:

| Type | Description | Agent Used |
|------|-------------|------------|
| **spec-impl** | OpenSpec vs Code Implementation | spec-impl-checker |
| **arch-design** | Top-Level Design vs Detailed Design | architecture-design-checker |
| **design-impl** | Detailed Design vs Code Implementation | design-impl-checker |
| **cross-doc** | Cross-document consistency (all docs) | cross-doc-checker |
| **full** | Complete check (all types) | All agents |

## Workflow

### 1. Determine Check Scope

Parse arguments to identify:
- Which check type(s) to run
- Which module/feature to focus on (optional)
- Specific document paths (optional)

### 2. Locate Documents

Find relevant documents based on common patterns:

**Top-Level Design (Architecture):**
```
docs/top-level-design/
docs/architecture/
design/architecture/
*.architecture.md
```

**Detailed Design (Key Design):**
```
docs/key-design/
docs/detailed-design/
design/modules/
*/design.md
*/detailed-design.md
```

**OpenSpec:**
```
openspec/specs/
specs/
*.spec.md
spec.md
```

### 3. Launch Appropriate Agents

**IMPORTANT: Concurrency Limit (Max 3 Parallel Agents)**

Batching Rule: Always launch up to 3 agents per batch until fewer than 3 remain.

```
remaining = total_agents
while remaining > 0:
    batch_size = min(3, remaining)
    launch batch_size agents in parallel
    wait for all to complete
    remaining -= batch_size
```

Examples:
- 4 agents → Batch 1 (3) → wait → Batch 2 (1)
- 5 agents → Batch 1 (3) → wait → Batch 2 (2)
- 6 agents → Batch 1 (3) → wait → Batch 2 (3)
- 7 agents → Batch 1 (3) → wait → Batch 2 (3) → wait → Batch 3 (1)

WRONG: 7 agents → 3 → 2 → 1 → 1 (decreasing batch sizes)
RIGHT: 7 agents → 3 → 3 → 1 (always max out each batch)

Based on check type:

**spec-impl**: Launch spec-impl-checker
- Input: OpenSpec files + implementation code paths
- Output: Spec compliance report

**arch-design**: Launch architecture-design-checker
- Input: Architecture docs + detailed design docs
- Output: Architecture alignment report

**design-impl**: Launch design-impl-checker
- Input: Detailed design docs + implementation code
- Output: Design compliance report

**cross-doc**: Launch cross-doc-checker
- Input: All document types
- Output: Cross-document consistency report

**full**: Launch all agents in batches (max 3 concurrent)
- Batch agents and wait for completion between batches
- Aggregate all reports into unified summary

### 4. Aggregate Results

Combine findings into unified report:

```markdown
# Consistency Check Summary

## Check Type: [type]
## Scope: [module/feature or "all"]

### Critical Issues (Must Fix)
- [checker]: Issue description [location]

### High Priority (Should Fix)
- [checker]: Issue description [location]

### Medium Priority (Consider)
- [checker]: Issue description [location]

### Document Updates Needed
- [document]: Suggested update

### Overall Compliance
- Spec-Implementation: X%
- Architecture-Design: Y%
- Design-Implementation: Z%
- Cross-Document: W%
```

## Usage Examples

**Check OpenSpec vs Implementation:**
```
/kuku-doc-consistency-toolkit:check-consistency spec-impl
```

**Check Architecture vs Detailed Design:**
```
/kuku-doc-consistency-toolkit:check-consistency arch-design
```

**Check Detailed Design vs Implementation:**
```
/kuku-doc-consistency-toolkit:check-consistency design-impl auth
# Focuses on auth module
```

**Full consistency check:**
```
/kuku-doc-consistency-toolkit:check-consistency full
```

**Cross-document check for specific module:**
```
/kuku-doc-consistency-toolkit:check-consistency cross-doc user-management
```

## Document Path Configuration

If your project uses non-standard paths, specify them:

```
/kuku-doc-consistency-toolkit:check-consistency spec-impl \
  --spec-path=my-specs/ \
  --impl-path=src/
```

## Agent Descriptions

**spec-impl-checker**:
- Parses GIVEN-WHEN-THEN specifications
- Maps requirements to code
- Verifies behavioral compliance
- Reports missing/incorrect implementations

**architecture-design-checker**:
- Compares architectural decisions to detailed designs
- Checks technology stack compliance
- Verifies pattern usage
- Reports architectural violations

**design-impl-checker**:
- Compares API/DB schemas to code
- Verifies configuration compliance
- Checks architectural patterns in code
- Reports design drift

**cross-doc-checker**:
- Builds document hierarchy map
- Traces requirements across levels
- Identifies conflicts and gaps
- Reports orphaned documents

## Tips

- **Start with cross-doc**: Get overview of document health first
- **Focus on modules**: Check specific modules for detailed analysis
- **Run after changes**: Verify consistency after updating docs or code
- **Update both sides**: Fix code OR update docs based on findings
- **Track over time**: Run periodically to catch drift

## Integration with Development Workflow

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
4. Archive orphaned documents
```

## Notes

- Agents analyze documents and code without modifying them
- Reports include specific file:line references
- Recommendations indicate whether to fix code or update docs
- All agents support multiple programming languages
