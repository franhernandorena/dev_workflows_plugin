---
name: project-init
version: 1.0.0
description: Use when starting work on a new single-repo codebase for the first time — runs full exploration, builds mental model, creates .context8/ with all agent-ready context files
---

# Project Init — New Project Bootstrap

## Overview
Full research, exploration, and documentation bootstrap for a new project. Runs systematic codebase exploration (directory structure, configs, git history, CI/CD, tests, entry points, infrastructure), builds a mental model, then creates a complete `.context8/` structure. No code changes.

## When to use
- First time working on a codebase
- Project has no `.context8/` directory
- Need to create agent-ready context before starting development

## When NOT to use
- Project already has `.context8/` → use `project-continue`
- Multi-repo workspace → use `workflow-init`
- Need an honest assessment before committing to full bootstrap → use `project-audit` first

## Output
- `.context8/AGENT_CONTEXT.md` — comprehensive project context
- `.context8/AGENT_SYSTEM_PROMPT.md` — ready-to-paste system prompt
- `.context8/PROJECT_OVERVIEW.md` — 1-page summary
- `.context8/architecture/` — data_flow, key_patterns, module_map, infrastructure

## Full Prompt

# NEW PROJECT — Research & Documentation Bootstrap

## RULE: No code changes before this setup is complete.

---

## Phase 1 — Codebase Exploration

Run all of the following commands. Never skip a step.

### 1.1 Directory structure
```bash
find . -not -path '*/node_modules/*' -not -path '*/.git/*' \
       -not -path '*/__pycache__/*' -not -path '*/.venv/*' \
       -not -path '*/dist/*' -not -path '*/build/*' \
       | sort | head -120
```

### 1.2 Root configuration files
Read every config file present:
- package.json / package-lock.json / yarn.lock / pnpm-lock.yaml
- pyproject.toml / setup.py / requirements*.txt / Pipfile
- dbt_project.yml / profiles.yml
- Cargo.toml / go.mod / build.gradle / pom.xml
- tsconfig.json / .eslintrc* / .prettierrc* / ruff.toml / .flake8
- docker-compose*.yml / Dockerfile*
- .env.example / .env.template (NEVER .env itself)
- Makefile / justfile / taskfile.yml

### 1.3 Git history & contributors
```bash
git log --oneline -30
git branch -a
git remote -v
git tag --sort=-creatordate | head -20
```

### 1.4 CI/CD pipelines
Read every file in:
- .github/workflows/
- .gitlab-ci.yml
- cloudbuild.yaml / cloudbuild*.yaml
- .circleci/config.yml
- bitbucket-pipelines.yml

### 1.5 Existing documentation
```bash
find . -name "*.md" -not -path '*/node_modules/*' | sort
find . -name "*.rst" -not -path '*/node_modules/*' | sort
```
Read every .md file found (README, CHANGELOG, CONTRIBUTING, ADRs, etc.)

### 1.6 Test suite
```bash
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" \
          -o -name "*.spec.ts" -o -name "*.test.tsx" -o -name "jest.config*" \
          -o -name "pytest.ini" -o -name "vitest.config*" \) \
     -not -path '*/node_modules/*' | sort | head -40
```

### 1.7 Entry points & main modules
Identify and read:
- Main app entry (main.py / app.py / index.ts / server.ts / main.rs / cmd/)
- Router definitions
- Core models / schemas / types
- Database migrations directory
- Seed data files

### 1.8 Infrastructure & cloud
Read any IaC files:
- terraform/ / pulumi/ / cdk/ / serverless.yml
- kubernetes/ / k8s/ / helm/

---

## Phase 2 — Mental Model Construction

Before writing any docs, synthesize what you found:

1. **Tech stack**: languages, frameworks, ORMs, databases, queues, caches
2. **Architecture pattern**: monolith / microservices / event-driven / layered / hexagonal / pipeline-based
3. **Data flow**: where data enters, how it transforms, where it exits
4. **Module dependency graph**: which modules import which (map the main ones)
5. **Code conventions**: naming style, file organization, error handling pattern, logging pattern
6. **Test strategy**: unit / integration / e2e — what's covered, what's not
7. **Deployment model**: local / Docker / cloud (GCP / AWS / Azure) — which services

---

## Phase 3 — Create Documentation Structure

Create the following structure. Every file is mandatory.

