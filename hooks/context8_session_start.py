#!/usr/bin/env python3
"""
Dev Workflows Session-Start Hook

Detects .context8/ at startup and routes the agent to the correct init skill
or summarises active tasks. Shared by all supported agents.
"""

import json
import re
import sys
import tempfile
from pathlib import Path

HOOK_EVENT_KEY = "hook_event_name"
SESSION_START = "SessionStart"

CONTEXT_FILES = [
    "WORKSPACE_OVERVIEW.md",
    "PROJECT_OVERVIEW.md",
    "AGENT_CONTEXT.md",
    "README.md",
]

ACTIVE_STATUSES = {"Planned", "In progress", "Blocked"}


def read_stdin_json() -> dict | None:
    """Read a single JSON object from stdin when piped; returns None if stdin is a TTY."""
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else None
    except (json.JSONDecodeError, OSError):
        return None


def classify_directory(cwd: Path) -> str:
    """Classify cwd as 'workspace', 'project', or 'unknown' when .context8/ is absent."""
    has_git = (cwd / ".git").is_dir()

    child_git_dirs = 0
    try:
        for child in cwd.iterdir():
            if child.is_dir() and (child / ".git").is_dir():
                child_git_dirs += 1
    except PermissionError:
        pass

    if has_git and child_git_dirs > 0:
        return "workspace"
    if child_git_dirs > 0:
        return "workspace"
    if has_git:
        return "project"

    config_hints = [
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "Gemfile",
        "setup.py",
        "CMakeLists.txt",
        "Makefile",
        "Rakefile",
        "pom.xml",
        "build.gradle",
        "composer.json",
    ]
    for hint in config_hints:
        if (cwd / hint).exists():
            return "project"

    return "unknown"


def read_context_summary(cwd: Path) -> dict[str, str | None]:
    """Read small context files and return their first 10 lines each."""
    summary = {}
    ctx_dir = cwd / ".context8"
    for name in CONTEXT_FILES:
        path = ctx_dir / name
        if path.exists():
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
                summary[name] = "\n".join(lines[:10]) + (
                    "\n..." if len(lines) > 10 else ""
                )
            except (OSError, UnicodeDecodeError):
                summary[name] = None
        else:
            summary[name] = None
    return summary


ACTIVE_TASK_RE = re.compile(
    r"^\*\*Status\*\*:\s*(" + "|".join(re.escape(s) for s in ACTIVE_STATUSES) + r")",
    re.IGNORECASE | re.MULTILINE,
)


def scan_tasks(tasks_dir: Path) -> list[dict]:
    """Scan a .context8/tasks/ directory for active tasks. Returns list of {path, status}."""
    active = []
    if not tasks_dir.is_dir():
        return active
    for task_file in sorted(tasks_dir.glob("*.md")):
        try:
            text = task_file.read_text(encoding="utf-8")
            m = ACTIVE_TASK_RE.search(text)
            if m:
                active.append({"path": str(task_file), "status": m.group(1)})
        except (OSError, UnicodeDecodeError):
            continue
    return active


def scan_child_repos(cwd: Path, max_depth: int = 2) -> list[dict]:
    """Scan child directories for active tasks in .context8/tasks/."""
    results = []
    try:
        stack = [(cwd / child, 0) for child in sorted(cwd.iterdir()) if child.is_dir()]
    except PermissionError:
        return results

    while stack:
        child, depth = stack.pop()
        if child.name.startswith(".") or child.name.startswith("_"):
            continue
        ctx_tasks = child / ".context8" / "tasks"
        if ctx_tasks.is_dir():
            repo_name = child.name
            for td in [ctx_tasks, child / ".context8" / "tasks"]:
                for task in scan_tasks(td):
                    task["repo"] = repo_name
                    results.append(task)
        elif depth < max_depth:
            try:
                for sub in sorted(child.iterdir()):
                    if sub.is_dir() and not sub.name.startswith("."):
                        stack.append((sub, depth + 1))
            except PermissionError:
                continue
    return results


def build_output(hook_data: dict | None, cwd: Path) -> dict:
    """Build the hook output dict."""
    ctx_dir = cwd / ".context8"

    if ctx_dir.is_dir():
        summary = read_context_summary(cwd)
        tasks = scan_tasks(ctx_dir / "tasks")
        child_tasks = scan_child_repos(cwd) if tasks else []
        output = {
            "has_context8": True,
            "context_summary": summary,
            "active_tasks_local": tasks,
            "active_tasks_child_repos": child_tasks,
        }
    else:
        classification = classify_directory(cwd)
        init_skill = {"workspace": "workflow-init", "project": "project-init"}.get(
            classification
        )
        instructions = []
        if init_skill:
            instructions.append(
                f"Run `dev-workflows:{init_skill}` to create .context8/ "
                f"before starting user work."
            )
        else:
            instructions.append(
                "Cannot determine context type. Inspect the directory structure "
                "then run `dev-workflows:project-init` or "
                "`dev-workflows:workflow-init` to create .context8/."
            )
        output = {
            "has_context8": False,
            "classification": classification,
            "instructions": instructions,
        }

    output["cwd"] = str(cwd)
    return output


