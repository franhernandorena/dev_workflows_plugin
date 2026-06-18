---
name: workflow-init
version: 1.0.0
description: Use when setting up a new multi-repo workspace for the first time — discovers child repos, creates root .context8/ and per-repo .context8/ with agent-ready context
---

# Workflow Init — Multi-Repo Workspace Bootstrap

## Overview
Bootstraps a workspace: a parent folder containing multiple independent repos. Creates a root `.context8/` (navigation + cross-repo overview) and a full `.context8/` inside each child repo. No code changes — documentation only.

## When to use
- First time working in a folder that contains multiple git repos
- Workspace has no `.context8/` at the root level
- Need agent-ready context before starting cross-repo work

## When NOT to use
- Single repo → use `project-init` instead
- Workspace already bootstrapped → use `workflow-continue`
- Adding one new repo to existing workspace → use `workflow-add-repo`

## Output
- `.context8/README.md` — workspace index
- `.context8/WORKSPACE_OVERVIEW.md` — cross-repo context
- `[repo]/.context8/` — full context for each child repo

## Full Prompt

# WORKSPACE BOOTSTRAP — Multi-Repo Parent Folder

## RULE: No code changes before this setup is complete. Run every phase in order.

A workspace is a parent folder containing multiple independent repositories (e.g., `proyecto_a/` holding `front_a/` and `back_a/`). This prompt bootstraps:
- A **root `.context8/`**: workspace-level guide, global tasks, cross-repo overview only.
- A **per-repo `.context8/`**: full independent context for each child repo.

---

## Phase 1 — Discover Workspace Structure

### 1.1 Map the workspace
```bash
find . -maxdepth 3 -not -path '*/.git/*' -not -path '*/node_modules/*' \
       -not -path '*/__pycache__/*' -not -path '*/.venv/*' \
       | sort | head -80
```

### 1.2 Identify child repos
```bash
find . -maxdepth 2 -name ".git" -type d | sed 's|/.git||' | sort
```
List every directory that is an independent git repo. These are your **child repos**.

### 1.3 Check for existing documentation
```bash
find . -name ".context8" -type d | sort
find . -name "*.md" -maxdepth 2 | sort
```

### 1.4 Check for workspace-level config
Read any files present at the root:
- `docker-compose*.yml` / `Makefile` / `justfile` / `taskfile.yml`
- `.env.example` / `.env.template` (NEVER `.env` itself)
- Any root `README.md`

---

## Phase 2 — Create Root `.context8/`

The root `.context8/` is a **navigation layer only**. It does NOT duplicate per-repo content.

```
.context8/
├── README.md                  # Workspace index — links to all child repos
├── WORKSPACE_OVERVIEW.md      # What this workspace is, who uses it, global architecture
└── tasks/
    └── (global / cross-repo task files go here)
```

### .context8/README.md
```markdown
# Workspace: [workspace name]

## Repos in this workspace

| Repo | Path | Purpose | Full docs |
|------|------|---------|-----------|
| [name] | ./[path] | [one-line purpose] | [path/.context8/README.md] |

## How to use this workspace
- For work on a specific repo: navigate to its folder and read `.context8/AGENT_CONTEXT.md`.
- For cross-repo tasks: read `WORKSPACE_OVERVIEW.md` and check `tasks/` here.
- To bootstrap a new session on a child repo: use `project-continue` skill inside that repo's folder.

## Global tasks
See `tasks/` in this directory for cross-repo or workspace-level work.
```

### .context8/WORKSPACE_OVERVIEW.md
Must include:
```markdown
# Workspace Overview

## Purpose
[What this workspace represents — product, platform, or project it belongs to]

## Repos

| Repo | Stack | Role | Key contacts |
|------|-------|------|-------------|
| [name] | [tech] | [frontend/backend/infra/etc] | [if known] |

## Cross-repo Relationships
[How the repos interact: API contracts, shared databases, event queues, shared packages]

## Shared Infrastructure
[Docker compose, shared envs, shared CI/CD, monorepo tooling if any]

## Global Conventions
[Naming, branching strategy, PR process, deploy process — things that apply to all repos]

## Known Cross-repo Constraints & Gotchas
[Non-obvious things that affect multiple repos simultaneously]
```

