---
name: create-frontend-agent
version: 1.0.0
description: Investigates the project, asks about frontend needs, and generates a professional Frontend Developer agent in the native format of the current tool
---

# Create Frontend Agent — Generate a Specialized Frontend Developer Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about frontend needs, and generates a complete Frontend Developer agent in the native agent format of the current tool.

## When to use
- Need a dedicated Frontend developer agent for UI components, styling, and client-side logic
- Project has frontend code that needs consistent patterns and standards
- Want enforcement of frontend conventions, a11y, and best practices

## When NOT to use
- No project code exists yet → use project-init first
- Project is purely backend → use create-backend-agent instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE FRONTEND AGENT — Generate a Frontend Developer Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to frontend development.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# Frontend frameworks
ls package.json 2>/dev/null && head -30 package.json | grep -i "react\|vue\|angular\|svelte\|next\|nuxt\|solid\|lit"
# Styling
ls tailwind.config* postcss.config* stylelint* 2>/dev/null
# Components
find . -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" -o -name "*.svelte" 2>/dev/null | head -15
```

### 1.3 Build context profile
Synthesize: frontend framework, styling approach, state management, UI library, testing framework, available plugins.

---

## Phase 2 — Domain Research: Frontend

```bash
# Component structure
find . -name "components*" -type d 2>/dev/null | head -5
find . -name "pages*" -o -name "views*" -o -name "screens*" -type d 2>/dev/null | head -5
# State management
ls store.ts store.js redux* zustand* pinia* 2>/dev/null
# Routing
ls router* routes* 2>/dev/null
```

Read a sample component and the main app entry point.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What frontend framework?** (React, Vue, Angular, Svelte, Solid, Lit, other)
2. **Styling approach?** (Tailwind, CSS Modules, styled-components, vanilla CSS, SCSS, other)
3. **State management?** (Context, Redux, Zustand, Pinia, signals, none needed)
4. **Accessibility requirements?** (WCAG level AA/AAA, basic a11y, not a priority)
5. **Design system or component library?** (custom design system, Material UI, Shadcn, Chakra, other)

---

## Phase 4 — Generate Agent

Create a **Frontend Developer agent** in the native format of the current tool.

The agent should include:
- Role: Frontend Developer for this project
- Available frontend-relevant skills/plugins from Phase 1
- Full prompt covering: component architecture, styling conventions, a11y, state management patterns, testing, performance
- Permission: full edit access to frontend code
- Temperature: 0.3
- Model: capable for UI code generation

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
