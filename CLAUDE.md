# Dev Workflows Plugin

Structured prompts for every stage of development work with an AI agent.

## Session-Start Hook

This plugin includes a session-start hook (`hooks/context8_session_start.py`) that runs at every startup.

- **Claude Code**: The hook runs automatically via `hooks/hooks.json` (`SessionStart` event).
- **Other agents**: The hook is available as a managed startup instruction in your context file. Run `python3 <hook-path>` at startup if instructions are present.

The hook checks whether the current directory has `.context8/`. If missing, it routes you to run `dev-workflows:workflow-init` or `dev-workflows:project-init`. If present, it summarises active tasks.

## Posture & Conventions

These rules apply to every session in every project. Skills inherit them; the
agent must follow them without being reminded.

### Environment & Permissions

Every project may have `dev`, `beta`, and `prod`. Before any task that touches
shared state (DB writes, API calls, deploys, branch pushes, infra changes), the
agent MUST identify the target environment and obey the permission matrix below.

| Env    | Detect by                                       | Agent may...                                      |
|--------|-------------------------------------------------|---------------------------------------------------|
| dev    | `feat/*` branch, localhost, `.env.dev`          | work freely, run migrations locally, push commits |
| beta   | `release/*` branch, staging URLs, `.env.beta`   | work, but ASK before each non-read op             |
| prod   | `main`/`master` branch, prod URLs, `.env.prod`  | DO NOTHING without explicit, written permission   |

Definitions:

- **"ASK"** = stop, present the planned action, wait for the user's explicit
  "yes" or "go". A silent continuation is NOT consent.
- **"Explicit permission"** = the user wrote out the action in their message.
  "Sure", "ok", "continue" without specifying the action does NOT count.
- **prod is sacred.** If a task would touch prod, surface it before starting
  `task-do` — even if the user said "do it".
- When the task file records an environment, write it explicitly:
  `**Environment**: dev | beta | prod`.
- If the environment is unclear, ASK. Do not guess.

### Available Tools — Use Them by Default

The plugin lives inside an ecosystem. The agent SHOULD prefer these tools
when applicable. Do not reinvent what they already do.

- **caveman** — compressed communication when output is large or requested.
  Use `caveman-commit` for commit messages, `caveman-review` for review
  feedback, `caveman-stats` to report token savings.
- **ponytail** — tail long outputs, structured agent-to-agent handoffs.
- **context-mode (`ctx_*`)** — gather & process large data OUT of conversation
  memory. Use `ctx_batch_execute` for parallel commands, `ctx_search` for
  knowledge-base queries, `ctx_execute_file` for file analysis.
- **code-review-graph** — auto-updated SQLite at `.code-review-graph/graph.db`.
  Updated on every Edit/Write/Bash. Query it for blast radius, callers, deps.
  See skills `change-impact`, `task-review` for usage patterns.
- **superpowers** — invoke `brainstorming` before any creative work, `TDD` for
  implementations, `systematic-debugging` for bugs,
  `verification-before-completion` before claiming "done".
- **context7, playwright, token-savior, code-simplifier, feature-dev,
  frontend-design, claude-mem, claude-md-management** — use when the task fits.

### Critical Posture — Question, Don't Just Do

The user expects the agent to challenge assumptions and demand clarity. The
default behavior is to question, not to comply.

- Before starting a non-trivial task, state your understanding of the goal
  in 2-3 sentences. If the user disagrees with that understanding, fix it
  before doing anything.
- When the user says "do X" but X is ambiguous: ask. Do not pick the most
  likely interpretation silently.
- When a request has hidden costs (touching prod, breaking a public API,
  large refactor, new dependency): surface the cost before acting.
- When you spot a better approach than the one requested: present it, then
  let the user decide. Do not silently substitute.
- "I understand, I will do X" is a valid response to a request ONLY when X
  is unambiguous. Otherwise the response is "I want to confirm: is X what
  you mean? Because Y could also be it."
- Saying "yes" to everything is a failure mode here, not a virtue.

### Commit Policy — Auto-Commit in dev/beta, ASK in prod

