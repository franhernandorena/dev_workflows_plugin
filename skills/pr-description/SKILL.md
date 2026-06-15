---
name: pr-description
version: 1.0.0
description: After task-review, generates a structured PR description from the current diff — change summary, file list, testing done, risks, screenshot instructions
---

# PR Description — Generate Structured Pull Request Descriptions

## Overview
After `task-review` passes, generates a complete, structured PR description from the current git diff. Produces the exact text to paste into GitHub/GitLab/Bitbucket: change summary, file-by-file breakdown, testing performed, risks, and review notes. Saves time and ensures consistent PR quality across the team.

## When to use
- After `task-review` approves changes and before opening a PR
- When you need to quickly generate a PR description from uncommitted work
- For standardizing PR quality across a team

## When NOT to use
- No changes committed yet → `task-do` first, then use this
- Trivial one-line change → write manually (faster)
- PR already has a good description → skip

## Output
- Markdown PR description printed inline, ready to paste into GitHub/GitLab/Bitbucket

## Full Prompt

# PR DESCRIPTION — Generate Structured Pull Request

## RULE: This skill reads git diff and generates text. No application code changes.

---

## Phase 1 — Gather Context

### 1.1 Read the diff
```bash
git diff HEAD~1 --stat
git diff HEAD~1
```

For uncommitted changes:
```bash
git diff --stat
git diff
```

### 1.2 Gather metadata
```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Branch: $CURRENT_BRANCH"

# Get issue/PR references from branch name
echo "Branch pattern: $(echo $CURRENT_BRANCH | grep -oE '[A-Z]+-[0-9]+' || echo 'none')"

# Last commit message
git log --oneline -1 --format="%s"
```

### 1.3 Check for related task files
```bash
ls .context8/tasks/ 2>/dev/null | sort -r | head -3
```

### 1.4 Check for related issues
```bash
# Try reading branch prefix as issue reference
BRANCH_NAME=$(git branch --show-current)
ISSUE_REF=$(echo "$BRANCH_NAME" | grep -oE '[A-Z]+-[0-9]+')
if [ -n "$ISSUE_REF" ] && which gh 2>/dev/null; then
  gh issue view "$ISSUE_REF" --json title,body 2>/dev/null | head -40
fi
```

---

## Phase 2 — Analyze Changes

### 2.1 Classify files by type
```bash
echo "=== Added ==="
git diff HEAD~1 --diff-filter=A --name-only
echo "=== Modified ==="
git diff HEAD~1 --diff-filter=M --name-only
echo "=== Deleted ==="
git diff HEAD~1 --diff-filter=D --name-only
echo "=== Renamed ==="
git diff HEAD~1 --diff-filter=R --name-only
```

### 2.2 Extract key changes
```bash
# New functions/classes added
git diff HEAD~1 -- '*.py' | grep -E '^\+.*def |^\+.*class ' | head -15
git diff HEAD~1 -- '*.ts' | grep -E '^\+.*(export |function |class )' | head -15

# Changed imports
git diff HEAD~1 -- '*.py' | grep -E '^[-+].*(import |from )' | head -10
git diff HEAD~1 -- '*.ts' | grep -E '^[-+].*import ' | head -10

# Test changes
git diff HEAD~1 -- '*test*' --stat 2>/dev/null
```

---

## Phase 3 — Check Testing

```bash
# Run relevant tests
pytest -x -q 2>&1 | tail -10

# If JavaScript
npm test 2>&1 | tail -10
```

---

## Phase 4 — Generate PR Description

Synthesize the following structured PR description:

```markdown
## Description

[Concise summary: what changed and why. 2-3 sentences.]

Fixes #[issue] | Implements #[issue]

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Performance improvement
- [ ] Documentation
- [ ] CI/CD / Build
- [ ] Other (specify)

## Changes by File

### Added
| File | Purpose |
|------|---------|
| `path/to/new-file.py` | What it does |

### Modified
| File | What changed |
|------|-------------|
| `path/to/file.py:45-60` | Brief description of the change |

### Deleted
| File | Reason |
|------|--------|
| `path/to/removed.py` | Why it was removed |

## Testing

- [ ] Existing tests pass
- [ ] New tests added
- [ ] Manual testing performed

**Test output:**
```
$ pytest -x -q
.......
7 passed in 0.45s
```

## Risks

- **Medium**: Changing shared auth module — 5 dependents. Reviewed impact with `change-impact`.
- **Low**: Adding new endpoint — no existing behavior modified.

## Screenshots

[If UI changes: add before/after screenshots]

## Review Notes

- Focus on [specific area for reviewers]
- Migration path: [if breaking changes]
- Follow-up: [anything deferred to a later PR]
```

---

## Rules
- Read the actual git diff. Never hallucinate changes.
- Include real test output from Step 3.
- Risk section must reflect actual risk from the diff, not generic boilerplate.
- Print the PR description inline. The user can copy-paste to GitHub/GitLab.
- Respect existing PR templates if found (look for `.github/PULL_REQUEST_TEMPLATE.md`).
