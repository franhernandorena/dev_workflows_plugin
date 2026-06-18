---
name: project-audit
version: 1.0.0
description: Use when joining a project with no .context8, stale documentation, unknown technical debt, or before starting new work on an unfamiliar codebase — produces scored assessment before any changes
---

# Project Audit — Assess Existing Project

## Overview
Read-only assessment of an existing project. Explores the codebase fully, evaluates 7 dimensions (documentation, tests, architecture, conventions, dependencies/security, operational readiness, technical debt), and writes a structured audit report with dimension scores, critical findings, and prioritized next steps. No code changes.

## When to use
- Joining an unfamiliar codebase
- `.context8/` doesn't exist or is clearly stale
- Suspecting significant technical debt before planning new work
- Need an honest baseline before committing to `project-init`

## When NOT to use
- Starting work when context is already known → use `project-continue`
- First session but project is well-documented → use `project-init` directly

## Output
- `.context8/AUDIT.md` — dimension scores, critical findings, recommended next steps

## Full Prompt

# PROJECT AUDIT — Assess an Existing Project Without Documentation

## RULE: No code changes. Read-only. Output is an audit report.

Use when joining a project that has no `.context8/`, has stale documentation, or when you need an honest assessment of the current state before planning work. Output goes into `.context8/AUDIT.md`.

---

## Phase 1 — Discover What Exists

### 1.1 Directory structure
```bash
find . -not -path '*/node_modules/*' -not -path '*/.git/*' \
       -not -path '*/__pycache__/*' -not -path '*/.venv/*' \
       -not -path '*/dist/*' -not -path '*/build/*' \
       | sort | head -120
```

### 1.2 Root configuration files
Read every config file present:
- package.json / package-lock.json / yarn.lock / pnpm-lock.yaml
- pyproject.toml / setup.py / requirements*.txt / Pipfile
- dbt_project.yml / profiles.yml
- Cargo.toml / go.mod / build.gradle / pom.xml
- tsconfig.json / .eslintrc* / .prettierrc* / ruff.toml / .flake8
- docker-compose*.yml / Dockerfile*
- .env.example / .env.template (NEVER .env itself)
- Makefile / justfile / taskfile.yml

### 1.3 Git history & activity
```bash
git fetch --prune 2>&1
git log --oneline -30
git branch -a
git remote -v
git shortlog -sn --all | head -10
git log --oneline --all --since="90 days ago" | wc -l
```

Para cada rama local, detectar su propósito:

```bash
echo "=== Ramas y su propósito ==="
for branch in $(git branch --format='%(refname:short)' | sort); do
  last_date=$(git log "$branch" -1 --format="%ci" 2>/dev/null)
  last_msg=$(git log "$branch" -1 --format="%s" 2>/dev/null)
  behind_main=$(git rev-list --count origin/main..."$branch" 2>/dev/null)
  echo "$branch | $last_date | $last_msg"
done
```

### 1.4 CI/CD pipelines
Read every file in:
- .github/workflows/
- .gitlab-ci.yml / cloudbuild.yaml / .circleci/config.yml / bitbucket-pipelines.yml

### 1.5 Existing documentation
```bash
find . -name "*.md" -not -path '*/node_modules/*' | sort
find . -name "*.rst" -not -path '*/node_modules/*' | sort
```
Read every .md and .rst file found.

### 1.6 Test suite
```bash
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" \
          -o -name "*.spec.ts" -o -name "*.test.tsx" -o -name "jest.config*" \
          -o -name "pytest.ini" -o -name "vitest.config*" \) \
     -not -path '*/node_modules/*' | sort | head -40
```

Try running the test suite:
```bash
pytest -x -q 2>&1 | tail -20
npm test -- --run 2>&1 | tail -20
```

### 1.7 Entry points & main modules
Identify and read:
- Main app entry (main.py / app.py / index.ts / server.ts / main.rs / cmd/)
- Router definitions
- Core models / schemas / types
- Database migrations directory

### 1.8 Infrastructure & cloud
Read any IaC files: terraform/ / pulumi/ / cdk/ / serverless.yml / kubernetes/ / k8s/

### 1.9 Security surface
```bash
# Check for hardcoded secrets patterns (no output = good)
grep -rn "password\s*=\s*['\"]" --include="*.py" --include="*.ts" --include="*.js" \
     -l 2>/dev/null | grep -v test | grep -v spec | head -10
grep -rn "api_key\s*=\s*['\"]" --include="*.py" --include="*.ts" --include="*.js" \
     -l 2>/dev/null | grep -v test | head -10
grep -rn "secret\s*=\s*['\"]" --include="*.py" --include="*.ts" --include="*.js" \
     -l 2>/dev/null | grep -v test | head -10
```

---

