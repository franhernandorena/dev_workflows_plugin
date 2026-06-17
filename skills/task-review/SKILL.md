---
name: task-review
version: 1.0.0
description: Use after task-do completes and before opening a PR — reviews diff for correctness, security vulnerabilities, test coverage gaps, convention violations, and regressions
---

# Task Review — Pre-PR Code Review

## Overview
Pre-PR review prompt. Loads the diff and task file, then systematically checks: correctness (logic vs. acceptance criteria), security (injection, secrets, auth), test coverage, convention compliance, and regressions. Produces a structured review report. Blocks PR if any security issue is unresolved.

## When to use
- `task-do` is complete
- Before opening a pull request
- Anytime you want a structured self-review of a diff

## When NOT to use
- Code not yet implemented → use `task-do` first
- Hotfix path (time-critical) → security check is still mandatory inside `task-hotfix`

## Output
- Review report (inline in session) with verdict: READY FOR PR or BLOCKED
- Missing tests added
- Task file updated with review outcome

## Full Prompt

# TASK REVIEW — Pre-PR Code Review

## RULE: Run this after `task-do` completes, before opening a PR.

Use this to catch issues before review from humans. Covers correctness, security, test coverage, conventions, and regressions.

---

## Phase 1 — Load Task & Diff

### 1.1 Identify what changed
```bash
git diff main...HEAD --stat
DIFF_STAT=$(git diff main...HEAD --stat)
git diff main...HEAD
```

Note: total files changed, lines added, lines removed — these go in the report.

### 1.2 Read the task file
Find and read the task file for this work:
```bash
ls -lt .context8/tasks/ | head -5
```

Verify:
- Status is "Complete" (or "In progress" if reviewing before final commit).
- All acceptance criteria are checked off.
- All modified files are listed.

### 1.3 Scope creep check

Compare files actually changed (from `git diff main...HEAD --stat`) against the **Files to Modify** section in the task file:

- **Files changed NOT in the task** → possible scope creep. Log them. If they are justified (e.g. refactoring needed to implement the task cleanly), note the justification. If not, flag as a finding.
- **Files in the task NOT changed** → possible incomplete implementation. Flag as a finding.

### 1.4 Workspace awareness

Check if this repo is part of a multi-repo workspace:
```bash
ls ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE_CHILD" || echo "SINGLE_REPO"
```

If `WORKSPACE_CHILD`:
- Read `.context8/WORKSPACE_LINK.md` (if exists) to understand sibling repo boundaries.
- Verify that no changes cross into sibling repos (all changed files should be within this repo).
- If any file in the diff belongs to a sibling repo, flag as **scope creep across workspace boundaries**.

### 1.5 Load relevant context
- `.context8/AGENT_CONTEXT.md` — conventions, patterns, gotchas.
- Every file modified in this diff (read fully, not just the diff).

---

## Phase 2 — Correctness Review

For every changed file, answer:

1. **Does the logic match the task's acceptance criteria?**
   If not: note the gap. Do not patch silently.

2. **Are there off-by-one errors, null/undefined handling gaps, or missed edge cases?**

3. **Are all error paths handled consistently with the rest of the codebase?**
   Check: does this codebase propagate exceptions, return Result types, use error codes? Follow the same pattern.

4. **Are there any race conditions, concurrency issues, or state mutation problems?**

5. **If touching I/O (DB, API, file system): are failures handled? Are transactions used where needed?**

---

## Phase 3 — Security Review

Check for:

- [ ] SQL injection: are all DB queries parameterized or ORM-based?
- [ ] Command injection: any `subprocess`, `exec`, `eval`, or shell interpolation with user input?
- [ ] Secrets or credentials hardcoded or logged?
- [ ] User input passed to file paths without sanitization?
- [ ] Auth/permission checks missing on new endpoints or functions?
- [ ] Sensitive data exposed in API responses, logs, or error messages?
- [ ] New dependencies added — are they from trusted sources?

If any issue found: **block the PR and fix before proceeding.**

---

## Phase 4 — Test Coverage Review

```bash
# Python — check coverage on changed files
pytest --cov=[module] --cov-report=term-missing -q 2>&1 | tail -30

# Node/TS
npm test -- --run --coverage 2>&1 | tail -30
```

For each changed function or branch:
- Is it covered by at least one test?
- Are the happy path AND the main error/edge paths tested?
- If a test is missing: note it. Add it or document the gap in the task file.

---

## Phase 5 — Convention Review

Check against `.context8/architecture/key_patterns.md` and `.context8/AGENT_CONTEXT.md`:

- [ ] Naming: files, functions, variables follow project conventions.
- [ ] Import ordering matches project style.
- [ ] No debug prints, commented-out code, or stray TODOs without task references.
- [ ] Docstrings/comments only where the WHY is non-obvious (not explaining what the code does).
- [ ] New modules or packages follow the existing module boundary rules.
- [ ] No new dependencies introduced without noting them in the task file.

---

## Phase 6 — Regression Check

```bash
# Run the full test suite
pytest -x -q 2>&1 | tail -30         # Python
npm test -- --run 2>&1 | tail -30    # Node/TS
```

All tests that passed before this task must still pass.

Also manually verify:
- Are there callers of the modified functions that were NOT updated but could be affected?
- Are there integration or e2e tests that exercise this code path?

---

## Phase 7 — Review Report

Produce a structured report. **Save it to disk** AND show it inline:

```bash
mkdir -p .context8/reviews/
REVIEW_DATE=$(date +%Y-%m-%d)
```

Write `.context8/reviews/${REVIEW_DATE}_<task-description>_review.md` with the template below, then print it inline.

```markdown
## Review Report — [task title]

**Date**: YYYY-MM-DD
**Branch**: [branch]
**Diff**: N files changed, X insertions(+), Y deletions(-)

### Scope Creep
- Files changed outside task scope: [list or "none"]
- Files expected but missing: [list or "none"]
- Workspace boundary crossings: [list or "none"]
- Justification for out-of-scope changes: [notes]

### Correctness
- [ ] Logic matches acceptance criteria
- [ ] Edge cases handled
- [ ] Error paths consistent with codebase pattern
- Issues found: [list or "none"]

### Security
- [ ] No injection vectors
- [ ] No hardcoded secrets
- [ ] Auth checks present where needed
- Issues found: [list or "none"]

### Test Coverage
- [ ] Changed code is covered
- [ ] Edge paths tested
- Missing tests: [list or "none"]

### Conventions
- [ ] Naming consistent
- [ ] No debug code left behind
- [ ] No undocumented new dependencies
- Issues found: [list or "none"]

### Regressions
- [ ] Full test suite passes
- [ ] Callers checked
- Issues found: [list or "none"]

### Questions
[Open questions about unclear logic, design decisions, or anything that needs clarification from the team or task author. "None" if nothing.]

### Verdict
READY FOR PR / BLOCKED: [reason]
```

If verdict is BLOCKED: fix issues, re-run relevant phases, update report.

---

## Completion Checklist

- [ ] Diff reviewed fully (not just changed lines — full file context).
- [ ] No security issues outstanding.
- [ ] Test suite passes.
- [ ] Review report written and verdict is READY FOR PR.
- [ ] Task file updated with review outcome.

---

## Rules
- Do not open the PR if any security issue is unresolved.
- Do not skip phases because the change "looks simple."
- If a missing test is found: add it now, not later.
- Review report must exist before PR is created.
- Write all documentation in English.
