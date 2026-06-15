---
name: create-architect-agent
version: 1.0.0
description: Investigates the project, asks about architecture needs, and generates a professional Software Architect agent in the native format of the current tool
---

# Create Architect Agent — Generate a Specialized Software Architect Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about architecture needs, and generates a complete Software Architect agent in the native agent format of the current tool.

## When to use
- Need a dedicated Software Architect agent for system design decisions
- Project needs architecture documentation, ADRs, and design reviews
- Want trade-off analysis and tech stack guidance

## When NOT to use
- No project code exists yet → use project-init first
- Simple single-file project → overkill, use task-plan instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE ARCHITECT AGENT — Generate a Software Architect Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to architecture or design.

Check for MCP servers or plugins:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
ls package.json pyproject.toml Cargo.toml go.mod build.gradle 2>/dev/null
# Architecture docs
find . -name "*.md" -path "*arch*" -o -name "ADR*" -o -name "adr*" 2>/dev/null | head -10
# Module structure
find . -not -path '*/node_modules/*' -not -path '*/.git/*' -maxdepth 2 -type d | sort | head -30
```

### 1.3 Build context profile
Synthesize: language, framework, current architecture pattern, existing docs, available plugins for diagramming or documentation.

---

## Phase 2 — Domain Research: Architecture

```bash
# Existing architecture documentation
find . -name "*.md" -not -path '*/node_modules/*' | xargs grep -l -i "architecture\|pattern\|design\|module" 2>/dev/null | head -10

# Entry points
ls main.py app.py index.ts server.ts main.go cmd/ 2>/dev/null

# Dependency files
ls package.json Cargo.toml go.mod pyproject.toml 2>/dev/null
```

Read key entry points and dependency files to understand module boundaries.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What architecture pattern does the project follow?** (layered, hexagonal, microservices, event-driven, monolith, other/unsure)
2. **What are the main quality attribute goals?** (scalability, maintainability, performance, security, cost-efficiency)
3. **Are there documented ADRs or architecture decisions?** (yes, no, partially — should we create them?)
4. **What are the primary external integrations?** (databases, APIs, message queues, third-party services)
5. **Any known technical debt or architecture concerns?**

---

## Phase 4 — Generate Agent

Create a **Software Architect agent** in the native format of the current tool.

The agent should include:
- Role: Software Architect for this project
- Available architecture-relevant skills/plugins from Phase 1
- Full prompt covering: ADR creation, trade-off analysis, module boundary enforcement, tech stack guidance, diagram generation
- Permission: read access to all code, write access to docs/architecture/ only
- Temperature: 0.3 (balanced for analysis)
- Model: capable model for complex reasoning

---

## Rules
- Generate in native format of the current tool.
- Save per-project (not global).
- All questions in English unless user prefers otherwise.
