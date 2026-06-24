---
name: task-compacting
version: 1.0.0
description: Use when .context8/tasks/ has accumulated many completed/cancelled tasks — archive old tasks and generate monthly summary documents for LLM-friendly historical overview.
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tasks, maintenance, archiving, context8]
    related_skills: [task-do, task-plan, task-continue, task-review]
---

# Task Compacting — Archive Old Tasks with Monthly Summaries

## Overview

Over time `.context8/tasks/` accumulates completed, cancelled, and stale task files. This degrades the signal-to-noise ratio: every session loads many irrelevant tasks, and the agent wastes context on completed work. This skill cleans up by:

1. Identifying completed/cancelled tasks older than a configurable threshold.
2. Moving them to `.context8/tasks/archive/`.
3. Generating or updating monthly summary files (`YYYY-MM-summary.md`) with one paragraph per task — enough for an LLM to know what happened without reading individual files.

## When to use

- `.context8/tasks/` has 10+ task files, most marked Complete or Cancelled
- Before starting a major new feature on a project with a long task history
- Periodically (e.g., monthly) as project maintenance
- Before `project-audit` or `project-review` to declutter the workspace

## When NOT to use

- You want to delete task files permanently — this skill only moves them
- The project has no `.context8/tasks/` directory
- You need to archive tasks outside the current repo
- All tasks are still active (Planned / In progress) — nothing to archive

## Output

- Old task files moved to `.context8/tasks/archive/<task-file>.md`
- Monthly summary file created/updated: `.context8/tasks/archive/YYYY-MM-summary.md`
- Inline report of actions taken (moved files, new summaries, skipped files)
- Git commit of all changes

---

## Full Prompt

# Task Compacting Execution

## Phase 1 — Scan Task Directory

### 1.1 Verify .context8/tasks/ exists

```bash
if [ ! -d ".context8/tasks" ]; then
  echo "❌ .context8/tasks/ does not exist. Nothing to archive."
  exit 1
fi
```

### 1.2 Ensure archive directory exists

```bash
mkdir -p ".context8/tasks/archive"
```

### 1.3 List all task files (excluding existing archive contents)

```bash
ls .context8/tasks/*.md 2>/dev/null | sort
```

If no task files found in the root directory, exit with message.

---

## Phase 2 — Identify Archive Candidates

### 2.1 Parse each task file for status

For each `.md` file under `.context8/tasks/` (not in `archive/`), read the first 15 lines
to extract the YAML-like frontmatter or markdown metadata. Look for:

- `**Status**:` line — **Complete** / **Cancelled** / **In progress** / **Planned**
- `**Date**:` line — determines which month the task belongs to
- `# Task:` first heading — the task title

```bash
for f in .context8/tasks/*.md; do
  echo "=== $(basename "$f") ==="
  head -15 "$f"
done
```

### 2.2 Determine threshold date

Default: tasks whose file **mtime** is older than 30 days from today.

```bash
THRESHOLD_DAYS=30
```

Override via `--older-than N` if provided. If no flag, use default.

### 2.3 Classify each file

For each file:

| Condition | Verdict |
|-----------|---------|
| Status "Complete" or "Cancelled" AND mtime older than threshold | ✅ Archive candidate |
| Status "Complete" or "Cancelled" but mtime newer than threshold | 📋 Too recent — skip |
| Status "Planned" or "In progress" | 🔵 Active — do NOT touch |
| Status missing | ⚠️ Unknown — ask user or skip |

```bash
for f in .context8/tasks/*.md; do
  STATUS=$(head -15 "$f" | grep "^\*\*Status\*\*:" | sed 's/.*: //')
  MTIME_DAYS=$(( ( $(date +%s) - $(stat -c %Y "$f") ) / 86400 ))
  # ... classification logic
done
```

---

## Phase 3 — Review Candidates (User Confirmation)

### 3.1 Present the list

Display candidates clearly:

```
═══ Archive Candidates (threshold: ${THRESHOLD_DAYS} days) ═══

  Complete:
    1. 2026-05-01_user-auth-refactor.md    (Completed, 45 days old)
    2. 2026-05-15_dependency-audit.md      (Completed, 36 days old)

  Cancelled:
    3. 2026-04-20_experiment-feature.md    (Cancelled, 61 days old)

  ⚠️ Unknown status:
    4. 2026-03-10_old-notes.md             (No status found)

  🔵 Active (NOT archived):
    - 2026-06-20_task-compacting-skill.md  (Planned)
```

### 3.2 Handle unknown status files

For each file with no recognizable status:
```
⚠️ "2026-03-10_old-notes.md" has no recognisable status.
  What do you want to do?
  [a] — archive it anyway
  [s] — skip it (default)
```

### 3.3 Ask for confirmation

```
Proceed with archiving? (y/N, or dry-run)
  y   — archive now
  N   — cancel (default)
  d   — dry-run (show what would happen, don't move anything)
```

If `--dry-run` flag was passed, skip this prompt and show the preview.

### 3.4 If `--force` flag was set

Skip the age threshold check — archive ALL completed/cancelled tasks regardless
of mtime. Still confirm in Phase 3.3 unless `--yes` flag is also set.

---

## Phase 4 — Archive Task Files

### 4.1 Process each candidate

For each confirmed candidate:

```bash
BASENAME=$(basename "$f")
DEST=".context8/tasks/archive/$BASENAME"

# Handle name collisions
if [ -f "$DEST" ]; then
  COUNT=1
  while [ -f ".context8/tasks/archive/${BASENAME%.md}_${COUNT}.md" ]; do
    COUNT=$((COUNT + 1))
  done
  DEST=".context8/tasks/archive/${BASENAME%.md}_${COUNT}.md"
fi

# Move the file
mv "$f" "$DEST"
echo "→ Archived: $BASENAME → archive/$(basename "$DEST")"
```

