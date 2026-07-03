# Skills Posture & Conventions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bake the user's best practices (environment permissions, no auto-commit, no HH:MM, MCP-aware, code-review-graph-aware, critical posture) into the dev-workflows plugin so every agent that installs it inherits them by default.

**Architecture:** Single global `Posture & Conventions` section injected into `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` (3 files). Eight core skills (`project-continue`, `task-plan`, `task-do`, `task-continue`, `task-review`, `task-hotfix`, `task-compacting`, `change-impact`) updated structurally to follow the global posture and add `**Environment**` field to task file templates, replace `[HH:MM]` with `YYYY-MM-DD:`, and replace auto-commit with ASK-before-commit. Version bump 1.0.0 → 1.1.0.

**Tech Stack:** Markdown (skills/prompts), Python 3.11+ (installer untouched), Conventional Commits.

**Reference spec:** `docs/superpowers/specs/2026-07-01-skills-posture-conventions-design.md`

**Branch:** All work happens on a new branch `feat/skills-posture-conventions` based on `develop`. Each task ends with a commit. **The agent MUST ASK the user for explicit "go" before executing any `git commit` command.** No auto-commit.

---

## File Structure (locked-in decomposition)

| File | Action | Owner task |
|------|--------|-----------|
| `AGENTS.md` | edit (add `Posture & Conventions` section) | Task 1 |
| `CLAUDE.md` | edit (add `Posture & Conventions` section + update skill index) | Task 1, Task 10 |
| `GEMINI.md` | edit (add `Posture & Conventions` section) | Task 1 |
| `README.md` | edit (add `Posture & Conventions` summary section) | Task 2 |
| `.context8/AGENT_CONTEXT.md` | edit (register conventions of the plugin itself) | Task 3 |
| `skills/project-continue/SKILL.md` | edit (Phase 0 + template + graph) | Task 4 |
| `skills/project-continue/prompt.md` | edit (mirror of SKILL.md) | Task 4 |
| `skills/task-plan/SKILL.md` | edit (Phase 0 + graph + env field) | Task 5 |
| `skills/task-plan/prompt.md` | edit (mirror) | Task 5 |
| `skills/task-do/SKILL.md` | edit (Phase 0 + ASK-before-commit + graph) | Task 6 |
| `skills/task-do/prompt.md` | edit (mirror) | Task 6 |
| `skills/task-continue/SKILL.md` | edit (env reminder + no HH:MM) | Task 7 |
| `skills/task-continue/prompt.md` | edit (mirror) | Task 7 |
| `skills/task-review/SKILL.md` | edit (env check + graph + verdict) | Task 8 |
| `skills/task-review/prompt.md` | edit (mirror) | Task 8 |
| `skills/task-hotfix/SKILL.md` | edit (strict env gate + ASK-before-commit) | Task 9 |
| `skills/task-hotfix/prompt.md` | edit (mirror) | Task 9 |
| `skills/task-compacting/SKILL.md` | edit (no HH:MM + env grouping) | Task 10 |
| `skills/task-compacting/prompt.md` | edit (mirror) | Task 10 |
| `skills/change-impact/SKILL.md` | edit (graph primary) | Task 11 |
| `skills/change-impact/prompt.md` | edit (mirror) | Task 11 |
| `pyproject.toml` | edit (bump version) | Task 12 |
| 8 skill frontmatters (`version: 1.0.0` → `1.1.0`) | edit | Task 12 |

Total: 22 file edits, 12 tasks, 12 commits.

---

## Task 1: Add global `Posture & Conventions` section to AGENTS.md, CLAUDE.md, GEMINI.md

**Files:**
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `GEMINI.md`

- [ ] **Step 1.1: Create the new section text (single source of truth)**

The exact text below is the canonical `Posture & Conventions` section. It will be inserted at the top of each of the 3 files, after the existing `# Dev Workflows Plugin` header and any other top-of-file content, but before the existing `## Session-Start Hook` section.

Create the text as a literal block (do not paraphrase):

```markdown
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

### Commit Policy — Never Auto-Commit

The agent MUST ask before creating a commit. "ASK" here means: present the
exact `git add` + `git commit -m "<message>"` command, then wait for explicit
"yes" or "go".

- This applies to ALL commits: feature steps, doc updates, fixups, anything.
- `--no-verify`, `--amend`, force-push, and empty commits are forbidden
  unless the user wrote the exact command in their message.
- Rebase, cherry-pick, reset, and branch deletion also require explicit
  permission, even on the agent's own branches.
- Conventional Commits format is encouraged: `type(scope): description`.
  Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `perf`.
- The agent SHOULD draft commit messages but MUST NOT execute `git commit`
  without the user's go-ahead.

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

```

- [ ] **Step 1.2: Insert section in `AGENTS.md`**

Open `AGENTS.md`. Find the line `## Available Skills`. INSERT the entire
`Posture & Conventions` block (from Step 1.1) immediately BEFORE that line.
Result: the file becomes `# Dev Workflows Plugin` → `## Posture & Conventions`
(block) → `## Available Skills` → ... existing content.

- [ ] **Step 1.3: Insert section in `CLAUDE.md`**

Open `CLAUDE.md`. Find the line `## Available Skills`. INSERT the entire
`Posture & Conventions` block (from Step 1.1) immediately BEFORE that line.
Same shape as Step 1.2.

- [ ] **Step 1.4: Insert section in `GEMINI.md`**

Open `GEMINI.md`. The file is short. Find the line `## Skills` (after the
`## Session-Start Hook` block). INSERT the entire `Posture & Conventions`
block (from Step 1.1) immediately BEFORE that line. (GEMINI uses `@include`
to pull SKILL.md files — `Posture & Conventions` is part of the agent
context, not a skill include.)

