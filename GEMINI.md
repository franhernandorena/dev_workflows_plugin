# Dev Workflows Plugin

## Session-Start Hook

At session start, run the hook to check .context8/ state:

    python3 hooks/context8_session_start.py

- If .context8/ is missing, run `dev-workflows:workflow-init` or `dev-workflows:project-init` before user work.
- If active tasks are reported, load or mention them before starting new work.

## Skills

@./skills/project-continue/SKILL.md
