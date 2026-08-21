# Task: Task Compacting Skill — Archive Old Tasks with Summaries

**Date**: 2026-06-20
**Status**: Planned
**Branch**: feat/task-compacting-skill
**Estimated total complexity**: medium

## Objective

Crear una skill `task-compacting` que archive las tareas completadas/canceladas viejas de `.context8/tasks/` a un subdirectorio `.context8/tasks/archive/` y genere resúmenes por mes (un párrafo por tarea) para que un LLM tenga un overview de qué pasó sin tener que leer los archivos individuales.

Esto resuelve la degradación de señal/ruido en `.context8/tasks/` cuando se acumulan decenas de tareas completadas.

## Acceptance Criteria

- [ ] `skills/task-compacting/SKILL.md` con frontmatter completo y fases estructuradas (Pattern B — Workflow Skill)
- [ ] La skill escanea `.context8/tasks/` e identifica tareas con status "Complete" o "Cancelled"
- [ ] Opción de filtro por antigüedad (default: >30 días desde last-modified del archivo)
- [ ] Mueve los archivos de tarea a `.context8/tasks/archive/<nombre>.md` — renombra si hay colisión
- [ ] Genera/actualiza resúmenes mensuales en `.context8/tasks/archive/YYYY-MM-summary.md`
- [ ] Cada resumen mensual contiene un párrafo por tarea con: título, estado final, objetivo (1-2 frases), resultado/decisiones clave
- [ ] Las tareas activas (status "Planned" o "In progress") NO se tocan
- [ ] Modo `--dry-run` para previsualizar qué se archivaría sin mover nada
- [ ] Modo `--force` para archivar aunque el threshold no se haya cumplido
- [ ] Update `install.py` para registrar el nuevo skill
- [ ] Skill listada en `AGENTS.md` bajo "### Tasks"
- [ ] Skill listada en `CLAUDE.md` bajo "### Tasks"
- [ ] Sync a `~/.hermes/skills/dev-workflows/task-compacting/` para Hermes

## Out of Scope

- Modificar el formato de los task files existentes
- Archivar tareas de otros proyectos fuera del repo actual
- Borrar archivos (solo mover a archive/)
- Interferir con `task-continue` o resumption de tareas planificadas
- Multi-repo workspace support (fase futura, no ahora)

## Unknowns & Risks

| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| Puede haber task files sin status explícito en el frontmatter | medium | La skill debe detectar ausencia de status y preguntar, o saltar ese archivo |
| El resumen puede ser impreciso si el task file no tiene Objective claro | medium | Usar heurística: first line after "## Objective", o fallback a title + first paragraph |
| Threshold de 30 días puede no ser apropiado para todos los proyectos | low | Hacerlo configurable con flag `--older-than N` (default 30) |
| Nombres de archivo duplicados al mover a archive/ | low | Añadir sufijo numérico si el destino ya existe |

## Implementation Plan

### Step 1: Crear skills/task-compacting/SKILL.md

**Files**: `skills/task-compacting/SKILL.md` (create)
**Depends on**: none
**Estimated complexity**: medium
**Reversible**: yes

#### What
Crear el archivo SKILL.md completo siguiendo Pattern B (Workflow Skill) con:

- Frontmatter YAML (name, description, version, author, license, metadata)
- Overview explicando qué hace y por qué
- When to use / When NOT to use
- Output description
- Full prompt con fases:
  - **Phase 1 — Scan**: Listar task files y leer status
  - **Phase 2 — Filter**: Identificar candidatos a archivar (Complete/Cancelled + threshold)
  - **Phase 3 — Review**: Mostrar candidatos al usuario, pedir confirmación
  - **Phase 4 — Archive**: Mover archivos a `archive/`, manejar colisiones
  - **Phase 5 — Summarize**: Leer cada tarea archivada, generar/actualizar resumen mensual
  - **Phase 6 — Commit**: git add + commit de los cambios
- Completion Checklist
- Rules

Formato de cada párrafo en el resumen mensual:
```markdown
- **[Task Title]** — Status: Complete. [Objetivo en 1-2 frases]. [Decisiones clave o resultado].
```

