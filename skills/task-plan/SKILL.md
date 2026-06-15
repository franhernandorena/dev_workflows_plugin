---
name: task-plan
version: 1.0.0
description: Use before implementing any complex feature, cross-module change, or risky refactor — produces a detailed step-by-step task file with acceptance criteria, risks, and ordered implementation steps
---

# Task Plan — Detailed Task Breakdown

## Overview
Planning-only prompt. Loads project context, understands the task, runs targeted codebase reconnaissance, and produces detailed `.context8/tasks/` files with ordered steps, acceptance criteria, unknowns, risks, and a test plan. Supports single repos (one task file) and multi-repo workspaces (root-index + per-repo task files). No application code is written.

## When to use
- Complex features spanning multiple files or modules
- Risky refactors where implementation order matters
- Any task where you want a written plan before starting
- Use when the task is ambiguous and you need to force clarification first

## When NOT to use
- Task is trivial and well-understood → go straight to `task-do`
- Hotfix needed urgently → use `task-hotfix`

## Output
- Single repo: `.context8/tasks/YYYY-MM-DD_[description].md` — complete task file with status "Planned"
- Workspace (multi-repo): root-index task file + per-repo task files in each child repo's `.context8/tasks/`

## Full Prompt

# TASK PLANNING — Detailed Task Breakdown

## RULE: This prompt plans only. No code changes. Output is a task file in `.context8/tasks/`.

Use this when you need a thorough plan before starting work — complex features, cross-module changes, risky refactors, or anything where implementation order matters.

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

### 1.1 Detect context: workspace or single repo
```bash
ls .context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE" || echo "NOT_WORKSPACE_ROOT"
```

If `WORKSPACE_OVERVIEW.md` exists, the current folder is a **multi-repo workspace parent**.
Read it now to understand the workspace structure and which repos are involved.

**If NOT a workspace root**: check if this repo is a child of a multi-repo workspace.
```bash
ls ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE_CHILD" || echo "SINGLE_REPO"
```

If `../../.context8/WORKSPACE_OVERVIEW.md` exists, this repo is a **child of a multi-repo workspace**.
Read the parent WORKSPACE_OVERVIEW.md for sibling context (high-level: what other repos exist and what they do). This prevents planning cross-repo work in a single-repo task.

**Workspace mode** → output will be a root-index task file + per-repo task files.
**Workspace child mode** → output is one task file scoped to this repo, with workspace context (sibling awareness).
**Single repo mode** → output is one task file (current behavior).

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

Route based on context detected in Phase 1.1.

### 5.1 Single repo mode

Create `.context8/tasks/YYYY-MM-DD_short_description.md` with the structure below:

```markdown
# Task: [clear, specific title]

**Date**: YYYY-MM-DD
**Status**: Planned
**Branch**: [branch name — create if needed: type/short-description]
**Estimated total complexity**: trivial | small | medium | large | XL

## Objective
[One paragraph: what needs to be done and why. Reuse Phase 2 answer.]

## Acceptance Criteria
- [ ] [Concrete, observable, testable.]
- [ ] [Each criterion maps to at least one step.]
- [ ] [Include: tests pass, no regressions, docs updated if needed.]

## Out of Scope
[Explicit boundaries. Prevents scope creep during implementation.]

## Unknowns & Risks
| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| [X] | high/med/low | [how to handle it] |

## Implementation Plan
[Paste all steps from Phase 4 here, in order.]

## Dependencies
[External: other tasks, PRs, or deploys.]
[Internal: none (if self-contained).]

## Files to Modify
| File | Change type | Notes |
|------|-------------|-------|
| `path/to/file.py` | modify / create / delete | [what changes] |

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

### 5.2 Workspace mode (multi-repo)

Create root-index + per-repo task files.

#### 5.2.1 Root-index task file

`.context8/tasks/YYYY-MM-DD_short_description.md`

```markdown
# Task: [clear, specific title]

**Date**: YYYY-MM-DD
**Status**: Planned
**Type**: Workspace (multi-repo)

## Objective
[What needs to be done and why. Reuse Phase 2 answer.]

## Acceptance Criteria
- [ ] [Cross-repo criteria — behaviors that span repos]
- [ ] [Per-repo criteria, grouped by repo]

## Repo Tasks

| Repo | Task File | Status | Description |
|------|-----------|--------|-------------|
| `frontend/` | `../../frontend/.context8/tasks/YYYY-MM-DD_frontend.md` | Planned | [one-liner] |
| `backend/` | `../../backend/.context8/tasks/YYYY-MM-DD_backend.md` | Planned | [one-liner] |

## Cross-repo Dependencies
[Ordering constraints between repos. E.g., "Backend API first, then frontend consumes it."]

## Unknowns & Risks
| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| [X] | high/med/low | [how to handle it] |

## Decisions Made
(filled in during implementation)

## Blockers
(filled in during implementation)
```

#### 5.2.2 Per-repo task files

For each repo with work, create `[repo]/.context8/tasks/YYYY-MM-DD_[repo]_description.md`:

```markdown
# Task: [repo name] — [clear, specific title]

**Date**: YYYY-MM-DD
**Status**: Planned
**Parent task**: `../../.context8/tasks/YYYY-MM-DD_short_description.md`
**Branch**: [branch name — create if needed: type/short-description]

## Objective
[What this specific repo needs to do. Scoped to this repo only.]

## Acceptance Criteria
- [ ] [Concrete, observable, testable.]
- [ ] [Each criterion maps to at least one step.]
- [ ] [Tests pass, no regressions, docs updated.]

## Out of Scope
[Work that belongs to sibling repos — be explicit about boundaries.]

## Implementation Plan
[Steps specific to this repo from Phase 4, in order.]

## Dependencies
[Cross-repo: what must be completed in other repos first.]
[Internal: none (if self-contained within this repo).]

## Files to Modify
| File | Change type | Notes |
|------|-------------|-------|
| `path/to/file.py` | modify / create / delete | [what changes] |

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

### Single repo checks
- [ ] Every acceptance criterion maps to at least one step.
- [ ] Every step has a "how to verify" check.
- [ ] Steps are ordered correctly (no step depends on a later step).
- [ ] All files to be modified are listed.
- [ ] Unknowns and risks are explicitly stated (not hidden).
- [ ] No implementation has started (this is planning only).
- [ ] The branch name follows the project's naming convention.
- [ ] If the task is XL: consider splitting into multiple task files with explicit handoff points.

### Workspace (multi-repo) checks
- [ ] Root-index task has all child repos listed in **Repo Tasks** table.
- [ ] Each child repo with work has its own per-repo task file in that repo's `.context8/tasks/`.
- [ ] Per-repo task files have a **Parent task** field linking back to the root index.
- [ ] Cross-repo dependencies are documented in the root-index task.
- [ ] Each per-repo task is scoped only to that repo (no cross-contamination of steps).
- [ ] Out of Scope section in each per-repo task explicitly excludes sibling repo work.
- [ ] Acceptance criteria in the root-index cover cross-repo behaviors.

---

## Rules
- Planning means producing the task file. It does not mean writing any application code.
- If you cannot plan without reading more code: read the code in Phase 3, then plan. Never skip directly to implementing.
- If a step is "large" or "XL": break it down further until every step is "medium" or smaller.
- If a risk has no mitigation: flag it explicitly and ask before proceeding.
- Write all documentation in English.
- Do not invent steps for hypothetical future requirements. Plan only what is asked.