- [ ] **Step 1.5: Verify the section is present in all 3 files**

Run:
```bash
grep -l "## Posture & Conventions" AGENTS.md CLAUDE.md GEMINI.md
```
Expected output: 3 file paths, one per line. If only 1 or 2 print, re-do the
missing one.

- [ ] **Step 1.6: Verify the section is placed BEFORE `## Available Skills` / `## Skills`**

Run:
```bash
for f in AGENTS.md CLAUDE.md GEMINI.md; do
  POSTURE=$(grep -n "^## Posture & Conventions" "$f" | head -1 | cut -d: -f1)
  SKILLS=$(grep -nE "^## (Available Skills|Skills)" "$f" | head -1 | cut -d: -f1)
  if [ -n "$POSTURE" ] && [ -n "$SKILLS" ] && [ "$POSTURE" -lt "$SKILLS" ]; then
    echo "OK $f: posture line $POSTURE < skills line $SKILLS"
  else
    echo "FAIL $f: posture=$POSTURE skills=$SKILLS"
  fi
done
```
Expected: 3 `OK` lines.

- [ ] **Step 1.7: Stage and ASK the user before committing**

Show the user:
```bash
git diff --stat
```
Expected: ~3 files changed, ~150 insertions per file. Present the commit
command to the user verbatim:
```
docs(plugin): add global Posture & Conventions section

Adds 5 sub-sections to AGENTS.md, CLAUDE.md, GEMINI.md:
- Environment & Permissions (dev/beta/prod matrix)
- Available Tools (caveman, ponytail, ctx-mode, code-review-graph, superpowers)
- Critical Posture (question, don't comply)
- Commit Policy (never auto-commit)
- Task File Conventions (date-only, no HH:MM)
```
Ask: "¿Puedo hacer commit con este mensaje? (yes/no)". Only on "yes" run:
```bash
git add AGENTS.md CLAUDE.md GEMINI.md
git commit -m "docs(plugin): add global Posture & Conventions section"
```

---

## Task 2: Add `Posture & Conventions` summary section to README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 2.1: Locate insertion point in README.md**

Find the line `## Rules` near the bottom of `README.md`. The new section goes
immediately BEFORE that line.

- [ ] **Step 2.2: Insert the summary section**

Use this exact text (kept short for a README — the full version lives in
AGENTS.md):

```markdown
## Posture & Conventions

The plugin ships with a global `Posture & Conventions` section that every
agent inherits after installation. The full text is in `AGENTS.md` /
`CLAUDE.md` / `GEMINI.md`. Highlights:

- **Environments** — `dev` (free), `beta` (ASK per op), `prod` (explicit
  written permission required for every action).
- **No auto-commit** — the agent drafts commit messages but always ASKS
  before executing `git commit`.
- **No timestamps in task files** — progress logs use `YYYY-MM-DD:` bullets,
  never `[HH:MM]`.
- **Critical posture** — the agent is expected to question, surface hidden
  costs, and propose alternatives before complying.
- **Use the ecosystem** — prefer `caveman`, `ponytail`, `context-mode`,
  `code-review-graph`, `superpowers`, and the other installed plugins /
  MCPs when the task fits.

```

- [ ] **Step 2.3: Verify insertion**

Run:
```bash
grep -n "^## Posture & Conventions" README.md
grep -n "^## Rules" README.md
```
Expected: `## Posture & Conventions` line number is LESS than `## Rules`.

- [ ] **Step 2.4: Stage and ASK the user before committing**

Present:
```
docs(plugin): add Posture & Conventions summary to README
```
Ask for "yes/go" before running `git commit`.

---

## Task 3: Update `.context8/AGENT_CONTEXT.md` to register the new conventions

**Files:**
- Modify: `.context8/AGENT_CONTEXT.md`

- [ ] **Step 3.1: Add a new section after the `## Core Design Patterns & Conventions` heading**

Find that heading in the file. After the last bullet under it (the line that
reads `- **Skill format**: YAML frontmatter + Overview + When to use + Output + Full Prompt`),
APPEND a new sub-section:

```markdown

### Posture & Conventions (global, inherited by all skills)

- **Environment permissions**: dev = free, beta = ASK per op, prod = explicit
  written permission. See global config.
- **No auto-commit**: agent drafts commits, never executes `git commit` without
  the user's "go".
- **No HH:MM in task files**: progress logs use `YYYY-MM-DD:` bullets only.
- **Task file template** must include `**Environment**: dev | beta | prod`.
- **Critical posture**: the agent questions, surfaces hidden costs, and proposes
  alternatives before complying — it does not just say "yes".
- **MCPs / plugins preferred**: caveman, ponytail, context-mode, code-review-graph,
  superpowers, and the rest of the ecosystem take precedence over reinventing
  equivalent logic.
```

- [ ] **Step 3.2: Verify the new sub-section is present**

```bash
grep -n "Posture & Conventions (global" .context8/AGENT_CONTEXT.md
```
Expected: one match.

- [ ] **Step 3.3: Stage and ASK the user before committing**

Present:
```
docs(agent-context): register global Posture & Conventions
```
Ask before commit. Commit message body should note this rolls into Task 1's
commit if you prefer to combine them — otherwise separate commit is fine.

Note: if you want a single combined commit for Tasks 1+2+3, amend the
previous commit instead of creating a new one. Otherwise keep separate
commits. Default: separate commits, easier to review.

---

## Task 4: Update `project-continue` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/project-continue/SKILL.md`
- Modify: `skills/project-continue/prompt.md`

- [ ] **Step 4.1: Add the Posture header at the top of `SKILL.md`**

