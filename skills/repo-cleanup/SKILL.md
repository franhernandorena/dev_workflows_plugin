---
name: repo-cleanup
version: 1.0.0
description: Revisa ramas del repositorio, limpia automáticamente las propias mergeadas y pide permiso antes de tocar ramas ajenas. Mantiene .context8/repo-branches.md con las convenciones del proyecto.
---

# Repo Cleanup — Limpieza Segura de Ramas Git

## Overview

Escanea ramas del repositorio, clasifica por autoría, y limpia de forma segura:
ramas propias mergeadas se borran automáticamente con `git branch -d`; ramas
ajenas mergeadas requieren permiso explícito. Mantiene un archivo de referencia
(`.context8/repo-branches.md`) con las ramas protegidas, tags, y patrones
detectados, que otras skills (task-do, deploy-plan, release) pueden consultar.

## Cuando usar

- Periódicamente para mantener limpio el repositorio local
- Después de mergear varios PRs
- Antes de empezar una nueva feature (para evitar confusión de ramas viejas)
- Cualquier sesión de mantenimiento de git

## Cuando NO usar

- En repositorios donde no tienes permisos de escritura
- En medio de un rebase o merge conflict sin resolver
- Si hay cambios sin commitear (el stash no protege contra branch -d)

## Output

- Ramas propias mergeadas eliminadas
- `.context8/repo-branches.md` creado o actualizado
- Reporte inline con resumen de acciones tomadas, pendientes de aprobación, y ramas no mergeadas

## Full Prompt

# REPO CLEANUP — Limpieza Segura de Ramas

## Regla: Siempre usar `-d` (seguro). `-D` solo con aprobación explícita del usuario.

---

## Fase 1 — Cargar Convenciones del Repositorio

### 1.1 Identificar usuario git

```bash
GIT_USER_NAME=$(git config user.name)
GIT_USER_EMAIL=$(git config user.email)
echo "Usuario: $GIT_USER_NAME <$GIT_USER_EMAIL>"
```

### 1.2 Crear o leer `.context8/repo-branches.md`

```bash
mkdir -p .context8
```

Si el archivo no existe, créalo con la siguiente estructura. Si existe,
cárgalo para respetar las convenciones ya documentadas.

```markdown
# Repo Branches — Convenciones de Ramas y Tags

## Protected Branches
Lista de ramas que NUNCA se borran. Detectadas automáticamente.

- `main`
- `develop`
- [añadir otras detectadas]

## Git User
- **Name**: [git config user.name]
- **Email**: [git config user.email]

## Branch Naming Patterns
Patrones detectados en ramas existentes (para clasificar autoría).

- `fran/*` — ramas del usuario principal

## Tags
| Tag | Fecha | Propósito |
|-----|-------|-----------|
| v1.0.0 | 2024-01-01 | Primer release |

## Histórico de Limpiezas
| Fecha | Ramas eliminadas | Ramas pendientes |
|-------|-----------------|------------------|
| YYYY-MM-DD | N | M |

## Notas
[Información adicional sobre el flujo de ramas del proyecto.]
```

### 1.3 Detectar default branch y otras protegidas

```bash
# Default branch (main o master)
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@.*/@@' || echo "main"

# Todas las ramas con commits de 2+ personas = protegidas candidatas
```

### 1.4 Listar tags existentes

```bash
git tag --sort=-creatordate | head -20
```

Para cada tag, registrar propósito:
```bash
git log --oneline <tag> -1
```

Si el tag no está documentado en `.context8/repo-branches.md`, añadirlo.

---

## Fase 2 — Listar y Clasificar Ramas

### 2.1 Ramas mergeadas en cada protected branch

```bash
for branch in main develop; do
  echo "=== Mergeadas en $branch ==="
  git branch --merged "$branch" | grep -v "^\*\|^  $branch$" | sed 's/^..//'