```
.context8/
├── README.md                     # Index + quick-start for agents
├── AGENT_CONTEXT.md              # Comprehensive project context
├── AGENT_SYSTEM_PROMPT.md        # System prompt for new agent instantiation
├── PROJECT_OVERVIEW.md           # 1-page high-level summary
├── architecture/
│   ├── data_flow.md              # End-to-end data / request flow
│   ├── key_patterns.md           # Design patterns, conventions, anti-patterns
│   ├── module_map.md             # Module/package dependency overview
│   └── infrastructure.md        # Deployment, cloud resources, env vars
└── tasks/
    └── (task files go here)
```

Add additional architecture files as needed (e.g., `audit_system.md`, `pipeline_stages.md`).

---

## Phase 4 — Populate Documentation

### .context8/AGENT_CONTEXT.md
Must include ALL of the following sections. Be exhaustive — a future agent must not need to re-read source code to operate.

```markdown
# Agent Context

## Tech Stack
[Languages, runtime versions, key frameworks, databases, cloud services]

## Architecture
[Pattern name + brief description. Diagram in ASCII or mermaid if helpful.]

## Directory Structure (annotated)
[Top-level dirs with one-line purpose each]

## Entry Points
[How the app starts, main files, CLI commands]

## Data Flow
[How data moves through the system — inputs → processing → outputs]

## Key Modules & Their Responsibilities
[Table or list: module → what it does → key files]

## Core Design Patterns & Conventions
[Naming, error handling, logging, validation, testing patterns used in this codebase]

## Configuration & Environment
[All env vars, their purpose, and where they're used. No secret values.]

## Database & Schema
[Tables/collections, key relationships, migration tool]

## External Integrations & APIs
[Third-party services, internal APIs, MCP servers if any]

## Testing Strategy
[Frameworks used, how to run tests, what's covered]

## CI/CD Pipeline
[Stages, triggers, deployment targets]

## Known Constraints & Gotchas
[Non-obvious limitations, tech debt, things to be careful about]

## Versioning & Release Process
[How versions are managed, changelog convention, release steps]
```

### .context8/AGENT_SYSTEM_PROMPT.md
Write a ready-to-paste system prompt that:
- Describes the project in 2–3 sentences
- Lists the tech stack
- States the primary workflow (use `project-continue` skill → read AGENT_CONTEXT.md → check tasks/)
- Lists the top 3–5 conventions to follow strictly
- States what NOT to do (common mistakes for this codebase)

### .context8/PROJECT_OVERVIEW.md
1-page summary: what the project does, who uses it, key architectural decisions, current state, next priorities.

### .context8/architecture/data_flow.md
Trace the full lifecycle of a request or data record from entry to exit.
Include: sources → ingestion → processing/transformation → storage → output/API.

### .context8/architecture/key_patterns.md
Document:
- File/folder naming conventions
- Module boundary rules
- Error propagation pattern
- Logging conventions
- How new features should be added (step-by-step pattern)
- Anti-patterns observed in the codebase (what NOT to do)

### .context8/architecture/module_map.md
Visual (ASCII or mermaid) map of the main modules and their dependencies.

### .context8/architecture/infrastructure.md
- Cloud provider(s) and services used
- All environment variables (name, purpose, example value — no real secrets)
- Container setup (ports, volumes, networks)
- How to run locally
- How to deploy

---

## Phase 5 — Update Project README

Add or update a section in the root README.md:

```markdown
## Agent Documentation

This project uses a structured documentation system in `.context8/`.
See [`.context8/README.md`](.context8/README.md) for the full index.

When working with an AI agent, use `.context8/AGENT_SYSTEM_PROMPT.md`
as the system prompt and `.context8/AGENT_CONTEXT.md` as the primary reference.
```

---

## Completion Checklist

Before considering this task done, verify:
- [ ] All Phase 1 commands were run and their output was analyzed
- [ ] .context8/ directory exists with all required files
- [ ] AGENT_CONTEXT.md has all required sections populated (not placeholder text)
- [ ] AGENT_SYSTEM_PROMPT.md is ready to paste as a system prompt
- [ ] Root README.md references .context8/
- [ ] All documentation is written in English
- [ ] No secrets or .env values were written to any file

---

## Rules
- Use English for all documentation, always.
- Document what exists, not what should exist.
- If a section has no content (e.g., no tests exist), write: "None currently. [Reason if known]."
- Never truncate or skip a Phase 1 step because the project "looks simple."
- If MCP tools are available (GitHub, Linear, Jira, Notion), check for existing issues, epics, or specs and reference them in AGENT_CONTEXT.md.
