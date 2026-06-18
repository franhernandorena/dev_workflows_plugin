# Task: Automatizar desarrollo de dev-workflows — sync, tests, CI/CD, release

**Date**: 2026-06-15
**Status**: Planned
**Branch**: feat/ci-cd-and-dev-automation
**Estimated total complexity**: XL

## Objective

El proyecto `dev-workflows` provee flujos de trabajo estructurados para otros desarrolladores, pero su propio proceso de desarrollo es completamente manual: los source prompts y los skills empaquetados se sincronizan a mano (`640eab7`), `install.py` no tiene tests, no hay CI/CD, no hay changelog, y la documentación interna (module map, AGENT_CONTEXT) está parcialmente desactualizada. Esta tarea automatiza el ciclo de desarrollo del repo mismo: sync de skills, tests, CI/CD, y release.

## Acceptance Criteria

- [ ] **Sync script**: `make sync` o `uv run sync-skills.py` sincroniza `workflows/*.md` → `skills/workflow-*/` y `projects/*.md` → `skills/project-*/` y `tasks/*.md` → `skills/task-*/`. Detecta archivos fuente modificados, genera SKILL.md + prompt.md. Modo dry-run (`--dry-run`) y modo diff (`--diff`).
- [ ] **Tests**: `pytest tests/` pasa. Tests cubren: detección de herramientas, escritura de archivos (dry-run y real), flag `--uninstall`, flag `--dry-run`, edge cases (tool no detectado, skill faltante).
- [ ] **GitHub Actions**: PR workflow corre `ruff check .` + `pytest -x -q`. Release workflow: al pushear tag `v*`, genera GitHub Release con CHANGELOG.
- [ ] **Linter**: `ruff` configurado en `pyproject.toml`. `ruff check .` pasa sin errores.
- [ ] **CHANGELOG.md**: Formato [Keep a Changelog](https://keepachangelog.com/). Entradas para las versiones existentes (1.0.0) y la nueva.
- [ ] **Housekeeping**: Module map actualizado (generators ya no son "[Future]"). AGENT_CONTEXT.md refleja que Hermes Agent es tool soportado.
- [ ] README.md actualizado si aplica.
- [ ] Los skills instalados en Hermes (via copies previas) NO se modifican — solo se actualizan los archivos fuente en el repo.

## Out of Scope

- Modificar el contenido/filosofía de los skills existentes
- Añadir nuevos skills
- Cambiar la arquitectura del instalador (`install.py`)
- Migrar a otro gestor de paquetes
- Modificar skills de Hermes fuera del repo

## Unknowns & Risks

| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| GitHub Actions no está habilitado en el repo | high | Verificar antes; si no está, pedir al usuario que lo active o documentar setup manual |
| ruff puede tener conflictos con el estilo actual de install.py | low | Ejecutar `ruff check --fix` y revisar cambios manualmente |
| El sync script puede ser complejo si los formatos de SKILL.md vs prompt.md difieren mucho entre skills | medium | Analizar todos los skills primero para encontrar el denominador común |
| Cambiar el module map y AGENT_CONTEXT puede quedar inconsistente si se tocan manualmente después | low | Es documentación estática — se actualiza una vez |

## Implementation Plan

## Step 1: Configurar ruff linter

**Files**: `pyproject.toml` (modify)
**Depends on**: none
**Estimated complexity**: trivial
**Reversible**: yes

### What
Añadir sección `[tool.ruff]` a `pyproject.toml` con:
- `line-length = 100`
- `target-version = "py311"`
- Select: `E`, `F`, `I` (pycodestyle, pyflakes, isort)

### Why
Base para que el CI corra linting. Sin config de linter no se puede exigir calidad de código.

### How to verify
```bash
uv run ruff check . 2>&1 | head -20
# Debe mostrar errores existentes (si los hay), no "error: no config"
```

### Risks
Ninguno.

---

## Step 2: Escribir tests para install.py

**Files**: `tests/test_install.py` (create), `pyproject.toml` (modify — añadir pytest)
**Depends on**: none
**Estimated complexity**: medium
**Reversible**: yes

### What
Crear `tests/test_install.py` con tests unitarios usando `pytest` y `tmp_path`. No mockear el filesystem real — usar `tmp_path` para simular instalaciones.

Tests a cubrir:
1. **`test_get_skill_files_local`** — lee un skill existente del directorio `skills/`, verifica que devuelve `SKILL.md` y `prompt.md`
2. **`test_get_skill_files_local_missing`** — pide un skill inexistente, verifica que devuelve dict vacío
3. **`test_write_file_create`** — escribe archivo nuevo, verifica contenido
4. **`test_write_file_update`** — escribe sobre archivo existente, verifica backup creado y contenido actualizado
5. **`test_write_file_dry_run`** — con dry=True, verifica que NO se escribe nada
6. **`test_install_tool_creates_files`** — `install_tool()` con tool que tiene `files_per_skill`, verifica que crea los archivos esperados
7. **`test_install_tool_context_file`** — `install_tool()` con tool OpenCode (sin `files_per_skill`), verifica que escribe AGENTS.md
8. **`test_uninstall_tool_removes_skills`** — `uninstall_tool()` elimina directorios de skills
9. **`test_detect_tool_by_path`** — `detect_tool()` con path existente devuelve True
10. **`test_detect_tool_by_binary`** — `detect_tool()` con binary en PATH devuelve True
11. **`test_detect_tool_not_found`** — `detect_tool()` sin path ni binary devuelve False
12. **`test_backup_path`** — verifica que `backup_path()` genera sufijo `.bak_*`

Añadir a `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = ["pytest"]
```

### Why
`install.py` es el entry point para todos los usuarios. Sin tests, un bug puede romper instalaciones sin que nadie lo detecte hasta que es demasiado tarde.

### How to verify
```bash
uv run --group dev pytest tests/ -x -q
# All tests pass
```

### Risks
Algunas funciones (`get_skill_files`, `get_context_file`) dependen de `SCRIPT_DIR` y del filesystem real. Usar `monkeypatch` de pytest para controlar rutas.

---

## Step 3: Limpiar install.py con ruff

**Files**: `install.py` (modify)
**Depends on**: Step 1 (ruff config), Step 2 (tests aseguran no regresión)
**Estimated complexity**: small
**Reversible**: yes

### What
Ejecutar `ruff check --fix install.py` y corregir manualmente los errores restantes. Típicamente:
- Import order (isort)
- Espaciado, líneas en blanco
- Nombres de variables no usadas

### Why
El CI va a exigir `ruff check .` limpio. Mejor hacerlo ahora con `--fix` antes de que el pipeline falle.

### How to verify
```bash
ruff check install.py
# No output = clean
```

### Risks
`ruff --fix` es seguro para E, F, I. No usar `--unsafe-fixes`. Si hay W (warnings) dejarlos para discusión.

---

## Step 4: Crear sync-skills.py

**Files**: `sync-skills.py` (create)
**Depends on**: Step 2 (los tests no dependen de esto, pero es bueno tener tests antes de añadir código nuevo)
**Estimated complexity**: medium
**Reversible**: yes

### What
Script que sincroniza source prompts → skills empaquetados.

**Mapping source → skill**:
| Source dir | Source file | Skill dir |
|------------|-------------|-----------|
| `workflows/init.md` | → | `skills/workflow-init/` |
| `workflows/continue.md` | → | `skills/workflow-continue/` |
| `workflows/add-repo.md` | → | `skills/workflow-add-repo/` |
| `projects/init.md` | → | `skills/project-init/` |
| `projects/continue.md` | → | `skills/project-continue/` |
| `projects/handoff.md` | → | `skills/project-handoff/` |
| `projects/audit.md` | → | `skills/project-audit/` |
| `tasks/plan.md` | → | `skills/task-plan/` |
| `tasks/do.md` | → | `skills/task-do/` |
| `tasks/review.md` | → | `skills/task-review/` |
| `tasks/hotfix.md` | → | `skills/task-hotfix/` |

**Lógica del script**:
1. Leer cada archivo fuente `.md`
2. Extraer frontmatter YAML (si existe) del source
3. Tomar el SKILL.md existente en destino, extraer su frontmatter original
4. Generar `prompt.md` = contenido del source (sin frontmatter)
5. Generar `SKILL.md` = frontmatter original + `@prompt.md` directive + prompt inlined
6. Modo `--dry-run`: mostrar qué archivos cambiarían sin escribirlos
7. Modo `--diff`: mostrar diff unificado de los cambios
8. Modo `--check` (para CI): exit 1 si hay cambios pendientes

Formato de `prompt.md`: el contenido del source prompt exactamente como está (sin frontmatter).
Formato de `SKILL.md`: frontmatter YAML (heredado del actual) + `\n---\n` + prompt inlined.

### Why
Actualmente la sincronización es manual (commit `640eab7`). Esto garantiza que source prompts y skills nunca divergen. El modo `--check` permite al CI rechazar PRs que modifiquen un source sin actualizar el skill correspondiente.

### How to verify
```bash
# Editar workflows/init.md, luego:
uv run sync-skills.py --dry-run
# Debe mostrar que skills/workflow-init/ será actualizado

uv run sync-skills.py
# Debe actualizar skills/workflow-init/

git diff --stat
# Muestra cambios solo en skills/workflow-init/SKILL.md y prompt.md

uv run sync-skills.py --check
# Exit 0 (todo sincronizado)
```

### Risks
- Los skills `create-*-agent/` NO tienen source prompt en `workflows/`, `projects/`, o `tasks/` — fueron creados directamente como SKILL.md. El script debe ignorarlos explícitamente (solo operar sobre el mapping definido).
- Algunos SKILL.md pueden tener formato personalizado. Verificar que la regeneración conserva el frontmatter.

---

## Step 5: Crear CI/CD con GitHub Actions

**Files**: `.github/workflows/ci.yml` (create), `.github/workflows/release.yml` (create)
**Depends on**: Step 1 (ruff), Step 2 (tests), Step 4 (sync check)
**Estimated complexity**: medium
**Reversible**: yes

### What
**CI workflow** (`.github/workflows/ci.yml`):
```yaml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group dev
      - run: uv run ruff check .
      - run: uv run pytest tests/ -x -q
      - run: uv run sync-skills.py --check
```

**Release workflow** (`.github/workflows/release.yml`):
```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group dev
      - run: uv run pytest tests/ -x -q
      - run: uv run ruff check .
      - name: Extract changelog
        run: |
          VERSION=${GITHUB_REF_NAME#v}
          awk "/^## \\[${VERSION}\\]/{flag=1;next}/^## \\[/{flag=0}flag" CHANGELOG.md > release-notes.md
      - uses: softprops/action-gh-release@v2
        with:
          body_path: release-notes.md
```

### Why
Sin CI/CD, los tests y el linter son optativos. Con CI, cada PR los exige. El release workflow automatiza lo que hoy es manual.

### How to verify
Hacer push a una branch y verificar que GitHub Actions corre. O crear un tag `v1.0.1` y verificar que genera release.

### Risks
- `softprops/action-gh-release` necesita `GITHUB_TOKEN` con permisos de contents:write (default en GH Actions)
- Si el repo no tiene Actions habilitado, el workflow no corre. El plan incluye verificarlo.

---

## Step 6: Crear CHANGELOG.md

**Files**: `CHANGELOG.md` (create)
**Depends on**: Step 5 (opcional — puede ir antes)
**Estimated complexity**: trivial
**Reversible**: yes

### What
Crear `CHANGELOG.md` con formato [Keep a Changelog](https://keepachangelog.com/).

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] — 2026-06-06

### Added
- 11 core skills: workflow-init, workflow-continue, workflow-add-repo, project-init, project-continue, project-handoff, project-audit, task-plan, task-do, task-review, task-hotfix
- 8 agent-generator skills: create-architect-agent, create-backend-agent, create-cloud-agent, create-database-agent, create-devops-agent, create-frontend-agent, create-qa-agent, create-security-agent
- Interactive TUI installer (`install.py`) with questionary
- Multi-tool support: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Hermes Agent
- Plugin manifests for Claude, Codex, Cursor, Gemini

### Changed
- Skills refactored with inlined prompts (640eab7)
- Workspace awareness for child repos (9ad79d3)
- Hierarchical multi-repo task organization (77d8e7c)

## [Unreleased] — TBD

(To be filled by the release workflow)
```

### Why
Sin changelog es imposible saber qué cambió entre versiones. El release workflow de GitHub Actions lo necesita para generar release notes.

### How to verify
```bash
head -30 CHANGELOG.md
# Formato correcto, versiones listadas
```

### Risks
Ninguno.

---

## Step 7: Housekeeping — actualizar module map y AGENT_CONTEXT

**Files**: `.context8/architecture/module_map.md` (modify), `.context8/AGENT_CONTEXT.md` (modify)
**Depends on**: none
**Estimated complexity**: trivial
**Reversible**: yes

### What
**module_map.md**: Cambiar la sección `[Future] Agent Generators` a sección normal, sin tag "[Future]". Ya existen 8 skills de generadores.

**AGENT_CONTEXT.md**: 
- En la sección "External Integrations & APIs", añadir Hermes Agent (falta)
- En "CI/CD Pipeline", cambiar "None configured" por "GitHub Actions (planned)"
- En "Testing Strategy", cambiar "None currently" por "pytest (planned)"
- En "Versioning & Release Process", añadir que CHANGELOG.md y tags están configurados

### Why
La documentación del proyecto debe reflejar la realidad. Actualmente dice que los generators son "[Future]" y que no hay tests/CI/CD, pero después de esta tarea los va a haber.

### How to verify
```bash
grep -c "Future" .context8/architecture/module_map.md
# 0 (ya no aparece)
grep -c "CI/CD" .context8/AGENT_CONTEXT.md
# Debe mostrar la nueva entrada
```

### Risks
Ninguno.

---

## Dependencies

- **External**: GitHub Actions debe estar habilitado en el repo `fnhernandorena/agents_prompts`. Si no lo está, pedir al usuario que lo active.
- **Internal**: Step 5 (CI/CD) depende de Steps 1, 2, 4 — pero no bloqueante, los workflows pueden existir aunque fallen hasta que los pasos anteriores estén listos.

## Files to Modify

| File | Change type | Notes |
|------|-------------|-------|
| `pyproject.toml` | modify | Añadir ruff config + pytest dev dep |
| `install.py` | modify | Ruff fixes (cosmetic) |
| `sync-skills.py` | create | Nuevo script de sincronización |
| `tests/test_install.py` | create | Tests unitarios para install.py |
| `.github/workflows/ci.yml` | create | CI workflow |
| `.github/workflows/release.yml` | create | Release workflow |
| `CHANGELOG.md` | create | Historial de versiones |
| `.context8/architecture/module_map.md` | modify | Quitar tag "[Future]" de generators |
| `.context8/AGENT_CONTEXT.md` | modify | Actualizar testing, CI/CD, Hermes, versioning |

## Test Plan

- [x] (Step 2) Tests unitarios para `install.py` con pytest
- [x] (Step 1) `ruff check .` pasa sin errores
- [x] (Step 4) `sync-skills.py --check` en CI detecta skills desincronizados
- [x] (Step 5) CI workflow corre en cada PR: lint + test + sync-check
- [x] (Step 5) Release workflow se activa con tag `v*`
- [ ] **Manual**: push a branch + verificar GitHub Actions corre
- [ ] **Manual**: git tag v1.0.1 + push --tags + verificar Release creada

## Progress Log
(filled in during implementation)

## Decisions Made
(filled in during implementation)

## Blockers
(filled in during implementation)
