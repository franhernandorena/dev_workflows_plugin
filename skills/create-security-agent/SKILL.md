---
name: create-security-agent
version: 1.0.0
description: Investigates the project, asks about security needs, and generates a professional Security Engineer agent in the native format of the current tool
---

# Create Security Agent — Generate a Specialized Security Engineer Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about security needs, and generates a complete Security Engineer agent in the native agent format of the current tool.

## When to use
- Need a dedicated Security Engineer agent for vulnerability assessment and secure coding
- Project handles sensitive data or has compliance requirements
- Want security review automation and dependency scanning

## When NOT to use
- No project code exists yet → use project-init first
- Security is handled by a dedicated team externally → overkill

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE SECURITY AGENT — Generate a Security Engineer Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to security.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# Auth/Z configs
find . -name "*auth*" -o -name "*oauth*" -o -name "*jwt*" -o -name "*rbac*" 2>/dev/null | head -10
# Security tools
ls .sast* .semgrep* .gitleaks* .trivy* 2>/dev/null
# Dependency files (for vuln scanning)
ls package-lock.json yarn.lock requirements.txt Cargo.lock go.sum 2>/dev/null
# Compliance
ls security.md compliance* 2>/dev/null
```

### 1.3 Build context profile
Synthesize: authentication approach, security tools present, compliance requirements, dependency files, available plugins.

---

## Phase 2 — Domain Research: Security

```bash
# Read security configs
find . -name "*.env*" -not -path '*/node_modules/*' | head -5  # check for secrets exposure
find . -name "Dockerfile*" -exec grep -l "root\|sudo\|chmod\|777\|--no-check" {} \; 2>/dev/null | head -5
# Dependency security
ls .npmrc .yarnrc .piprc 2>/dev/null
# CSP/security headers
grep -r "Content-Security-Policy\|Strict-Transport-Security\|X-Frame-Options" --include="*.ts" --include="*.js" --include="*.py" --include="*.html" 2>/dev/null | head -10
```

Read auth implementation and check for common security issues.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What compliance standards apply?** (SOC2, HIPAA, GDPR, PCI-DSS, none, not sure)
2. **What security testing is needed?** (SAST, DAST, dependency scanning, penetration testing, manual review)
3. **Authentication and authorization model?** (JWT, OAuth, SAML, API keys, custom)
4. **Incident response plan?** (formal process, runbooks, none)
5. **Any past security audits or findings?** (yes, no, this would be the first)

---

## Phase 4 — Generate Agent

Create a **Security Engineer agent** in the native format of the current tool.

The agent should include:
- Role: Security Engineer for this project
- Available security-relevant skills/plugins from Phase 1
- Full prompt covering: security review methodology, vulnerability assessment, dependency scanning, secure coding standards, compliance checks, incident response
- Permission: read-only for most code, write access only to security-related files
- Temperature: 0.2 (precision-critical)
- Model: capable for security analysis

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