def format_text(output: dict) -> str:
    """Format hook output as human-readable text."""
    lines = [f"# Dev Workflows Session-Start Hook", f"**cwd**: {output['cwd']}", ""]
    if output["has_context8"]:
        lines.append("## .context8/ found")
        summary = output.get("context_summary", {})
        for name, content in summary.items():
            if content:
                if content.endswith("\n..."):
                    lines.append(f"\n### {name} (truncated)")
                else:
                    lines.append(f"\n### {name}")
                lines.append(content)
        local = output.get("active_tasks_local", [])
        if local:
            lines.append(f"\n### Active tasks ({len(local)} found)")
            for t in local:
                lines.append(f"- {t['status']}: `{t['path']}`")
        child = output.get("active_tasks_child_repos", [])
        if child:
            lines.append(f"\n### Active tasks in child repos ({len(child)} found)")
            for t in child:
                lines.append(
                    f"- [{t['repo']}] {t['status']}: `{t['path']}`"
                )
    else:
        lines.append(f"## .context8/ not found — {output['classification']}")
        for instr in output.get("instructions", []):
            lines.append(f"- {instr}")
    return "\n".join(lines)


def format_json(output: dict) -> str:
    """Format hook output as additionalContext for Claude Code SessionStart."""
    return json.dumps({"additionalContext": format_text(output)})


def run(cwd: Path, hook_data: dict | None) -> str:
    """Run the hook and return formatted output."""
    output = build_output(hook_data, cwd)
    if hook_data and hook_data.get(HOOK_EVENT_KEY) == SESSION_START:
        return format_json(output)
    return format_text(output)


def self_test() -> None:
    """Run minimal self-checks against temporary directories."""
    errors = []

    def check(label: str, condition: bool):
        if not condition:
            errors.append(f"FAIL: {label}")

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        # Project — single .git dir, no .context8
        (tmpdir / ".git").mkdir()
        result = build_output(None, tmpdir)
        check("project classification",
              result == {
                  "cwd": str(tmpdir),
                  "has_context8": False,
                  "classification": "project",
                  "instructions": [
                      "Run `dev-workflows:project-init` to create .context8/ "
                      "before starting user work."
                  ],
              })

        # Workspace — root with child .git dirs
        (tmpdir / ".git").rmdir()
        (tmpdir / "repo-a" / ".git").mkdir(parents=True)
        (tmpdir / "repo-b" / ".git").mkdir(parents=True)
        result = build_output(None, tmpdir)
        check("workspace classification", result["classification"] == "workspace")
        check("workspace init skill",
              result["instructions"][0].startswith("Run `dev-workflows:workflow-init`"))

        # Existing .context8/ with tasks
        (tmpdir / "context-project" / ".context8" / "tasks").mkdir(parents=True)
        (tmpdir / "context-project" / ".context8" / "PROJECT_OVERVIEW.md").write_text(
            "# Test Project\n\nStable.", encoding="utf-8"
        )
        (tmpdir / "context-project" / ".context8" / "tasks" / "active.md").write_text(
            "# Task\n\n**Status**: In progress\n\n## Objective\n\nTest.",
            encoding="utf-8",
        )
        (tmpdir / "context-project" / ".context8" / "tasks" / "done.md").write_text(
            "# Task\n\n**Status**: Complete\n\n## Objective\n\nDone.",
            encoding="utf-8",
        )
        result = build_output(None, tmpdir / "context-project")
        check("existing context found", result["has_context8"] is True)
        local = result.get("active_tasks_local", [])
        check("active task detected", len(local) == 1)
        check("active task status", local[0]["status"] == "In progress")

        # JSON output for SessionStart
        hook_data = {HOOK_EVENT_KEY: SESSION_START}
        json_out = run(tmpdir / "context-project", hook_data)
        check("JSON output for SessionStart", json_out.startswith('{"additionalContext":'))

    print(f"Self-test: {len(errors)} failure(s)")
    for e in errors:
        print(f"  {e}")
    sys.exit(1 if errors else 0)


def main():
    if "--self-test" in sys.argv:
        self_test()
        return

    cwd = Path.cwd()
    hook_data = read_stdin_json()
    output = run(cwd, hook_data)
    print(output)


if __name__ == "__main__":
    main()
