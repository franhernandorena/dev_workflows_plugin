# TASK EXECUTION — Implement a Planned Task

## RULE: A task file in `.context8/tasks/` with status "Planned" must exist before running this prompt.

Use this after `task-plan` has produced a task file. This prompt drives the implementation.

---

## Phase 0 — Environment Gate

Read the task file's `**Environment**` field. If it is missing, ASK the
user to provide it. Then obey the matrix:

| Environment | Rule |
|-------------|------|
| `dev`       | Proceed. ASK before each commit (global rule). |
| `beta`      | Proceed. Restate the ASK-per-op rule before any non-read action. |
| `prod`      | Do not start Phase 1. Surface the task, get explicit written permission. |

`prod` is sacred. Even if the task file says `prod`, the agent must still
get a fresh "go" from the user before touching shared state.

---

## Phase 1 — Load Task & Context

### 1.1 Find the task file
```bash
ls -lt .context8/tasks/ | head -10
```
Read the task file you are about to implement. If status is not "Planned", confirm before proceeding.

### 1.2 Load project context
Read in this order:
1. `.context8/AGENT_CONTEXT.md` — tech stack, architecture, patterns, gotchas.
2. Every file listed under **Files to Read** in the task file.
3. Relevant architecture docs flagged in the task file.

### 1.3 Set task status to "In progress"
Update the task file: `**Status**: In progress`
Add a progress log entry: `- YYYY-MM-DD: Started execution. Branch: [branch name].`

---

## Phase 2 — Branch Setup

```bash
git branch --show-current
```

- If already on the correct branch: proceed.
- If not: create or switch to the branch specified in the task file.
  ```bash
  git checkout -b [branch-name]
  ```

Run the baseline test suite before touching any code:
```bash
# Python
pytest -x -q 2>&1 | tail -20
# Node/TS
npm test -- --run 2>&1 | tail -20
```

Record result in the progress log: `- YYYY-MM-DD: Baseline: X tests passed, Y failed.`

---

## Phase 3 — Execute Each Step

Work through the **Implementation Plan** in the task file step by step.

For each step:

1. **Read** every file the step will modify (if not already in context this session).
2. **Implement** the change exactly as specified. No scope creep.
3. **Verify** using the step's "how to verify" check.
4. **Log** in the task file:
   - `- YYYY-MM-DD: Step N complete. [One-line summary of what changed.]`
5. **ASK the user before committing.** Present the exact command, then
   wait for "go":
   ```
   Proposed: git add [specific files] && git commit -m "type(scope): short description"
   Proceed? (yes/no)
   ```
   Do NOT execute `git commit` without explicit consent. See global
   `Commit Policy` in `AGENTS.md`.
6. **Validate against the code-review-graph** (non-blocking by default):
   ```bash
   sqlite3 .code-review-graph/graph.db "SELECT * FROM edges WHERE source IN ([files-changed]);"
   ```
   If the graph shows unexpected new callers/dependents, log under
   `## Blockers` in the task file and surface to the user.

### Hard stops — pause and document before continuing
- A file you need to modify has unexpected content (different from what Phase 3 of planning found).
- A test that should pass is failing for an unrelated reason.
- A risk flagged in the task file is materializing.
- The step requires a change not listed in the plan.
- User did not answer an ASK within reasonable scope. Do not assume "yes".
- Environment changed mid-task (branch switched, deploy happened). Re-run
  Phase 0.
- `.code-review-graph` shows unexpected new callers of a modified symbol.
  Log under `## Blockers` and ask the user.

When a hard stop occurs: write it under **Blockers** in the task file, then surface it.

---

## Phase 4 — Post-Implementation Checks

After all steps are complete:

### 4.1 Run the full test suite
```bash
# Python
pytest -x -q 2>&1 | tail -30
# Node/TS
npm test -- --run 2>&1 | tail -30
```
All tests that passed at baseline must still pass.

### 4.2 Lint check
```bash
# Python
ruff check . 2>/dev/null || flake8 . 2>/dev/null || true
# Node/TS
npm run lint 2>/dev/null || true
```

### 4.3 Verify every acceptance criterion
Go through each `- [ ]` in the task file's **Acceptance Criteria**.
Check it off only when you can cite the specific change that satisfies it.
If a criterion cannot be checked off, do NOT mark the task complete.

---

## Phase 5 — Close the Task

### 5.1 Update the task file
```markdown
**Status**: Complete

## Files Modified
| File | Change type | Notes |
|------|-------------|-------|
| `path/to/file.py` | modify / create / delete | [what changed] |

## Progress Log
- YYYY-MM-DD: All steps complete. Tests pass. Linting clean.
```

### 5.2 Update .context8/ if architecture changed
- Data flow changed → update `.context8/architecture/data_flow.md`
- New module or changed boundaries → update `.context8/architecture/module_map.md`
- New/changed env vars → update `.context8/architecture/infrastructure.md`
- Significant persistent change → update `.context8/AGENT_CONTEXT.md`

### 5.3 ASK before final commit
Propose:
```
Proposed: git add [all relevant files] && git commit -m "type(scope): short description"
Proceed? (yes/no)
```
Do NOT execute without explicit "yes" or "go".

### 5.4 ASK before opening PR

In `beta` and `dev`, a single ASK is sufficient.

In `prod`, two separate ASKs are required:
1. ASK to propose the PR content (title, body, base/head branches).
   Wait for "yes".
2. ASK to actually execute `gh pr create`. Wait for "go".

After both ASKs, run:
```bash
gh pr create --title "[title]" --body "$(cat <<'EOF'
## Summary
- [bullet points from task objective and acceptance criteria]

## Test plan
- [ ] All existing tests pass
- [ ] [new tests added for this feature]
- [ ] No linting errors

Closes #[issue number if any]
EOF
)"
```
Link the PR URL in the task file.

---

## Phase 6 — Final Checklist

- [ ] All acceptance criteria checked off.
- [ ] Tests pass (final run complete).
- [ ] No linting errors.
- [ ] Task file status = "Complete", all modified files listed.
- [ ] Relevant `.context8/` docs updated if architecture changed.
- [ ] All commits use semantic messages.
- [ ] No secrets, debug prints, or commented-out code left behind.
- [ ] PR opened and linked (if required by the project workflow).

---

## Rules
- Execute the plan as written. If the plan is wrong, update the plan first — don't silently deviate.
- One step at a time. Do not implement step N+1 before step N is verified.
- If you discover that a step is impossible as written: document it as a blocker and stop.
- Do not add features, refactors, or improvements beyond what the task file specifies.
- Write all documentation in English.
