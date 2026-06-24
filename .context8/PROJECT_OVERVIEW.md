# Dev Workflows — Project Overview

## What it does

Plug-n-play structured prompts for AI coding agents. Install once via `uv run install.py`, then invoke any skill from your AI agent via `/dev-workflows:<skill-name>`. Each skill enforces a reproducible, phased workflow — no more improvisation.

## Who uses it

Developers using Claude Code, Codex, Cursor, Gemini CLI, or OpenCode who want consistent, structured agent interactions.

## Key architectural decisions

- **Skills as Markdown files**: Simple, version-controllable, platform-agnostic
- **Single installer for all tools**: `install.py` detects the environment and adapts
- **Phased prompts**: Every skill has mandatory phases — no skipping, no improvisation
- **File-based state**: Tasks, handoffs, audits all go to `.context8/` on disk

## Current state

Stable with 11+ skills covering workspace management, project lifecycle, task execution, and agent generation. Includes a session-start hook (`hooks/context8_session_start.py`) that checks `.context8/` at startup and routes agents to the correct init skill or summarises active tasks.

## Next priorities

- Add tests for `install.py` and the session-start hook
- Add CI/CD pipeline
- Verify native hook support for Codex, Cursor, Gemini CLI, OpenCode, and Hermes Agent
