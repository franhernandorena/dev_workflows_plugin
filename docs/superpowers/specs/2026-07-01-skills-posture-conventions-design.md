# Skills Posture & Conventions — Design

**Date**: 2026-07-01
**Status**: Approved (pending written-spec review)
**Author**: brainstorming session
**Branch**: `feat/skills-posture-conventions`
**Target version**: 1.1.0 (semver minor — backward-compatible prompt changes)

---

## 1. Problem

The dev-workflows plugin is consumed by multiple AI coding agents (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Hermes Agent). Each agent that installs the plugin receives the same skill files but inherits NO shared posture for:

- **Environment awareness** — agents don't reliably detect dev/beta/prod before touching shared state.
- **MCP / plugin usage** — agents don't know which ecosystem tools are available (caveman, ponytail, context-mode, code-review-graph, superpowers, etc.).
- **Commit hygiene** — `task-do` and `task-hotfix` currently instruct the agent to commit on its own. This is too aggressive for prod/beta and conflicts with the user's "never auto-commit" rule.
- **Task file template** — the progress log uses `[HH:MM]` timestamps. The user wants date-only entries.
- **Critical posture** — agents default to compliance. The user wants the agent to question, demand clarity, surface hidden costs, and propose alternatives.

The result is that each session restarts the agent's defaults, and good behavior depends on the user remembering to remind it.

## 2. Goal

Make good behavior the **default** for every agent that installs the plugin. After this change:

1. The global config (`AGENTS.md` / `CLAUDE.md` / `GEMINI.md`) carries a `Posture & Conventions` section that all skills inherit.
2. The 8 core skills (`project-continue`, `task-plan`, `task-do`, `task-continue`, `task-review`, `task-hotfix`, `task-compacting`, `change-impact`) follow that posture structurally.
3. Task file templates use `YYYY-MM-DD:` in the progress log, never `[HH:MM]`.
4. `task-do` and `task-hotfix` ask before every commit, never auto-commit.
5. Skills that benefit from a code-graph (`change-impact`, `task-review`, `task-plan`, `project-continue`) consult `.code-review-graph/graph.db` as primary source.
6. The agent's default posture is to question, not to comply silently.

## 3. Non-goals

