---
name: create-qa-agent
version: 1.0.0
description: Investigates the project, asks about testing needs, and generates a professional QA/Test Engineer agent in the native format of the current tool
---

# Create QA Agent — Generate a Specialized QA/Test Engineer Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about testing needs, and generates a complete QA/Test Engineer agent. The agent is created in the native agent format of the tool you are running in (e.g., `.opencode/agents/qa-agent.md` for OpenCode, `.claude/agents/qa-agent.md` for Claude Code, etc.).

## When to use
- Need a specialized QA/testing agent for the current project
- Want test coverage analysis, test generation, and quality enforcement
- Need a dedicated agent for test-driven development workflows

## When NOT to use
- No project code exists yet → use project-init first
- Only need a one-time test run → use task-do instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE QA AGENT — Generate a QA/Test Engineer Agent

## RULE: This skill generates an agent. No application code changes. The output is an agent definition in the native format of the current tool.

---

## Phase 1 — Preflight

Run all of the following to build a context profile before generating the agent.

### 1.1 Inventory installed skills/plugins
```bash
# Check which skills from this dev-workflows plugin are available
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files that are relevant to testing or quality.

Check for MCP servers or other plugins that might be useful for a QA agent:
```bash
# OpenCode
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
# Claude Code
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
# Generic
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# Languages and frameworks
ls package.json pyproject.toml Cargo.toml go.mod build.gradle 2>/dev/null
# Test-related configs
ls jest.config* vitest.config* pytest.ini tox.ini .nycrc 2>/dev/null
# CI/CD
ls .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile 2>/dev/null
```

### 1.3 Build context profile
Synthesize what you found: project language, test framework (if any), CI system, available skills/plugins that could enhance a QA agent.

---

## Phase 2 — Domain Research: Testing & Quality

Explore the project's testing landscape:

```bash
# Find existing test files
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" \
          -o -name "*.spec.ts" -o -name "*.test.js" -o -name "*.spec.js" \
          -o -name "*.test.tsx" \) -not -path '*/node_modules/*' \
          -not -path '*/.venv/*' | head -20

# Check for coverage config
ls .coveragerc codecov.yml sonar-project.properties 2>/dev/null

# Check for QA/lint tools
ls .eslintrc* .prettierrc* ruff.toml .flake8 biome.json 2>/dev/null
```

Read a sample of test files to understand patterns used.

---

## Phase 3 — Domain Questions

Ask the user these questions one at a time:

1. **What types of testing do you need?** (unit, integration, e2e, visual, performance, security — select all that apply)
2. **What test framework do you prefer?** (jest, vitest, pytest, Playwright, Cypress, other)
3. **What are your coverage goals?** (percentage targets, critical paths, no preference)
4. **How should tests integrate with CI/CD?** (gate on failures, report generation, parallel runs)
5. **Any specific QA workflows?** (TDD, BDD, manual test plans, visual regression, API testing)

---

## Phase 4 — Generate Agent

Create a specialized **QA/Test Engineer agent** for this project.

The agent must be created in the **native agent format of the tool you are running in**, saved in the **per-project agents directory** (not global).

The generated agent should include:
- Role: QA/Test Engineer specialist for this specific project
- Inventory of available testing skills/plugins from Phase 1
- Full system prompt covering: test strategy, framework usage, CI integration, coverage enforcement, reporting
- Permission configuration appropriate for QA work (read + test execution, no production code edits)
- Model suggestion (balanced for capability/speed)
- Temperature: 0.2 (deterministic for test assertions)

Use Phase 1 and Phase 3 answers to personalize the agent. The agent should know what test framework to use, what to test, and how to integrate with CI.

---

## Rules
- Generate the agent in the native format of the current tool. The AI knows what tool it is and how to create agents for it.
- Save in the per-project directory (e.g., `.opencode/agents/` for OpenCode, `.claude/agents/` for Claude Code).
- All user-facing questions in English unless the user prefers another language.
- Do not modify any application code.
