---
name: create-devops-agent
version: 1.0.0
description: Investigates the project, asks about DevOps needs, and generates a professional DevOps/SRE agent in the native format of the current tool
---

# Create DevOps Agent — Generate a Specialized DevOps/SRE Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about DevOps needs, and generates a complete DevOps/SRE agent in the native agent format of the current tool.

## When to use
- Need a dedicated DevOps/SRE agent for CI/CD, monitoring, and operations
- Project needs pipeline management, infrastructure automation, or reliability engineering
- Want SLO tracking, incident response, and operational best practices

## When NOT to use
- No project code exists yet → use project-init first
- Only need cloud architecture → use create-cloud-agent instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE DEVOPS AGENT — Generate a DevOps/SRE Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to DevOps, CI/CD, or operations.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# CI/CD
ls .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile 2>/dev/null
# Container
ls Dockerfile* docker-compose* 2>/dev/null
# Monitoring
ls prometheus* grafana* datadog* newrelic* 2>/dev/null
# Scripts
find . -name "deploy*" -o -name "rollback*" -o -name "*.sh" -path "*scripts*" 2>/dev/null | head -10
```

### 1.3 Build context profile
Synthesize: CI/CD system, container/orch setup, monitoring tools, deployment strategy, available plugins.

---

## Phase 2 — Domain Research: DevOps

```bash
# Read CI/CD configs
cat .github/workflows/*.yml 2>/dev/null | head -60
cat .gitlab-ci.yml 2>/dev/null | head -60
# Docker config
cat Dockerfile 2>/dev/null
cat docker-compose.yml 2>/dev/null
# Deploy scripts
find . -name "deploy*" -o -name "Dockerfile*" 2>/dev/null | head -10
```

Read the CI/CD pipeline config and deployment scripts.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What CI/CD system?** (GitHub Actions, GitLab CI, Jenkins, CircleCI, other, none)
2. **Deployment strategy?** (rolling, blue/green, canary, manual, not yet defined)
3. **Monitoring and alerting?** (Prometheus/Grafana, Datadog, New Relic, Sentry, none)
4. **Incident response process?** (on-call rotation, runbooks, postmortems, none)
5. **SLOs/SLIs defined?** (yes with targets, partially, no)

---

## Phase 4 — Generate Agent

Create a **DevOps/SRE agent** in the native format of the current tool.

The agent should include:
- Role: DevOps/SRE for this project
- Available DevOps-relevant skills/plugins from Phase 1
- Full prompt covering: CI/CD pipeline management, containerization, monitoring/observability, incident response, SLO tracking, infrastructure automation
- Permission: full access to CI/CD configs, infrastructure files, and scripts
- Temperature: 0.3
- Model: capable for operations automation

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