- Unify `SKILL.md` and `prompt.md` (still duplicated; future iteration).
- Add new skills (`environment-check`, `code-review-graph` standalone) — global rule is enough.
- Modify `install.py` beyond a version bump.
- Modify `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `gemini-extension.json` (they work as-is).
- Touch the 25 skills that are not in the core-tasks set — they inherit via the global section.
- Add tests or CI/CD (no test framework in the plugin today; not blocking).

## 4. Architecture

### 4.1 Layered rule model

```
┌─────────────────────────────────────────────────────────────────┐
│ Global (AGENTS.md / CLAUDE.md / GEMINI.md)                      │
│   Posture & Conventions                                         │
│   - 4.1 Environment & Permissions (dev/beta/prod matrix)        │
│   - 4.2 Available Tools (caveman, ponytail, ctx-mode,           │
│                            code-review-graph, superpowers, etc.) │
│   - 4.3 Critical Posture (question, don't comply)               │
│   - 4.4 Commit Policy (ask before every commit)                 │
│   - 4.5 Task File Conventions (date-only, no HH:MM)             │
└─────────────────────────────────────────────────────────────────┘
                              │ inherited by
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Core skills (8)                                                 │
│   project-continue, task-plan, task-do, task-continue,          │
│   task-review, task-hotfix, task-compacting, change-impact      │
│                                                                 │
│   Each adds:                                                    │
│   - Header referencing the global section                      │
│   - Phase 0 — Environment Gate (where applicable)              │
│   - No [HH:MM] in any template                                  │
│   - ASK before every commit (replaces auto-commit)             │
│   - code-review-graph awareness (where blast radius matters)   │
└─────────────────────────────────────────────────────────────────┘
                              │ inherited by
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Remaining 25 skills                                             │
│   Unchanged structurally. Inherit posture via global section.   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Environment & Permissions matrix

| Env    | Detect by                                       | Agent may...                                     |
|--------|-------------------------------------------------|--------------------------------------------------|
| dev    | `feat/*` branch, localhost, `.env.dev`          | work freely, run migrations locally, push       |
| beta   | `release/*` branch, staging URLs, `.env.beta`   | work, but ASK before each non-read op            |
| prod   | `main`/`master` branch, prod URLs, `.env.prod`  | DO NOTHING without explicit, written permission |

Definitions (will appear verbatim in the global section):

- **"ASK"** = stop, present the planned action, wait for the user's explicit "yes" or "go". A silent continuation is NOT consent.
- **"Explicit permission"** = the user wrote out the action in their message. "Sure", "ok", "continue" without specifying the action does NOT count.
- **prod is sacred.** If a task would touch prod, surface it before starting `task-do` — even if the user said "do it".
- When the task file records an environment, write it explicitly: `**Environment**: dev | beta | prod`.

### 4.3 Available tools (referenced in global)

| Tool | Use it for |
|---|---|
| caveman | Compressed communication, commit messages, review feedback, token stats. |
| ponytail | Tail long outputs, agent-to-agent handoffs. |
| context-mode (`ctx_*`) | Gather & process large data OUT of conversation memory. `ctx_batch_execute`, `ctx_search`, `ctx_execute_file`. |
| code-review-graph | Auto-updated SQLite at `.code-review-graph/graph.db`. Updated on every Edit/Write/Bash. Query it for blast radius, callers, deps. |
| superpowers | `brainstorming` before creative work, `TDD` for implementations, `systematic-debugging` for bugs, `verification-before-completion` before "done". |
| context7, playwright, token-savior, code-simplifier, feature-dev, frontend-design, claude-mem, claude-md-management | Use when the task fits. |

### 4.4 Commit policy (verbatim in global)

- The agent MUST ask before creating a commit. "Ask" = present the exact `git add` + `git commit -m "<message>"` command, then wait for explicit "yes" or "go".
- This applies to ALL commits: feature steps, doc updates, fixups.
- `--no-verify`, `--amend`, force-push, empty commits are forbidden unless the user wrote the exact command in their message.
- Rebase, cherry-pick, reset, branch deletion also require explicit permission, even on the agent's own branches.
- Conventional Commits format encouraged: `type(scope): description`. Types: feat, fix, refactor, docs, test, chore, ci, perf.
- The agent SHOULD draft commit messages but MUST NOT execute `git commit` without the user's go-ahead.

### 4.5 Task file conventions (verbatim in global)

Task files live in `.context8/tasks/YYYY-MM-DD_short_description.md`. The progress log uses date + bullet, NOT `[HH:MM]`.

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

## 5. Per-skill changes

### 5.1 `project-continue`

- **+ Phase 0 — Environment & Posture**: before Phase 1, ask the user to confirm the target environment if not clear. Confirm current branch matches. If prod → STOP and require explicit permission.
- **+ Phase 2**: load `.code-review-graph/graph.db` summary (nodes/edges counts) via `ctx_execute` or `sqlite3` CLI; do not dump the DB into context.
- **~ Phase 3.2 task file template**: replace `[HH:MM]` with `YYYY-MM-DD:`. Add `**Environment**` field.

### 5.2 `task-plan`

- **+ Phase 0 — Question first**: agent writes 2-3 sentences confirming its understanding of the objective. If the task is ambiguous, stop and ask.
- **+ Phase 1 (Investigate)**: consult `.code-review-graph` for blast radius, callers, dependencies of files to touch. Use `ctx_execute` with `sqlite3` to keep the graph out of context.
- **+ Task file template**: add `**Environment**` field.
- **~ Progress log template**: `YYYY-MM-DD:`.
- **− Remove** any "commit the plan" instructions (the plan is not committed).

### 5.3 `task-do`

- **+ Phase 0 — Environment Gate**: if `**Environment**` is missing from the task file, request it. If `prod` or `beta`, restate the permission rule before starting.
- **~ Phase 3, step 5**: replace "Commit if the step is a clean logical unit" with "**ASK the user before committing.** Present the exact `git add` + `git commit -m "..."` and wait for 'go'."
- **+ After each step (not commit)**: validate against `.code-review-graph` that no unexpected new caller was broken.
- **~ Phase 5.3 (Final commit)**: convert "Final commit" to "**ASK before final commit**".
- **~ Phase 5.4 (Open PR)**: convert to "**ASK before opening PR**". In `prod`, this means two separate ASKs: (a) ASK to propose the PR content (title, body, base/head branches), wait for "yes"; (b) ASK to actually execute `gh pr create`, wait for "go". In `beta` and `dev`, a single ASK for the full action is sufficient.
- **~ Progress log**: `YYYY-MM-DD:`.
- **+ Hard stops**: user did not answer ASK within reasonable scope; environment changed mid-task; code-review-graph shows unexpected new callers.

### 5.4 `task-continue`

- **+ Re-read `**Environment**`** from the task file. If prod/beta, show a permission reminder on resume.
- **~ Progress log**: `YYYY-MM-DD:`.
- **− Remove** implicit commit instructions (resume does not commit).

### 5.5 `task-review`

- **+ Phase 0 — Environment check**: the review's strictness depends on the PR target environment. prod = every criterion is blocking. beta = standard. dev = lighter.
- **+ Phase 1.5 — Code review graph consultation**: before correctness review, query `.code-review-graph` for:
  - All callers of each modified function/class.
  - Files not in the diff but transitively affected.
  - Tests that exercise the changed code.
- **~ Phase 7 (Review Report)**: add `**Target Environment**` and `**Commit / Merge Plan**` blocks. The agent proposes; the user executes.
- **~ Verdict**: change from `READY FOR PR` to `READY TO PROPOSE PR` — the agent never opens the PR alone.
- **− Remove** any auto-commit references.

### 5.6 `task-hotfix`

- **+ Phase 0 — Environment Gate (strict)**: prod blocks ALL actions until the user writes the exact action. beta asks per commit. dev follows the global rule (ASK per commit, unless the user has explicitly granted batch commit permission for this hotfix at hotfix-start time — in which case the agent proposes all commits at the end and asks once).
- **~ Progress log**: `YYYY-MM-DD:`.
- **~ Replace** every "commit the fix" with "ASK before committing the fix".
- **+ New hard stop**: any change > 20 lines in prod → stop and re-plan.

### 5.7 `task-compacting`

- **~ Progress log template**: `YYYY-MM-DD:`.
- **+ Monthly summary**: group also by `**Environment**` to surface trends (e.g., "3 prod hotfixes in July").

### 5.8 `change-impact`

- **~ Phase 1 (Identify changes)**: first step is to query `.code-review-graph/graph.db` with `ctx_execute` for callers, importers, and dependents. `grep` only as fallback.
- **+ Phase 2 (Blast radius)**: graph is primary source.
- **+ Report**: include `**Environment**` detected and recommended permissions for the change.
- No template time changes (no task file).

### 5.9 Transversal changes (all 8 skills)

- Header at top: `> Posture: see AGENTS.md → Posture & Conventions. This skill follows the global environment, MCP, commit, and questioning rules.`
- Replace ALL occurrences of `[HH:MM]` with `YYYY-MM-DD:`.
- Replace ALL "commit if..." with "ASK before committing..." (except where the skill is explicitly showing the user a proposed command).
- Add `**Environment**` field in task file templates where applicable.

## 6. Implementation plan

10 atomic commits, in this order. All on a new branch `feat/skills-posture-conventions` from `develop`.

| # | Type | Scope | Files | Commit message |
|---|---|---|---|---|
| 1 | docs | plugin | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `.context8/AGENT_CONTEXT.md` | `docs(plugin): add global Posture & Conventions section` |
| 2 | refactor | skills/project-continue | `SKILL.md`, `prompt.md` | `refactor(skills/project-continue): env gate, no HH:MM, code-review-graph aware` |
| 3 | refactor | skills/task-plan | `SKILL.md`, `prompt.md` | `refactor(skills/task-plan): question first, env field, graph query` |
| 4 | refactor | skills/task-do | `SKILL.md`, `prompt.md` | `refactor(skills/task-do): ask-before-commit, env gate, no auto-merge` |
| 5 | refactor | skills/task-continue | `SKILL.md`, `prompt.md` | `refactor(skills/task-continue): env reminder, no HH:MM` |
| 6 | refactor | skills/task-review | `SKILL.md`, `prompt.md` | `refactor(skills/task-review): code-review-graph consultation, env-aware verdict, no auto-PR` |
| 7 | refactor | skills/task-hotfix | `SKILL.md`, `prompt.md` | `refactor(skills/task-hotfix): strict env gate, ask-before-commit always` |
| 8 | refactor | skills/task-compacting | `SKILL.md`, `prompt.md` | `refactor(skills/task-compacting): no HH:MM, env grouping` |
| 9 | refactor | skills/change-impact | `SKILL.md`, `prompt.md` | `refactor(skills/change-impact): code-review-graph as primary source` |
| 10 | docs | plugin | `CLAUDE.md`, `AGENTS.md`, `pyproject.toml` + 8 skill frontmatters | `chore(release): bump version 1.0.0 → 1.1.0, update skill index` |

## 7. Acceptance criteria

- [ ] All 3 global files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) contain the `## Posture & Conventions` section with 5 sub-sections (4.1–4.5 of the global config).
- [ ] `grep -rn '\[HH:MM\]' skills/` returns 0 matches.
- [ ] `grep -rn 'git commit' skills/` shows only "ASK before committing" or proposed-command contexts — no autonomous action.
- [ ] All 8 core skills carry the `> Posture: see AGENTS.md → Posture & Conventions` header.
- [ ] All 8 core skills reference `.code-review-graph/` or `code-review-graph` at least once (except `task-compacting` if blast radius is not relevant).
- [ ] `task-do` and `task-hotfix` contain a `## Phase 0 — Environment Gate` with the dev/beta/prod matrix and the prod double-ASK for PR.
- [ ] `task-review` verdict changed from `READY FOR PR` to `READY TO PROPOSE PR`.
- [ ] `pyproject.toml` and the 8 modified skill frontmatters are at version `1.1.0`.
- [ ] No regression in `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `gemini-extension.json`.
- [ ] Commits follow Conventional Commits and are atomic (one per logical group).
- [ ] `git diff --stat` final shows coherent changes, no orphan files.

## 8. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Old task files with `[HH:MM]` become inconsistent with the new template | High | Low | Forward-only change; document in design doc that historical files are not migrated. |
| `.code-review-graph` not present in every project | Medium | Medium | Skills use "try graph → fallback to grep". Never fail because the graph is missing. |
| Drift between `SKILL.md` and `prompt.md` (still duplicated) | Medium | Medium | Each commit applies to both files in the same commit. Documented as out-of-scope to unify. |
| 8 modified skills = large PR = harder review | Medium | Low | `pr-description` skill summarizes per-skill in the PR body. Atomic commits mitigate. |
| `install.py` behavior change risk | Low | Medium | Don't touch `install.py` beyond version bump. Verify with `uv run install.py --dry-run` at the end. |
| User forgets the new posture is now default | Low | Low | Document the change prominently in `README.md` "Posture & Conventions" section. |

## 9. Out of scope (explicit)

- Unify `SKILL.md` and `prompt.md`.
- Add new skills (`environment-check`, `code-review-graph` standalone).
- Add tests or CI/CD.
- Modify the 25 non-core skills.
- Create a new CHANGELOG.md (out of scope; optional add-on, decide in commit 10).

## 10. References

- User conversation: brainstorming session on 2026-07-01.
- Existing `AGENT_CONTEXT.md` and `PROJECT_OVERVIEW.md` in `.context8/`.
- Plugin README.md: typical-flow section that must remain intact.
- Hooks: `hooks/context8_session_start.py` (not modified, but its output should reflect the new posture once skills are updated).
