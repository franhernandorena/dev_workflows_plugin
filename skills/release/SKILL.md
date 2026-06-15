---
name: release
version: 1.0.0
description: End-to-end release workflow — version bump, changelog generation, tagging, release notes, cross-repo coordination, and post-release verification
---

# Release — Tag, Changelog, and Publish

## Overview
Orchestrates the full release lifecycle: bump version, generate changelog from git history, create git tag, write release notes (GitHub/GitLab), and verify post-release. Supports single-repo and multi-repo workspaces.

## When to use
- Ready to cut a new release
- After `deploy-plan` has been agreed upon
- When the changelog needs updating for a release
- At the end of a sprint/iteration

## When NOT to use
- Just want to deploy existing code → use `deploy-plan`
- Just want a changelog entry → use `changelog-update` (or manual edit)
- Mid-development → releases should be milestones, not every commit
- Hotfix → use `task-hotfix` workflow, then `release` for the patch bump

## Output
- Updated version in manifest files (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.)
- `CHANGELOG.md` updated
- Git tag created (`vX.Y.Z`)
- Release notes file: `.context8/releases/vX.Y.Z.md`
- (Optional) GitHub/GitLab release published

---

## Full Prompt

## Phase 0 — Prerequisites

Before starting, verify:
```bash
git status                   # No uncommitted changes? (unless intentional)
git log --oneline HEAD..origin/HEAD  # All changes pushed?
```

If changes are local and uncommitted → commit or stash first.
If ahead of remote → push first.

---

## Phase 1 — Determine Version Bump

### 1.1 Read the current version
```
cat pyproject.toml | grep '^version' | head -1
cat package.json | jq '.version'
cat Cargo.toml | grep '^version' | head -1
cat .context8/architecture/module_map.md | grep 'Current version' 2>/dev/null
```

### 1.2 Determine bump type based on content
Analyze commits since last tag:
```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
git log $LAST_TAG..HEAD --oneline
git log $LAST_TAG..HEAD --oneline | grep -iE '^feat|^feature|^breaking' 2>/dev/null
```

- **PATCH** (1.0.0 → 1.0.1): bug fixes only, no new features
- **MINOR** (1.0.0 → 1.1.0): new features, backward compatible
- **MAJOR** (1.0.0 → 2.0.0): breaking API changes

If unsure: ask the user for the bump type.

---

## Phase 2 — Update Changelog

### 2.1 Generate changelog entries
```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
git log --format="%s (%h)" $LAST_TAG..HEAD
```

Group by type:
- **Features**: commits starting with `feat:`
- **Bug Fixes**: commits starting with `fix:`
- **Documentation**: commits starting with `docs:`
- **Refactoring**: commits starting with `refactor:`
- **Dependencies**: commits starting with `deps:` or `chore(deps):`
- **Other**: unclassified changes

### 2.2 Update CHANGELOG.md
Prepend a new version section to `CHANGELOG.md`:

```markdown
## [vX.Y.Z] - YYYY-MM-DD

### Features
- Item 1 (#PR, @author)
- Item 2 (#PR, @author)

### Bug Fixes
- Item 1 (#PR, @author)

### Dependencies
- Updated dep X from v1 to v2 (#PR, @author)

### Other
- Item 1 (#PR, @author)
```

If no CHANGELOG.md exists, create one with the current and recent major releases.

---

## Phase 3 — Bump Version

Update the version in ALL manifest files:
```bash
# Python (pyproject.toml)
sed -i 's/^version = ".*"/version = "X.Y.Z"/' pyproject.toml

# Node (package.json)
npm version X.Y.Z --no-git-tag-version 2>/dev/null

# Rust (Cargo.toml)
sed -i 's/^version = ".*"/version = "X.Y.Z"/' Cargo.toml

# Go / others — detect and update similarly
```

---

## Phase 4 — Create Tag & Release Notes

### 4.1 Write release notes
Create `.context8/releases/vX.Y.Z.md`:
```markdown
# Release vX.Y.Z

**Date**: YYYY-MM-DD

## Highlights
- [Top 2-3 user-facing changes]

## Changelog
[Paste CHANGELOG.md section]

## Upgrade Notes
[Breaking changes, migration steps, config changes]

## Repos
- repo-a: vX.Y.Z
- repo-b: vX.Y.Z  (if multi-repo)

## Verification
- [ ] CI green
- [ ] Tests pass
- [ ] Smoke test passed
- [ ] Changelog reviewed
```

### 4.2 Commit and tag
```bash
git add -A
git commit -m "chore(release): vX.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main
git push origin vX.Y.Z
```

### 4.3 (Optional) Create GitHub/GitHub release
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file .context8/releases/vX.Y.Z.md \
  --target main
```

---

## Phase 5 — Multi-Repo Coordination (if workspace)

If this project is part of a multi-repo workspace:
```bash
cat ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null
```

For each sibling repo that shares this release:
- Does it need a version bump too?
- Does it need dependency updates to point at the new release?
- Check if a coordinated release tag is needed across repos

---

## Phase 6 — Post-Release Verification

- [ ] CI is green on the release commit
- [ ] Tag exists in remote (`git ls-remote --tags origin`)
- [ ] GitHub release page shows the new release (if published)
- [ ] Package is installable (if publishing): `pip install`, `npm install`, etc.
- [ ] Changelog renders correctly
- [ ] Follow-up: bump version to `X.Y.Z-dev` or `X.Y.(Z+1)-dev` for next iteration

---

## Completion Checklist

- [ ] Version bumped in all manifest files
- [ ] CHANGELOG.md updated with grouped entries
- [ ] Release notes written to `.context8/releases/vX.Y.Z.md`
- [ ] Git tag created and pushed
- [ ] Cross-repo coordination done (if multi-repo)
- [ ] Post-release verification complete (CI, tag, changelog)

---

## Rules
- Do NOT bump version without user confirmation of the bump type (PATCH/MINOR/MAJOR).
- Changelog must be grouped by type (Features, Bug Fixes, etc.) — never a flat list of commits.
- Push tag separately from branch push (safer rollback).
- All output in English.
