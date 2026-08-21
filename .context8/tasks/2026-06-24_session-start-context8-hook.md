# Task: Session-start Context8 hook

**Date**: 2026-06-24
**Status**: Complete
**Branch**: `feat/session-start-context8-hook`
**Estimated total complexity**: medium

## Objective

Add a session-start hook to the Dev Workflows plugin so every supported agent checks the current working repo at startup, ensures `.context8/` exists, routes missing context to `workflow-init` or `project-init`, and reports active task state from workspace roots and child projects.

## Acceptance Criteria

- [x] Installing the plugin installs the session-start behavior for every supported tool: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, and Hermes Agent.
- [x] On session start, the hook detects whether the current directory already has `.context8/`.
- [x] If `.context8/` is missing, the hook classifies the current directory as a workspace root or single project and forces the agent's first action to run `dev-workflows:workflow-init` or `dev-workflows:project-init`.
- [x] If `.context8/` exists, the hook summarizes relevant context files and reports active tasks in the current project/workspace.
- [x] For workspace roots, the hook also scans child repos for `.context8/tasks/` and reports active planned/in-progress/blocked work.
- [x] The hook does not duplicate the full logic of `project-init` or `workflow-init`; it only detects state and routes the agent into the existing skills.
- [x] The hook is fast, stdlib-only, and safe to run repeatedly at startup.
- [x] Installer dry-run and uninstall paths include hook assets.
- [x] README and agent context files document the startup behavior.
- [x] Tests or a small self-check cover project detection, workspace detection, existing-context summaries, and task scanning.

## Out of Scope

- Rewriting `project-init` or `workflow-init` as executable Python.
- Adding network calls, package dependencies, or background daemons.
- Solving tool-specific hook features that do not exist in a supported agent; those agents should use the best available startup-instruction fallback.
- Migrating existing `.context8/` formats.

## Unknowns & Risks

| Unknown / Risk | Impact | Mitigation |
|----------------|--------|------------|
| Not every supported agent has native lifecycle hooks. | high | Implement a support matrix: native plugin hook where available, startup instruction fallback elsewhere. Document any weaker guarantee explicitly. |
| A command hook cannot directly invoke an agent slash skill in all tools. | high | Hook emits mandatory startup context telling the agent to run the selected skill before user work; do not duplicate skill internals. |
| Workspace/project classification can be ambiguous. | medium | Use conservative rules: multiple child `.git` dirs means workflow; current dir `.git` means project; both means project unless child repos are present. |
| Startup scanning can become noisy in large workspaces. | medium | Limit child scan depth and output only task counts plus latest active task paths. |
| Existing user changes in `install.py`, `CLAUDE.md`, or `skills/task-compacting/` may overlap. | medium | Read current files before editing and preserve unrelated local changes. |

## Implementation Plan

## Step 1: Define the hook contract and support matrix

**Files**: `README.md`, `.context8/architecture/key_patterns.md` or `.context8/AGENT_CONTEXT.md`
**Depends on**: none
**Estimated complexity**: small
**Reversible**: yes

### What

Document the startup hook contract:
- Input: current working directory, optional native hook JSON from the agent.
- Output: concise startup context for the agent.
- Missing `.context8/`: output a mandatory first action to run `dev-workflows:workflow-init` or `dev-workflows:project-init`.
- Existing `.context8/`: output context summary and task inventory.

Add a support matrix:
- Claude Code: native plugin hook via `hooks/hooks.json` and `SessionStart`.
- Codex, Cursor, Gemini CLI, OpenCode, Hermes Agent: installer-managed startup instruction fallback unless native hooks are confirmed in this repo's supported format.

### Why

The project supports several agents, but native hook capability is not represented in the current installer. The behavior must be explicit so implementation does not overfit to Claude Code.

### How to verify

Read the docs and confirm each supported tool has an install path and a startup behavior listed.

### Risks

The fallback behavior is weaker than a native hook. The docs must call that out without blocking the feature.

## Step 2: Add the stdlib hook script

**Files**: `hooks/context8_session_start.py`
**Depends on**: Step 1
**Estimated complexity**: medium
**Reversible**: yes

### What

Create a Python 3.11 stdlib-only script that:
- Reads hook JSON from stdin when present and falls back to `Path.cwd()`.
- Detects `.context8/`.
- Classifies missing-context folders:
  - workspace root when multiple child directories contain `.git`;
  - project when current directory contains `.git` or project config files;
  - unknown otherwise, with a conservative message asking the agent to inspect before init.