#### Why
El core de la skill. Sin el SKILL.md no hay nada que implementar.

#### How to verify
```bash
cat skills/task-compacting/SKILL.md | head -10
# Debe mostrar frontmatter válido con name y description
```

#### Risks
Ninguno.

---

### Step 2: Registrar en install.py

**Files**: `install.py` (modify)
**Depends on**: Step 1
**Estimated complexity**: trivial
**Reversible**: yes

#### What
Añadir `task-compacting` a la lista SKILLS en `install.py` (alfabéticamente).

#### Why
`install.py` es el inventario central de skills empaquetadas.

#### How to verify
```bash
grep "task-compacting" install.py
# Debe mostrar la entrada
```

#### Risks
Ninguno.

---

### Step 3: Actualizar AGENTS.md y CLAUDE.md

**Files**: `AGENTS.md` (modify), `CLAUDE.md` (modify)
**Depends on**: Step 1
**Estimated complexity**: trivial
**Reversible**: yes

#### What
Añadir entrada bajo "### Tasks" en ambos archivos:
```
- `dev-workflows:task-compacting` — archive completed/cancelled tasks with monthly summaries
```

#### Why
Los usuarios descubren skills a través de estos índices.

#### How to verify
```bash
grep "task-compacting" AGENTS.md CLAUDE.md
# Ambas líneas presentes
```

#### Risks
Ninguno.

---

### Step 4: Validar SKILL.md localmente

**Files**: `skills/task-compacting/SKILL.md`
**Depends on**: Step 1
**Estimated complexity**: trivial
**Reversible**: yes

#### What
Ejecutar validación del frontmatter:
```python
import yaml, re
content = open("skills/task-compacting/SKILL.md").read()
assert content.startswith("---")
m = re.search(r'\n---\s*\n', content[3:])
fm = yaml.safe_load(content[3:m.start()+3])
assert "name" in fm and "description" in fm
assert len(fm["description"]) <= 1024
assert len(content) <= 100_000
```

#### Why
Garantiza que el SKILL.md pasa los chequeos del validador de Hermes.

#### How to verify
Script corre sin errores.

#### Risks
Ninguno.

---

### Step 5: Sync a Hermes y commit final

**Files**: `~/.hermes/skills/dev-workflows/task-compacting/`
**Depends on**: Step 1-4
**Estimated complexity**: trivial
**Reversible**: no (pero el commit puede revertirse)

#### What
```bash
mkdir -p ~/.hermes/skills/dev-workflows/
cp -r skills/task-compacting ~/.hermes/skills/dev-workflows/task-compacting/
git add skills/task-compacting/ install.py AGENTS.md CLAUDE.md
git commit -m "feat(skills): add task-compacting skill — archive old tasks with monthly summaries"
```

#### Why
Sin este paso, la skill existe solo en el repo pero Hermes no la carga.

#### How to verify
```bash
ls ~/.hermes/skills/dev-workflows/task-compacting/SKILL.md
# Existe
```

#### Risks
Ninguno.

---

## Dependencies

- **Internal**: Steps 2-5 dependen de Step 1 (SKILL.md)
- **External**: Ninguna

## Files to Modify

| File | Change type | Notes |
|------|-------------|-------|
| `skills/task-compacting/SKILL.md` | create | Core skill |
| `install.py` | modify | Añadir a lista SKILLS |
| `AGENTS.md` | modify | Añadir bullet bajo Tasks |
| `CLAUDE.md` | modify | Añadir bullet bajo Tasks |

## Test Plan

- [ ] Validar frontmatter (Step 4 — script inline)
- [ ] `python -c "import yaml; yaml.safe_load(open('skills/task-compacting/SKILL.md').read().split('---')[1])"` — YAML parsea sin error
- [ ] Ejecución manual: correr la skill en este repo y verificar que archiva tareas viejas + genera summary
- [ ] Verificar que tasks activas (Planned) no se tocan

## Progress Log
(filled in during implementation)

## Decisions Made
(filled in during implementation)

## Blockers
(filled in during implementation)