- **dev / beta**: the agent commits automatically. No ask, no wait. Stage
  the specific files touched, write a Conventional Commits message
  (`type(scope): description`), and run `git commit` directly.
- **prod**: unchanged — the agent MUST ask before creating a commit.
  Present the exact `git add` + `git commit -m "<message>"` command, wait
  for explicit "yes" or "go", then execute it. Prod is sacred (see
  Environment & Permissions above).
- `--no-verify`, `--amend`, force-push, and empty commits are forbidden
  unless the user wrote the exact command in their message — in any
  environment.
- Rebase, cherry-pick, reset, and branch deletion also require explicit
  permission, even on the agent's own branches, in any environment.
- Conventional Commits format is encouraged: `type(scope): description`.
  Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `perf`.

### Task File Conventions

Task files live in `.context8/tasks/YYYY-MM-DD_short_description.md`. They do
NOT include timestamps. The progress log uses date + bullet, not `[HH:MM]`.

```markdown
**Date**: YYYY-MM-DD
**Status**: Planned | In progress | Blocked | Complete
**Branch**: [branch]
**Environment**: dev | beta | prod   ← identify at task-plan time
**Workspace**: [name — only if part of a multi-repo workspace]

## Progress Log
- YYYY-MM-DD: Started. Reading X, Y, Z.
- YYYY-MM-DD: Step 1 complete. [summary]
- YYYY-MM-DD: Step 2 complete. [summary]
```

## Available Skills

### Workflows (multi-repo workspaces)
- `dev-workflows:workflow-init` — bootstrap a new multi-repo workspace
- `dev-workflows:workflow-continue` — resume an existing workspace session
- `dev-workflows:workflow-add-repo` — add a new repo to an existing workspace
- `dev-workflows:workflow-status` — multi-repo workspace visibility in one glance

### Projects (single repos)
- `dev-workflows:project-init` — bootstrap a new project (creates .context8/)
- `dev-workflows:project-continue` — start a session on an existing project (follows global Posture)
- `dev-workflows:project-handoff` — close a session cleanly for the next agent
- `dev-workflows:project-audit` — assess a project with no or stale documentation
- `dev-workflows:project-review` — full project health check before milestones

### Tasks
- `dev-workflows:task-plan` — produce a detailed implementation plan (follows global Posture)
- `dev-workflows:task-do` — execute a planned task step by step (follows global Posture)
- `dev-workflows:task-continue` — resume a partially completed task (follows global Posture)
- `dev-workflows:task-compacting` — archive completed/cancelled tasks with monthly LLM-friendly summaries (follows global Posture)
- `dev-workflows:task-compacting` — archive completed/cancelled tasks with monthly LLM-friendly summaries
- `dev-workflows:task-review` — pre-PR code review (correctness, security, tests) (follows global Posture)
- `dev-workflows:task-hotfix` — urgent production fix with controlled speed (follows global Posture)

### Repository Maintenance
- `dev-workflows:repo-cleanup` — revisa ramas git, limpia automáticamente las propias mergeadas y pide permiso antes de tocar ajenas
- `dev-workflows:tag-create` — crea tags git semver: analiza cambios desde el último tag, sugiere versión, genera mensaje descriptivo y pide confirmación

### Documents
- `document:make-report` — generate structured markdown reports optimized for ClickUp Docs with proper tables, diagrams, and formatting

### Analysis
- `dev-workflows:change-impact` — analyze blast radius before implementing (follows global Posture)
- `dev-workflows:dependency-audit` — audit dependencies (vulns, outdated, unused)

### Pull Requests
- `dev-workflows:pr-description` — generate structured PR description from diff

### Deployments
- `dev-workflows:deploy-plan` — plan a deployment with rollback and verification
- `dev-workflows:release` — end-to-end release (version bump, changelog, tag, publish)

## Typical Flow

```
project-audit → project-init → project-continue → task-plan → task-do → task-review
                                                                        ↓
                                                               task-hotfix (if prod breaks)
```

## Rules
- Every skill enforces phases. Do not skip phases, even for "simple" tasks.
- Skills produce files (`.context8/`, task files, handoff summaries). Output goes to disk, not inline.
- All documentation written in English unless explicitly overridden.
