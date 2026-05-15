# agents_prompts

Colección de prompts de bootstrap para agentes de IA (Claude Code y similares). Cada prompt es un protocolo de arranque que le dice al agente qué leer, en qué orden, y cómo estructurar su trabajo antes de tocar código.

## Problema que resuelve

Un agente sin contexto inicial improvisa: lee archivos al azar, omite convenciones, mezcla decisiones con implementación, y deja rastros inconsistentes entre sesiones. Estos prompts eliminan ese problema forzando una secuencia reproducible de orientación → documentación → trabajo.

## Prompts disponibles

### `project.md` — Bootstrap de proyecto nuevo
Úsalo la **primera vez** que un agente trabaja en un repositorio.

- Explora estructura, config, git, CI/CD, tests, entry points.
- Construye modelo mental: stack, arquitectura, patrones, convenciones.
- Crea `md_docs/` con documentación completa y autosuficiente.
- Genera `AGENT_CONTEXT.md` (referencia permanente), `AGENT_SYSTEM_PROMPT.md` (listo para pegar), arquitectura, infraestructura, mapa de módulos.

**Regla**: no toca código. Solo documenta lo que existe.

---

### `session.md` — Bootstrap de sesión de trabajo
Úsalo al **inicio de cada sesión** en un repo ya documentado.

- Verifica git status, rama, cambios locales.
- Carga `md_docs/AGENT_CONTEXT.md` y docs de arquitectura relevantes.
- Crea o retoma un task file en `md_docs/tasks/`.
- Establece reglas de trabajo: código, git, tests, documentación.
- Checklist de cierre: criterios cumplidos, tests pasando, commits semánticos, docs actualizados.

**Regla**: no empieza el task hasta completar los 3 primeros phases.

---

### `workspace.md` — Bootstrap de workspace multi-repo
Úsalo cuando la carpeta raíz contiene **múltiples repos independientes** (ej: `proyecto_a/front_a` + `proyecto_a/back_a`).

- Descubre automáticamente qué subdirectorios son repos git.
- Crea `md_docs/` raíz: solo índice, WORKSPACE_OVERVIEW y tareas globales. No duplica contenido de repos hijos.
- Por cada repo hijo: ejecuta exploración completa y crea su propio `md_docs/` autosuficiente.
- Cada AGENT_CONTEXT.md hijo incluye sección "Workspace Relationships" con relaciones inter-repo.

**Regla**: docs raíz = navegación global. Docs por repo = totalmente autocontenidos.

---

### `task_plan.md` — Planificación detallada de task
Úsalo cuando necesitas un **plan antes de implementar** — features complejas, cambios cross-módulo, refactors con riesgo.

- Carga contexto de `md_docs/`.
- Fuerza responder: qué se pide, por qué importa, qué es "done", qué está fuera de scope, qué es desconocido.
- Recon de codebase acotada al task: archivos afectados, callers, tests existentes, git history.
- Genera plan paso a paso: cada step con archivos, dependencias, complejidad, cómo verificar, riesgos.
- Escribe task file completo en `md_docs/tasks/` con criterios de aceptación, tabla de archivos, plan de tests.

**Regla**: no escribe código de aplicación. Output es solo el task file.

---

## Estructura de docs generada

```
[repo]/
└── md_docs/
    ├── README.md                  # Índice para agentes
    ├── AGENT_CONTEXT.md           # Contexto completo del proyecto
    ├── AGENT_SYSTEM_PROMPT.md     # System prompt listo para pegar
    ├── PROJECT_OVERVIEW.md        # Resumen de 1 página
    ├── architecture/
    │   ├── data_flow.md
    │   ├── key_patterns.md
    │   ├── module_map.md
    │   └── infrastructure.md
    └── tasks/
        └── YYYY-MM-DD_descripcion.md
```

Para workspace multi-repo, `md_docs/` raíz agrega `WORKSPACE_OVERVIEW.md`.

## Flujo recomendado

```
Repo nuevo          →  project.md  →  genera md_docs/
Sesión de trabajo   →  session.md  →  retoma desde md_docs/
Task complejo       →  task_plan.md → genera tasks/YYYY-MM-DD_*.md
Multi-repo          →  workspace.md → genera md_docs/ raíz + md_docs/ por repo
```

## Convenciones

- Toda documentación generada en **inglés**.
- Nunca documenta lo que debería existir, solo lo que existe.
- Nunca escribe valores reales de `.env` en ningún archivo.
- Los task files siguen formato semántico: `type(scope): descripción`.
