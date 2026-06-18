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

### 1.3 Git history & branches

```bash
git fetch --prune 2>&1
git log --oneline -30
git branch -a
git remote -v
git tag --sort=-creatordate | head -20
```

Para cada rama local (excluyendo `main`, `master`, `develop`), detectar su propósito:

```bash
for branch in $(git branch --format='%(refname:short)' | grep -v '^main$\|^master$\|^develop$'); do
  last_msg=$(git log "$branch" -1 --format="%s" 2>/dev/null)
  last_date=$(git log "$branch" -1 --format="%ci" 2>/dev/null)
  echo "  $branch | $last_date | $last_msg"
done
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
├── REPO_BRANCHES.md              # Branches, tags, git conventions (shared con repo-cleanup)
├── PIPELINES.md                  # CI/CD pipelines, triggers, entornos (shared con skill ci/cd)
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

### .context8/repo-branches.md
Create the branch reference file. Run these commands to gather data:

```bash
# Protected branches (convention)
echo "## Protected Branches"
echo "- \`main\` — Producción estable"
echo "- \`develop\` — Integración de desarrollo"

# Git user
echo ""
echo "## Git Conventions"
echo "- User: $(git config user.name) <$(git config user.email)>"
echo "- Merge: [merge strategy used in this project]"

# All local branches with dates and last messages
echo ""
echo "## Branches"
for branch in $(git branch --format='%(refname:short)' | sort); do
  last_date=$(git log "$branch" -1 --format="%ci" 2>/dev/null)
  last_msg=$(git log "$branch" -1 --format="%s" 2>/dev/null)
  behind=$(git rev-list --count --left-right origin/HEAD..."$branch" 2>/dev/null | cut -f2)
  ahead=$(git rev-list --count --left-right "$branch"...origin/"$branch" 2>/dev/null | cut -f1)
  echo "- \`$branch\` — (último: $last_date) $last_msg"
done

# Tags
echo ""
echo "## Tags"
for tag in $(git tag --sort=-creatordate | head -10); do
  tag_date=$(git log "$tag" -1 --format="%ci" 2>/dev/null)
  echo "- \`$tag\` — $tag_date"
done
```

Use the output to write `.context8/repo-branches.md`:

```markdown
# Repo Branches — [project name]

## Protected Branches
- `main` — Producción estable
- `develop` — Integración de desarrollo

## Git Conventions
- **User**: [name] <[email]>
- **Branch naming**: [convention, e.g. feat/xxx, fix/xxx, hotfix/xxx]

## Branches

| Branch | Last activity | Purpose | Status |
|--------|--------------|---------|--------|
| `main` | YYYY-MM-DD | Producción estable | active |
| `develop` | YYYY-MM-DD | Integración | active |
| `feat/xxx` | YYYY-MM-DD | [inferred from commit messages] | stale / active / merged |

## Tags
| Tag | Date | Type | Description | Trigger |
|-----|------|------|-------------|---------|
| v1.0.0 | YYYY-MM-DD | release | v1.0.0 — [summary] | Deploys production |
| v1.0.0-rc1 | YYYY-MM-DD | release-candidate | RC para QA | Deploys preprod |
| v0.9.0 | YYYY-MM-DD | release | [summary] | Deploys production |

### Tag naming convention
- `v<major>.<minor>.<patch>` — release estable a producción
- `v<major>.<minor>.<patch>-rc<N>` — release candidate para QA/preprod
- `v<major>.<minor>.<patch>-hotfix.<desc>` — hotfix a producción
- `<any>-alpha.<N>` / `<any>-beta.<N>` — pre-release tests

### Tag triggers
- Crear un tag `v*` normalmente dispara un deploy a producción vía Cloud Build / GitHub Actions.
- Crear un tag `*-rc*` normalmente dispara un deploy a preprod.
- Los tags se crean con `git tag -a vX.Y.Z -m "mensaje" && git push origin vX.Y.Z`.
```

### .context8/PIPELINES.md

Create the CI/CD reference file. Run these commands to gather data:

```bash
echo "## GitHub Actions"
ls .github/workflows/ 2>/dev/null | head -20

echo ""
echo "## Cloud Build"
ls cloudbuild*yaml cloudbuild*/ 2>/dev/null | head -10

echo ""
echo "## Cloud Run / Cloud Functions triggers"
gcloud functions list --format="table(name, trigger.eventType)" 2>/dev/null | head -20 || echo "(gcloud CLI no disponible)"
```

Auto-detect triggers from GitHub Actions:

```bash
for file in .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null; do
  echo "=== $file ==="
  sed -n '/^on:/,/^jobs:/p' "$file"
  echo ""
done
```

Write `.context8/PIPELINES.md`:

```markdown
# Pipelines — [project name]

## Triggers overview

| Pipeline | Trigger | Action | Target | Source config |
|----------|---------|--------|--------|---------------|
| Deploy preprod | push to `main` | build + deploy | Cloud Run — pre | `.github/workflows/deploy-pre.yml` |
| Deploy production | tag `v*` | build + deploy | Cloud Run — prod | `cloudbuild-prod.yaml` |
| Tests | PR to `develop` / `feat/*` | pytest + lint | CI (GitHub Actions) | `.github/workflows/test.yml` |
| Nightly e2e | schedule (06:00 UTC) | e2e tests | CI (Cloud Build) | `cloudbuild-nightly.yaml` |

## GitHub Actions workflows

| Workflow | Triggers | Description |
|----------|----------|-------------|
| `test.yml` | PR a develop, feat/* | Tests unitarios + lint |
| `deploy-pre.yml` | push a main | Build + deploy a preprod |
| `release.yml` | tag v* | Build + deploy a producción |

## Cloud Build triggers

| Trigger | Event | Target | Config |
|---------|-------|--------|--------|
| deploy-prod | tag v* | Cloud Run production | `cloudbuild-prod.yaml` |

> Si el trigger está desplegado manualmente en GCP Console
> y no tiene archivo YAML en el repo, se documenta como **External**.

## External triggers (no están en el repo)

Los siguientes triggers existen en el entorno cloud pero NO tienen configuración en el repositorio:

| Trigger | Source | Action | Environment | Config location |
|---------|--------|--------|-------------|-----------------|
| Deploy preprod | push a `main` (GCP trigger) | Build → Cloud Run Pre | preprod | GCP Console — Cloud Build triggers |
| Nightly DB backup | Cloud Scheduler (06:00 UTC) | Backup script | production | GCP Console — Cloud Scheduler |
| PubSub → Function | Pub/Sub topic `new-user` | Cloud Function `onboard-user` | production | GCP Console — Cloud Functions |

> **Mantenimiento**: Si se crea, modifica o elimina un trigger externo,
> actualizar esta sección manualmente o vía CI/CD skill.

## Environments

| Environment | URL / endpoint | Deploy method | Deploy trigger | Approvals |
|-------------|----------------|---------------|----------------|-----------|
| Development | `localhost:8080` | docker compose / `uv run` | — | — |
| Preproduction | `pre.example.com` | Cloud Build push to main | automático | — |
| Production | `example.com` | Cloud Build tag v* | manual | requiere approval |

## How to trigger a deploy manually

```bash
# Preproducción: push a main
git push origin main

# Producción: crear tag semver
git tag -a v1.2.3 -m "release: auth module refactor"
git push origin v1.2.3
```
```

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
- [ ] REPO_BRANCHES.md created with all branches listed and purpose inferred
- [ ] PIPELINES.md created with CI/CD triggers, workflows, and external triggers documented
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