- Reads only small, known context files when `.context8/` exists: `WORKSPACE_OVERVIEW.md`, `PROJECT_OVERVIEW.md`, `AGENT_CONTEXT.md`, `README.md`.
- Scans `.context8/tasks/*.md` for active statuses: Planned, In progress, Blocked.
- For workspace roots, scans child repos at depth 1 or 2 for `.context8/tasks/*.md`.
- Emits Claude-compatible JSON when `hook_event_name == "SessionStart"` and plain text otherwise.

### Why

One script keeps startup behavior consistent across all agents and avoids duplicating logic in installer branches.

### How to verify

Run local self-checks against temporary directories:
- no `.context8/` + one `.git` -> recommends `project-init`;
- no `.context8/` + multiple child `.git` dirs -> recommends `workflow-init`;
- `.context8/` + task files -> reports active tasks.

### Risks

The script must not be too clever. Keep parsing shallow and deterministic.

## Step 3: Add Claude native plugin hook assets

**Files**: `hooks/hooks.json`, `.claude-plugin/plugin.json`
**Depends on**: Step 2
**Estimated complexity**: small
**Reversible**: yes

### What

Add a plugin hook config for Claude Code:
- event: `SessionStart`;
- matcher: `startup|resume`;
- type: `command`;
- command: `${CLAUDE_PLUGIN_ROOT}/hooks/context8_session_start.py`;
- timeout: short, for example 10 seconds.

Keep the manifest metadata unchanged unless the plugin format requires declaring bundled hooks.

### Why

Claude Code supports plugin hooks from `hooks/hooks.json`, and `SessionStart` can inject `additionalContext` at startup.

### How to verify

Inspect the installed plugin layout and confirm `hooks/hooks.json` references the bundled script path.

### Risks

Executable bit may not survive every install path. The installer should either preserve mode or invoke the script through `python3`.

## Step 4: Extend installer to install hook assets

**Files**: `install.py`
**Depends on**: Step 2, Step 3
**Estimated complexity**: medium
**Reversible**: yes

### What

Add hook asset handling to `TOOLS` and installer functions:
- Copy `hooks/context8_session_start.py` for tools that can use a script.
- Copy `hooks/hooks.json` for Claude plugin/global/project install where applicable.
- For fallback tools, inject or update a "Dev Workflows Session Start Hook" block in their context file (`AGENTS.md`, `GEMINI.md`, or equivalent installed context surface).
- Include hook files in `--dry-run`.
- Remove hook files or managed blocks in `--uninstall`.

Use marker comments for fallback blocks so repeated installs update the block instead of duplicating it.

### Why

The current installer only copies skills or a whole context file. Hook installation needs first-class installer support to work for all supported agents.

### How to verify

Run:
- `uv run install.py --dry-run`
- a project-local install into a temporary directory for each tool path shape
- uninstall dry-run

### Risks

Context file block editing can damage user content if done with broad string replacement. Use exact markers and preserve all other content.

## Step 5: Add startup instructions to agent context files

**Files**: `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`
**Depends on**: Step 1, Step 4
**Estimated complexity**: small
**Reversible**: yes

### What

Add a concise startup rule:
- At session start, run the Dev Workflows Session Start Hook if native hooks are unavailable.
- If the hook reports missing `.context8/`, execute the recommended init skill before other work.
- If active tasks are reported, load or mention them before starting new work.

### Why

This gives non-native-hook agents an explicit startup path while keeping all logic in one script.

### How to verify

Read each context file and confirm the instruction names the same script and behavior.

### Risks

Too much startup prose increases noise. Keep the block short.

## Step 6: Update plugin/package metadata and docs

**Files**: `README.md`, `.context8/AGENT_CONTEXT.md`, `.context8/PROJECT_OVERVIEW.md`
**Depends on**: Step 4, Step 5
**Estimated complexity**: small
**Reversible**: yes

### What

Document:
- what the hook does;
- how it is installed;
- which agents use native hooks vs fallback instructions;
- how to disable/remove it through uninstall;
- how active tasks are summarized.

Update `.context8/` docs because installer behavior and project architecture changed.

### Why

The hook changes a core plugin behavior: install once, then every session starts with context awareness.

### How to verify

README installation details match `install.py` behavior.

### Risks

Docs can drift from installer behavior. Keep the support matrix in one place and refer to it elsewhere.

## Step 7: Add minimal tests or self-checks

**Files**: `tests/test_context8_session_start.py` or `hooks/context8_session_start.py`
**Depends on**: Step 2
**Estimated complexity**: small
**Reversible**: yes

### What

