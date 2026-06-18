---
name: project-handoff
version: 1.0.0
description: Use when closing a project session — updates all stale .context8, captures in-progress task state and git status, writes HANDOFF.md so the next agent can resume without re-reading source code
---

# Project Handoff — Close Session for Next Agent

## Overview
Closes a project session cleanly. Captures current git state, updates every stale section of `.context8/`, documents in-progress tasks with precise progress logs, and writes `.context8/HANDOFF.md` with immediate next steps, blockers, and warnings. No code changes.

## When to use
- Ending a session before work is fully complete
- Handing off to another agent or developer
- Before taking a long break from a project

## When NOT to use
- Work is fully complete → just commit and close
- Starting a session → use `project-continue`

## Output
- Updated `.context8/AGENT_CONTEXT.md` (stale sections refreshed)
- Updated in-progress task files
- `.context8/HANDOFF.md` with state, blockers, next steps

## Full Prompt

# PROJECT HANDOFF — Close a Project Session for Another Agent or Developer

## RULE: No code changes. Documentation and state capture only.

Use this when leaving a project so the next agent (or developer) can pick up with zero ambiguity. Output is an updated `.context8/` and a handoff summary.

---

## Phase 1 — Capture Current State

### 1.1 Git state
```bash
git fetch --prune 2>&1
git status
git log --oneline -20
git branch -a
git stash list
git diff --stat HEAD
```

### 1.2 Branch documentation
Repasar el estado actual de cada rama y actualizar `.context8/REPO_BRANCHES.md` si hay cambios (ramas nuevas, mergeadas, o eliminadas desde la última sesión).

```bash
for branch in $(git branch --format='%(refname:short)'); do
  last_date=$(git log "$branch" -1 --format="%ci" 2>/dev/null)
  ahead=$(git rev-list --count "$branch" --not origin/"$branch" 2>/dev/null)
  echo "  $branch | $last_date | ahead=$ahead"
done
```

### 1.3 Open tasks
```bash
ls -lt .context8/tasks/ | head -20
```
Read every task file whose status is "In progress" or "Blocked".

### 1.4 Uncommitted or unpushed work
```bash
git diff --name-only
git diff --cached --name-only
git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null || true
```

Document everything found. Nothing should be hidden from the next agent.

---

## Phase 2 — Update .context8/

### 2.1 AGENT_CONTEXT.md and REPO_BRANCHES.md
Read `.context8/AGENT_CONTEXT.md`. For every section, verify it reflects the current state of the codebase:

- Tech stack: any new dependencies or version changes?
- Architecture: any structural changes made during this work?
- Data flow: any new ingestion paths, transformations, or outputs?
- Module map: any new modules or changed boundaries?
- Configuration & environment: any new or removed env vars?
- External integrations: any new third-party services?
- Known constraints & gotchas: anything discovered that should be recorded?

Update every section that is stale. Mark sections you cannot verify as `[Unverified as of YYYY-MM-DD]`.

Also read `.context8/REPO_BRANCHES.md` (if it exists) and update it:
- Add any new branches created during this session.
- Mark merged branches as `merged`, stale branches as `stale`.
- Update last-activity dates.

### 2.2 Architecture docs
For each file in `.context8/architecture/`, verify and update if stale:
- `data_flow.md` — if data paths changed.
- `key_patterns.md` — if new patterns emerged or anti-patterns were found.
- `module_map.md` — if module structure changed.
- `infrastructure.md` — if env vars, cloud resources, or local setup changed.

### 2.3 Task files
For every "In progress" task:
- Write the current state precisely in the **Progress Log**.
- List every file modified so far under **Files Modified**.
- Write every unresolved question under **Blockers**.
- Set status to "Blocked" if work cannot continue without human input.

---

## Phase 3 — Write Handoff Summary

Create or update `.context8/HANDOFF.md`:

```markdown
# Handoff — [project name]

**Date**: YYYY-MM-DD
**Handing off from**: [agent or developer name / session ID]
**Next action owner**: [if known]

## Current State
[1–2 paragraphs: what is the state of the project right now. What was just done. What is not done.]

## Active Tasks
| Task file | Status | Blocked on |
|-----------|--------|------------|
| `.context8/tasks/YYYY-MM-DD_x.md` | In progress | [or "nothing"] |

## Git State
- Branch: [branch name]
- Branches doc: `.context8/REPO_BRANCHES.md` (updated)
- Uncommitted changes: [yes/no — list files if yes]
- Unpushed commits: [yes/no — list if yes]
- Open PRs: [link or "none"]

## Immediate Next Steps
1. [Concrete first action the next agent should take.]
2. [Second action.]
3. [...]

## Known Blockers
| Blocker | Impact | Who can resolve |
|---------|--------|-----------------|
| [description] | high/med/low | [human / other system / unknown] |

## Context Gaps
[Things the next agent will need to know that are NOT documented in .context8/. Be explicit.]

## Decisions Pending
[Any architectural or implementation decisions left unmade. Include relevant context.]

## Do Not Touch
[Files, systems, or areas that should not be modified until a specific condition is met.]

## Warnings
[Non-obvious things that could cause problems. Things discovered that surprised you.]
```

---

## Phase 4 — Verify Handoff Completeness

- [ ] `.context8/AGENT_CONTEXT.md` is up to date (no stale sections).
- [ ] All in-progress task files have current progress logs.
- [ ] `HANDOFF.md` exists and has no empty required sections.
- [ ] Git state is documented (uncommitted changes, unpushed commits).
- [ ] All blockers are surfaced — none hidden.
- [ ] "Immediate Next Steps" are concrete and actionable (not vague).
- [ ] No secrets or credentials left in any file.

---

## Rules
- Document what IS, not what SHOULD BE.
- If something is unknown, write "Unknown — needs investigation" rather than guessing.
- A handoff with documented unknowns is better than a handoff with hidden gaps.
- If you cannot update a section of AGENT_CONTEXT.md without reading code: read the code.
- Write all documentation in English.
