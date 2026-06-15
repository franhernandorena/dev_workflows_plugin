---
name: task-continue
version: 1.0.0
description: Resume a partially completed task — reloads state from task file, checks what's been done, and continues from the last incomplete phase
---

# Task Continue — Resume Interrupted Work

## Overview
Loads the task file from `.context8/tasks/`, identifies the last completed and next incomplete phase, and continues execution from that point. Preserves all context, decisions, and partial outputs from the previous session.

## When to use
- A `task-do` session was interrupted (timeout, tool error, manual stop)
- You need to resume work on a task with status "In progress"
- You're starting a new session and a previous task is incomplete

## When NOT to use
- The task has status "Complete" → no resumption needed
- The task file doesn't exist → the session is lost, use `task-plan` to re-plan
- You want to start a new task → use `task-plan` + `task-do`
- Needs a production hotfix → use `task-hotfix` (separate flow)

## Output
- Task file updated with resumption timestamp
- Current phase status printed inline
- Execution continues from the next uncompleted phase

---

## Full Prompt

## Phase 1 — Find the Task

### 1.1 Locate the task file
```bash
ls -lt .context8/tasks/ 2>/dev/null | head -5
```

Look for the most recent task file that has status "In progress" or "Complete" with incomplete post-tasks.

### 1.2 Read the task file
Read the full content of the most recent task file.

Identify:
- **Task title and description**: what was the goal?
- **Status**: "In progress" → good candidate. "Complete" → check if post-tasks remain.
- **Current phase**: which phase was last completed?
- **Acceptance criteria**: are some checked off?
- **Modified files**: which files were already touched?
- **Decisions**: what decisions were made?
- **Blockers**: were there any unresolved blockers?

---

## Phase 2 — Assess Continuability

Check for blockers:

| Condition | Verdict |
|-----------|---------|
| Task file found, status "In progress", no blockers | ✅ Continue |
| Task file found, status "In progress", has blockers | ⚠️ Resolve blockers first |
| Task file found, status "Complete" | ✅ All done — review post-tasks |
| No task file found | ❌ Cannot resume — re-plan |

If blockers exist:
- Can they be resolved now?
- If yes, continue. If not, present to user and ask.

---

## Phase 3 — Rebuild Context

### 3.1 Restore project context
```bash
cat .context8/AGENT_CONTEXT.md 2>/dev/null
```

### 3.2 Check git status
```bash
git status
git log --oneline -5
```

Are there uncommitted changes from the previous session? Note them.

### 3.3 Re-read modified files
For each file listed in the task as modified:
```
Read it fully — the file may have changed since the task file was written.
```

### 3.4 Verify test status
```bash
pytest -q --tb=short 2>/dev/null | tail -5
npm test 2>/dev/null | tail -5
```

Note: if tests are red, were they red before the task started? If not, something broke in the previous session.

---

## Phase 4 — Continue from Next Phase

Find the phase planner in the task file:
```markdown
## Phase Plan
- [x] Phase 1 — Setup
- [x] Phase 2 — Implementation (50%)
- [ ] Phase 3 — Testing
- [ ] Phase 4 — Documentation
```

For this example: Phase 2 was partially done (50%). So:

### 4.1 Complete Phase 2
- What parts of the implementation remain?
- Continue from the point of interruption.
- Do NOT redo completed work unless something changed.

### 4.2 Continue the task-do cycle
After completing the remaining parts of the current phase, proceed through the standard phases:
1. Implementation (continued)
2. Testing
3. Documentation
4. Verification
5. Cleanup

---

## Phase 5 — Update Task Status

After resuming and making progress:

```markdown
**Status**: In progress (resumed)
**Resumed at**: YYYY-MM-DD HH:MM
**Last session ended at**: [timestamp from task file or session end]
**Phase progress**: [updated]
**Notes**: 
- Previous session completed Phases 1-2
- Resumed with Phase 3
- [any context that changed between sessions]
```

---

## Completion Checklist

- [ ] Task file located and read
- [ ] Continuability assessed
- [ ] Context rebuilt (AGENT_CONTEXT, git, files, tests)
- [ ] Next incomplete phase identified
- [ ] Work continuing from point of interruption

---

## Rules
- Do NOT restart the task from scratch unless the task file is lost or corrupted.
- Do NOT redo completed phases — verify and move forward.
- If tests were passing before interruption and failing now, diagnose before continuing implementation.
- If the project has changed significantly (new dependencies, different branch), flag it before resuming.
- All output in English.
