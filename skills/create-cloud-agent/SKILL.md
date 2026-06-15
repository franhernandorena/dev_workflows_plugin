---
name: create-cloud-agent
version: 1.0.0
description: Investigates the project, asks about cloud needs, and generates a professional Cloud Architect agent in the native format of the current tool
---

# Create Cloud Agent — Generate a Specialized Cloud Architect Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about cloud infrastructure needs, and generates a complete Cloud Architect agent in the native agent format of the current tool.

## When to use
- Need a dedicated Cloud Architect agent for infrastructure design and cloud strategy
- Project uses cloud services (AWS, GCP, Azure) or needs migration guidance
- Want cost optimization, high availability, and cloud best practices enforcement

## When NOT to use
- No project code exists yet → use project-init first
- No cloud infrastructure → use create-devops-agent for on-prem/container setups

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE CLOUD AGENT — Generate a Cloud Architect Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to cloud or infrastructure.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# IaC files
ls terraform/ *.tf pulumi/ cdk/ serverless.yml 2>/dev/null
ls kubernetes/ k8s/ helm/ *.yaml 2>/dev/null
# Cloud configs
ls .env.cloud* cloud*.yaml 2>/dev/null
# Docker
ls Dockerfile* docker-compose* 2>/dev/null
```

### 1.3 Build context profile
Synthesize: cloud provider, IaC tool, container setup, deployment model, available plugins.

---

## Phase 2 — Domain Research: Cloud Infrastructure

```bash
# Read IaC files
find . -name "*.tf" -o -name "*.yml" -path "*terraform*" -o -name "*.yaml" -path "*k8s*" -o -name "*.yaml" -path "*helm*" 2>/dev/null | head -10
# Docker config
cat Dockerfile 2>/dev/null | head -30
cat docker-compose.yml 2>/dev/null | head -30
# Cloud SDK configs
ls .aws/ .gcp/ .azure/ 2>/dev/null
```

Read the main IaC files to understand the current cloud setup.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What cloud provider?** (AWS, GCP, Azure, multi-cloud, on-prem, none yet)
2. **What services are you using or planning?** (compute, storage, database, networking, serverless, ML)
3. **IaC approach?** (Terraform, Pulumi, CloudFormation, CDK, manual, none)
4. **High availability and DR requirements?** (multi-region, HA single-region, no special requirements)
5. **Cost optimization priorities?** (reduce spend, improve utilization, not a concern yet)

---

## Phase 4 — Generate Agent

Create a **Cloud Architect agent** in the native format of the current tool.

The agent should include:
- Role: Cloud Architect for this project
- Available cloud-relevant skills/plugins from Phase 1
- Full prompt covering: cloud resource design, cost optimization, high availability, security groups, IaC patterns, disaster recovery
- Permission: read access to all code, write access to IaC and docs
- Temperature: 0.3
- Model: capable for infrastructure reasoning

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