## Phase 2 — Assess Against Key Dimensions

For each dimension, write findings: what exists, what is missing, severity (high/medium/low).

### 2.1 Documentation coverage
- Is there a README? Is it accurate?
- Does `.context8/` exist? Is it current?
- Are architecture decisions documented (ADRs)?
- Can a new developer understand the project from existing docs alone?

### 2.2 Test coverage
- Do tests exist?
- Do they run cleanly?
- What is covered: unit / integration / e2e?
- What critical paths have zero test coverage?

### 2.3 Architecture clarity
- Is the architecture pattern identifiable (monolith / microservices / layered / pipeline)?
- Are module boundaries clear or is there significant coupling?
- Is the data flow traceable end-to-end?
- Are there architectural anti-patterns (circular imports, god modules, mixed concerns)?

### 2.4 Code conventions
- Is there a consistent naming convention?
- Is there a linter/formatter configured and passing?
- Is the error handling pattern consistent?
- Are there obvious code smells (magic numbers, dead code, duplicated logic)?

### 2.5 Dependencies & security
- Are dependencies pinned or floating?
- Are there obviously outdated or deprecated dependencies?
- Were any hardcoded secrets found in Phase 1.9?
- Is there a `.gitignore` that covers `.env` and credentials?

### 2.6 Operational readiness
- Is there a documented way to run the project locally?
- Is there a documented deploy process?
- Are environment variables documented?
- Is there logging? Is it structured?
- Is there observability (metrics, traces, alerts)?

### 2.7 Technical debt
- Are there open TODOs, FIXMEs, or HACKs in the codebase?
  ```bash
  grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" --include="*.ts" --include="*.js" \
       -not -path '*/node_modules/*' | wc -l
  grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" --include="*.ts" --include="*.js" \
       -not -path '*/node_modules/*' | head -20
  ```
- Is there commented-out code suggesting abandoned work?
- Are there migrations that have never been run or are inconsistent?

---

## Phase 3 — Write Audit Report

Create `.context8/AUDIT.md`:

```markdown
# Project Audit — [project name]

**Date**: YYYY-MM-DD
**Auditor**: [agent / session ID]
**Codebase snapshot**: [git commit hash]

## Executive Summary
[2–3 sentences: overall health, most critical gaps, recommended first action.]

## Tech Stack
[Languages, frameworks, databases, cloud services — as found, not as intended.]

## Architecture Assessment
[What pattern is in use. How clear the structure is. Key coupling issues.]

## Dimension Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Documentation | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Test coverage | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Architecture clarity | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Code conventions | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Dependencies & security | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Operational readiness | 🔴 / 🟡 / 🟢 | [one-line summary] |
| Technical debt | 🔴 / 🟡 / 🟢 | [one-line summary] |

🔴 = critical gaps / 🟡 = partially covered / 🟢 = adequate

## Critical Findings (must address before new work)
| Finding | Severity | Recommended action |
|---------|----------|--------------------|
| [description] | high/med/low | [action] |

## Documentation Gaps
[What is missing from .context8/. Which sections of AGENT_CONTEXT.md do not exist yet.]

## Test Coverage Gaps
[Specific modules or paths with zero or insufficient coverage.]

## Security Concerns
[Anything found in Phase 1.9 or Phase 2.5. Be specific.]

## Technical Debt Inventory
[Top 10 TODOs/FIXMEs by impact. Count of total debt markers.]

## Recommended Next Steps
1. [Highest-priority action. Be specific.]
2. [Second action.]
3. [...]

## What NOT to Do Before Addressing Critical Findings
[Explicit list of risky actions given the current state.]
```

---

## Phase 4 — Bootstrap Documentation (optional)

If `.context8/` does not exist and the audit reveals the project is ready for it:
- Stop here and run `project-init` using findings from this audit as a head start.
- Reference this audit file in the new AGENT_CONTEXT.md.

If `.context8/` exists but is stale:
- Update stale sections using findings from this audit.
- Note in each updated section: `[Updated by audit on YYYY-MM-DD]`.

---

## Completion Checklist

- [ ] All Phase 1 steps complete (no steps skipped).
- [ ] All 7 dimensions assessed in Phase 2.
- [ ] `.context8/AUDIT.md` written with all required sections.
- [ ] Critical findings explicitly listed with severity.
- [ ] Security concerns surfaced (even if "none found").
- [ ] Recommended next steps are concrete and prioritized.
- [ ] No code was changed during this audit.

---

## Rules
- Audit what exists, not what should exist.
- If a section has nothing to report: write "None found." — do not omit it.
- Security findings are always high severity. Never downgrade them.
- Do not start fixing issues during the audit. Record them. Fix comes after.
- If the codebase is too large to audit fully: note what was sampled and what was skipped.
- Write all documentation in English.