Add the smallest runnable check:
- Prefer a `tests/test_context8_session_start.py` using stdlib `unittest` and `tempfile`.
- If no test structure is desired, add a `--self-test` mode to the hook script.

Cover:
- project classification;
- workspace classification;
- task status extraction;
- JSON output for Claude SessionStart.

### Why

The hook has branches and filesystem detection; a small check prevents silent startup regressions.

### How to verify

Run `python -m unittest` or `python hooks/context8_session_start.py --self-test`.

### Risks

No existing test suite means adding tests may require documenting the command in README.

## Step 8: Verify install/uninstall behavior end to end

**Files**: no new files expected
**Depends on**: Steps 1-7
**Estimated complexity**: small
**Reversible**: yes

### What

Run final verification:
- hook self-checks;
- installer dry-run;
- project-local install into a temp fixture;
- inspect installed paths for each supported tool shape;
- uninstall from temp fixture.

### Why

The feature is mostly installation behavior, so file layout verification matters as much as script logic.

### How to verify

Commands complete without errors and installed temp directories contain the expected skill/context/hook files.

### Risks

Global install tests should not touch the user's real agent config. Use temp project-local paths for verification.

## Dependencies

External: none.

Internal:
- Existing `project-init` and `workflow-init` skills must remain the source of truth for creating `.context8/`.
- Existing installer patterns in `install.py`.

## Files Modified

| File | Change type | Notes |
|------|-------------|-------|
| `hooks/context8_session_start.py` | create | Shared startup detector and task reporter. Self-test + 13 unittest tests. |
| `hooks/hooks.json` | create | Claude Code native plugin hook config (SessionStart event). |
| `install.py` | modify | Hook asset install/uninstall, fallback block injection/removal. |
| `CLAUDE.md` | modify | Session-Start Hook section added at top. |
| `GEMINI.md` | modify | Session-Start Hook + fallback instruction added. |
| `AGENTS.md` | modify | Session-Start Hook section added at top. |
| `README.md` | modify | Session-Start Hook section, support matrix, repo structure updated. |
| `.context8/AGENT_CONTEXT.md` | modify | Hook contract and support matrix added. |
| `.context8/PROJECT_OVERVIEW.md` | modify | Current state updated with hook info. |
| `tests/test_context8_session_start.py` | create | 13 stdlib unittest tests covering classification, tasks, output. |

## Test Plan

- [ ] Run existing baseline checks before implementation: `uv run install.py --dry-run`.
- [ ] Run hook self-checks or `python -m unittest`.
- [ ] Run hook manually in temp fixtures for project, workspace, and existing-context cases.
- [ ] Run installer dry-run after changes.
- [ ] Run project-local install/uninstall into a temporary directory, not real global agent config.
- [ ] Confirm no unrelated local changes are overwritten.

## Progress Log

- [16:??] Planned auto-init session hook after user clarified the hook must create/use `.context8` automatically because installing the plugin means opting into Context8.
- [17:16] Started execution. Branch: feat/session-start-context8-hook.
- [17:17] Step 1 complete. Added hook contract and support matrix to README.md and AGENT_CONTEXT.md.
- [17:18] Step 2 complete. Created hooks/context8_session_start.py. Self-test passes (0 failures). Manual test for current project reports 3 active tasks.
- [17:19] Step 3 complete. Created hooks/hooks.json for Claude Code native SessionStart hook.
- [17:20] Step 4 complete. Extended install.py with hook asset installation, fallback block injection/removal, and uninstall support.
- [17:21] Step 5 complete. Added startup instructions to CLAUDE.md, GEMINI.md, and AGENTS.md.
- [17:22] Step 6 complete. Updated README.md repo structure and PROJECT_OVERVIEW.md.
- [17:22] Step 7 complete. Created tests/test_context8_session_start.py (13 unittest tests) — all pass.
- [17:23] Step 8 complete. Hook self-test passes (0 failures). Installer hook logic verified in temp fixture. All 16 sub-tests pass.
- [17:24] All steps complete. All acceptance criteria checked off. Tests pass. Linting (ruff): no issues.

## Decisions Made

- Use auto-init routing behavior: missing `.context8/` must cause the agent to run `workflow-init` or `project-init` before user work.
- Do not duplicate the full init skills in Python; the hook detects and routes into existing skills.
- Use native Claude Code `SessionStart` plugin hooks where available; use managed startup instruction fallback for the other supported agents.
- Keep implementation stdlib-only.

## Blockers

- Native hook support for Codex, Cursor, Gemini CLI, OpenCode, and Hermes Agent must be verified during implementation. If absent, the documented fallback is the supported path.