### 4.2 Dry-run override

If `--dry-run` was used, output what WOULD be moved but do NOT `mv` anything.

```
[Dry-run] Would move: 2026-05-01_user-auth-refactor.md → archive/
[Dry-run] Would create/update: archive/2026-05-summary.md
```

---

## Phase 5 — Generate Monthly Summaries

### 5.1 Group moved files by month

Determine each task's month from its `**Date**:` field (YYYY-MM-DD). Fallback
to file mtime if date field is missing.

```
2026-05-01_user-auth-refactor.md → 2026-05
2026-05-15_dependency-audit.md   → 2026-05
2026-04-20_experiment-feature.md → 2026-04
```

### 5.2 For each month, produce a summary paragraph per task

For each archived task file, parse:

- **Title**: line starting with `# Task:` (or `# ` heading)
- **Status**: `**Status**:`
- **Date**: `**Date**:`
- **Objective**: text in the `## Objective` section (first paragraph)
- **Decisions**: text in `## Decisions Made` section (first bullet or sentence)
- **Complexity**: `**Estimated total complexity**:`

Generate a summary entry for each task:

```markdown
- **[Task Title]** — Status: **Complete** (medium complexity, 2026-05-01).
  [Objective in 1-2 sentences, taken directly from the Objective section].
  [Key decisions made during implementation, from Decisions Made section,
   or a brief outcome note if Decisions Made is empty.]
```

Examples:

```
- **User Auth Refactor** — Status: **Complete** (medium, 2026-05-01).
  Refactored the authentication layer from JWT to session-based cookies.
  Decided to keep Redis sessions and add refresh token rotation.
- **Dependency Audit** — Status: **Complete** (small, 2026-05-15).
  Audited all Python dependencies for vulnerabilities; 3 critical fixes applied.
- **Experiment Feature** — Status: **Cancelled** (2026-04-20).
  Prototype for real-time collaboration feature. Cancelled after perf benchmarks
  showed 300ms latency — deferred to next quarter.
```

**Concision rules:**
- Maximum 3 sentences per entry.
- Use present tense for status descriptions, past tense for outcomes.
- Include the **complexity** indicator for Complete tasks.
- If the task was Cancelled, include the reason if stated in the Objective.
- If Decisions Made is populated, prefer that over Objective for the outcome
  description — it's more concrete.
- If neither Objective nor Decisions Made are parseable, describe the task
  from the `# Task:` heading + first non-empty paragraph.

### 5.3 Read existing summary if present

If `.context8/tasks/archive/YYYY-MM-summary.md` already exists, read it first.
Prepend new entries for the just-archived tasks at the top. Do NOT reorder or
modify existing entries.

```markdown
# 2026-05 Summary

*Generated by task-compacting on 2026-06-20.*

- **[new task]** — Status: **Complete**. ...
- **[another new task]** — Status: **Cancelled**. ...

---

## Archived Tasks

- **[previously archived task]** — Status: **Complete**. ...
```

New entries go at the top (most recent archival run first). Existing entries
stay as-is.

### 5.4 Write summary file

```bash
MONTH_DIR=".context8/tasks/archive"
MONTH="2026-05"
SUMMARY_FILE="${MONTH_DIR}/${MONTH}-summary.md"
# Write or update the file with new entries prepended
```

### 5.5 Print inline summary

After archiving and summarising, print:

```
═══ Compaction Report ═══

Archived:   4 task files
  → 2026-05-01_user-auth-refactor.md
  → 2026-05-15_dependency-audit.md
  → 2026-04-20_experiment-feature.md
  → 2026-03-10_old-notes.md

Summaries:
  → Created: archive/2026-04-summary.md (1 task)
  → Updated: archive/2026-05-summary.md (2 tasks — 1 new)

Skipped (too recent): 1
Skipped (active):     1
Skipped (no status):  0
```

---

## Phase 6 — Commit Changes

### 6.1 Stage and commit

```bash
git add .context8/tasks/archive/
git add .context8/tasks/*.md 2>/dev/null  # tracks deletions from tasks/
# Only if there are actually deletions
if git diff --cached --name-only | grep -q "^.context8/tasks/[^a]"; then
  git commit -m "chore(tasks): archive $(echo "$COUNT") completed/cancelled tasks older than $THRESHOLD_DAYS days"
fi
```

**Rule**: Only commit if there are actual staged changes. If `--dry-run` was used,
do NOT stage or commit anything.

---

## Completion Checklist

- [ ] `.context8/tasks/archive/` exists
- [ ] All confirmed candidates moved from `.context8/tasks/` → `archive/`
- [ ] No name collisions occurred (or were handled gracefully)
- [ ] Monthly summary files created or updated with new entries at top
- [ ] Each summary entry ≤ 3 sentences, captures title, status, objective, outcome
- [ ] Active tasks (Planned, In progress) were NOT touched
- [ ] Dry-run mode did NOT move or commit anything
- [ ] Report printed with counts of archived, skipped, and summarised files
- [ ] Changes committed with descriptive message

## Rules

- **Never** delete files — only move them to `archive/`.
- **Never** archive tasks with status "Planned" or "In progress".
- **Never** modify existing summary entries — only prepend new ones.
- **Always** ask for confirmation before moving files (unless `--yes` flag).
- **Always** handle name collisions with a numeric suffix.
- Dry-run flag means **nothing** is moved, written, or committed.
- Summary entries are factual, not interpretive. If the Objective is empty, say
  "[No objective recorded]" — do not fabricate.
- Write all documentation in English.
