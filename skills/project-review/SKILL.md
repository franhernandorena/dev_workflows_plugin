---
name: project-review
version: 1.0.0
description: Full project-level architecture and quality review — analyzes codebase, dependencies, security posture, test health, and technical debt before significant milestones
---

# Project Review — Full Project Health Check

## Overview
Comprehensive project review that goes beyond diff-level `task-review`. Loads the full project context, audits architecture, dependencies, security, tests, docs, and technical debt. Produces a structured review report with actionable items. Blocks major milestones if critical issues are unresolved.

## When to use
- Before a major release
- Before taking on significant new feature work
- After `project-audit` when you need detail
- When joining an existing project for the first time
- Quarterly or milestone-based project health checks

## When NOT to use
- Reviewing a single PR/diff → use `task-review`
- Quick project assessment → use `project-audit` (lighter)
- During active development on a specific task → use `task-do` first

## Output
- `PROJECT_REVIEW.md` in `.context8/reports/` with sections: architecture audit, dependency audit, security posture, test health, documentation health, technical debt, action items
- Review report also printed inline

---

## Full Prompt

## Phase 1 — Load Project Context

### 1.1 Read project overview
```
ls .context8/
cat .context8/PROJECT_OVERVIEW.md 2>/dev/null || echo "No overview"
cat .context8/AGENT_CONTEXT.md 2>/dev/null || echo "No agent context"
```

### 1.2 Identify project type
```
ls pyproject.toml package.json Cargo.toml go.mod 2>/dev/null
cat pyproject.toml 2>/dev/null | head -30
cat package.json 2>/dev/null | head -30
```

### 1.3 Read architecture docs
```
ls .context8/architecture/ 2>/dev/null
```

---

## Phase 2 — Architecture Review

For each module/package in `src/` or equivalent:

1. **Module boundaries**: Are they clear? Do cross-module imports suggest boundary erosion?
2. **Dependency direction**: Do high-level modules depend on low-level ones (good) or vice versa (bad)?
3. **Cycles**: Any circular imports or dependency cycles?
4. **File sizes**: Any files > 500 lines that should be split?
5. **Duplication**: Similar code patterns in multiple places that should be abstracted?

Check for common anti-patterns:
- God classes / God modules
- Shotgun changes (a single change requires touching many files)
- Inconsistent patterns (some modules use functions, others use classes for the same thing)

---

## Phase 3 — Dependency Audit

```
# Python
cat pyproject.toml | grep -E "^\[tool\.poetry|^\[project\]|^dependencies" -A 20 2>/dev/null
pip list --outdated 2>/dev/null

# Node/TS
cat package.json | jq '.dependencies, .devDependencies' 2>/dev/null
npm outdated 2>/dev/null

# Rust
cat Cargo.toml | grep -E "^\[dependencies" -A 30 2>/dev/null
cargo outdated 2>/dev/null
```

Checklist:
- [ ] Any dependency at major version N-2 or older (seriously outdated)?
- [ ] Any deprecated or unmaintained dependencies?
- [ ] Any known CVEs in the dependency tree?
- [ ] Dev dependencies leaking into production?
- [ ] Unused dependencies (dead weight)?
- [ ] Pinning to exact versions vs ranges (safety vs flexibility)?

---

## Phase 4 — Security Posture

- [ ] AuthN/AuthZ: Is authentication implemented? Are permissions checked on every protected endpoint?
- [ ] Secrets: Any secrets in `.env` files committed? In source code? In CI configs?
- [ ] Input validation: Are all external inputs validated/sanitized?
- [ ] SQL injection: Parameterized queries everywhere?
- [ ] XSS/CSRF: Proper headers and escaping for web apps?
- [ ] Rate limiting: On public endpoints?
- [ ] Logging: Sensitive data being logged? Structured logging?
- [ ] Data exposure: Any excessive data returned in API responses?
- [ ] Dependencies: Any high/CVSS 9+ vulnerabilities?
- [ ] CI/CD: Are security scans running? SAST, SCA, secret scanning?

---

## Phase 5 — Test Health

```
# Coverage
pytest --cov=src --cov-report=term-missing -q 2>&1 | tail -20
npm test -- --coverage 2>&1 | tail -20
cargo tarpaulin 2>&1 | tail -10
```

- [ ] Coverage >= 70% (adjust for project goals)?
- [ ] Tests run in CI?
- [ ] Tests are deterministic (not flaky)?
- [ ] Integration/e2e tests exist for critical paths?
- [ ] Test names follow a consistent convention (e.g. `test__unit__function__scenario`)?
- [ ] Slow tests are tagged and in a separate CI job/step?

---

## Phase 6 — Documentation Health

- [ ] README exists and is current?
- [ ] Architecture docs exist (`.context8/architecture/`)?
- [ ] API docs exist (OpenAPI, JSDoc, pydoc)?
- [ ] Changelog is maintained?
- [ ] CONTRIBUTING.md exists for multi-contributor projects?
- [ ] Setup instructions work (can a new dev go from clone to running in < 10 min)?

---

## Phase 7 — Technical Debt Assessment

Look for:
- [ ] TODO/FIXME/HACK comments without issue references
- [ ] Deprecated code paths still in use
- [ ] Dead code (functions/variables never referenced)
- [ ] Tests that are skipped or marked `@pytest.mark.skip`
- [ ] Known performance bottlenecks
- [ ] Missing error handling in key paths

---

## Phase 8 — Review Report

```markdown
# Project Review — [project name]

**Date**: YYYY-MM-DD
**Reviewer**: [agent/tool]
**Version**: [git describe or version]

## Architecture
- Health: ✅ / ⚠️ / ❌
- Key findings: [list]

## Dependencies
- Health: ✅ / ⚠️ / ❌
- Outdated: [count]
- Vulnerabilities: [count, list critical ones]
- Action: [upgrade / monitor / nothing]

## Security
- Health: ✅ / ⚠️ / ❌
- Issues: [list, by severity]
- Critical blockers: [list]

## Tests
- Coverage: [%]
- Health: ✅ / ⚠️ / ❌
- Issues: [list]

## Documentation
- Health: ✅ / ⚠️ / ❌
- Gaps: [list]

## Technical Debt
- Health: ✅ / ⚠️ / ❌
- TODOs: [count]
- Dead code: [count]
- Action items: [list]

## Overall Verdict
✅ HEALTHY / ⚠️ NEEDS WORK / ❌ BLOCKED

## Recommended Priorities
1. [P0 - fix now]
2. [P1 - fix this sprint]
3. [P2 - schedule next]
```

If verdict is BLOCKED: do NOT proceed with the milestone until critical items are resolved.

---

## Completion Checklist

- [ ] Architecture reviewed and findings documented
- [ ] Dependencies audited and vulnerabilities noted
- [ ] Security posture assessed and critical issues flagged
- [ ] Test health evaluated
- [ ] Documentation gaps identified
- [ ] Technical debt documented
- [ ] Review report generated in `.context8/reports/PROJECT_REVIEW.md`
- [ ] Overall verdict delivered inline and in report

---

## Rules
- Do not skip any phase for "well-known" projects.
- If any security vulnerability is CVSS 9+, the project is BLOCKED until fixed.
- Write review report to `.context8/reports/` and also print summary inline.
- All output in English unless project language is explicitly non-English.
