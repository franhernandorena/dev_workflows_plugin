# TASK REVIEW — Pre-PR Code Review

## RULE: Run this after `task-do` completes, before opening a PR.

Use this to catch issues before review from humans. Covers correctness, security, test coverage, conventions, and regressions.

---

## Phase 0 — Environment Check

Identify the target environment of the PR. Strictness scales with it:

| Target env | Review strictness |
|------------|-------------------|
| `dev`      | Lighter. Findings are advisory. |
| `beta`     | Standard. Each finding must be addressed or explicitly waived. |
| `prod`     | Strict. Every criterion is blocking. No waivers. |

State the detected target env in the review report header.

---

## Phase 1 — Load Task & Diff

### 1.1 Identify what changed
```bash
git diff main...HEAD --stat
git diff main...HEAD
```

### 1.2 Read the task file
Find and read the task file for this work:
```bash
ls -lt .context8/tasks/ | head -5
```

Verify:
- Status is "Complete" (or "In progress" if reviewing before final commit).
- All acceptance criteria are checked off.
- All modified files are listed.

### 1.3 Code review graph consultation

Before correctness review, query `.code-review-graph/graph.db`:

```bash
# List all callers of each modified symbol — keep the graph out of context
sqlite3 .code-review-graph/graph.db "SELECT * FROM edges WHERE source IN (modified-files);"
```

Surface in the report:
- All callers of each modified function/class.
- Files NOT in the diff but transitively affected (per the graph).
- Tests that exercise the changed code (per the graph's test edges).

### 1.4 Load relevant context
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

Produce a structured report before opening the PR:

```markdown
## Review Report — [task title]

**Date**: YYYY-MM-DD
**Branch**: [branch]
**Files changed**: N

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

### Target Environment
`dev` | `beta` | `prod` (taken from the PR base/head branches or `**Environment**`
in the task file). Strictness of the review scales with this.

### Commit / Merge Plan
Proposed sequence of actions to land this PR — listed, not executed:
- `git add [files]`
- `git commit -m "type(scope): description"`
- (if PR) `gh pr create --title ... --body ...`
- (if merge) `gh pr merge --squash` (or `--merge` / `--rebase`, your choice)

The agent MUST NOT execute any of the above. The user runs them.

### Verdict
READY TO PROPOSE PR / BLOCKED: [reason]
```

If verdict is BLOCKED: fix issues, re-run relevant phases, update report.

---

## Completion Checklist

- [ ] Diff reviewed fully (not just changed lines — full file context).
- [ ] No security issues outstanding.
- [ ] Test suite passes.
- [ ] Review report written and verdict is READY TO PROPOSE PR.
- [ ] Task file updated with review outcome.

---

## Rules
- Do not open the PR if any security issue is unresolved.
- Do not skip phases because the change "looks simple."
- If a missing test is found: add it now, not later.
- Review report must exist before PR is created.
- Write all documentation in English.