done
```

### 2.2 Fetch remoto para detectar ramas ya eliminadas upstream

```bash
git fetch --prune 2>&1 || true
```

### 2.3 Clasificar por autoría

Para cada rama mergeada (excluyendo protected branches):

- Obtener autores únicos de los commits de la rama:
  ```bash
  git log origin/main..<branch> --format="%an <%ae>" | sort -u
  ```
  o, si la rama ya está fully mergeada, usar `git log` con un rango
  apropiado.

- **Propia**: todos los commits son de `$GIT_USER_NAME` / `$GIT_USER_EMAIL`
- **Ajena**: cualquier commit de otra persona
- **Sin autor claro**: considerar ajena (más seguro)

---

## Fase 3 — Limpiar Ramas Propias Mergeadas

### 3.1 Para cada rama propia mergeada en `main` o `develop`:

```bash
git branch -d <branch>
```

Confirmar que se eliminó:
```bash
git branch -a | grep <branch> || echo "Eliminada correctamente"
```

Notificar al usuario:
`→ Eliminada: <branch> (propia, mergeada)`

### 3.2 Manejo de errores

Si `git branch -d` falla porque la rama no está fully merged:
- Verificar manualmente con `git merge-base --is-ancestor <branch> <protected>`
- Si realmente no está mergeada: mover a la lista de "no mergeadas" (Fase 5)
- Si está mergeada pero git no lo reconoce (merge complejo): listar como pendiente

---

## Fase 4 — Ramas Ajenas Mergeadas (Pedir Permiso)

### 4.1 Mostrar ramas ajenas mergeadas

Listar cada rama ajena mergeada con su autor principal y fecha del último commit:

```bash
git log --format="%an <%ae> — %ci" <branch> -1 | head -1
```

### 4.2 Pedir permiso explícito

Presentar al usuario:

```
═══ Ramas ajenas mergeadas — requieren aprobación ═══
  1. feature/xyz  (autor: otro@dev.com, último commit: 2024-03-01)
  2. fix/abc      (autor: otro@dev.com, último commit: 2024-02-15)
  3. ...

¿Qué quieres hacer?
  [número(s)] — eliminar ramas específicas (con -d seguro)
  all          — eliminar todas (con -d seguro)
  force <n>    — eliminar con -D (forzado, solo si falla -d)
  skip         — no eliminar ninguna, dejar como está
  review <n>   — abrir revisión de la rama antes de decidir
```

NO ejecutar ninguna acción sin respuesta del usuario.

Si el usuario autoriza:

```bash
git branch -d <branch>
```

Si `-d` falla y el usuario pidió `force`:

```bash
git branch -D <branch>
```

---

## Fase 5 — Ramas No Mergeadas (Solo Informativo)

### 5.1 Listar ramas no mergeadas en ninguna protected branch

```bash
git branch --no-merged main
git branch --no-merged develop
```

### 5.2 Calcular antigüedad

```bash
git log --format="%ci" <branch> -1
```

### 5.3 Mostrar resumen informativo

```
═══ Ramas no mergeadas (NO se tocan) ═══
  - fix/wip          (último commit: 2024-06-10 — 7 días atrás)
  - experiment/foo   (último commit: 2024-03-01 — 108 días atrás)
```

No ofrecer borrarlas. Solo informar. Si el usuario pregunta por alguna,
entonces discutir.

---

## Fase 6 — Actualizar `.context8/repo-branches.md`

### 6.1 Actualizar protected branches

Si se descubrieron nuevas ramas protegidas durante la ejecución,
añadirlas al archivo.

### 6.2 Añadir nuevos tags detectados

Cualquier tag que no estuviera documentado en fase 1, añadirlo con
su propósito inferido del mensaje del commit.

### 6.3 Registrar el histórico de limpieza

Añadir una fila a la tabla **Histórico de Limpiezas**:

```
| YYYY-MM-DD | N propias eliminadas, N ajenas pendientes | N |
```

### 6.4 Hacer commit del archivo actualizado

```bash
git add .context8/repo-branches.md
git commit -m "docs(repo-branches): actualizar tras limpieza de ramas"
```

---

## Completion Checklist

- [ ] `.context8/repo-branches.md` existe con protected branches, tags y user identity
- [ ] Ramas propias mergeadas eliminadas con `-d`
- [ ] Ramas ajenas mergeadas: preguntado al usuario (aprobado o diferido)
- [ ] Ramas no mergeadas listadas informativamente
- [ ] Histórico de limpieza actualizado
- [ ] No se usó `-D` sin autorización explícita
- [ ] Protected branches intactas

---

## Rules

- **Siempre** `git branch -d` (seguro). `-D` solo con permiso explícito del usuario.
- **Nunca** borrar protected branches (main, develop, y las documentadas).
- **Nunca** borrar ramas ajenas sin preguntar.
- **Siempre** notificar al usuario las acciones tomadas.
- **Nunca** tocar ramas no mergeadas — solo informar de su existencia.
- Si el usuario dice "skip" en fase 4, dejar todas las ramas ajenas como están.
- Escribir toda la documentación en español.
