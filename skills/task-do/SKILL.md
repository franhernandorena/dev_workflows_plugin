---
name: task-do
version: 1.1.0
description: Use to implement a task that already has a Planned task file in .context8/tasks/ — executes each step with verification, hard stops on unexpected state, and closes the task with full documentation
---

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.

# Task Do — Execute a Planned Task

## Overview
Implementation prompt. Requires a task file with status "Planned". Loads context, sets up the branch, runs baseline tests, then executes each step from the implementation plan with verification, commits, and hard stops. Closes the task with updated documentation and an optional PR.

## When to use
- A task file with status "Planned" exists in `.context8/tasks/`
- Ready to implement (context loaded, branch set up)

## When NOT to use
- No task file exists → run `task-plan` first
- Urgent production bug → use `task-hotfix`

## Output
- Implemented changes committed atomically
- Task file updated to "Complete"
- `.context8/` updated if architecture changed
- PR opened (if required)

## Full Prompt

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

### 1.4 Detect if this is a workspace root-index task or workspace child
```bash
ls .context8/WORKSPACE_OVERVIEW.md 2>/dev/null && grep -q "Workspace (multi-repo)" .context8/tasks/*.md 2>/dev/null && echo "WORKSPACE_INDEX" || echo "NOT_INDEX"
```

If the task has `**Type**: Workspace (multi-repo)`, this is a **root-index task**.
Read the **Repo Tasks** table and **Cross-repo Dependencies** sections.
- Root-index task → skip Phase 2, go to **Phase 3A — Workspace execution mode**.

**If NOT a root-index**: check if this repo is a child of a multi-repo workspace.
```bash
ls ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE_CHILD" || echo "SINGLE_REPO"
```

If `../../.context8/WORKSPACE_OVERVIEW.md` exists, this repo is a **child of a multi-repo workspace**.
Read `.context8/WORKSPACE_LINK.md` (if it exists) for sibling context. Internalize: implement only what belongs to this repo — do NOT cross into sibling repo territory.

- Single repo task → proceed to Phase 2 as normal.

---

## Phase 2 — Git Setup & Branch

### 2.1 Fetch para evitar worktree obsoleto

```bash
git fetch --prune 2>&1
```

### 2.2 Detectar rama base (develop)

Leer `.context8/repo-branches.md` para identificar la rama de desarrollo:

```bash
DEVELOP_BRANCH=$(grep -A5 "^## Protected Branches" .context8/repo-branches.md 2>/dev/null | grep "^\s*\- \`" | grep -v "main\|master" | head -1 | sed 's/.*`\(.*\)`.*/\1/')
```

Si no se encontró en el archivo, detectar por convención:

```bash
# Buscar develop primero, sino main
for b in develop main master; do
  git show-ref --verify refs/heads/$b >/dev/null 2>&1 && { DEVELOP_BRANCH=$b; break; } 2>/dev/null
done
DEVELOP_BRANCH=${DEVELOP_BRANCH:-main}
echo "Rama base (desarrollo): $DEVELOP_BRANCH"
```

**Regla**: las feature branches SIEMPRE parten de `$DEVELOP_BRANCH`, no de `main`.

### 2.3 Verificar rama actual

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Rama actual: $CURRENT_BRANCH"
```

- **Si ya estás en la rama correcta** (la que especifica el task file):
  - Verificar que está actualizada contra `$DEVELOP_BRANCH`:
    ```bash
    git merge-base --is-ancestor origin/$DEVELOP_BRANCH HEAD && echo "✅ Actualizada" || echo "⚠️ Está detrás de $DEVELOP_BRANCH — considera rebase"
    ```
  - Proceder.

- **Si estás en una rama con prefijo `feat/*`, `feature/*`, `fix/*`** (no coincide con la del task):
  ```
  ⚠️ Estás en <CURRENT_BRANCH>, no en la rama planeada en el task.
  ¿Qué quieres hacer?
    [c] continuar en <CURRENT_BRANCH> (actualizas el task file con esta rama)
    [n] crear rama nueva <task-branch> desde $DEVELOP_BRANCH
  ```

- **Si estás en `main`, `master`, `develop`**:
  ```bash
  git checkout -b [branch-name-from-task]
  ```

- **Si estás en otra rama** (no feature, no base):
  - Avisar y preguntar si continuar ahí o crear desde `$DEVELOP_BRANCH`.

### 2.4 Asegurar que la rama parte del último `$DEVELOP_BRANCH`

Al crear la rama nueva, partir del último commit de `$DEVELOP_BRANCH`:

```bash
git checkout $DEVELOP_BRANCH
git pull origin $DEVELOP_BRANCH 2>&1
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

**Team routing**: if `.context8/TEAM.md` exists, dispatch each step to the
matching specialist from its Routing Map (backend → backend-agent, frontend →
frontend-agent, tests → qa-agent, …) as a subagent. Give the specialist the
step spec, the files involved, and the expected output; review its result,
integrate, and continue as orchestrator. If TEAM.md is missing, surface it to
the user (optionally run `team-setup`).

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

## Phase 3A — Workspace Execution Mode (root-index task)

If Phase 1.4 detected a root-index task, use this phase instead of Phase 3.

### 3A.1 Understand the cross-repo plan
- Read the **Repo Tasks** table — each row is one repo with a link to its per-repo task.
- Read **Cross-repo Dependencies** — this defines the execution order.

### 3A.2 Execute per-repo tasks in dependency order

For each repo listed as "Planned", in dependency order:

**Option A — Delegate to sub-agent** (preferred for isolated repos):
```bash
# Navigate to the repo first to verify its state
cd [repo-path]
git status
git log --oneline -3
cd ..
```
Then use `delegate_task` to spawn a sub-agent for that repo:
- **Goal**: "Implement the changes specified in `<per-repo-task-file>` for `<repo-name>`."
- **Context**: Include the per-repo task file content, the repo's `.context8/AGENT_CONTEXT.md`, and the parent workspace overview.
- The sub-agent works independently in that repo: reads, implements, tests, commits.
- After the sub-agent returns: verify by checking git log and running tests in that repo.

**Option B — Manual execution**:
- Navigate into the repo: `cd [repo-path]`
- Read the per-repo task file and the repo's AGENT_CONTEXT.md.
- Implement each step from the per-repo task (same as Phase 3).
- Verify tests pass in that repo.
- Commit changes.
- Return to workspace root: `cd [workspace-root]`

### 3A.3 Update root-index after each repo

After completing work in a repo (whether delegated or manual):

1. Update the root-index task file:
   - Mark that repo's row: change status from "Planned" to "Complete".
   - Add a log entry to the **Progress Log** section:
     `- YYYY-MM-DD: <repo>: All steps complete. Tests pass.`
2. Commit the root-index update:
   ```bash
   git add .context8/tasks/[task-file].md
   git commit -m "docs(tasks): mark <repo> complete in root-index"
   ```

### 3A.4 Finalize root-index

When all repos are complete:
- Set root-index task status to "Complete".
- Add final progress log entry.
- Proceed to Phase 4 for cross-repo post-checks.

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

**If this is a per-repo task** (has a **Parent task** field): also update the parent root-index task.
- Navigate to the workspace root.
- Open the parent root-index task file.
- Mark this repo's status as "Complete" in the **Repo Tasks** table.
- If all repos are complete, set root-index status to "Complete".
- Commit: `docs(tasks): mark <repo> complete in root-index`
- Return to this repo.

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
