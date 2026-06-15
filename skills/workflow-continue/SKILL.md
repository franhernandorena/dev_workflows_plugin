---
name: workflow-continue
version: 1.0.0
description: Use when resuming work on a multi-repo workspace that was previously bootstrapped — reorients across all repos, finds in-progress tasks, syncs remotes before any work
---

# Workflow Continue — Resume Multi-Repo Workspace

## Overview
Session bootstrap for returning to an existing workspace. Checks git state across all repos, loads cross-repo context, finds the active task, and enforces working rules for the session. Do not start work until all phases are complete.

## When to use
- Starting a new session on a workspace that already has `.context8/`
- Resuming after a handoff from another agent

## When NOT to use
- Workspace not yet bootstrapped → use `workflow-init` first
- Single repo (no workspace) → use `project-continue`

## Output
- Oriented agent with loaded context, active task identified, remotes synced

## Full Prompt

# WORKFLOW RESUME — Continue an Existing Multi-Repo Workspace

## RULE: Complete every step in order before doing any work.

A workflow resume is for returning to a workspace you have previously bootstrapped.
The root `.context8/` and per-repo `.context8/` already exist. Your goal: reorient fast
and pick up exactly where the last session left off.

**Important**: This is a WORKFLOW (multi-repo workspace), not a single repository.
The root folder contains multiple independent child repos. Each child repo is a
self-contained project with its own `.context8/`. Do NOT confuse the workspace root
with a project root — they serve different purposes.

---

## Phase 1 — Reorient in the Workspace

### 1.1 Check workspace-level state
```bash
find . -maxdepth 2 -name ".git" -type d | sed 's|/.git||' | sort
```

### 1.2 Check git status in every child repo
```bash
for repo in $(find . -maxdepth 2 -name ".git" -type d | sed 's|/.git||'); do
  echo "=== $repo ===" && git -C "$repo" status --short && git -C "$repo" log --oneline -5
done
```

### 1.3 Check for in-progress or open tasks
```bash
ls -lt .context8/tasks/ 2>/dev/null | head -10
find . -path '*/.context8/tasks/*.md' | sort
```

Read any task file whose status is "In progress" or "Blocked".

**If a root-index task** (has `**Type**: Workspace (multi-repo)`): read its **Repo Tasks** table
to see which per-repo tasks are still "Planned" or "In progress" and which are "Complete".

---

## Phase 2 — Load Context

Read in this order. Skip files you already have in context.

1. `.context8/WORKSPACE_OVERVIEW.md` — cross-repo relationships, global conventions.
2. `.context8/README.md` — workspace index, repo links.
3. For each repo you will touch: `[repo]/.context8/AGENT_CONTEXT.md`.
4. Relevant architecture docs only (same rule as per-repo `project-continue`).

If `.context8/` does not exist: stop and run `workflow-init` first.

---

## Phase 3 — Resume Task

### 3.1 Identify the active task
- Read the most recent task file across all repos.
- If multiple tasks are "In progress", confirm with the user which one to resume.
- **If a root-index task**: also check each per-repo task's status.
  - A root-index task can be "In progress" even when some per-repo tasks are "Complete"
    and others are still "Planned". The active work is in the per-repo tasks that are
    still "In progress" or still "Planned".

### 3.2 Check where work stopped
- Read the **Progress Log** section of the task file.
- **For root-index tasks**: check the **Repo Tasks** table to see which repos are done
  and which are pending. Read the per-repo task files for any pending repos.
- Re-read any files listed under **Files Modified** to refresh state.
- Check if any blockers from the last session are still unresolved.

### 3.3 Sync with remotes
```bash
for repo in $(find . -maxdepth 2 -name ".git" -type d | sed 's|/.git||'); do
  echo "=== $repo ===" && git -C "$repo" fetch --all 2>&1 | tail -3
done
```

---

## Phase 4 — Pre-Work Checklist

Before writing or modifying any code:

- [ ] I know which workspace and which repos are in scope.
- [ ] I have read WORKSPACE_OVERVIEW.md and the relevant AGENT_CONTEXT.md files.
- [ ] I know which branch I'm on in each repo and it's correct.
- [ ] I have read the active task file and know exactly where work stopped.
- [ ] I understand cross-repo dependencies that affect this task.
- [ ] No unresolved blockers are hidden or skipped.

---

## Phase 5 — Working Rules

Follow these at all times:

### Cross-repo coordination
- When a change in one repo requires a change in another, plan both before implementing either.
- Note cross-repo dependencies explicitly in the task file.
- Never assume an API contract is stable — re-read the interface definition.

### Code
- Read before writing. Never modify a file you haven't read this session.
- Respect per-repo conventions (they may differ between repos).
- Do not refactor code outside the current task scope.

### Git
- Commit atomically per repo: one logical change per commit.
- Semantic commit messages: `type(scope): short description`
- Never commit directly to `main` or `master` unless explicitly expected.
- Never commit secrets, .env files, or local config overrides.

### Testing
```bash
# Run tests in the affected repo before and after changes
pytest -x -q 2>&1 | tail -20       # Python
npm test -- --run 2>&1 | tail -20  # Node
```

### Documentation
- Update `WORKSPACE_OVERVIEW.md` only for changes to cross-repo relationships or shared infra.
- Update per-repo `.context8/` files as per that repo's `project-continue` rules.
- Always update the task file's progress log as you work.

---

## Phase 6 — Post-Task Checklist

Before closing the session or marking the task complete:

- [ ] All acceptance criteria are met across all affected repos.
- [ ] Tests pass in every repo touched.
- [ ] No linting errors in any affected repo.
- [ ] Task file updated: status "Complete", all modified files listed.
- [ ] Relevant `.context8/` files updated if architecture or cross-repo relationships changed.
- [ ] Changes committed with semantic messages in each repo.
- [ ] No secrets or debug code left behind.
- [ ] If PRs are expected: opened and linked in the task file.

---

## Rules
- Always respond in English unless explicitly asked otherwise.
- If task scope crosses repos, confirm the full blast radius before starting.
- If you discover missing context in WORKSPACE_OVERVIEW.md, add it before closing.
- Never silently skip a phase because the task "seems small."
