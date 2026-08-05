---
name: create-research-agent
version: 1.0.0
description: Investigates the project, asks about research needs, and generates a professional Research agent in the native format of the current tool
---

# Create Research Agent — Generate a Specialized Research Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about research needs, and generates a complete Research/analysis agent in the native agent format of the tool you are running in (e.g., `.opencode/agents/research-agent.md` for OpenCode, `.claude/agents/research-agent.md` for Claude Code, etc.). This is the specialist used for market/competitor research, literature review, codebase analysis, and documentation work.

## When to use
- Need a dedicated research specialist for the current project (market, competitors, docs, literature, data analysis)
- Project involves recurring research work that should not pollute the main agent's context
- Team setup (`team-setup`) selected the research role

## When NOT to use
- No project code exists yet → use project-init first
- Only a one-off research question → just do it in the session, no agent needed
- The research is about code only → use create-architect-agent instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE RESEARCH AGENT — Generate a Research Specialist Agent

## RULE: This skill generates an agent. No application code changes. The output is an agent definition in the native format of the current tool.

---

## Phase 1 — Preflight

Run all of the following to build a context profile before generating the agent.

### 1.1 Inventory installed skills/plugins
```bash
# Check which skills from this dev-workflows plugin are available
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to research (web scraping, reports, note-taking).

Check for MCP servers or other plugins that might help a research agent:
```bash
# OpenCode
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
# Claude Code
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
# Generic
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project research landscape
```bash
# Existing reports and docs
ls .context8/reports/ 2>/dev/null
find . -maxdepth 2 \( -iname "*research*" -o -iname "*report*" -o -iname "*brief*" -o -iname "*notes*" \) -not -path '*/node_modules/*' | head -20
# Where does the project live / who are the competitors (if product)?
cat .context8/PROJECT_OVERVIEW.md 2>/dev/null | head -30
# Data sources available
ls data/ datasets/ 2>/dev/null
```

### 1.3 Build context profile
Synthesize: what the project is, what research has been done, what sources exist, which skills/plugins could enhance a research agent.

---

## Phase 2 — Domain Research: Research & Analysis

Explore the project's research needs:
```bash
# Data / analysis tooling
ls requirements*.txt pyproject.toml package.json 2>/dev/null
# Any scraping / collection code
find . \( -iname "*scraper*" -o -iname "*collect*" -o -iname "*crawl*" \) -not -path '*/node_modules/*' | head -10
# Knowledge base / notes
find . \( -iname "*.md" \) -not -path '*/node_modules/*' -not -path '*/.git/*' | head -20
```

---

## Phase 3 — Domain Questions

Ask the user these questions one at a time:

1. **What kind of research?** (market/competitor, academic/literature, codebase analysis, data analysis, general web research — select all that apply)
2. **What sources?** (web search, specific sites/APIs, local docs/reports, databases, interviews)
3. **Output format?** (markdown report, tables/CSV, spreadsheet, structured notes for .context8/reports/)
4. **Depth vs speed?** (exhaustive, balanced, quick scan)
5. **Citations/sources required?** (yes, list every source — or no)

---

## Phase 4 — Generate Agent

Create a specialized **Research agent** for this project.

The agent must be created in the **native agent format of the tool you are running in**, saved in the **per-project agents directory** (not global).

The generated agent should include:
- Role: Research Specialist for this specific project
- Inventory of available research skills/plugins from Phase 1
- Full system prompt covering: research methodology, source verification, output structure, citation discipline
- Permission configuration: read + web access, NO application code edits
- Model suggestion: fast/cheap model with tool access (research is token-heavy)
- Temperature: 0.3 (balanced for synthesis)
- Explicit instruction: never fabricate sources or data — mark anything unverified

Use Phase 1 and Phase 3 answers to personalize the agent: what to research, which sources to prefer, and how to deliver results.

---

## Rules
- Generate the agent in the native format of the current tool. The AI knows what tool it is and how to create agents for it.
- Save in the per-project directory (e.g., `.opencode/agents/` for OpenCode, `.claude/agents/` for Claude Code).
- All user-facing questions in English unless the user prefers another language.
- Do not modify any application code.