---

## Phase 3 — Bootstrap Each Child Repo

For **each child repo** discovered in Phase 1, run the full per-repo bootstrap independently.

### 3.1 Navigate to repo
Work from inside the child repo directory for this phase.

### 3.2 Run full codebase exploration (per repo)

#### Directory structure
```bash
find . -not -path '*/node_modules/*' -not -path '*/.git/*' \
       -not -path '*/__pycache__/*' -not -path '*/.venv/*' \
       -not -path '*/dist/*' -not -path '*/build/*' \
       | sort | head -120
```

#### Root configuration files
Read every config file present:
- package.json / package-lock.json / yarn.lock / pnpm-lock.yaml
- pyproject.toml / setup.py / requirements*.txt / Pipfile
- dbt_project.yml / profiles.yml
- Cargo.toml / go.mod / build.gradle / pom.xml
- tsconfig.json / .eslintrc* / .prettierrc* / ruff.toml / .flake8
- docker-compose*.yml / Dockerfile*
- .env.example / .env.template (NEVER .env itself)
- Makefile / justfile / taskfile.yml

#### Git history & branches
```bash
git fetch --prune 2>&1
git log --oneline -30
git branch -a
git remote -v
```

#### CI/CD pipelines
Read every file in:
- .github/workflows/
- .gitlab-ci.yml / cloudbuild.yaml / .circleci/config.yml

#### Existing documentation
```bash
find . -name "*.md" -not -path '*/node_modules/*' | sort
```
Read every .md file found.

#### Test suite
```bash
find . \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" \
          -o -name "*.spec.ts" -o -name "*.test.tsx" -o -name "jest.config*" \
          -o -name "pytest.ini" -o -name "vitest.config*" \) \
     -not -path '*/node_modules/*' | sort | head -40
```

#### Entry points & main modules
Identify and read:
- Main app entry (main.py / app.py / index.ts / server.ts / main.rs / cmd/)
- Router definitions
- Core models / schemas / types
- Database migrations directory

#### Infrastructure & cloud
Read any IaC files: terraform/ / pulumi/ / cdk/ / serverless.yml / kubernetes/ / k8s/

### 3.3 Create per-repo `.context8/`

Inside the child repo, create:
```
[repo]/.context8/
├── README.md                     # Index + quick-start for agents
├── AGENT_CONTEXT.md              # Comprehensive repo context
├── AGENT_SYSTEM_PROMPT.md        # System prompt for new agent instantiation
├── PROJECT_OVERVIEW.md           # 1-page high-level summary
├── REPO_BRANCHES.md              # Branches, tags, git conventions
├── PIPELINES.md                  # CI/CD pipelines, triggers, entornos
├── WORKSPACE_LINK.md             # Reference to sibling repos (Phase 3.8)
├── architecture/
│   ├── data_flow.md
│   ├── key_patterns.md
│   ├── module_map.md
│   └── infrastructure.md
└── tasks/
    └── (task files go here)
```

### 3.4 Populate AGENT_CONTEXT.md (per repo)

Must include ALL sections. Be exhaustive — a future agent must not need to re-read source code.

```markdown
# Agent Context — [repo name]

## Tech Stack
[Languages, runtime versions, key frameworks, databases, cloud services]

## Architecture
[Pattern name + brief description. ASCII or mermaid diagram if helpful.]

## Directory Structure (annotated)
[Top-level dirs with one-line purpose each]

## Entry Points
[How the app starts, main files, CLI commands]

## Data Flow
[How data moves: inputs → processing → outputs]

## Key Modules & Their Responsibilities
[Table: module → what it does → key files]

## Core Design Patterns & Conventions
[Naming, error handling, logging, validation, testing patterns]

## Configuration & Environment
[All env vars, their purpose, example values. No secret values.]

## Database & Schema
[Tables/collections, key relationships, migration tool]

## External Integrations & APIs
[Third-party services, internal APIs, contracts with other repos in this workspace]

## Testing Strategy
[Frameworks, how to run tests, what's covered]

## CI/CD Pipeline
[Stages, triggers, deployment targets]

## Known Constraints & Gotchas
[Non-obvious limitations, tech debt, things to be careful about]

## Workspace Relationships
[How this repo connects to others in the workspace: API calls, shared DB, events, packages]
```

