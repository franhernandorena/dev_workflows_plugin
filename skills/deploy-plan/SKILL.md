---
name: deploy-plan
version: 1.0.0
description: First skill in the deployments domain — plans a deployment with target environment, ordered steps, rollback plan, post-deploy verification, and communication
---

# Deploy Plan — Structured Deployment Planning

## Overview
Plans a deployment from start to finish: identifies the target environment, orders the deployment steps, defines the rollback plan, specifies post-deploy verification, and plans stakeholder communication. Enables a completely new domain in dev-workflows — deployments.

## When to use
- Before deploying to staging, production, or any shared environment
- When you need a documented rollback plan
- When multiple people or teams are involved in a deployment
- For compliance or audit requirements (deployment records)

## When NOT to use
- Deploying to local dev environment → no plan needed
- Rapid hotfix to production already deployed → use `task-hotfix` then retroactively document
- CI/CD fully automates the deploy → just verify the pipeline, but still useful for rollback

## Output
- Markdown deploy plan printed inline and optionally saved to `.context8/deploy-plans/YYYY-MM-DD_description.md`

## Full Prompt

# DEPLOY PLAN — Structured Deployment Planning

## RULE: This skill plans only. No code changes. Output is a deploy plan file.

---

## Phase 1 — Understand the Deployment

### 1.1 Identify what is being deployed
```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Branch: $CURRENT_BRANCH"

# Last commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "no-tags")
echo "Last tag: $LAST_TAG"
git log --oneline "$LAST_TAG..HEAD" 2>/dev/null | head -30 || git log --oneline -10

# Check for uncommitted changes
git status --short | head -10
```

### 1.2 Ask clarifying questions
Ask the user (one at a time):
1. **Target environment?** (production, staging, canary, custom)
2. **Type of deployment?** (full release, hotfix, feature flag rollout, config change)
3. **Any known risks or concerns?** (breaking changes, migrations, deprecations)
4. **Rollback criteria?** (what signals trigger a rollback? error rate > X%, response time > Yms, manual decision)
5. **Stakeholders to notify?** (team, specific people, #deployments channel, none)

---

## Phase 2 — Pre-Deploy Checks

### 2.1 Verify deploy readiness
```bash
# Branch check
echo "Current branch: $(git branch --show-current)"
echo "Expected deploy branch: [main/staging/develop]"
git log --oneline -1

# CI status (if gh available)
which gh 2>/dev/null && gh run list --branch $(git branch --show-current) --limit 1 --json conclusion 2>/dev/null || echo "gh not available"

# Uncommitted
git status --short
```

### 2.2 Check dependencies
- Are there database migrations? If yes, are they reversible?
- Are there API version changes?
- Are there config/environment changes?
- Are there third-party service changes?

### 2.3 Check changelog
```bash
head -30 CHANGELOG.md 2>/dev/null || echo "No CHANGELOG.md"
```

---

## Phase 3 — Build the Plan

Synthesize into a structured deploy plan:

```markdown
# Deploy Plan — [Descriptive Name]

**Date**: YYYY-MM-DD
**Target**: [production/staging/canary/other]
**Branch**: [branch name]
**Deploy type**: [full release / hotfix / feature flag / config change]
**Plan version**: 1

## Pre-Deploy Checklist

- [ ] All tests passing on target branch
- [ ] CI pipeline green
- [ ] Changelog updated
- [ ] Version bumped (if applicable)
- [ ] Database migrations reviewed
- [ ] Release notes drafted
- [ ] Team notified of deploy window

## Ordered Steps

### Step 1: [Step name]
**What**: [Exact action — command, script, or manual step]
**Who**: [person or team]
**Verification**: [how to confirm this step succeeded]
**Rollback**: [how to undo this step]

### Step 2: ...
...

## Rollback Plan

### Rollback trigger
[What conditions automatically or manually trigger rollback]

### Rollback steps
1. `git revert <commit>` or `git checkout <previous-tag>`
2. Run any reverse migrations
3. Redeploy
4. Verify: [how to confirm rollback succeeded]

### Time estimate
[Estimated time to rollback]

## Post-Deploy Verification

### Automated checks
- [ ] Health endpoint returns 200
- [ ] Error rate < baseline + 1%
- [ ] Response time < baseline + 10%
- [ ] [Custom metric]

### Manual checks
- [ ] [Specific user flow to verify]
- [ ] [Data integrity check]
- [ ] [Integration check with dependent systems]

## Communication

| When | What | To whom |
|------|------|---------|
| 5m before | Deploy starting | @team, #deployments |
| During | Progress updates | @team, #deployments |
| After (success) | Deploy complete | @team, #deployments |
| After (rollback) | Deploy rolled back, root cause investigation | @team, #deployments, @stakeholders |

## Monitoring

- **Dashboard**: [link to monitoring dashboard]
- **Alerts**: [what alerts to watch during/after deploy]
- **Logs**: [log stream command or link]

---

## Phase 4 — Save Plan

Save the plan to `.context8/deploy-plans/YYYY-MM-DD_description.md`.

Print the plan inline for review before executing.

---

## Rules
- Planning only. No code changes.
- Every step must have a rollback. If a step is not reversible, flag it with ⚠️.
- Pre-deploy checks are mandatory. If any fail, flag and ask if user wants to proceed.
- Post-deploy verification must include both automated and manual checks.
- Save the plan to `.context8/deploy-plans/` for audit trail.