Find the existing frontmatter end (line 5 — the `---` after `description: Use at the start of any session...`). Right after that `---`, INSERT this line as the first line of the body:

```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 4.2: Insert `Phase 0 — Environment & Posture` before `Phase 1` in `SKILL.md`**

Find the heading `## Phase 1 — Orient in the Codebase` in `SKILL.md`. INSERT
the following block immediately BEFORE that heading:

```markdown
## Phase 0 — Environment & Posture

Before doing any work, confirm the target environment and posture:

1. **Detect the environment** from the current branch, `.env.*` files, or
   any other signal. If unclear, ASK the user.
2. **State the detected environment** explicitly in 1 sentence. Example:
   "Current branch is `feat/foo` → `dev`. Confirmed?"
3. **If `prod`**: STOP. Do not start `Phase 1` until the user has written
   the exact action they want performed. "Sure, go ahead" is not enough.
4. **If `beta`**: proceed but restate the ASK-per-op rule before any
   non-read action.
5. **If `dev`**: proceed.

Record the environment in the task file: `**Environment**: dev | beta | prod`.

```

- [ ] **Step 4.3: Add code-review-graph reference in `Phase 2` of `SKILL.md`**

Find the existing `## Phase 2 — Load Project Context` heading. After the
intro line "Read in this exact order. Do not skip or reorder." INSERT a
new numbered item 4 (renumber the existing 3 if necessary, but keep the
existing 3 untouched in wording — just add a new item):

```markdown
4. **`.code-review-graph/graph.db` summary** — run via `ctx_execute` with
   `sqlite3` to read `nodes` and `edges` counts only. Do NOT dump the DB
   into conversation memory. Use the counts to anticipate blast radius
   while reading the architecture docs.
```

- [ ] **Step 4.4: Replace `[HH:MM]` with `YYYY-MM-DD:` in the task file template**

In the existing `### 3.2 Task file structure` block, find:
```
## Progress Log
- [HH:MM] Started. Reading X, Y, Z.
- [HH:MM] ...
```
Replace with:
```
## Progress Log
- YYYY-MM-DD: Started. Reading X, Y, Z.
- YYYY-MM-DD: ...
```

- [ ] **Step 4.5: Add `**Environment**` to the task file template**

In the same `### 3.2 Task file structure` block, find the field
`**Workspace**: [workspace name — only if parent workspace detected in 2.1]`
and INSERT a new field immediately BEFORE it:

```markdown
**Environment**: dev | beta | prod
```

- [ ] **Step 4.6: Apply Steps 4.1, 4.2, 4.3, 4.4, 4.5 to `prompt.md`**

`prompt.md` contains the same Phase structure as `SKILL.md` but without
the SKILL-only header. Apply identical edits to it (skip Step 4.1 because
`prompt.md` has no frontmatter to anchor on — start with Step 4.2).

- [ ] **Step 4.7: Verify both files have the new content**

```bash
grep -n "^> Posture: see" skills/project-continue/SKILL.md skills/project-continue/prompt.md
grep -n "## Phase 0 — Environment & Posture" skills/project-continue/SKILL.md skills/project-continue/prompt.md
grep -n "YYYY-MM-DD: Started" skills/project-continue/SKILL.md skills/project-continue/prompt.md
grep -n "code-review-graph/graph.db" skills/project-continue/SKILL.md
```
Expected: each command prints at least one match per file (the last one
only needs to match SKILL.md since the graph reference is in Phase 2 which
is duplicated in both).

- [ ] **Step 4.8: Stage and ASK the user before committing**

Present:
```
refactor(skills/project-continue): env gate, no HH:MM, code-review-graph aware
```
Ask for "yes/go" before `git commit`.

---

## Task 5: Update `task-plan` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/task-plan/SKILL.md`
- Modify: `skills/task-plan/prompt.md`

- [ ] **Step 5.1: Add Posture header to `SKILL.md`**

After the closing `---` of the frontmatter (line 5), INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 5.2: Insert `Phase 0 — Question first` before `Phase 1`**

Find `## Phase 1 — Load Context` in `SKILL.md`. INSERT immediately BEFORE:

```markdown
## Phase 0 — Question First

Before doing any planning work, the agent MUST:

1. Restate the task in 2-3 sentences, in its own words, including:
   - What is being asked.
   - Why it matters.
   - The target environment (`dev` / `beta` / `prod`).
2. If the task is ambiguous, STOP here. Write the interpretation and ask
   the user to confirm or correct it. Do not proceed to planning.
3. If the user has not stated the environment, ASK.

This step exists because plans based on silent assumptions are the most
common cause of wasted implementation work.

```

- [ ] **Step 5.3: Add code-review-graph step in `Phase 3 — Codebase Reconnaissance`**

Find `### 3.1 Find affected files`. The current text is:
```
grep -r "[relevant keyword]" --include="*.py" -l 2>/dev/null | head -20
```
ADD immediately AFTER the `### 3.1 Find affected files` intro (before the
bash block) a new sub-step:

```markdown
### 3.0 Consult the code-review-graph (preferred over grep for callers/imports)

```bash
# Use ctx_execute to keep the graph out of conversation memory
sqlite3 .code-review-graph/graph.db "SELECT name FROM sqlite_master WHERE type='table';"
# Then for each primary file: list its callers and importers from the graph
```
If the graph is missing or stale, fall back to `grep` per 3.1.
```

- [ ] **Step 5.4: Add `**Environment**` field to the single-repo task file template**

In `### 5.1 Single repo mode`, find the template block. INSERT a new line
immediately AFTER `**Status**: Planned`:

```markdown
**Environment**: dev | beta | prod
```

- [ ] **Step 5.5: Add `**Environment**` to the workspace root-index task file template**