### 3.5 Populate AGENT_SYSTEM_PROMPT.md (per repo)

Ready-to-paste system prompt:
- Project in 2–3 sentences
- Tech stack
- Primary workflow: use `project-continue` skill → read `AGENT_CONTEXT.md` → check `tasks/`
- Top 3–5 conventions to follow strictly
- What NOT to do (common mistakes for this codebase)
- Reference to workspace: "This repo is part of workspace `[name]`. Cross-repo context: `../../.context8/WORKSPACE_OVERVIEW.md`"

### 3.6 Populate remaining docs (per repo)

**PROJECT_OVERVIEW.md**: 1-page — what it does, who uses it, key architectural decisions, current state, next priorities.

**architecture/data_flow.md**: Full lifecycle of a request from entry to exit.

**architecture/key_patterns.md**: Naming conventions, module boundary rules, error propagation, logging, how to add new features, anti-patterns.

**architecture/module_map.md**: ASCII or mermaid map of main modules and dependencies.

**architecture/infrastructure.md**: Cloud services, env vars (name + purpose + example, no real secrets), container setup, how to run locally, how to deploy.

### 3.7 Create repo-branches.md (per repo)

For each child repo, create `.context8/repo-branches.md`:

```bash
# Gather data
echo "## Protected Branches"
echo "- \`main\` — Producción estable"
echo "- \`develop\` — Integración de desarrollo"
echo ""
echo "## Branches"
for branch in $(git branch --format='%(refname:short)' | sort); do
  last_date=$(git log "$branch" -1 --format="%ci" 2>/dev/null)
  last_msg=$(git log "$branch" -1 --format="%s" 2>/dev/null)
  echo "- \`$branch\` — ($last_date) $last_msg"
done
echo ""
echo "## Tags"
for tag in $(git tag --sort=-creatordate | head -10); do
  tag_date=$(git log "$tag" -1 --format="%ci" 2>/dev/null)
  echo "- \`$tag\` — $tag_date"
done
```

Write `<repo>/.context8/repo-branches.md`:

```markdown
# Repo Branches — [repo name]

## Protected Branches
- `main` — Producción estable
- `develop` — Integración de desarrollo

## Branches

| Branch | Last activity | Purpose | Status |
|--------|--------------|---------|--------|
| `main` | YYYY-MM-DD | Producción estable | active |
| `develop` | YYYY-MM-DD | Integración | active |
| `feat/xxx` | YYYY-MM-DD | [commit message] | active |

## Tags
| Tag | Date | Type | Description | Trigger |
|-----|------|------|-------------|---------|
| v1.0.0 | YYYY-MM-DD | release | [summary] | Deploys production |
| v1.0.0-rc1 | YYYY-MM-DD | release-candidate | RC para QA | Deploys preprod |

### Tag naming convention
- `v<major>.<minor>.<patch>` — release estable
- `<version>-rc<N>` — release candidate
- `<version>-hotfix.<desc>` — hotfix
- `<any>-alpha.<N>` / `<any>-beta.<N>` — pre-release

### Tag triggers
- Tag `v*` → normalmente despliega a producción.
- Tag `*-rc*` → normalmente despliega a preprod.
- Crear: `git tag -a vX.Y.Z -m "mensaje" && git push origin vX.Y.Z`
```

### 3.8 Create PIPELINES.md (per repo)

For each child repo, create `.context8/PIPELINES.md`:

```bash
# Detect CI/CD files
echo "=== GitHub Actions ==="
ls .github/workflows/ 2>/dev/null || echo "(none)"

echo ""
echo "=== Cloud Build ==="
ls cloudbuild*yaml cloudbuild*/ 2>/dev/null || echo "(none)"
```

For each GitHub Actions workflow, detect trigger events:

```bash
for file in .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null; do
  echo "=== $file ==="
  sed -n '/^on:/,/^jobs:/p' "$file"
  echo ""
done
```

Write `<repo>/.context8/PIPELINES.md`:

