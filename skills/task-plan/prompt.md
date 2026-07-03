# TASK PLANNING — Detailed Task Breakdown

## RULE: This prompt plans only. No code changes. Output is a task file in `.context8/tasks/`.

Use this when you need a thorough plan before starting work — complex features, cross-module changes, risky refactors, or anything where implementation order matters.

---

## Phase 0 — Question First

Before doing any planning work, the agent MUST:

1. Restate the task in 2-3 sentences, in its own words, including:
   - What is being asked.
   - Why it matters.
   - The target environment (`dev` / `beta` / `prod`).
2. If the task is ambiguous, STOP here. Write the interpretation and ask
   the user to confirm or correct it. Do not proceed to planning.
3. If the user has not stated the environment, ASK.

This step exists because plans based on silent assumptions are the most
common cause of wasted implementation work.

---

## Phase 1 — Load Context

Read in this exact order. Do not skip.

1. **`.context8/AGENT_CONTEXT.md`** — tech stack, architecture, patterns, conventions, gotchas.
2. **`.context8/PROJECT_OVERVIEW.md`** — high-level orientation.
3. **Relevant architecture docs** (only what applies to this task):
   - `.context8/architecture/data_flow.md` → if touching data pipelines, ingestion, or APIs
   - `.context8/architecture/key_patterns.md` → if adding features or refactoring
   - `.context8/architecture/module_map.md` → if crossing module boundaries
   - `.context8/architecture/infrastructure.md` → if touching config, env vars, or deployment

If `.context8/` does not exist: stop and run `project-init` first.

---

## Phase 2 — Understand the Task

Before planning anything, answer these questions in writing (they become sections in the task file):

1. **What is being asked?** Restate the task in your own words. One paragraph.
2. **Why does it matter?** Business or technical reason. One sentence.
3. **What does "done" look like?** Concrete, observable outcomes. List format.
4. **What are the boundaries?** What is explicitly out of scope.
5. **What is unknown or risky?** Unknowns that could derail the plan. Surface them now.

If the task is ambiguous, stop here. Write your interpretation and ask for confirmation before planning further.

---

## Phase 3 — Codebase Reconnaissance

Run targeted exploration relevant to this specific task. Only read what is needed.

### 3.0 Consult the code-review-graph (preferred over grep for callers/imports)

```bash
# Use ctx_execute to keep the graph out of conversation memory
sqlite3 .code-review-graph/graph.db "SELECT name FROM sqlite_master WHERE type='table';"
# Then for each primary file: list its callers and importers from the graph
```
If the graph is missing or stale, fall back to `grep` per 3.1.

### 3.1 Find affected files
```bash
# Find files likely touched by this task (adjust patterns to the task)
grep -r "[relevant keyword]" --include="*.py" -l 2>/dev/null | head -20
grep -r "[relevant keyword]" --include="*.ts" -l 2>/dev/null | head -20
find . -name "[relevant filename pattern]" -not -path '*/node_modules/*' | sort
```

### 3.2 Read entry points and interfaces
- Read every file that will be modified (fully — no skimming).
- Read callers of functions you will change.
- Read any interfaces, types, or schemas the change must conform to.

### 3.3 Check existing tests
```bash
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.spec.ts" \) \
     -not -path '*/node_modules/*' | xargs grep -l "[relevant keyword]" 2>/dev/null | head -10
```
Read all relevant test files. Note: what's covered, what's missing, what will break.

### 3.4 Check git history for context
```bash
git log --oneline --follow -10 -- [relevant file path]
git log --oneline --all --grep="[relevant keyword]" | head -10
```

---

## Phase 4 — Build the Plan

Produce a detailed step-by-step plan. Each step must be atomic, independently verifiable, and ordered by dependency.

### Step format
```
## Step N: [verb + specific thing]

**Files**: `path/to/file.py`, `path/to/other.ts`
**Depends on**: Step X (or "none")
**Estimated complexity**: trivial | small | medium | large
**Reversible**: yes | no | partially

### What
[Precise description of what changes in each file. Not vague. Name functions, classes, fields.]

### Why
[Why this step is needed. What breaks if skipped.]

### How to verify
[Exact command or observable behavior that confirms this step is complete.]

### Risks
[What could go wrong. Empty if none.]
```

### Ordering rules
- Database migrations before application code.
- Interface/type changes before implementations.
- Shared utilities before callers.
- Tests last (or alongside, never before the code exists).
- Reversible steps before irreversible ones.

---

## Phase 5 — Write the Task File

Create the file at: `.context8/tasks/YYYY-MM-DD_short_description.md`

Use this structure:

```markdown
# Task: [clear, specific title]

**Date**: YYYY-MM-DD
**Status**: Planned
**Environment**: dev | beta | prod
**Branch**: [branch name — create if needed: type/short-description]
**Estimated total complexity**: trivial | small | medium | large | XL

## Objective
[One paragraph: what needs to be done and why. Reuse Phase 2 answer.]

## Acceptance Criteria
- [ ] [Concrete, observable, testable. No vague criteria like "works correctly".]
- [ ] [Each criterion maps to at least one step in the plan.]
- [ ] [Include: tests pass, no regressions, docs updated if needed.]

## Out of Scope
- [Explicit boundaries. Prevents scope creep during implementation.]

## Unknowns & Risks
| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| [X] | high/med/low | [how to handle it] |

## Implementation Plan

[Paste all steps from Phase 4 here, in order.]

## Dependencies
[External: other tasks, PRs, or deploys that must complete before this one starts.]
[Internal: none (if this is self-contained).]

## Files to Modify
| File | Change type | Notes |
|------|-------------|-------|
| `path/to/file.py` | modify / create / delete | [what changes] |

## Files to Read (before starting)
- `path/to/file.py` — [why it must be read]

## Test Plan
- [ ] Run existing tests before starting (baseline).
- [ ] [Specific tests that cover the change.]
- [ ] [New tests to write and where.]
- [ ] Run full test suite after all steps complete.

## Progress Log
(filled in during implementation)

## Decisions Made
(filled in during implementation)

## Blockers
(filled in during implementation)
```

---

## Phase 6 — Validate the Plan

Before handing off this plan for implementation, verify:

- [ ] Every acceptance criterion maps to at least one step.
- [ ] Every step has a "how to verify" check.
- [ ] Steps are ordered correctly (no step depends on a later step).
- [ ] All files to be modified are listed.
- [ ] Unknowns and risks are explicitly stated (not hidden).
- [ ] No implementation has started (this is planning only).
- [ ] The branch name follows the project's naming convention.
- [ ] If the task is XL: consider splitting into multiple task files with explicit handoff points.

---

## Rules
- Planning means producing the task file. It does not mean writing any application code.
- If you cannot plan without reading more code: read the code in Phase 3, then plan. Never skip directly to implementing.
- If a step is "large" or "XL": break it down further until every step is "medium" or smaller.
- If a risk has no mitigation: flag it explicitly and ask before proceeding.
- Write all documentation in English.
- Do not invent steps for hypothetical future requirements. Plan only what is asked.