In `### 5.2.1 Root-index task file`, find the template block. INSERT
immediately AFTER `**Status**: Planned`:

```markdown
**Environment**: dev | beta | prod
```

- [ ] **Step 5.6: Replace `[HH:MM]` with `YYYY-MM-DD:` in the progress log templates**

Search for any occurrence of `[HH:MM]` in `SKILL.md` and `prompt.md`:
```bash
grep -n "\[HH:MM\]" skills/task-plan/SKILL.md skills/task-plan/prompt.md
```
For each match, replace `[HH:MM]` with `YYYY-MM-DD:`. Expected matches:
- "## Progress Log" intro line "(filled in during implementation)" stays — no change.

- [ ] **Step 5.7: Apply identical edits to `prompt.md`**

`prompt.md` mirrors the SKILL.md. Apply Steps 5.2, 5.3, 5.4, 5.5, 5.6 to
`prompt.md` (skip 5.1, prompt.md has no frontmatter).

- [ ] **Step 5.8: Verify**

```bash
grep -c "Environment\*\*: dev | beta | prod" skills/task-plan/SKILL.md skills/task-plan/prompt.md
grep -c "Phase 0 — Question First" skills/task-plan/SKILL.md skills/task-plan/prompt.md
grep -c "code-review-graph" skills/task-plan/SKILL.md skills/task-plan/prompt.md
grep -c "\[HH:MM\]" skills/task-plan/SKILL.md skills/task-plan/prompt.md
```
Expected: first three print 1+ per file. Last prints 0 per file.

- [ ] **Step 5.9: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-plan): question first, env field, graph query
```
Ask for "yes/go".

---

## Task 6: Update `task-do` skill (SKILL.md + prompt.md) — biggest change

**Files:**
- Modify: `skills/task-do/SKILL.md`
- Modify: `skills/task-do/prompt.md`

- [ ] **Step 6.1: Add Posture header to `SKILL.md`**

After the closing `---` of the frontmatter, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 6.2: Insert `Phase 0 — Environment Gate` before `Phase 1`**

Find `## Phase 1 — Load Task & Context` in `SKILL.md`. INSERT immediately
BEFORE:

```markdown
## Phase 0 — Environment Gate

Read the task file's `**Environment**` field. If it is missing, ASK the
user to provide it. Then obey the matrix:

| Environment | Rule |
|-------------|------|
| `dev`       | Proceed. ASK before each commit (global rule). |
| `beta`      | Proceed. Restate the ASK-per-op rule before any non-read action. |
| `prod`      | Do not start Phase 1. Surface the task, get explicit written permission. |

`prod` is sacred. Even if the task file says `prod`, the agent must still
get a fresh "go" from the user before touching shared state.

```

- [ ] **Step 6.3: Replace auto-commit instruction in `Phase 3, step 5`**

In `### Phase 3 — Execute Each Step`, the current step 5 reads:
```
5. **Commit** if the step is a clean logical unit:
   ```bash
   git add [specific files]
   git commit -m "type(scope): short description"
   ```
```
REPLACE with:
```
5. **ASK the user before committing.** Present the exact command, then
   wait for "go":
   ```
   Proposed: git add [specific files] && git commit -m "type(scope): short description"
   Proceed? (yes/no)
   ```
   Do NOT execute `git commit` without explicit consent. See global
   `Commit Policy` in `AGENTS.md`.
```

- [ ] **Step 6.4: Add code-review-graph validation between steps**

In the same `### Phase 3` block, INSERT a new step 6 immediately AFTER the
replaced step 5 (renumber existing 6+ if any):

```markdown
6. **Validate against the code-review-graph** (non-blocking by default):
   ```bash
   sqlite3 .code-review-graph/graph.db "SELECT * FROM edges WHERE source IN ([files-changed]);"
   ```
   If the graph shows unexpected new callers/dependents, log under
   `## Blockers` in the task file and surface to the user.
```

- [ ] **Step 6.5: Convert `Phase 5.3 Final commit` to ASK-before-commit**

Find:
```
### 5.3 Final commit
```bash
git add [all relevant files]
git commit -m "type(scope): short description"
```
```
REPLACE with:
```
### 5.3 ASK before final commit
Propose:
```
Proposed: git add [all relevant files] && git commit -m "type(scope): short description"
Proceed? (yes/no)
```
Do NOT execute without explicit "yes" or "go".
```

- [ ] **Step 6.6: Convert `Phase 5.4 Open PR` to ASK-before-open with double-ASK in prod**

Find the current `### 5.4 Open PR if required` block (contains the
`gh pr create` heredoc). REPLACE the heading and intro with:

```markdown
### 5.4 ASK before opening PR

In `beta` and `dev`, a single ASK is sufficient.

In `prod`, two separate ASKs are required:
1. ASK to propose the PR content (title, body, base/head branches).
   Wait for "yes".
2. ASK to actually execute `gh pr create`. Wait for "go".

After both ASKs, run:
```

The rest of the `gh pr create` heredoc stays as-is.

- [ ] **Step 6.7: Replace `[HH:MM]` with `YYYY-MM-DD:` in progress log lines**

In `Phase 1.3` and `Phase 5.1`, find:
```
- [HH:MM] Started execution. Branch: [branch name].
```
and
```
- [HH:MM] All steps complete. Tests pass. Linting clean.
```
Replace `[HH:MM]` with `YYYY-MM-DD:` in both. Verify with:
```bash
grep -n "\[HH:MM\]" skills/task-do/SKILL.md skills/task-do/prompt.md
```
Expected: 0 matches.

- [ ] **Step 6.8: Add Hard Stop entries for new failure modes**

In the existing "Hard stops" block (search for `### Hard stops`), ADD a new
bullet at the end:

