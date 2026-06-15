---
name: workflow-status
description: Multi-repo workspace visibility in one glance — what repos exist, current branch of each, active tasks, uncommitted changes, CI status
---

# Workflow Status — Workspace Visibility at a Glance

## Overview
Provides a single-pane overview of a multi-repo workspace: which repos exist, what branch each is on, active tasks, uncommitted changes, and CI status. Designed for anyone managing multiple repos who needs a quick health check before starting work.

## When to use
- First thing in a session to understand workspace state
- Before planning cross-repo changes
- Before a deploy to verify all repos are ready
- When you need to quickly check which repos have pending work

## When NOT to use
- Single-repo project → use project-continue instead
- You need detailed status of a specific repo → use git directly or project-continue

## Output
- Markdown summary printed inline and optionally saved to `.context8/WORKSPACE_STATUS.md`

## Full Prompt

# WORKFLOW STATUS — Workspace Visibility

## RULE: This skill reads but does not modify anything. Read-only view of the workspace.

---

## Phase 1 — Detect Workspace Context

### 1.1 Find workspace root
```bash
WORKSPACE_FILE=$(find . -name "WORKSPACE_OVERVIEW.md" -maxdepth 3 2>/dev/null | head -1)
if [ -z "$WORKSPACE_FILE" ]; then
  echo "NOT_WORKSPACE"
else
  WORKSPACE_ROOT=$(dirname "$WORKSPACE_FILE")
  echo "WORKSPACE_ROOT=$WORKSPACE_ROOT"
fi
```

If no workspace found, check if this is a child of one:
```bash
ls ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE_CHILD" || echo "SINGLE_REPO"
```

If SINGLE_REPO: print "Single repo — no workspace context. Use project-continue instead." and stop.

### 1.2 Read workspace overview
If workspace found, read the overview:
```bash
cat "$WORKSPACE_ROOT/WORKSPACE_OVERVIEW.md" 2>/dev/null || cat "../../.context8/WORKSPACE_OVERVIEW.md" 2>/dev/null
```

Identify all repos listed in the workspace.

---

## Phase 2 — Gather Repo Status

For each repo in the workspace, gather the following. Run queries in parallel where possible.

### 2.1 Current branch
```bash
git branch --show-current
```

### 2.2 Uncommitted changes
```bash
git status --short | head -20
```

### 2.3 Ahead/behind remote
```bash
git fetch --quiet 2>/dev/null
git rev-list --count --left-right HEAD...@{upstream} 2>/dev/null || echo "no upstream"
```

### 2.4 Active tasks (context8 tasks)
```bash
ls .context8/tasks/ 2>/dev/null | head -5
```

### 2.5 Last commit
```bash
git log --oneline -1
```

---

## Phase 3 — CI Status (if available)

### 3.1 Check gh CLI availability
```bash
which gh 2>/dev/null && echo "gh_available" || echo "gh_unavailable"
```

### 3.2 Get CI status for current branch
```bash
# Only if gh is available
gh run list --branch $(git branch --show-current) --limit 3 --json conclusion,headBranch,displayTitle,createdAt 2>/dev/null | head -30
```

---

## Phase 4 — Compile Overview

Synthesize findings into a structured markdown report:

```markdown
# Workspace Status — YYYY-MM-DD HH:MM

## Summary
| Repo | Branch | Status | Ahead/Behind | Active Tasks | CI |
|------|--------|--------|-------------|--------------|-----|
| repo-a | main | clean | 0/0 | 1 task | ✅ passing |
| repo-b | feat/x | 2 modified | 3/0 | 2 tasks | 🟡 in progress |
| repo-c | develop | 1 staged | 0/1 | none | ❌ failed |
```

## Detailed

### repo-a (`path/to/repo-a`)
- **Branch**: main
- **Status**: clean
- **Ahead/Behind**: 0 ahead, 0 behind
- **Active tasks**: 2026-06-15_add-auth.md (in_progress)
- **CI**: ✅ passing
- **Last commit**: a1b2c3d fix login redirect

### repo-b (`path/to/repo-b`)
- ... etc
```

Print the report. Optionally save to `.context8/WORKSPACE_STATUS.md`.

---

## Phase 5 — Highlight Blockers

Call out anything that needs attention:

- ⚠️ Repos with uncommitted changes (stash or commit before switching context)
- ⚠️ Repos behind remote (pull before starting new work)
- ⚠️ Repos ahead of remote (push before leaving)
- ⚠️ CI failures on current branches
- ⚠️ Active tasks in multiple repos (focus risk)

---

## Rules
- Read-only. Never modify any file.
- Respect workspace context files. If none found, stop gracefully.
- Use `gh` only if available — never install it.
- Print output inline. Saving to disk is optional.
