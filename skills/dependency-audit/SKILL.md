---
name: dependency-audit
version: 1.0.0
description: Audits project dependencies for vulnerabilities, outdated packages, deprecated libraries, and unused dependencies — cross-language (Python, Node, Rust, Go)
---

# Dependency Audit — Security & Health Check for Project Dependencies

## Overview
Scans the dependency tree for known vulnerabilities, outdated major versions, deprecated packages, and unused dependencies. Produces a structured audit report with actionable upgrade paths. Designed for pre-release or periodic maintenance.

## When to use
- Before a release
- Before a major upgrade or migration
- As part of `project-review`
- Monthly/quarterly dependency maintenance
- When a CVE is announced affecting your tech stack

## When NOT to use
- Just reviewing a single PR → use `task-review` (security phase covers new deps)
- Just checking if `npm audit` / `pip audit` is clean → run that directly, this is for the full report
- During active feature development → use `dependency-audit` as a scheduled check, not mid-task

## Output
- `DEPENDENCY_AUDIT.md` in `.context8/reports/` with categorized findings (critical, high, medium, low, info)
- Upgrade plan with step-by-step migration notes for breaking changes
- Summary printed inline

---

## Full Prompt

## Phase 1 — Detect Project Language & Package Managers

```
ls pyproject.toml requirements.txt Pipfile poetry.lock package.json yarn.lock pnpm-lock.yaml Cargo.toml go.mod go.sum composer.json 2>/dev/null
```

From this, determine:
- Python: pip / pipenv / poetry / uv
- Node: npm / yarn / pnpm
- Rust: cargo
- Go: go modules
- Multi-language: all apply

---

## Phase 2 — Vulnerability Scan

### Python
```bash
# pip-audit (pip)
pip-audit 2>/dev/null || python -m pip install pip-audit && pip-audit

# Safety (poetry)
poetry run safety check 2>/dev/null || echo "safety not installed"

# pip-audit on requirements
pip-audit -r requirements.txt 2>/dev/null

# Check for known vulnerability databases
pip list --format=columns 2>/dev/null | tail +3
```

### Node/TypeScript
```bash
npm audit --audit-level=moderate 2>/dev/null
# or
yarn audit 2>/dev/null
# or
pnpm audit 2>/dev/null

# Check for direct vs transitive vulns
npm audit --json 2>/dev/null | python -c "
import json,sys
d=json.load(sys.stdin)
print(f'Critical: {d.get(\"metadata\",{}).get(\"vulnerabilities\",{}).get(\"critical\",0)}')
print(f'High: {d.get(\"metadata\",{}).get(\"vulnerabilities\",{}).get(\"high\",0)}')
print(f'Moderate: {d.get(\"metadata\",{}).get(\"vulnerabilities\",{}).get(\"moderate\",0)}')
print(f'Low: {d.get(\"metadata\",{}).get(\"vulnerabilities\",{}).get(\"low\",0)}')
" 2>/dev/null
```

### Rust
```bash
cargo audit 2>/dev/null || cargo install cargo-audit && cargo audit
```

### Go
```bash
govulncheck ./... 2>/dev/null
go list -m all 2>/dev/null
```

---

## Phase 3 — Outdated Dependency Check

```bash
# Python
pip list --outdated 2>/dev/null | head -40

# Node/TS
npm outdated 2>/dev/null | head -40
# or yarn outdated
yarn outdated 2>/dev/null | head -40

# Rust
cargo outdated 2>/dev/null | head -40

# Go
go list -u -m all 2>/dev/null | head -40
```

For each outdated dep, note:
- Current version → Latest version → Major version gap
- Is the new version a breaking change? (major version bump or not)
- Is the package still maintained? (check latest publish date if unsure)

---

## Phase 4 — Unused Dependency Detection

```bash
# Python
pip install dephell 2>/dev/null && dephell deps list --from pyproject.toml 2>/dev/null
# Or manual: grep imports in code vs declared deps
find src -name '*.py' -exec grep -h '^import\|^from' {} \; | sort -u | cut -d' ' -f2 | cut -d'.' -f1 | sort -u

# Node/TS
npx depcheck 2>/dev/null
npm prune --dry-run 2>/dev/null

# Rust
cargo udeps 2>/dev/null
```

---

## Phase 5 — Deprecation & License Check

```bash
# Check for deprecated packages
# Python
pip show <package> 2>/dev/null | grep -i "home-page\|requires"

# Node
npm view <package> deprecated 2>/dev/null

# Check licenses
# Node
npx license-checker --summary 2>/dev/null
```

Flag any:
- Package marked as deprecated on PyPI/npm/crates.io
- License incompatible with project license (GPL in MIT project, etc.)
- Unmaintained packages (no updates in 2+ years)

---

## Phase 6 — Cross-Repo Dependency Sync (if workspace)

If this is part of a multi-repo workspace:
```bash
cat ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null
```

Check:
- Are shared dependencies at the same version across repos?
- Are there duplicate packages in the workspace?
- Are internal packages properly versioned?

---

## Phase 7 — Audit Report

```markdown
# Dependency Audit — [project]

**Date**: YYYY-MM-DD
**Language(s)**: [Python, Node, etc.]
**Total dependencies**: N (N dev)

## Vulnerability Summary
| Severity | Count | Action |
|----------|-------|--------|
| Critical | N | Fix immediately |
| High | N | Fix before release |
| Moderate | N | Schedule next sprint |
| Low | N | Monitor |

### Critical/High Vulnerabilities
| Package | Version | CVE | Severity | Fix |
|---------|---------|-----|----------|-----|
| pkg | 1.0.0 | CVE-2026-XXXX | Critical | Upgrade to 1.0.3 |

## Outdated Dependencies
| Package | Current | Latest | Breaking? | Action |
|---------|---------|--------|-----------|--------|
| pkg | 1.0.0 | 2.0.0 | Yes | Plan migration |

## Unused Dependencies
- pkg (declared, never imported)

## Deprecated Packages
- pkg (deprecated since 2024, suggested replacement: new-pkg)

## Upgrade Plan
### Immediate (P0)
1. [Step]

### Before Release (P1)
1. [Step]

### Next Sprint (P2)
1. [Step]
```

---

## Completion Checklist

- [ ] Vulnerability scan run (all languages)
- [ ] Outdated deps identified
- [ ] Unused deps identified
- [ ] Deprecation check done
- [ ] Cross-repo consistency checked (if multi-repo)
- [ ] Audit report written to `.context8/reports/DEPENDENCY_AUDIT.md`
- [ ] Upgrade plan included for breaking changes

---

## Rules
- Always run the vulnerability scan first — if Critical CVEs found, escalate before continuing.
- Do not auto-upgrade packages. Report findings and let the user decide.
- For breaking changes, include migration notes.
- All output in English.