```markdown
- User did not answer an ASK within reasonable scope. Do not assume "yes".
- Environment changed mid-task (branch switched, deploy happened). Re-run
  Phase 0.
- `.code-review-graph` shows unexpected new callers of a modified symbol.
  Log under `## Blockers` and ask the user.
```

- [ ] **Step 6.9: Apply identical edits to `prompt.md`**

Apply Steps 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8 to `prompt.md` (skip 6.1).

- [ ] **Step 6.10: Verify**

```bash
grep -c "Phase 0 — Environment Gate" skills/task-do/SKILL.md skills/task-do/prompt.md
grep -c "ASK the user before committing" skills/task-do/SKILL.md skills/task-do/prompt.md
grep -c "ASK before opening PR" skills/task-do/SKILL.md skills/task-do/prompt.md
grep -c "code-review-graph" skills/task-do/SKILL.md skills/task-do/prompt.md
grep -c "\[HH:MM\]" skills/task-do/SKILL.md skills/task-do/prompt.md
```
Expected: first four print 1+ per file. Last prints 0 per file.

- [ ] **Step 6.11: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-do): ask-before-commit, env gate, no auto-merge
```
Ask for "yes/go". This is the largest skill change — review the diff with
the user carefully before committing.

---

## Task 7: Update `task-continue` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/task-continue/SKILL.md`
- Modify: `skills/task-continue/prompt.md`

- [ ] **Step 7.1: Add Posture header to `SKILL.md`**

After the frontmatter `---`, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 7.2: Insert environment reminder at the start of `Phase 1`**

Find `## Phase 1 — Find the Task`. After the `### 1.1 Locate the task file`
sub-section, INSERT a new sub-section `### 1.0 Environment reminder`:

```markdown
### 1.0 Environment reminder

Read the task file's `**Environment**` field. If `prod` or `beta`, show
a brief reminder to the user before resuming:

> Resuming in `<env>` mode — every non-read op will be ASKED per the
> global Commit Policy.

If the field is missing, ASK the user to fill it in before resuming.
```

- [ ] **Step 7.3: Replace `[HH:MM]` with `YYYY-MM-DD:` and remove "Resumed at" timestamp**

Find the `## Phase 5 — Update Task Status` block. Current text contains:
```
**Status**: In progress (resumed)
**Resumed at**: YYYY-MM-DD HH:MM
```
REPLACE `**Resumed at**: YYYY-MM-DD HH:MM` with `**Resumed at**: YYYY-MM-DD`.
Also find any other `HH:MM` references and replace with `YYYY-MM-DD`.

- [ ] **Step 7.4: Apply identical edits to `prompt.md`**

Apply Steps 7.2 and 7.3 to `prompt.md` (skip 7.1).

- [ ] **Step 7.5: Verify**

```bash
grep -c "Environment reminder" skills/task-continue/SKILL.md skills/task-continue/prompt.md
grep -c "Resumed at\*\*: YYYY-MM-DD" skills/task-continue/SKILL.md skills/task-continue/prompt.md
grep -c "\[HH:MM\]\|HH:MM" skills/task-continue/SKILL.md skills/task-continue/prompt.md
```
Expected: first two print 1+ per file. Last prints 0 per file.

- [ ] **Step 7.6: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-continue): env reminder, no HH:MM
```
Ask for "yes/go".

---

## Task 8: Update `task-review` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/task-review/SKILL.md`
- Modify: `skills/task-review/prompt.md`

- [ ] **Step 8.1: Add Posture header to `SKILL.md`**

After the frontmatter `---`, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 8.2: Insert `Phase 0 — Environment check` before `Phase 1`**

Find `## Phase 1 — Load Task & Diff`. INSERT immediately BEFORE:

```markdown
## Phase 0 — Environment Check

Identify the target environment of the PR. Strictness scales with it:

| Target env | Review strictness |
|------------|-------------------|
| `dev`      | Lighter. Findings are advisory. |
| `beta`     | Standard. Each finding must be addressed or explicitly waived. |
| `prod`     | Strict. Every criterion is blocking. No waivers. |

State the detected target env in the review report header.

```

- [ ] **Step 8.3: Add `Phase 1.5 — Code review graph consultation`**

Find `### 1.4 Workspace awareness` (or the end of `### 1.3 Scope creep check`).
INSERT a new sub-section `### 1.5 Code review graph consultation`
immediately AFTER `### 1.4`:

```markdown
### 1.5 Code review graph consultation

Before correctness review, query `.code-review-graph/graph.db`:

```bash
# List all callers of each modified symbol — keep the graph out of context
sqlite3 .code-review-graph/graph.db "SELECT * FROM edges WHERE source IN (modified-files);"
```

Surface in the report:
- All callers of each modified function/class.
- Files NOT in the diff but transitively affected (per the graph).
- Tests that exercise the changed code (per the graph's test edges).
```

- [ ] **Step 8.4: Add `**Target Environment**` and `**Commit / Merge Plan**` blocks to review report template**

In the `### 7. Review Report` block, find the existing template that ends
with `### Verdict / READY FOR PR / BLOCKED`. INSERT before `### Verdict`:

```markdown
### Target Environment
`dev` | `beta` | `prod` (taken from the PR base/head branches or `**Environment**`
in the task file). Strictness of the review scales with this.

### Commit / Merge Plan
Proposed sequence of actions to land this PR — listed, not executed:
- `git add [files]`
- `git commit -m "type(scope): description"`
- (if PR) `gh pr create --title ... --body ...`
- (if merge) `gh pr merge --squash` (or `--merge` / `--rebase`, your choice)

The agent MUST NOT execute any of the above. The user runs them.
```

- [ ] **Step 8.5: Change verdict wording**

