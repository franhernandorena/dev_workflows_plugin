---
name: project-continue
description: Use at the start of any session on an existing project — checks git state, loads .context8 context, sets up or resumes task file, and enforces working rules before any code changes
---

# Project Continue — Session Bootstrap

## Overview
Session bootstrap for an existing project. Orients in the codebase (git state, branch, local changes), loads project context from `.context8/`, sets up or resumes a task file, and establishes working rules for code, git, testing, and documentation. Do not start work until Phase 3 is complete.

## When to use
- Starting any new session on a project that already has `.context8/`
- Resuming after a handoff

## When NOT to use
- Project has no `.context8/` → use `project-init` first
- Multi-repo workspace → use `workflow-continue`

## Output
- Oriented agent with loaded context, task file ready, working rules active

## Full Prompt

# SESSION BOOTSTRAP — Read This Before Any Work

## RULE: Complete every step in order. Do not start the task until Phase 3 is done.

---

## Phase 1 — Orient in the Codebase

Run these immediately at session start:

### 1.1 Git status
```bash
git status
git log --oneline -15
git diff --stat HEAD~1 HEAD 2>/dev/null || true
git stash list
```

### 1.2 Verify you are on the right branch
```bash
git branch --show-current
```
If uncertain about which branch to use, stop and ask before proceeding.

### 1.3 Check for local changes
```bash
git diff --name-only
git diff --cached --name-only
```
Read any modified files before touching them.

---

## Phase 2 — Load Project Context

Read in this exact order. Do not skip or reorder.

1. **`.context8/AGENT_CONTEXT.md`** — internalize everything: tech stack, architecture, patterns, conventions, gotchas.
2. **`.context8/PROJECT_OVERVIEW.md`** — high-level orientation.
3. **Relevant architecture docs** — read only the ones that apply to this task:
   - `.context8/architecture/data_flow.md` → if touching data pipelines, ingestion, or APIs
   - `.context8/architecture/key_patterns.md` → if adding new features or refactoring
   - `.context8/architecture/module_map.md` → if crossing module boundaries
   - `.context8/architecture/infrastructure.md` → if touching config, env vars, or deployment

If `.context8/` does not exist: stop and run `project-init` before continuing.

---

## Phase 3 — Task Setup

### 3.1 Check for existing task files
```bash
ls -lt .context8/tasks/ 2>/dev/null | head -10
```
- If a relevant task file exists → read it. Resume from where it left off.
  - **If the task has a `Parent task` field**: this repo is part of a multi-repo workspace.
    Read the parent root-index task at the path specified. Check the **Repo Tasks** table
    for cross-repo context and dependencies.
- If no task file exists → create one:
  `.context8/tasks/YYYY-MM-DD_short_description.md`
  - **If a parent workspace exists** (look for `../../.context8/WORKSPACE_OVERVIEW.md`):
    add a `**Parent task**` field linking to the workspace root-index if one exists.

### 3.2 Task file structure
```markdown
# Task: [clear, specific title]

**Date**: YYYY-MM-DD
**Status**: In progress | Blocked | Complete
**Branch**: [branch name]

## Objective
[One paragraph: what needs to be done and why.]

## Acceptance Criteria
- [ ] ...
- [ ] ...

## Approach
[Brief plan: what files will be touched and in what order.]

## Progress Log
- [HH:MM] Started. Reading X, Y, Z.
- [HH:MM] ...

## Decisions Made
[Any architectural or implementation decisions taken, with reasoning.]

## Blockers
[Anything preventing progress.]

## Files Modified
- `path/to/file.py` — [what changed and why]
```

### 3.3 If MCP tools are connected (GitHub, Linear, Jira)
- Check for open issues or PRs related to this task.
- Link the issue ID in the task file.
- Do NOT create duplicate issues.

---

## Phase 4 — Pre-Work Checklist

Before writing or modifying any code:

- [ ] I have read AGENT_CONTEXT.md and understand the architecture.
- [ ] I know which branch I'm on and it's the correct one.
- [ ] I have read every file I am about to modify.
- [ ] I understand how the module I'm working in connects to the rest of the system.
- [ ] I know the naming conventions for this codebase and will follow them.
- [ ] I know how errors are handled in this codebase and will follow the same pattern.
- [ ] A task file exists and has a clear objective and acceptance criteria.

---

## Phase 5 — Working Rules

Follow these at all times during the session:

### Code
- Read before writing. Never modify a file you haven't read in this session.
- Respect the existing code style: indentation, naming, comment style, import ordering.
- Do not introduce new dependencies without noting it in the task file and checking if an equivalent already exists in the project.
- Do not refactor code that is not part of the current task scope.
- Do not leave debug prints, commented-out code, or TODOs without a task reference.

### Git
- Commit atomically: one logical change per commit.
- Use semantic commit messages:
  `type(scope): short description`
  Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `perf`
  Example: `feat(rag): add BM25 reranking to hybrid search pipeline`
- Never commit directly to `main` or `master` unless the project explicitly works that way.
- Never commit secrets, .env files, or local config overrides.

### Testing
- Run existing tests before making changes to establish a baseline:
  ```bash
  # Python
  pytest -x -q 2>&1 | tail -20
  # Node
  npm test -- --run 2>&1 | tail -20
  ```
- Run tests again after changes. All previously passing tests must still pass.
- If you add new functionality, add tests for it (same pattern as existing tests).

### Documentation
- If you change the architecture, data flow, or a key pattern → update the relevant `.context8/architecture/` file.
- If you add or remove env vars → update `.context8/architecture/infrastructure.md`.
- If you add a new module or change module boundaries → update `.context8/architecture/module_map.md`.
- Update AGENT_CONTEXT.md only for significant, persistent changes (not minor fixes).
- Always update the task file's progress log as you work.

---

## Phase 6 — Post-Task Checklist

Before closing the session or marking the task complete:

- [ ] All acceptance criteria are met.
- [ ] Tests pass (run them one final time).
- [ ] No linting errors:
  ```bash
  # Python
  ruff check . 2>/dev/null || flake8 . 2>/dev/null || true
  # Node/TS
  npm run lint 2>/dev/null || true
  ```
- [ ] Task file is updated: status set to "Complete", all modified files listed.
- [ ] Relevant `.context8/` docs updated if architecture changed.
- [ ] Changes committed with semantic commit messages.
- [ ] No secrets or debug code left behind.
- [ ] If a PR is expected: open it and link it in the task file.

---

## Rules
- Always respond in English unless explicitly asked otherwise.
- If the task is ambiguous, write your interpretation in the task file and confirm before proceeding.
- If you discover something missing from AGENT_CONTEXT.md that would have helped you, add it before closing.
- If you are blocked for any reason, document it in the task file and surface it clearly.
- Never silently skip a phase because the task "seems small."
