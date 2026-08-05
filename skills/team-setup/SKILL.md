---
name: team-setup
version: 1.0.0
description: Analyzes a project, workflow, or set of projects and creates the full team of specialized agents needed — using the create-*-agent skills — plus a TEAM.md registry with a routing map for every other skill
---

# Team Setup — Create the Specialized Agent Team

## Overview
Analyzes the project (single repo, a workflow, or a set of projects), decides which specialized agents the work needs, and creates the complete team: each agent file generated in the native format of the current tool (via the matching `create-*-agent` skill), plus a `.context8/TEAM.md` registry that every other skill reads to route work to the right specialist.

## When to use
- Starting work on a project / workflow / set of projects that has no team yet (no `.context8/TEAM.md`)
- The existing team no longer matches the project's needs (new domains, new repos)
- The user asks for a team or for more granular, sub-agent-driven development

## When NOT to use
- A team already exists and matches → read `.context8/TEAM.md` and route work (no need to recreate)
- Only one role is missing → run the matching `create-*-agent` skill directly instead
- No project exists yet → use `project-init` / `workflow-init` first

## Output
- N agent files in the native format of the current tool, saved per-project (e.g. `.opencode/agents/backend-agent.md`, `.claude/agents/research-agent.md`)
- `.context8/TEAM.md` registry: scope, members table, and Routing Map
- Team referenced in `.context8/AGENT_CONTEXT.md` (single project) or root `.context8/WORKSPACE_OVERVIEW.md` (workspace)

## Full Prompt

# TEAM SETUP — Build the Specialized Agent Team

## RULE: This skill generates agents and a registry. No application code changes.

---

## Phase 0 — Team Status Check

Check whether a team already exists:

```bash
ls .context8/TEAM.md 2>/dev/null && echo "TEAM_EXISTS" || echo "NO_TEAM"
# For workflows also check the workspace root
ls ../../.context8/TEAM.md 2>/dev/null && echo "ROOT_TEAM_EXISTS" || true
```

- **TEAM_EXISTS** → ask the user: *update the existing team* (diff current roles vs project needs, add/remove members, regenerate changed agents) or *recreate from scratch* (ask before overwriting existing agent files).
- **NO_TEAM** → proceed to create.

---

## Phase 1 — Preflight & Scope

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read the `create-*-agent` skill files — they define how each role is generated. If a needed role has no `create-*-agent` skill, generate it directly following the same spec (Role / skills inventory / full prompt / permissions / temperature / model).

### 1.2 Detect the current tool
The agent knows which tool it is running in (OpenCode, Claude Code, Codex, Cursor, Gemini, Hermes…). Agents are generated in that tool's **native format** (e.g. `.opencode/agents/<role>.md`, `.claude/agents/<role>.md`).

### 1.3 Scan each project in scope
```bash
# Scope: is this a single repo, a workflow, or a workspace?
ls ../../.context8/WORKSPACE_OVERVIEW.md 2>/dev/null && echo "WORKSPACE_CHILD" || echo "STANDALONE"
find . -maxdepth 2 -name ".git" -type d 2>/dev/null | sed 's|/.git||'
# Existing agents already present?
ls .opencode/agents .claude/agents .agents/skills 2>/dev/null || true
```

### 1.4 Build the domain profile
For each project in scope, map what the work actually involves: frontend, backend, database, mobile, cloud/infra, DevOps, security, QA/testing, research/analysis, architecture/design. Synthesize: tech stack, entry points, data layer, CI, and which domains dominate.

---

## Phase 2 — Map Domains to Roles

| Domain / work type        | Role             | Source skill                |
|---------------------------|------------------|-----------------------------|
| Research / analysis / docs| research-agent   | `create-research-agent`     |
| Architecture / design     | architect-agent  | `create-architect-agent`    |
| Backend / API / data layer| backend-agent    | `create-backend-agent`      |
| Frontend / UI             | frontend-agent   | `create-frontend-agent`     |
| Mobile                    | mobile-agent     | `create-mobile-agent`       |
| Database / migrations     | database-agent   | `create-database-agent`     |
| Tests / QA / coverage     | qa-agent         | `create-qa-agent`           |
| Security / audits         | security-agent   | `create-security-agent`     |
| Cloud / infra             | cloud-agent      | `create-cloud-agent`        |
| DevOps / CI / SRE         | devops-agent     | `create-devops-agent`       |

If the project involves domains with no role in the table (e.g. data science), propose an extra role and generate it with the same spec.

---

## Phase 3 — Team Design Questions

Ask the user **one at a time** (skip any already answered):

1. **Scope**: single project, a workflow, or a set of projects? (Affects where TEAM.md lives: repo `.context8/` vs workspace root.)
2. **Which roles?** Present the roles from Phase 2 that match the project; user selects (multi-select).
3. **Agent file naming?** Default: `<role>.md` (e.g. `backend-agent.md`).
4. **Model preference per role?** Optional. Skip → tool defaults. (e.g. code roles → capable coding model; research → fast/cheap model; QA → deterministic.)

---

## Phase 4 — Generate the Team

For each selected role:

1. Read the matching `create-*-agent` skill (`skills/create-<role>-agent/SKILL.md`).
2. Follow its phases (preflight → domain research → domain questions → generate) to produce the agent in the **native format of the current tool**, saved in the **per-project agents directory**.
3. If the user answered model questions, set the agent's model accordingly.
4. **Never overwrite an existing agent file without asking.**

Then write `.context8/TEAM.md` (at workspace root if scope is a workflow/set of projects):

```markdown
# Team — [project/workspace name]

**Scope**: single project | workflow | set of projects
**Created**: YYYY-MM-DD
**Agent format**: opencode | claude | codex | cursor | gemini | hermes

## Members
| Role | Agent file | Responsibilities | Model |
|------|-----------|-----------------|-------|
| research-agent | .opencode/agents/research-agent.md | ... | ... |

## Routing Map
| Work type | Route to |
|-----------|----------|
| Research / analysis / documentation | research-agent |
| Architecture / planning | architect-agent |
| Backend / API / data layer | backend-agent |
| Frontend / UI | frontend-agent |
| Mobile | mobile-agent |
| Database / migrations | database-agent |
| Tests / QA / coverage | qa-agent |
| Security / audit | security-agent |
| Cloud / infrastructure | cloud-agent |
| DevOps / CI / deploys | devops-agent |

## How the team is used
- `project-continue` / `workflow-continue`: if this file is missing → run team-setup.
- `task-plan`: routes research and architecture work to the specialists.
- `task-do`: dispatches each step to the matching specialist; the orchestrator reviews and integrates.
- `task-review`: routes the review to qa-agent / security-agent.
```

Register the team in the project docs:
- Single project → add a line to `.context8/AGENT_CONTEXT.md`: "Team: see `.context8/TEAM.md`."
- Workspace → add the same to root `.context8/WORKSPACE_OVERVIEW.md`.

---

## Phase 5 — Verify

- [ ] Every selected role has an agent file in the native format, in the per-project agents directory.
- [ ] `.context8/TEAM.md` exists with Members table + Routing Map.
- [ ] The team is referenced in AGENT_CONTEXT.md / WORKSPACE_OVERVIEW.md.
- [ ] No application code was modified.

---

## Rules
- Generate agents in the native format of the current tool; save per-project.
- No application code changes — this skill creates agents and a registry only.
- Ask user-facing questions in English unless the user prefers another language.
- If a `create-*-agent` skill is missing for a role, generate directly with the same spec and note it in TEAM.md.