Find the line `### Verdict` in the template, and the value `READY FOR PR`.
REPLACE `READY FOR PR` with `READY TO PROPOSE PR`. The BLOCKED wording
stays.

- [ ] **Step 8.6: Replace any `[HH:MM]`**

```bash
grep -n "\[HH:MM\]" skills/task-review/SKILL.md skills/task-review/prompt.md
```
Replace any match with `YYYY-MM-DD:`.

- [ ] **Step 8.7: Apply identical edits to `prompt.md`**

Apply Steps 8.2, 8.3, 8.4, 8.5, 8.6 to `prompt.md` (skip 8.1).

- [ ] **Step 8.8: Verify**

```bash
grep -c "Phase 0 — Environment Check" skills/task-review/SKILL.md skills/task-review/prompt.md
grep -c "Code review graph consultation" skills/task-review/SKILL.md skills/task-review/prompt.md
grep -c "READY TO PROPOSE PR" skills/task-review/SKILL.md skills/task-review/prompt.md
grep -c "READY FOR PR\b" skills/task-review/SKILL.md skills/task-review/prompt.md
```
Expected: first three print 1+ per file. Last prints 0 per file
(`READY TO PROPOSE PR` contains `READY FOR PR` as substring — use the
`\b` word boundary to make sure no bare `READY FOR PR` remains).

- [ ] **Step 8.9: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-review): code-review-graph consultation, env-aware verdict, no auto-PR
```
Ask for "yes/go".

---

## Task 9: Update `task-hotfix` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/task-hotfix/SKILL.md`
- Modify: `skills/task-hotfix/prompt.md`

- [ ] **Step 9.1: Add Posture header to `SKILL.md`**

After the frontmatter `---`, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 9.2: Insert `Phase 0 — Environment Gate (strict)` before `Phase 1`**

Find `## Phase 1 — Triage (5 minutes max)`. INSERT immediately BEFORE:

```markdown
## Phase 0 — Environment Gate (strict)

Hotfixes target production by definition. Apply the matrix strictly:

| Environment | Rule |
|-------------|------|
| `prod` | Block ALL actions. The user must write the exact action they want performed. No inferred consent. |
| `beta` | ASK per commit. The agent drafts; the user types "go" before each `git commit`. |
| `dev`  | Follow the global rule (ASK per commit). If the user has granted explicit batch permission at hotfix-start time, the agent may propose all commits at the end and ask once. |

In `prod`: if the fix requires more than 20 lines changed, pause and
replan as a targeted mitigation (feature flag, rollback) plus a proper
follow-up task.

```

- [ ] **Step 9.3: Replace `### 5.1 Commit` with `### 5.1 ASK before committing`**

Find the current `### 5.1 Commit` block (contains the `git add [specific
files only — never git add .]` and `git commit -m "fix(scope): ..."`
commands). REPLACE the heading and intro with:

```markdown
### 5.1 ASK before committing

Propose:
```
git add [specific files only — never git add .]
git commit -m "fix(scope): short description of what was broken and how it is fixed"
```
Wait for explicit "go" before executing.
```

- [ ] **Step 9.4: Replace `### 5.2 PR (fast-track)` with `### 5.2 ASK before opening PR`**

Find the current `### 5.2 PR (fast-track)` block (contains the
`gh pr create` heredoc). REPLACE the heading with `### 5.2 ASK before
opening PR (fast-track)`. Add this note after the heading, before the
`gh pr create` block:

```markdown
For `prod` hotfixes, the ASK must include the proposed title and body.
For `beta` / `dev` hotfixes, a single ASK to run the full `gh pr create`
command is sufficient.

```

- [ ] **Step 9.5: Replace any `[HH:MM]`**

```bash
grep -n "\[HH:MM\]" skills/task-hotfix/SKILL.md skills/task-hotfix/prompt.md
```
Replace any match with `YYYY-MM-DD:`.

- [ ] **Step 9.6: Apply identical edits to `prompt.md`**

Apply Steps 9.2, 9.3, 9.4, 9.5 to `prompt.md` (skip 9.1).

- [ ] **Step 9.7: Verify**

```bash
grep -c "Phase 0 — Environment Gate (strict)" skills/task-hotfix/SKILL.md skills/task-hotfix/prompt.md
grep -c "ASK before committing" skills/task-hotfix/SKILL.md skills/task-hotfix/prompt.md
grep -c "ASK before opening PR" skills/task-hotfix/SKILL.md skills/task-hotfix/prompt.md
grep -c "\[HH:MM\]" skills/task-hotfix/SKILL.md skills/task-hotfix/prompt.md
```
Expected: first three print 1+ per file. Last prints 0 per file.

- [ ] **Step 9.8: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-hotfix): strict env gate, ask-before-commit always
```
Ask for "yes/go". This skill touches prod — pay extra attention to the diff.

---

## Task 10: Update `task-compacting` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/task-compacting/SKILL.md`
- Modify: `skills/task-compacting/prompt.md`

- [ ] **Step 10.1: Add Posture header to `SKILL.md`**

After the frontmatter `---`, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 10.2: Replace `[HH:MM]` with `YYYY-MM-DD:`**

The current `## Phase 6 — Commit Changes` block contains the
`git commit -m "chore(tasks): archive $(echo "$COUNT")..."` command. Find
any `[HH:MM]` occurrences in the file. Expected: this skill has no
explicit `[HH:MM]` references, but verify:

```bash
grep -n "\[HH:MM\]" skills/task-compacting/SKILL.md skills/task-compacting/prompt.md
```
If 0 matches, no edit needed. If any, replace with `YYYY-MM-DD:`.

- [ ] **Step 10.3: Add environment grouping to monthly summary template**