```markdown
# Pipelines — [repo name]

## Triggers overview

| Pipeline | Trigger | Action | Target | Source config |
|----------|---------|--------|--------|---------------|
| Tests | PR to develop | test + lint | CI | `.github/workflows/test.yml` |
| Deploy pre | push to main | build + deploy | preprod | `.github/workflows/deploy-pre.yml` |
| Deploy prod | tag v* | build + deploy | production | `cloudbuild.yaml` |

## GitHub Actions

| Workflow | Triggers | Description |
|----------|----------|-------------|
| test.yml | PR a develop | Tests + lint |
| deploy-pre.yml | push a main | Build + deploy preprod |

## Cloud Build

| Trigger | Event | Target | Config |
|---------|-------|--------|--------|
| deploy-prod | tag v* | Cloud Run prod | `cloudbuild.yaml` |

## External triggers

Triggers existentes en el entorno cloud pero SIN archivo en el repo:

| Trigger | Source | Action | Environment | Config location |
|---------|--------|--------|-------------|-----------------|
| [name] | [event] | [action] | [env] | GCP Console / GH UI |

> **Nota**: Actualizar esta sección cuando se creen/modifiquen triggers externos.

## Environments

| Environment | URL | Deploy trigger | Approvals |
|-------------|-----|---------------|-----------|
| Development | localhost | — | — |
| Preproduction | pre.example.com | push a main | automático |
| Production | example.com | tag v* | manual |

## Manual deploy

```bash
# Preprod
git push origin main

# Production
git tag -a v1.2.3 -m "release: message"
git push origin v1.2.3
```
```

### 3.9 Create WORKSPACE_LINK.md (per repo)

Inside each child repo's `.context8/`, create `WORKSPACE_LINK.md`:

```markdown
# Workspace Link — [repo name]

This repo is part of **workspace [name]**.

## Workspace root
`../../.context8/`

## Sibling repos

| Repo | Path | Purpose |
|------|------|---------|
| [name] | ../[path] | [one-line purpose] |
| [name] | ../[path] | [one-line purpose] |

## Why this matters
- Implement only what belongs to this repo.
- Before adding a new capability, check if a sibling repo already provides it.
- For cross-repo changes, work from the workspace root using `workflow-continue`.
```

### 3.10 Update repo README.md

Add or update:
```markdown
## Agent Documentation

This repo is part of the **[workspace name]** workspace.
See [`.context8/README.md`](.context8/README.md) for the full agent documentation index.
For cross-repo context: [`../../.context8/WORKSPACE_OVERVIEW.md`](../../.context8/WORKSPACE_OVERVIEW.md)
```

---

## Phase 4 — Finalize Root `.context8/`

After all child repos are bootstrapped, update the root `.context8/README.md`:
- Fill in the repo table with correct paths, purposes, and links.
- Note any cross-repo relationships discovered during Phase 3.
- Update WORKSPACE_OVERVIEW.md with any concrete details found (shared infra, API contracts, etc.)

---

## Completion Checklist

- [ ] All child repos identified in Phase 1
- [ ] Root `.context8/` created with README and WORKSPACE_OVERVIEW
- [ ] Each child repo has a complete `.context8/` with all required files
- [ ] AGENT_CONTEXT.md for each repo has all sections (no placeholder text)
- [ ] AGENT_SYSTEM_PROMPT.md for each repo is ready to paste
- [ ] REPO_BRANCHES.md created per repo with branches and tags listed
- [ ] PIPELINES.md created per repo with CI/CD triggers and external triggers documented
- [ ] Each repo's README.md references its `.context8/` and the root `.context8/`
- [ ] Root README.md (or WORKSPACE_OVERVIEW.md) links all repos
- [ ] All documentation written in English
- [ ] No secrets or .env values written to any file

---

## Rules
- Root `.context8/` = navigation + global context only. Never duplicate per-repo content there.
- Per-repo `.context8/` = fully self-contained. Agent working on one repo must not need to read another repo's files.
- Document what exists, not what should exist.
- If a section has no content, write: "None currently. [Reason if known]."
- Never truncate or skip a Phase 3 step because a repo "looks simple."
- If MCP tools are available (GitHub, Linear, Jira), check for existing issues and reference them.
