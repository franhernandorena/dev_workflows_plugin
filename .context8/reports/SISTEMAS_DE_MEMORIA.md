# Comparativa 3-Vías: dev_workflows_plugin vs Superpowers vs context-mode

**Versión**: 2.0 (tres sistemas, sinergia y convergencia)
**Última actualización**: 2026-06-17
**Autor**: Francisco Hernandorena
**Estado**: Final

---

> 📋 **ClickUp Docs**: usa `/toc` para tabla de contenidos automática. Los diagramas Mermaid requieren render externo.

---

## 1. Resumen Ejecutivo

Este documento compara **tres sistemas** que operan en el ecosistema de desarrollo con agentes de IA:


| Sistema                  | Qué es                                             | Creado por                                                                              |
| ------------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **dev_workflows_plugin** | Plugin de skills para ciclo de vida del desarrollo | Francisco Hernandorena                                                                  |
| **Superpowers**          | Framework de skills + metodología de desarrollo    | Prime Radiant (Jesse Vincent) — [obra/superpowers](https://github.com/obra/superpowers) |
| **context-mode**         | Plugin de memoria automática                       | Nous Research                                                                           |


**Conclusión anticipada**: Los tres sistemas **convergen** en objetivos y se **complementan** en capacidades. Ninguno reemplaza a los otros — juntos cubren el espectro completo: metodología de desarrollo (Superpowers) + ciclo de vida y contexto externo (dev_workflows_plugin) + memoria persistente automática (context-mode).

> La redundancia entre dev_workflows_plugin y Superpowers no es un problema — es una **fortaleza**: ambos atacan el mismo problema desde ángulos distintos, y sus solapamientos permiten elegir la herramienta adecuada para cada momento.

---

## 2. Los Tres Sistemas en Detalle

### 2.1 dev_workflows_plugin

**Repositorio**: [github.com/franhernandorena/dev_workflows_plugin](https://github.com/franhernandorena/dev_workflows_plugin) 

**Harness**: Claude code, Opencode, Codex, Antigravity, Cursor, etc
**Filosofía**: Prompts estructurados para cada etapa del desarrollo, con foco en continuidad de sesión y contexto de proyecto.

#### Skills (20+)


| Categoría      | Skills                                                                                                          |
| -------------- | --------------------------------------------------------------------------------------------------------------- |
| **Workflows**  | workflow-init, workflow-continue, workflow-add-repo, workflow-status                                            |
| **Proyectos**  | project-init, project-continue, project-handoff, project-audit, project-review                                  |
| **Tareas**     | task-plan, task-do, task-continue, task-review, task-hotfix                                                     |
| **GitHub**     | github-code-review, github-pr-workflow, github-issues, github-repo-management, github-auth, codebase-inspection |
| **CI/CD**      | deploy-plan, release, tag-create, repo-cleanup                                                                  |
| **Análisis**   | change-impact, dependency-audit                                                                                 |
| **Documentos** | make-report                                                                                                     |


#### Flujo principal

```
project-audit → project-init → project-continue
                                     ↓
                              task-plan → task-do → task-review
                                                       ↓
                                                 task-hotfix (prod)
                                     ↓
                              project-handoff (próximo agente)
```

#### Fortalezas únicas

- Ciclo de **sesión completo**: init → continue → handoff
- **Multi-repo** workspaces
- **GitHub** integration (PRs, issues, code review)
- **CI/CD**: PIPELINES.md, REPO_BRANCHES.md, deploy-plan, release
- **Análisis de impacto**: change-impact, dependency-audit
- **Estado persistente**: `.context8/tasks/*.md` + `.context8/` completo
- **Handoff entre agentes**: estado congelado para retomar después

#### Gaps que cubren los otros sistemas

- ❌ Sin brainstorming estructurado → lo cubre **Superpowers**
- ❌ Sin TDD forzado → lo cubre **Superpowers**
- ❌ Sin subagentes nativos → lo cubre **Superpowers**
- ❌ Sin captura automática de memoria → lo cubre **context-mode**

---

### 2.2 Superpowers (obra/superpowers)

**Repositorio**: [github.com/obra/superpowers](https://github.com/obra/superpowers)
**Creador**: Jesse Vincent (Prime Radiant)
**Harnesses**: Claude Code, Codex CLI/App, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, Antigravity, Pi (10+)
**Filosofía**: "Tu agente es un ingeniero júnior entusiasta pero sin disciplina. Ponle guardas de proceso."

#### Skills (14+)


| Skill                          | Propósito                                       |
| ------------------------------ | ----------------------------------------------- |
| brainstorming                  | Refinamiento Socrático de ideas antes de código |
| writing-plans                  | Desglose en tareas de 2-5 min con verificación  |
| subagent-driven-development    | Subagente fresco por tarea + revisión 2-etapas  |
| executing-plans                | Ejecución batch con checkpoints humanos         |
| test-driven-development        | RED-GREEN-REFACTOR obligatorio                  |
| using-git-worktrees            | Workspace aislado en rama separada              |
| requesting-code-review         | Pre-review checklist + issues por severidad     |
| receiving-code-review          | Responder a feedback                            |
| finishing-a-development-branch | Verificar tests, cerrar rama                    |
| systematic-debugging           | 4 fases root cause                              |
| dispatching-parallel-agents    | Workflows concurrentes                          |
| verification-before-completion | Asegurar fix real                               |
| writing-skills                 | Crear nuevas skills                             |
| using-superpowers              | Intro al sistema                                |


#### Flujo

```
brainstorming → writing-plans → git-worktrees → TDD → code-review → finishing-branch
                                                    ↓
                                          subagent-driven-development
```

#### Fortalezas únicas

- **Brainstorming Socrático**: refina ideas antes de codificar
- **TDD forzado**: no hay código sin test fallido primero
- **Subagentes**: cada tarea se delega con revisión independiente
- **Git worktrees**: aislamiento total de rama
- **Auto-triggering**: el agente DEBE revisar skills antes de cada acción
- **Multi-harness**: funciona en 10+ plataformas

#### Gaps que cubren los otros sistemas

- ❌ Sin ciclo de sesión / continuidad → lo cubre **dev_workflows_plugin**
- ❌ Sin contexto GitHub → lo cubre **dev_workflows_plugin**
- ❌ Sin CI/CD → lo cubre **dev_workflows_plugin**
- ❌ Sin multi-repo → lo cubre **dev_workflows_plugin**
- ❌ Sin captura automática de memoria → lo cubre **context-mode**

---

### 2.3 context-mode plugin

**Repositorio**: [github.com/mksglu/context-mode](https://github.com/mksglu/context-mode)
**Harnesses**: Claude Code, Codex CLI/App, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, Antigravity, Pi (10+)
**Filosofía**: Zero-effort — captura todo automáticamente sin que el agente tenga que acordarse.

#### Mecanismo

- Hooks `PostToolUse` se disparan tras cada tool call
- Extraen eventos clasificados del input/output
- Se almacenan en SQLite global (SessionDB)
- Se recuperan con `ctx_search` y `sort: "timeline"`

#### Categorías de eventos (26 tipos)


| Categoría                    | Captura                                   |
| ---------------------------- | ----------------------------------------- |
| `decision`                   | Correcciones del usuario, preferencias    |
| `error` / `error-resolution` | Fallos + soluciones                       |
| `blocker`                    | Obstáculos encontrados                    |
| `plan`                       | Planes creados                            |
| `user-prompt`                | Prompts del usuario                       |
| `rejected-approach`          | Enfoques descartados                      |
| `constraint`                 | Restricciones establecidas                |
| `tool-failure`               | Errores de herramientas                   |
| *(18 más)*                   | Latencia, archivos leídos, comandos, etc. |


#### Herramientas


| Tool                  | Uso                                        |
| --------------------- | ------------------------------------------ |
| `ctx_search`          | Búsqueda BM25 sobre todo el knowledge base |
| `ctx_index`           | Indexar contenido nuevo                    |
| `ctx_fetch_and_index` | Fetch + index de URLs                      |
| `ctx_insight`         | Dashboard web de sesiones                  |
| `ctx_purge`           | Limpieza por sesión o global               |
| `ctx_stats`           | Estadísticas de consumo de contexto        |


#### Fortalezas únicas

- **Captura automática**: sin intervención del agente ni del usuario
- **Timeline histórico**: búsqueda entre sesiones
- **Dashboard visual**: `ctx_insight` para métricas
- **26 tipos de eventos**: cubre decisiones, errores, planes, etc.

#### Gaps que cubren los otros sistemas

- ❌ Sin metodología de desarrollo → lo cubre **Superpowers**
- ❌ Sin ciclo de proyecto / sesión → lo cubre **dev_workflows_plugin**
- ❌ Sin GitHub / CI/CD → lo cubre **dev_workflows_plugin**
- ❌ Sin brainstorming / TDD → lo cubre **Superpowers**

---

## 3. Tabla Comparativa 3-Vías


| Aspecto                   | dev_workflows_plugin                | Superpowers                | context-mode         |
| ------------------------- | ----------------------------------- | -------------------------- | -------------------- |
| **Tipo**                  | Skills ciclo de vida + GitHub/CI-CD | Framework metodológico     | Memoria automática   |
| **Skills**                | 20+                                 | 14+                        | N/A (hooks)          |
| **Harness principal**     | Claude Code (10+)                   | Claude Code (10+)          | Claude Code (10+)    |
| **Auto-triggering**       | ❌ Carga explícita                   | ✅ Obligatorio              | ✅ Automático (hooks) |
| **Brainstorming**         | ❌                                   | ✅                          | ❌                    |
| **TDD forzado**           | ❌                                   | ✅                          | ❌                    |
| **Subagentes**            | ❌ (usa delegate_task)               | ✅ Nativo                   | ❌                    |
| **Git worktrees**         | ❌                                   | ✅                          | ❌                    |
| **Ciclo sesión**          | ✅ init → continue → handoff         | ❌                          | ✅ (timeline)         |
| **Multi-repo**            | ✅                                   | ❌                          | ❌                    |
| **GitHub PRs**            | ✅                                   | ❌                          | ❌                    |
| **GitHub Issues**         | ✅                                   | ❌                          | ❌                    |
| **Code review**           | ✅ (task-review + github)            | ✅ (requesting-code-review) | ❌                    |
| **CI/CD pipelines**       | ✅ PIPELINES.md                      | ❌                          | ❌                    |
| **Releases / tags**       | ✅                                   | ❌                          | ❌                    |
| **Deploy plan**           | ✅                                   | ❌                          | ❌                    |
| **Análisis impacto**      | ✅ change-impact                     | ❌                          | ❌                    |
| **Captura automática**    | ❌                                   | ❌                          | ✅ 26 tipos eventos   |
| **Timeline histórico**    | ❌ (solo task files)                 | ❌                          | ✅ ctx_search         |
| **Dashboard**             | ❌ (reportes markdown)               | ❌                          | ✅ ctx_insight        |
| **Handoff entre agentes** | ✅                                   | ❌                          | ❌                    |
| **Multi-harness**         | ✅ 10                                | ✅ 10+                      | ✅ 10                 |


---

## 4. La Ventaja Diferencial de dev_workflows_plugin

Hay dos áreas donde dev_workflows_plugin es **objetivamente superior** y sus competidores no se acercan:

### 4.1 Detalle de Tareas


| Aspecto          | dev_workflows_plugin                                                | Superpowers (writing-plans)    | context-mode                           |
| ---------------- | ------------------------------------------------------------------- | ------------------------------ | -------------------------------------- |
| **Formato**      | Archivo `.context8/tasks/<id>.md`                                   | Plan inline en la conversación | Evento en SQLite                       |
| **Contenido**    | Estado, progreso, decisiones, archivos modificados, blockers, notas | Ruta + código + verificación   | Solo metadatos del evento              |
| **Persistencia** | ✅ Perdura entre sesiones (archivo en disco)                         | ❌ Se pierde al cerrar sesión   | ✅ Persiste en SessionDB                |
| **Estructura**   | Estado + bitácora + decisiones + archivos tocados + bloqueos        | Tareas planas con verificación | Eventos planos sin estructura de tarea |
| **Búsqueda**     | `session_search` o lectura directa                                  | No hay búsqueda (inline)       | `ctx_search` timeline                  |
| **Handoff**      | ✅ Otro agente retoma exactamente donde quedó                        | ❌ No hay handoff posible       | ❌ Solo timeline, sin estado de tarea   |


**dev_workflows_plugin** no solo planifica — **trackea el estado completo** de cada tarea: qué se hizo, qué decisiones se tomaron, qué archivos se modificaron, qué bloqueos hubo. Superpowers planifica tareas de 2-5 minutos pero no preserva su estado entre sesiones. context-mode captura eventos pero no tiene concepto de "tarea".

### 4.2 Contexto General e Histórico


| Aspecto                        | dev_workflows_plugin                                                                     | Superpowers                   | context-mode                           |
| ------------------------------ | ---------------------------------------------------------------------------------------- | ----------------------------- | -------------------------------------- |
| **Estructura de proyecto**     | ✅ `.context8/` completo (AGENT_CONTEXT, REPO_BRANCHES, PIPELINES, architecture/, tasks/) | ❌ Sin estructura de proyecto  | ❌ Solo eventos planos                  |
| **Contexto GitHub**            | ✅ 6 skills + PRs/issues/repos                                                            | ❌ Nada                        | ❌ Nada                                 |
| **Contexto CI/CD**             | ✅ PIPELINES.md, deploy-plan, release                                                     | ❌ Nada                        | ❌ Nada                                 |
| **Multi-repo**                 | ✅ Workspace completo con dependencias entre repos                                        | ❌ Un repo a la vez            | ❌ Global, sin concepto de proyecto     |
| **Continuidad entre sesiones** | ✅ Handoff state congelado + `.context8/`                                                 | ❌ Cada sesión empieza de cero | ✅ Timeline pero sin estado de proyecto |
| **Decisiones de arquitectura** | ✅ Documentadas en task files + AGENT_CONTEXT                                             | ❌ Solo en conversación        | ✅ Capturadas como eventos `decision`   |
| **Historial de cambios**       | ✅ Archivos modificados por tarea, tags, releases                                         | ❌ Solo código actual          | ✅ Timeline de tools usadas             |


**dev_workflows_plugin** construye un **contexto de proyecto multidimensional**: no solo lo que pasó (timeline), sino también cómo está estructurado el proyecto, qué ramas existen, qué pipelines despliegan a qué entornos, qué decisión de arquitectura se tomó y por qué. context-mode da el "qué pasó cuándo". Superpowers da el "cómo escribir código ahora". dev_workflows_plugin da el **"dónde estamos, qué falta, cómo llegamos aquí y cómo seguir"**.

### 4.3 Sinergia: Cómo se Complementan

#### 4.3.1 Mapa de Capacidades

```
                      ┌─────────────────────────┐
                      │     context-mode         │
                      │  (memoria automática)    │
                      │                          │
                      │  • Captura 26 eventos    │
                      │  • Timeline histórico    │
                      │  • Dashboard ctx_insight │
                      └───────────┬─────────────┘
                                  │
                                  │ alimenta de contexto
                                  ▼
        ┌─────────────────────────────────────────────────┐
        │             ZONA DE CONVERGENCIA                 │
        │                                                   │
        │  ┌────────────────────┐  ┌────────────────────┐  │
        │  │ dev_workflows_     │  │   Superpowers      │  │
        │  │ plugin             │  │                    │  │
        │  │                    │  │  • Brainstorming   │  │
        │  │ • Ciclo sesión     │  │  • TDD forzado     │  │
        │  │ • GitHub PR/issues │  │  • Subagentes      │  │
        │  │ • CI/CD / releases │  │  • Git worktrees   │  │
        │  │ • Multi-repo       │  │  • Auto-triggering │  │
        │  │ • Handoff agentes  │  │  • Multi-harness   │  │
        │  └────────────────────┘  └────────────────────┘  │
        │                                                   │
        │  Ambos son frameworks de skills para desarrollo  │
        │  con solapamiento en: code-review, planificación, │
        │  ejecución, finalización de rama.                 │
        └─────────────────────────────────────────────────┘
```

### 4.2 Qué cubre cada uno

```
Necesidad                    | dev_workflows | Superpowers | context-mode
-----------------------------|:-------------:|:-----------:|:------------:
Planificar una tarea         | ✅            | ✅          | ❌
Escribir código (TDD)        | ❌            | ✅          | ❌
Revisar código               | ✅            | ✅          | ❌
Hacer brainstorming          | ❌            | ✅          | ❌
Gestionar PRs de GitHub      | ✅            | ❌          | ❌
Documentar CI/CD             | ✅            | ❌          | ❌
Hacer release                | ✅            | ❌          | ❌
Cerrar sesión para retomar   | ✅            | ❌          | ❌
Recordar decisiones pasadas  | ❌            | ❌          | ✅
Recuperar errores antiguos   | ❌            | ❌          | ✅
Dashboard de actividad       | ❌            | ❌          | ✅
Auditar proyecto existente   | ✅            | ❌          | ❌
Workspace multi-repo         | ✅            | ❌          | ❌
```

### 4.3 La redundancia es fortaleza, no problema

dev_workflows_plugin y Superpowers tienen **solapamiento en code review, planificación y ejecución**. Esto no es un bug — es una feature:

- Puedes usar **Superpowers** para el día a día (brainstorm → plan → TDD → review) y **dev_workflows_plugin** para el contexto global (GitHub, CI/CD, sesiones)
- **Superpowers** es mejor para equipos que quieren TDD y subagentes forzados
- **dev_workflows_plugin** es mejor cuando necesitas integración con GitHub, pipelines de CI/CD, y continuidad entre sesiones de agente
- Ambos pueden convivir: uno da la metodología, el otro da el contexto

---

## 5. Escenarios de Uso Combinado

### Escenario A: Desarrollo completo con los 3

```
1. context-mode captura AUTOMÁTICAMENTE todo lo que pasa
   (sin que nadie tenga que acordarse de guardar nada)

2. Superpowers o dev_workflows_plugin inician la sesión
   - Superpowers: brainstorming para refinar la idea
   - Superpowers: writing-plans planifica las tareas
   - dev_workflows: project-init si es proyecto nuevo

3. Implementación
   - Superpowers: TDD forzado - test fallido → código → test pasa
   - Superpowers: subagent-driven-development (cada tarea a subagente)
   - dev_workflows: task-do si se prefiere ejecución secuencial

4. Code review
   - Superpowers: requesting-code-review (checklist de calidad)
   - dev_workflows: github-code-review (PR con inline comments)
   - dev_workflows: github-pr-workflow (merge)

5. CI/CD y Release
   - dev_workflows: PIPELINES.md documenta triggers y entornos
   - dev_workflows: tag-create + release (versión, changelog, publish)
   - dev_workflows: deploy-plan (rollback plan)

6. Cierre de sesión
   - context-mode: ya capturó todo el timeline
   - dev_workflows: project-handoff (estado congelado próximo agente)
```

### Escenario B: Proyecto legacy sin documentación

```
1. dev_workflows: project-audit (analiza el estado del proyecto)
2. dev_workflows: dependency-audit (vulnerabilidades)
3. dev_workflows: change-impact (blast radius de cambios)
4. Superpowers: brainstorming (qué hacer con el proyecto)
5. Superpowers: writing-plans (cómo abordar los cambios)
6. context-mode: captura cada paso automáticamente
```

### Escenario C: Bug crítico en producción

```
1. context-mode: recupera sesiones anteriores del bug (ctx_search timeline)
2. dev_workflows: task-hotfix (fix controlado con fases)
3. dev_workflows: github-code-review (PR rápido)
4. dev_workflows: deploy-plan (despliegue con rollback)
5. Superpowers: verification-before-completion (confirmar fix)
6. context-mode: captura la solución para futuras referencias
```

---

## 6. Convergencia: Hacia Dónde Van

Los tres sistemas están convergiendo en dirección similar:


| Área                 | dev_workflows_plugin         | Superpowers            | context-mode         |
| -------------------- | ---------------------------- | ---------------------- | -------------------- |
| **Memoria**          | `.context8/` + tools memoria | —                      | ✅ Memoria automática |
| **Metodología**      | Fases por skill              | ✅ Metodología completa | —                    |
| **Auto-detección**   | —                            | ✅ Auto-triggering      | ✅ Hooks automáticos  |
| **Contexto externo** | ✅ GitHub + CI/CD             | —                      | —                    |
| **Multi-plataforma** | —                            | ✅ 10+ harnesses        | —                    |
| **Dashboard**        | Reportes markdown            | —                      | ✅ ctx_insight        |


---

## 7. Matriz de Capacidades Completa


| Capacidad                       | dev_workflows         | Superpowers           | context-mode    |
| ------------------------------- | --------------------- | --------------------- | --------------- |
| Brainstorming / diseño          | ❌                     | ✅                     | ❌               |
| Planificación de tareas         | ✅                     | ✅                     | ❌               |
| TDD forzado                     | ❌                     | ✅                     | ❌               |
| Code review                     | ✅                     | ✅                     | ❌               |
| Debugging estructurado          | ✅                     | ✅                     | ❌               |
| Subagentes                      | ❌ (usa delegate_task) | ✅                     | ❌               |
| Git worktrees                   | ❌                     | ✅                     | ❌               |
| Multi-repo workspaces           | ✅                     | ❌                     | ❌               |
| Ciclo de sesión (init→handoff)  | ✅                     | ❌                     | ❌               |
| Handoff entre agentes           | ✅                     | ❌                     | ❌               |
| Continuidad entre sesiones      | ✅ (.context8/)        | ❌                     | ✅ (timeline)    |
| Captura automática              | ❌                     | ❌                     | ✅ (hooks)       |
| Timeline histórico              | ❌ (solo task files)   | ❌                     | ✅ (ctx_search)  |
| Dashboard visual                | ❌ (markdown reports)  | ❌                     | ✅ (ctx_insight) |
| GitHub PRs                      | ✅                     | ❌                     | ❌               |
| GitHub Issues                   | ✅                     | ❌                     | ❌               |
| GitHub Code Review              | ✅                     | ❌                     | ❌               |
| CI/CD pipelines                 | ✅ (PIPELINES.md)      | ❌                     | ❌               |
| Releases / tags                 | ✅                     | ❌                     | ❌               |
| Deploy plan                     | ✅                     | ❌                     | ❌               |
| Análisis de impacto             | ✅ (change-impact)     | ❌                     | ❌               |
| Auditoría de dependencias       | ✅                     | ❌                     | ❌               |
| Auditoría de proyecto           | ✅                     | ❌                     | ❌               |
| Auto-triggering de skills       | ❌                     | ✅                     | ❌               |
| Multi-harness                   | ❌ ✅ (10+)             | ✅ (10+)               | ✅ (10+)         |
| Marketplace oficial             | ❌ Github              | ✅ (Anthropic, OpenAI) | ❌ Github        |
| Documentación CI/CD             | ✅                     | ❌                     | ❌               |
| Recuperación de contexto previo | ❌                     | ❌                     | ✅ (ctx_search)  |
| 26 tipos de eventos automáticos | ❌                     | ❌                     | ✅               |


---

## 8. Conclusión: Los 3 Convergen y Son Sinérgicos

**dev_workflows_plugin**, **Superpowers** y **context-mode** no compiten — **convergen** desde ángulos distintos hacia el mismo objetivo: hacer que los agentes de IA desarrollen software de forma estructurada, con contexto y con memoria.

### El aporte de cada uno

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  context-mode                                                   │
│  ─────────────                                                   │
│  "Memoria involuntaria"                                         │
│  Captura todo automáticamente.                                  │
│  Nadie tiene que acordarse de guardar nada.                     │
│                                                                 │
│         ▼ alimenta de contexto histórico ▼                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   ZONA DE CONVERGENCIA                   │   │
│  │                                                          │   │
│  │  dev_workflows_plugin         Superpowers                │   │
│  │  ─────────────────────        ──────────                 │   │
│  │  "Contexto y ciclo de vida"   "Metodología y disciplina" │   │
│  │                                                          │   │
│  │  • GitHub (PRs, issues)      • Brainstorming Socrático  │   │
│  │  • CI/CD (pipelines, deploy) • TDD forzado              │   │
│  │  • Multi-repo workspaces     • Subagentes con revisión  │   │
│  │  • Ciclo init→handoff        • Auto-triggering          │   │
│  │  • Handoff entre agentes     • Multi-harness (10+)      │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Por qué funcionan juntos


| Sistema             | Aporta                                                                                                                                      | Lo que le falta                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
|                     | dev_workflows_plugin                                                                                                                        | Superpowers                                                                       |
| ---------           | :--------------------:                                                                                                                      | :-----------:                                                                     |
| **Aporta**          | GitHub, CI/CD, multi-repo, ciclo sesión, handoff + **tareas detalladas con estado** + **contexto multidimensional**                         | Brainstorming, TDD, subagentes, worktrees, auto-triggering                        |
| **Lo que le falta** | Memoria automática, brainstorming, TDD                                                                                                      | Tareas detalladas persistentes, GitHub, CI/CD, ciclo sesión, contexto de proyecto |
| **Incomparable en** | ✅ **Detalle de tareas** (estado+decisiones+archivos+blockers) + **contexto general e histórico** (proyecto+GitHub+CI/CD+multi-repo+handoff) | Brainstorming Socrático + TDD forzado                                             |


> **dev_workflows_plugin es el único que trackea el estado completo de las tareas con persistencia entre sesiones y handoff entre agentes. Es el único que proporciona contexto multidimensional de proyecto (GitHub, CI/CD, multi-repo, arquitectura, decisiones). En estas áreas, es incomparable.**

### La redundancia como fortaleza

dev_workflows_plugin y Superpowers se solapan en code review, planificación y ejecución. Pero el solapamiento es solo parcial:

- **Planificación**: Superpowers (`writing-plans`) crea tareas inline de 2-5 min que se pierden al cerrar sesión. **dev_workflows_plugin** (`task-plan`) las persiste en `.context8/tasks/*.md` con estado, decisiones, archivos tocados, blockers. Para planificación detallada + persistente, **dev_workflows_plugin es superior**.
- **Code review**: Superpowers (`requesting-code-review`) es checklist genérico. **dev_workflows_plugin** (`task-review` + `github-code-review`) revisa contra el plan, analiza impacto, y publica en PRs de GitHub. Para code review conectado con GitHub, **dev_workflows_plugin es superior**.
- **Ejecución**: Superpowers usa subagentes (cada tarea a agente fresco). **dev_workflows_plugin** (`task-do`) ejecuta secuencial con trail de decisiones. Son enfoques diferentes para necesidades diferentes.

### Veredicto final

> **Usa los 3 juntos.** context-mode corre en segundo plano capturando todo sin esfuerzo. dev_workflows_plugin gestiona el ciclo de vida del proyecto, tareas detalladas con estado persistente, GitHub y CI/CD — es **el núcleo del contexto y la continuidad**. Superpowers aporta brainstorming Socrático, TDD forzado y subagentes cuando los necesitas. Cada uno aporta lo que los otros no tienen, y donde se solapan, dev_workflows_plugin lleva ventaja en detalle de tareas y contexto de proyecto.

---

*Reporte generado el 2026-06-17 — comparativa 3-vías con conclusión de convergencia y sinergia*