Find `## Phase 5 — Generate Monthly Summaries`. The current `### 5.2 For
each month, produce a summary paragraph per task` describes the entry
format. AFTER that sub-section, INSERT a new sub-section `### 5.6 Group by
environment`:

```markdown
### 5.6 Group by environment

For each monthly summary, after the per-task entries, append a section
grouping tasks by `**Environment**` to surface trends:

```markdown
## Environment distribution
- dev:  5 tasks
- beta: 2 tasks
- prod: 3 tasks   ← investigate if prod > 0 (hotfixes on prod are signals)
```

This helps detect operational risk patterns across months.
```

- [ ] **Step 10.4: Apply identical edits to `prompt.md`**

Apply Steps 10.2 and 10.3 to `prompt.md` (skip 10.1).

- [ ] **Step 10.5: Verify**

```bash
grep -c "Environment distribution" skills/task-compacting/SKILL.md skills/task-compacting/prompt.md
grep -c "\[HH:MM\]" skills/task-compacting/SKILL.md skills/task-compacting/prompt.md
```
Expected: first prints 1+ per file. Last prints 0 per file.

- [ ] **Step 10.6: Stage and ASK the user before committing**

Present:
```
refactor(skills/task-compacting): no HH:MM, env grouping
```
Ask for "yes/go".

---

## Task 11: Update `change-impact` skill (SKILL.md + prompt.md)

**Files:**
- Modify: `skills/change-impact/SKILL.md`
- Modify: `skills/change-impact/prompt.md`

- [ ] **Step 11.1: Add Posture header to `SKILL.md`**

After the frontmatter `---`, INSERT:
```markdown

> Posture: see `AGENTS.md` → `Posture & Conventions`. This skill follows the
> global environment, MCP, commit, and questioning rules.
```

- [ ] **Step 11.2: Add code-review-graph as primary source at the start of `Phase 2`**

Find `## Phase 2 — Dependency Analysis`. INSERT immediately AFTER the
heading, BEFORE the existing `### 2.1 Direct dependencies` sub-section:

```markdown
### 2.0 Consult the code-review-graph (primary source)

```bash
# Keep the graph out of conversation memory — use ctx_execute with sqlite3
sqlite3 .code-review-graph/graph.db ".tables"
# Then for each primary file/symbol: list callers, importers, dependents
```

Use the graph as the primary source. The `grep` sub-sections below
(2.1, 2.2, 2.3) are fallback if the graph is missing or stale.
```

- [ ] **Step 11.3: Add `**Environment**` field to the impact report template**

In the `## Phase 5 — Impact Report` template, find the line
`## Affected Files` (which appears in the `### Recommendations` block).
INSERT a new section BEFORE `## Affected Files`:

```markdown
## Environment
- Detected: `dev` | `beta` | `prod`
- Recommended permissions for the change: see global `Posture &
  Conventions` → `Environment & Permissions`.
```

- [ ] **Step 11.4: Apply identical edits to `prompt.md`**

Apply Steps 11.2 and 11.3 to `prompt.md` (skip 11.1).

- [ ] **Step 11.5: Verify**

```bash
grep -c "Consult the code-review-graph" skills/change-impact/SKILL.md skills/change-impact/prompt.md
grep -c "code-review-graph" skills/change-impact/SKILL.md skills/change-impact/prompt.md
grep -c "Detected: \`dev\`" skills/change-impact/SKILL.md skills/change-impact/prompt.md
```
Expected: 1+ per file for each.

- [ ] **Step 11.6: Stage and ASK the user before committing**

Present:
```
refactor(skills/change-impact): code-review-graph as primary source
```
Ask for "yes/go".

---

## Task 12: Bump version 1.0.0 → 1.1.0 in pyproject.toml and 8 skill frontmatters

**Files:**
- Modify: `pyproject.toml`
- Modify: 8 skill SKILL.md frontmatters

- [ ] **Step 12.1: Bump `pyproject.toml` version**

Open `pyproject.toml`. The current content is:
```toml
[project]
name = "dev-workflows"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = ["questionary"]
```

REPLACE `version = "1.0.0"` with `version = "1.1.0"`.

- [ ] **Step 12.2: Bump the 8 skill frontmatters**

For each of these files, change `version: 1.0.0` to `version: 1.1.0` in
the frontmatter (line 3 of each file):
- `skills/project-continue/SKILL.md`
- `skills/task-plan/SKILL.md`
- `skills/task-do/SKILL.md`
- `skills/task-continue/SKILL.md`
- `skills/task-review/SKILL.md`
- `skills/task-hotfix/SKILL.md`
- `skills/task-compacting/SKILL.md`
- `skills/change-impact/SKILL.md`

Use `replaceAll: true` if editing manually, or a single sed:
```bash
for f in skills/project-continue/SKILL.md skills/task-plan/SKILL.md skills/task-do/SKILL.md skills/task-continue/SKILL.md skills/task-review/SKILL.md skills/task-hotfix/SKILL.md skills/task-compacting/SKILL.md skills/change-impact/SKILL.md; do
  sed -i 's/^version: 1\.0\.0$/version: 1.1.0/' "$f"
done
```

- [ ] **Step 12.3: Verify all 9 versions are `1.1.0`**

```bash
grep -l "^version = \"1.1.0\"" pyproject.toml
grep -l "^version: 1.1.0" skills/project-continue/SKILL.md skills/task-plan/SKILL.md skills/task-do/SKILL.md skills/task-continue/SKILL.md skills/task-review/SKILL.md skills/task-hotfix/SKILL.md skills/task-compacting/SKILL.md skills/change-impact/SKILL.md
```
Expected: 1 line for `pyproject.toml`, 8 lines for the skill files.

