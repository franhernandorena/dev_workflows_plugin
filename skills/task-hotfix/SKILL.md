---
name: task-hotfix
version: 1.0.0
description: Use for urgent production bugs where normal planning overhead is too slow — triage, locate root cause, minimal fix, security check, verify, and ship with a fast-track PR
---

# Task Hotfix — Urgent Production Fix

## Overview
Compressed but complete fix workflow. Phases are triage (5 min max), root cause confirmation, minimal fix, security check, full verification, and fast-track PR. Speed with control — phases are compressed, not skipped. A rushed fix that introduces a regression is worse than the original bug.

## When to use
- Production is broken and time matters
- Normal `task-plan` → `task-do` cycle is too slow
- Root cause is suspected but needs confirmation

## When NOT to use
- Not urgent → use `task-plan` + `task-do` for full discipline
- Root cause completely unknown with no hypothesis → investigate first, then use this

## Hard rule
If the fix requires more than 20 lines changed: pause. Use a targeted mitigation (feature flag, rollback) while a proper fix is planned.

## Output
- Minimal fix committed on `hotfix/[description]` branch
- Task file with confirmed root cause
- Fast-track PR with root cause, fix, and blast radius documented

## Full Prompt

# HOTFIX — Urgent Production Fix

## RULE: Speed with control. Skip nothing that prevents shipping a broken fix.

Use for urgent bugs in production where normal planning overhead is too slow. Phases are compressed but not skipped. Every change is deliberate.

---

## Phase 1 — Triage (5 minutes max)

Answer these before touching any code:

1. **What is broken?** Exact symptom. What fails, where, for whom.
2. **What is the blast radius?** How many users/systems affected. Is data at risk.
3. **Is there an immediate mitigation?** Feature flag off, rollback, config change, traffic redirect. If yes: apply it now and buy time.
4. **What is the root cause hypothesis?** Best guess based on symptoms and recent changes.
5. **What is the fix?** One sentence. If you cannot state it, continue to Phase 2.

Record answers in a new task file:
```bash
touch .context8/tasks/$(date +%Y-%m-%d)_hotfix_[short-description].md
```

Task file status: `**Status**: In progress (hotfix)`

---

## Phase 2 — Locate the Bug

### 2.1 Check recent changes
```bash
git log --oneline -10
git diff HEAD~1 HEAD -- [suspected file]
```

### 2.2 Read the failing code
Read the exact files implicated by the root cause hypothesis. No skimming.

### 2.3 Reproduce locally (if possible)
Run the failing test or scenario:
```bash
# Python
pytest [specific test] -xvs 2>&1 | tail -40
# Node/TS
npm test -- --run [specific test] 2>&1 | tail -40
```

Document reproduction steps in the task file.

### 2.4 Confirm root cause
State in the task file: "Root cause confirmed: [exact explanation]."
Do not proceed to a fix until root cause is confirmed.

---

## Phase 3 — Fix

### 3.1 Branch
```bash
git checkout -b hotfix/[short-description]
```

### 3.2 Read before writing
Read every file you are about to modify. No exceptions.

### 3.3 Implement the minimal fix
Fix only the confirmed root cause. No refactoring. No cleanup. No "while I'm here" changes.
The fix should be as small as possible — the fewer lines changed, the lower the risk.

### 3.4 Security check (mandatory, even for hotfixes)
- Does the fix introduce any injection vector?
- Does it expose sensitive data?
- Does it bypass an auth check?

If yes to any: stop. A security regression is worse than the original bug.

---

## Phase 4 — Verify

### 4.1 Reproduce the fix
Run the same scenario from Phase 2.3. Confirm it no longer fails.

### 4.2 Run targeted tests
```bash
# Python — test the affected module
pytest [specific module or test file] -x -q 2>&1 | tail -20
# Node/TS
npm test -- --run [specific file] 2>&1 | tail -20
```

### 4.3 Run the full test suite
```bash
pytest -x -q 2>&1 | tail -30
npm test -- --run 2>&1 | tail -30
```

All previously passing tests must still pass.

### 4.4 Lint check
```bash
ruff check . 2>/dev/null || flake8 . 2>/dev/null || true
npm run lint 2>/dev/null || true
```

---

## Phase 5 — Ship

### 5.1 Commit
```bash
git add [specific files only — never git add .]
git commit -m "fix(scope): short description of what was broken and how it is fixed"
```

### 5.2 PR (fast-track)
```bash
gh pr create --title "hotfix: [short description]" --body "$(cat <<'EOF'
## Root Cause
[One paragraph: what was broken and why.]

## Fix
[What changed and why this fixes it.]

## Test plan
- [ ] Reproduction scenario verified fixed
- [ ] Full test suite passes
- [ ] No linting errors
- [ ] Security check: no new vectors introduced

## Blast radius of fix
[What could this change break? Why it won't.]
EOF
)"
```

### 5.3 Update task file
```markdown
**Status**: Complete (hotfix)

## Root Cause
[Confirmed explanation]

## Fix Applied
[What changed, file by file]

## Files Modified
| File | Change |
|------|--------|
| `path/to/file` | [what changed] |
```

---

## Completion Checklist

- [ ] Root cause confirmed before fixing.
- [ ] Fix is minimal — only what is necessary.
- [ ] Security check passed.
- [ ] Reproduction scenario verified fixed.
- [ ] Full test suite passes.
- [ ] PR opened with root cause and blast radius documented.
- [ ] Task file complete.
- [ ] Mitigation (if applied in Phase 1) can now be reverted.

---

## Rules
- Compress phases, do not skip them. A rushed fix that breaks something else is worse than a slow fix.
- Fix only the confirmed root cause. Resist the urge to clean up surrounding code.
- If you cannot confirm root cause in Phase 2: escalate. Do not guess at a fix.
- If the fix requires more than 20 lines changed: pause. A large hotfix is a risk. Consider a targeted mitigation + a proper fix in a follow-up task.
- Write all documentation in English.
