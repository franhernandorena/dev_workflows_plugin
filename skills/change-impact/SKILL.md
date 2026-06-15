---
name: change-impact
version: 1.0.0
description: Before task-plan or any complex change, analyzes which modules, files, tests, and dependencies will be affected
---

# Change Impact — Analyze Blast Radius Before Coding

## Overview
Before writing any code, analyzes the proposed change to identify which modules, files, tests, and dependencies will be affected. Helps estimate risk and effort by surfacing the full blast radius of a change before implementation begins. Complements `task-plan` by providing the dependency-aware context needed for accurate planning.

## When to use
- Before starting a complex cross-module change
- When you need to estimate effort or risk for a feature
- Before refactoring shared code or interfaces
- When changing a public API, type definition, or database schema
- As a prerequisite to `task-plan` for large tasks

## When NOT to use
- Trivial changes (typo fix, single-file cosmetic change) → go straight to `task-do`
- Urgent hotfix → use `task-hotfix`
- You already know the full impact from experience

## Output
- Markdown impact analysis printed inline with: summary stats, affected files, dependency chains, test coverage gaps, risk assessment

## Full Prompt

# CHANGE IMPACT — Blast Radius Analysis

## RULE: This skill analyzes only. No code changes. Output is an impact report.

---

## Phase 1 — Understand the Proposed Change

### 1.1 Clarify the change
Restate the proposed change and identify:
- **Primary files** that will be directly modified
- **Primary symbols** (functions, classes, types) involved
- **Nature of change**: addition, modification, deletion, rename, refactor

### 1.2 Ask clarifying questions (if needed)
If the change is ambiguous, ask:
1. What is the specific goal of this change? (fix, feature, refactor, performance)
2. Which files or symbols are you planning to touch?
3. Is this a public API or internal change?
4. Are there any constraints? (backward compatibility, performance targets, deadline)

---

## Phase 2 — Dependency Analysis

For each primary file or symbol, trace:

### 2.1 Direct dependencies (what it imports/uses)
```bash
# Python
grep -n "^import\|^from" <file>.py 2>/dev/null
# TypeScript/JavaScript
grep -n "^import " <file>.ts 2>/dev/null
```

### 2.2 Direct dependents (what imports/uses it)
```bash
# Search for all files that reference this symbol
grep -rn "symbol_name" --include="*.py" -l 2>/dev/null | head -20
grep -rn "symbol_name" --include="*.ts" -l 2>/dev/null | head -20
```

### 2.3 Transitive impact (dependents of dependents)
For each file found in 2.2 that is NOT a test file, run 2.2 again (one level deep).

### 2.4 Cross-repo impact (if workspace)
Check sibling repos that depend on this repo (from WORKSPACE_OVERVIEW.md or package manager configs):
```bash
grep -rn "repo-name" --include="*.json" --include="*.toml" --include="*.yaml" ../*/ 2>/dev/null | head -10
```

---

## Phase 3 — Test Coverage Analysis

### 3.1 Find related tests
```bash
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.spec.ts" \) \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' 2>/dev/null | \
  while read f; do grep -l "primary_symbol\|primary_module" "$f" 2>/dev/null; done
```

### 3.2 Assess coverage gaps
- Do the affected modules have tests?
- Are there integration tests for the affected data flow?
- Are edge cases covered (empty state, error state, boundary conditions)?

---

## Phase 4 — Risk Assessment

Rate each affected area:

| Area | Risk (H/M/L) | Reason |
|------|-------------|--------|
| Module A | H | Public API, 5 dependents, no tests |
| Module B | M | Internal, 2 dependents, has tests |
| types.py | L | Type-only change, no runtime impact |

### Risk factors to flag:
- 🔴 **H**: Breaking public API, database migration, security impact, no test coverage
- 🟡 **M**: Internal API change, multiple dependents, partial test coverage
- 🟢 **L**: Single file, internal, well-tested

---

## Phase 5 — Impact Report

Synthesize findings into a structured report:

```markdown
# Change Impact Report

## Summary
- **Primary files**: 2
- **Direct dependents**: 5 files across 2 modules
- **Transitive impact**: 12 files across 3 modules
- **Tests affected**: 4 test files, 2 new tests needed
- **Overall risk**: Medium

## Affected Files

### Direct (modified)
| File | Lines | Risk |
|------|-------|------|
| `src/auth/login.ts` | 45 | H |
| `src/auth/session.ts` | 120 | M |

### Dependent (may break)
| File | Dependents | Risk |
|------|-----------|------|
| `src/api/users.ts` (imports login) | 3 callers | H |
| `src/middleware/auth.ts` (imports session) | 2 callers | M |

## Test Coverage
| File | Has tests? | Coverage | New tests needed |
|------|-----------|----------|-----------------|
| `src/auth/login.ts` | ✅ yes | 70% | 2 (edge cases) |
| `src/auth/session.ts` | ✅ yes | 85% | 0 |
| `src/api/users.ts` | ❌ no | 0% | 3 (integration) |

## Recommendations
- Add tests for `src/api/users.ts` before making changes
- Consider breaking the login change into 2 smaller PRs to reduce risk
- Run `pytest -xvs tests/test_auth*` before and after changes
```

---

## Rules
- Read-only. No code changes.
- Always include risk ratings with reasoning.
- If cross-repo impact is detected via WORKSPACE_OVERVIEW.md, include it explicitly.
- Output analysis inline. Do not save to disk unless asked.
- Never suggest changes — only surface what the change would affect.
