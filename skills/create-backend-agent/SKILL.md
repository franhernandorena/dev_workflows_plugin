---
name: create-backend-agent
version: 1.0.0
description: Investigates the project, asks about backend needs, and generates a professional Backend Developer agent in the native format of the current tool
---

# Create Backend Agent — Generate a Specialized Backend Developer Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about backend needs, and generates a complete Backend Developer agent in the native agent format of the current tool.

## When to use
- Need a dedicated Backend developer agent for API development, data layer, or server-side logic
- Project has backend code that needs consistent patterns and standards
- Want enforcement of backend conventions and best practices

## When NOT to use
- No project code exists yet → use project-init first
- Project is purely frontend → use create-frontend-agent instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE BACKEND AGENT — Generate a Backend Developer Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to backend development.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# Backend languages and frameworks
ls package.json pyproject.toml Cargo.toml go.mod build.gradle 2>/dev/null
# API routes
find . -name "routes*" -o -name "*router*" -o -name "*api*" -o -name "*controller*" -o -name "*handler*" 2>/dev/null | head -15
# Data layer
find . -name "*model*" -o -name "*schema*" -o -name "*migration*" -o -name "*entity*" 2>/dev/null | head -15
```

### 1.3 Build context profile
Synthesize: backend language, framework, API style, ORM, auth approach, available plugins.

---

## Phase 2 — Domain Research: Backend

```bash
# Entry points
ls server.ts app.py main.go index.ts 2>/dev/null
# Config files
ls .env.example config*.py config*.ts application.yml 2>/dev/null
# Auth patterns
find . -name "*auth*" -o -name "*middleware*" 2>/dev/null | head -10
```

Read the main entry point and a sample of routes/controllers.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What backend language and framework?** (Node/Express, Python/FastAPI, Go, Rust, Java/Spring, other)
2. **What API style?** (REST, GraphQL, gRPC, WebSocket, hybrid)
3. **What data layer?** (ORM name, raw SQL, query builder, document DB)
4. **Authentication approach?** (JWT, sessions, OAuth, API keys, third-party auth)
5. **Error handling and logging patterns?** (structured logging, error boundaries, monitoring)

---

## Phase 4 — Generate Agent

Create a **Backend Developer agent** in the native format of the current tool.

The agent should include:
- Role: Backend Developer for this project
- Available backend-relevant skills/plugins from Phase 1
- Full prompt covering: API patterns, data layer conventions, auth patterns, error handling, testing, performance
- Permission: full edit access to backend code, restricted for frontend/infra
- Temperature: 0.3
- Model: capable for code generation

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