- [ ] **Step 12.4: Update CLAUDE.md and AGENTS.md skill index**

In `CLAUDE.md`, the `## Available Skills` section has bullet lines like
`- \`dev-workflows:task-do\` — execute a planned task step by step`. Find
the 8 modified skills and add a small annotation at the end of their
line: ` (follows global Posture)`. Specifically modify the lines for:
`project-continue`, `task-plan`, `task-do`, `task-continue`, `task-review`,
`task-hotfix`, `task-compacting`, `change-impact`.

In `AGENTS.md`, the same skill index exists under `## Available Skills`.
Apply the same annotation to the same 8 skills.

- [ ] **Step 12.5: Verify the annotation appears 8 times in each file**

```bash
grep -c "follows global Posture" CLAUDE.md AGENTS.md
```
Expected: 8 in each file (8 skills × 1 file). Total 16.

- [ ] **Step 12.6: Stage and ASK the user before committing**

Present:
```
chore(release): bump version 1.0.0 → 1.1.0, annotate modified skills

8 skills now follow the global Posture & Conventions section:
project-continue, task-plan, task-do, task-continue, task-review,
task-hotfix, task-compacting, change-impact.

Semver: minor bump — prompt content is backward-compatible (agents
without v1.1.0 still receive the same skill content; v1.1.0 adds the
Posture & Conventions section as a default).
```

Ask for "yes/go".

---

## Final acceptance check (after all 12 tasks)

Run the full verification suite:

```bash
echo "=== 1. Global section in 3 files ==="
grep -l "^## Posture & Conventions" AGENTS.md CLAUDE.md GEMINI.md | wc -l   # expect 3

echo "=== 2. No [HH:MM] anywhere in skills/ ==="
grep -rn "\[HH:MM\]" skills/ | wc -l                                          # expect 0

echo "=== 3. No autonomous git commit in skills/ ==="
grep -rn "^git commit" skills/ | grep -v "ASK" | wc -l                       # expect 0
# (Acceptable: the command shown inside an ASK block; not acceptable: a bare 'git commit' as an action.)

echo "=== 4. Posture header in 8 core skills ==="
for s in project-continue task-plan task-do task-continue task-review task-hotfix task-compacting change-impact; do
  grep -l "^> Posture: see" skills/$s/SKILL.md skills/$s/prompt.md
done | wc -l                                                                # expect 16

echo "=== 5. code-review-graph referenced in 7+ skills ==="
grep -rln "code-review-graph" skills/ | wc -l                                # expect 7+

echo "=== 6. task-review verdict updated ==="
grep -rn "READY TO PROPOSE PR" skills/task-review/ | wc -l                    # expect 2
grep -rnE "READY FOR PR\b" skills/task-review/ | wc -l                        # expect 0

echo "=== 7. Version bumps ==="
grep -l "^version = \"1.1.0\"" pyproject.toml | wc -l                         # expect 1
grep -l "^version: 1.1.0" skills/*/SKILL.md | wc -l                          # expect 8

echo "=== 8. No uncommitted changes ==="
git status --porcelain                                                       # expect empty

echo "=== 9. Commit count ==="
git log --oneline origin/develop..HEAD | wc -l                               # expect 12
```

If any check fails, fix the affected task before opening the PR.

---

## Out-of-scope reminders (do not do these in this plan)

- Do NOT unify `SKILL.md` and `prompt.md`. They stay duplicated.
- Do NOT modify `install.py` (only `pyproject.toml` version).
- Do NOT modify the 17 skills not listed in this plan. They inherit the
  global posture automatically.
- Do NOT open the PR yourself. The user opens the PR after review.
- Do NOT create a git tag (`v1.1.0`) — the user may want to do that.

---

## Self-Review (post-write)

**1. Spec coverage:**
- Section 4.1 (env matrix) — Task 1, Task 4, Task 6, Task 9. ✓
- Section 4.2 (available tools) — Task 1. ✓
- Section 4.3 (critical posture) — Task 1. ✓
- Section 4.4 (commit policy) — Task 1, Task 6, Task 7, Task 8, Task 9. ✓
- Section 4.5 (task file template) — Task 1, Task 4, Task 5. ✓
- Section 5.1 (project-continue) — Task 4. ✓
- Section 5.2 (task-plan) — Task 5. ✓
- Section 5.3 (task-do) — Task 6. ✓
- Section 5.4 (task-continue) — Task 7. ✓
- Section 5.5 (task-review) — Task 8. ✓
- Section 5.6 (task-hotfix) — Task 9. ✓
- Section 5.7 (task-compacting) — Task 10. ✓
- Section 5.8 (change-impact) — Task 11. ✓
- Section 5.9 (transversal) — Task 1, Task 4-11. ✓
- Section 6 (10 commits) — covered as 12 commits in this plan (Tasks 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). The spec said "10 commits" assuming AGENTS.md+CLAUDE.md+GEMINI.md+README.md+AGENT_CONTEXT.md were 1 commit and version bump was 1 commit. This plan split them for cleaner atomic commits. The user may want to combine Tasks 1+2+3 into a single commit or keep them separate — both are valid; the spec says "atomic".

**2. Placeholder scan:** No TBD / TODO / "fill in" / "similar to" found. All edits show exact old→new text or exact new text to insert.

**3. Type consistency:**
- "ASK" defined in Task 1, used in Tasks 4-11. Consistent.
- "**Environment**: dev | beta | prod" exact string used in Tasks 1, 4, 5, 6, 7, 8, 9, 11. Consistent.
- "code-review-graph" exact path used in Tasks 1, 4, 5, 6, 8, 11. Consistent.
- "YYYY-MM-DD:" exact format used in all tasks. Consistent.

Plan complete and ready for execution handoff.
