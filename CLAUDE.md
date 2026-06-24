# Dev Workflows Plugin

Structured prompts for every stage of development work with an AI agent.

## Session-Start Hook

This plugin includes a session-start hook (`hooks/context8_session_start.py`) that runs at every startup.

- **Claude Code**: The hook runs automatically via `hooks/hooks.json` (`SessionStart` event).
- **Other agents**: The hook is available as a managed startup instruction in your context file. Run `python3 <hook-path>` at startup if instructions are present.

The hook checks whether the current directory has `.context8/`. If missing, it routes you to run `dev-workflows:workflow-init` or `dev-workflows:project-init`. If present, it summarises active tasks.

## Available Skills

### Workflows (multi-repo workspaces)
- `dev-workflows:workflow-init` — bootstrap a new multi-repo workspace
- `dev-workflows:workflow-continue` — resume an existing workspace session
- `dev-workflows:workflow-add-repo` — add a new repo to an existing workspace
- `dev-workflows:workflow-status` — multi-repo workspace visibility in one glance

### Projects (single repos)
- `dev-workflows:project-init` — bootstrap a new project (creates .context8/)
- `dev-workflows:project-continue` — start a session on an existing project
- `dev-workflows:project-handoff` — close a session cleanly for the next agent
- `dev-workflows:project-audit` — assess a project with no or stale documentation
- `dev-workflows:project-review` — full project health check before milestones

### Tasks
- `dev-workflows:task-plan` — produce a detailed implementation plan
- `dev-workflows:task-do` — execute a planned task step by step
- `dev-workflows:task-continue` — resume a partially completed task
- `dev-workflows:task-compacting` — archive completed/cancelled tasks with monthly LLM-friendly summaries
- `dev-workflows:task-compacting` — archive completed/cancelled tasks with monthly LLM-friendly summaries
- `dev-workflows:task-review` — pre-PR code review (correctness, security, tests)
- `dev-workflows:task-hotfix` — urgent production fix with controlled speed

### Repository Maintenance
- `dev-workflows:repo-cleanup` — revisa ramas git, limpia automáticamente las propias mergeadas y pide permiso antes de tocar ajenas
- `dev-workflows:tag-create` — crea tags git semver: analiza cambios desde el último tag, sugiere versión, genera mensaje descriptivo y pide confirmación

### Documents
- `document:make-report` — generate structured markdown reports optimized for ClickUp Docs with proper tables, diagrams, and formatting

### Analysis
- `dev-workflows:change-impact` — analyze blast radius before implementing
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
