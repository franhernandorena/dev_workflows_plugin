# Agent Context

## Tech Stack

- **Lenguajes**: Python 3.11+ (installer), Markdown (skills/prompts)
- **Runtime**: Python, uv
- **Dependencias**: questionary (installer TUI)
- **Formatos**: JSON, YAML, Markdown

## Architecture

Plugin de skills para AI coding agents. Arquitectura plana de skills:
- Cada skill es un directorio con `SKILL.md` (frontmatter + full prompt) y `prompt.md` (contenido del prompt)
- `install.py` copia las skills segun la herramienta destino y el scope elegido
- Skills registradas en `plugin.json` (.claude-plugin, .codex-plugin, .cursor-plugin) y `gemini-extension.json`

## Directory Structure (annotated)

```
agents_prompts/
├── install.py                    # Instalador cross-platform (TUI con questionary)
├── CLAUDE.md                     # Contexto del plugin para Claude Code
├── GEMINI.md                     # Contexto del plugin para Gemini CLI
├── AGENTS.md                     # Contexto del plugin para OpenCode
├── gemini-extension.json         # Manifest de extension Gemini
├── pyproject.toml                # Config Python (uv)
├── .claude-plugin/               # Manifest para Claude Code
├── .codex-plugin/                # Manifest para Codex
├── .cursor-plugin/               # Manifest para Cursor
│
├── workflows/                    # Source prompts — multi-repo
├── projects/                     # Source prompts — single repo
├── tasks/                        # Source prompts — task execution
│
├── skills/                       # Skills empaquetadas (instalables)
│   ├── workflow-init/
│   ├── workflow-continue/
│   ├── workflow-add-repo/
│   ├── project-init/
│   ├── project-continue/
│   ├── project-handoff/
│   ├── project-audit/
│   ├── task-plan/
│   ├── task-do/
│   ├── task-review/
│   └── task-hotfix/
│
├── projects/                     # Prompts fuente para skills de projects
├── workflows/                    # Prompts fuente para skills de workflows
└── tasks/                        # Prompts fuente para skills de tasks
```

## Entry Points

- **Instalacion**: `uv run install.py` (TUI interactiva)
- **Invocacion**: `/dev-workflows:<skill-name>` desde el AI coding agent
- **Plugins**: Auto-detectados por Claude Code, Codex, Cursor, Gemini CLI, OpenCode

## Data Flow

Usuario invoca skill -> AI agent carga SKILL.md -> Sigue fases del prompt -> Produce output (`.context8/` files, tareas, PRs, etc.)

## Session-Start Hook

The hook (`hooks/context8_session_start.py`) runs at every agent startup.

**Contract:**
- Input: current working directory, optional native hook JSON from the agent.
- Missing `.context8/` → classify (workspace or project) and output a mandatory first action to run `dev-workflows:workflow-init` or `dev-workflows:project-init`.
- Existing `.context8/` → output context summary and task inventory from `.context8/tasks/*.md`.
- Workspace roots → also scan child repos at depth 1-2 for active tasks.

**Support matrix:**

| Agent | Mechanism |
|-------|-----------|
| Claude Code | Native `SessionStart` plugin hook via `hooks/hooks.json` |
| Codex, Cursor, Gemini CLI, OpenCode, Hermes | Managed startup instruction block in context file |

## Key Modules & Their Responsibilities

| Modulo | Proposito | Archivos clave |
|--------|-----------|----------------|
| Installer | Instalacion cross-platform | `install.py`, `pyproject.toml` |
| Workflow skills | Multi-repo workspace management | `skills/workflow-*/` |
| Project skills | Single-repo project lifecycle | `skills/project-*/` |
| Task skills | Task planning & execution | `skills/task-*/` |

## Core Design Patterns & Conventions

- **Fases estrictas**: Cada skill tiene fases que NO se pueden saltar
- **Output a disco**: Skills producen archivos (`.context8/`, task files, handoffs)
- **Idioma**: Todo en ingles (a menos que se especifique lo contrario)
- **Skill format**: YAML frontmatter + Overview + When to use + Output + Full Prompt
- **Branch naming**: `type/short-description`

## Configuration & Environment

No hay variables de entorno. Toda la config esta en:
- `plugin.json` (Claude/Codex/Cursor) — nombre, skills path, metadata
- `gemini-extension.json` — contextFileName para Gemini
- `install.py` — TOOLS dict con paths de instalacion

## External Integrations & APIs

- **Claude Code**: Skills via `/dev-workflows:<skill>` (lee de `~/.claude/skills/`)
- **Codex (OpenAI)**: Skills via `~/.agents/skills/`
- **Cursor**: Skills via `~/.cursor/skills/`
- **Gemini CLI**: Skills via `~/.gemini/skills/` (GEMINI.md)
- **OpenCode**: Skills via `~/.config/opencode/AGENTS.md`

## Testing Strategy

None currently. No hay tests automatizados para `install.py` o las skills.

## CI/CD Pipeline

None configured. No hay workflows de GitHub Actions, GitLab CI, ni otros pipelines.

## Known Constraints & Gotchas

- Los skills se instalan via install.py, no via package managers
- OpenCode usa un solo archivo `AGENTS.md` en lugar de directorio de skills
- Gemini CLI requiere `@include` directives en GEMINI.md (no copia skills directamente)

## Versioning & Release Process

- Version en `pyproject.toml` = 1.0.0
- Git tags no configurados
- Sin changelog formal
