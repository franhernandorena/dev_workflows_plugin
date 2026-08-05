# Task: team-setup skill + team routing en dev-workflows

**Date**: 2026-08-05
**Status**: In progress
**Branch**: develop
**Environment**: dev
**Workspace**: (plugin repo — sin workspace padre)

## Objective
Crear el skill `team-setup` (analiza un proyecto / workflow / set de proyectos y genera el equipo de agentes especializados usando los skills `create-*-agent` existentes, más un registro `.context8/TEAM.md` con Routing Map) y actualizar el resto de los skills del plugin para que: (1) al iniciar/continuar verifiquen si existe team, (2) si no existe → correr `team-setup`, (3) rutear el trabajo al especialista correspondiente (research → research-agent, dev → backend/frontend-agent, tests → qa-agent, etc.). Agregar también `create-research-agent` (el rol de investigación no existe todavía).

## Acceptance Criteria
- [ ] `skills/team-setup/SKILL.md` existe y sigue la estructura de los create-*-agent
- [ ] `skills/create-research-agent/SKILL.md` existe (misma plantilla que create-qa-agent)
- [ ] `install.py` registra ambos skills nuevos
- [ ] workflow-init, project-init, workflow-continue, project-continue, task-plan, task-do, task-continue, task-review, task-hotfix tienen bloque de Team Routing
- [ ] README.md y AGENTS.md listan los skills nuevos
- [ ] Sync a `~/.hermes/skills/dev-workflows`
- [ ] Commit en develop (ASK — política del repo en develop: Never Auto-Commit)

## Approach
1. Escribir `team-setup` (fases: status check del team, preflight/scope, mapeo dominio→rol, preguntas, generación vía create-*-agent, TEAM.md con Routing Map, verificación).
2. Escribir `create-research-agent`.
3. Patch `install.py` + 9 skills + README + AGENTS.md.
4. Sync manual a `~/.hermes/skills/dev-workflows` (espejo de install.py para hermes).
5. Commit con confirmación del usuario.

## Progress Log
- 2026-08-05: Iniciado. Checkout develop (main ya tenía develop mergeado). Revisados create-*-agent, workflow-continue, project-continue, dispatching-parallel-agents.
- 2026-08-05: Creados skills/team-setup y skills/create-research-agent. Patch install.py (registro de ambos), 9 skills con Team Routing (workflow-init, project-init, workflow-continue, project-continue, task-plan, task-do, task-continue, task-review, task-hotfix), README.md y AGENTS.md/CLAUDE.md. Sync a ~/.hermes/skills/dev-workflows (11 archivos).

## Decisions Made
- Team registry = `.context8/TEAM.md` (root para workflows/multi-repo; repo-level para proyecto simple) con tablas Members + Routing Map.
- Agentes generados en formato nativo del tool actual (reuso de create-*-agent), guardados per-project (`.opencode/agents/`, `.claude/agents/`, etc.).
- Routing map estándar: research→research-agent, architecture→architect-agent, backend→backend-agent, frontend→frontend-agent, mobile→mobile-agent, database→database-agent, tests/QA→qa-agent, security→security-agent, cloud→cloud-agent, devops→devops-agent.

## Files Modified
- `skills/team-setup/SKILL.md` — nuevo: crea el equipo de agentes especializados + TEAM.md con Routing Map
- `skills/create-research-agent/SKILL.md` — nuevo: genera el agente de investigación (misma plantilla que create-qa-agent)
- `install.py` — registra team-setup y create-research-agent en SKILLS
- `skills/workflow-init/SKILL.md` — Phase 5 Team Setup
- `skills/project-init/SKILL.md` — Phase 6 Team Setup
- `skills/workflow-continue/SKILL.md` — 2.1 Team check
- `skills/project-continue/SKILL.md` — 1.5 Team check
- `skills/task-plan/SKILL.md` — 1.2 Consult the team
- `skills/task-do/SKILL.md` — Team routing en Phase 3
- `skills/task-continue/SKILL.md` — 3.5 Team check
- `skills/task-review/SKILL.md` — 1.7 Route the review to the team
- `skills/task-hotfix/SKILL.md` — 1.1 Team routing
- `README.md` — tabla Agent Generators + sección Team Setup
- `CLAUDE.md` (AGENTS.md es symlink) — sección Team en Available Skills
- `.context8/tasks/2026-08-05_team-setup-skill.md` — este task file
- `~/.hermes/skills/dev-workflows/` — sync de los 11 SKILL.md

## Blockers
- Ninguno.
