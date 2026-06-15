#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["questionary"]
# ///
"""
Dev Workflows Installer
Run with: uv run install.py [--uninstall] [--dry-run]
"""

import argparse
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

import questionary
from questionary import Choice

# ─── Config ───────────────────────────────────────────────────────────────────

REPO = "fnhernandorena/agents_prompts"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

SKILLS = [
    ("workflow-init",     "Bootstrap a new multi-repo workspace"),
    ("workflow-continue", "Resume an existing workspace session"),
    ("workflow-add-repo", "Add a new repo to an existing workspace"),
    ("project-init",      "Bootstrap a new single-repo project"),
    ("project-continue",  "Start a session on an existing project"),
    ("project-handoff",   "Close a session cleanly for the next agent"),
    ("project-audit",     "Assess a project with no or stale documentation"),
    ("task-plan",         "Produce a detailed implementation plan"),
    ("task-do",           "Execute a planned task step by step"),
    ("task-review",       "Pre-PR code review (correctness, security, tests)"),
    ("task-hotfix",       "Urgent production fix with controlled speed"),
    ("create-qa-agent",       "Generate a professional QA/Test engineer agent prompt"),
    ("create-architect-agent", "Generate a professional Software Architect agent prompt"),
    ("create-backend-agent",   "Generate a professional Backend developer agent prompt"),
    ("create-frontend-agent",  "Generate a professional Frontend developer agent prompt"),
    ("create-database-agent",  "Generate a professional Database expert agent prompt"),
    ("create-cloud-agent",     "Generate a professional Cloud architect agent prompt"),
    ("create-devops-agent",    "Generate a professional DevOps/SRE agent prompt"),
    ("create-security-agent",  "Generate a professional Security engineer agent prompt"),
    ("workflow-status",    "Multi-repo workspace visibility in one glance"),
    ("change-impact",      "Analyze blast radius of a proposed change before coding"),
    ("pr-description",     "Generate a structured PR description from the current diff"),
    ("deploy-plan",        "Plan a deployment with steps, rollback, and verification"),
    ("create-mobile-agent", "Generate a professional Mobile Developer agent prompt"),
    ("project-review",   "Full project architecture, security, and quality review"),
    ("dependency-audit", "Auditoría de dependencias: vulnerabilidades y versiones"),
    ("release",          "End-to-end release workflow: tag, changelog, publish"),
    ("task-continue",    "Resume a partially completed task from the last phase"),
]

SKILL_NAMES = [s[0] for s in SKILLS]

TOOLS = [
    {
        "id": "claude",
        "name": "Claude Code",
        "binaries": ["claude"],
        "detect": [Path.home() / ".claude"],
        "global_dir": Path.home() / ".claude" / "skills",
        "project_subdir": Path(".claude") / "skills",
        "files_per_skill": ["SKILL.md", "prompt.md"],
        "global_label": "~/.claude/skills/",
        "project_label": ".claude/skills/",
    },
    {
        "id": "codex",
        "name": "Codex (OpenAI)",
        "binaries": ["codex"],
        "detect": [Path.home() / ".codex", Path.home() / ".agents"],
        "global_dir": Path.home() / ".agents" / "skills",
        "project_subdir": Path(".agents") / "skills",
        "files_per_skill": ["SKILL.md", "prompt.md"],
        "global_label": "~/.agents/skills/",
        "project_label": ".agents/skills/",
    },
    {
        "id": "cursor",
        "name": "Cursor",
        "binaries": ["cursor"],
        "detect": [Path.home() / ".cursor"],
        "global_dir": Path.home() / ".cursor" / "skills",
        "project_subdir": Path(".cursor") / "skills",
        "files_per_skill": ["SKILL.md", "prompt.md"],
        "global_label": "~/.cursor/skills/",
        "project_label": ".cursor/skills/",
    },
    {
        "id": "gemini",
        "name": "Gemini CLI",
        "binaries": ["gemini"],
        "detect": [Path.home() / ".gemini"],
        "global_dir": Path.home() / ".gemini" / "skills",
        "project_subdir": Path(".agents") / "skills",
        "files_per_skill": ["SKILL.md"],
        "global_label": "~/.gemini/skills/",
        "project_label": ".agents/skills/",
    },
    {
        "id": "opencode",
        "name": "OpenCode",
        "binaries": ["opencode"],
        "detect": [
            Path.home() / ".config" / "opencode",
            Path.home() / ".opencode",
        ],
        "global_dir": Path.home() / ".config" / "opencode",
        "project_subdir": Path("."),
        "files_per_skill": None,
        "context_file": "AGENTS.md",
        "global_label": "~/.config/opencode/AGENTS.md",
        "project_label": "./AGENTS.md",
    },
    {
        "id": "hermes",
        "name": "Hermes Agent",
        "binaries": ["hermes"],
        "detect": [Path.home() / ".hermes"],
        "global_dir": Path.home() / ".hermes" / "skills" / "dev-workflows",
        "project_subdir": Path(".hermes") / "skills" / "dev-workflows",
        "files_per_skill": ["SKILL.md"],
        "global_label": "~/.hermes/skills/dev-workflows/",
        "project_label": ".hermes/skills/dev-workflows/",
    },
]

# ─── Source detection ─────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
LOCAL_SKILLS = SCRIPT_DIR / "skills"
SOURCE = "local" if LOCAL_SKILLS.exists() else "remote"

def detect_tool(tool: dict) -> bool:
    for path in tool["detect"]:
        if path.exists():
            return True
    for binary in tool.get("binaries", []):
        if shutil.which(binary):
            return True
    return False

def get_skill_files(skill: str) -> dict[str, str]:
    if SOURCE == "local":
        result = {}
        for fname in ["SKILL.md", "prompt.md"]:
            path = LOCAL_SKILLS / skill / fname
            if path.exists():
                result[fname] = path.read_text(encoding="utf-8")
        return result
    else:
        result = {}
        for fname in ["SKILL.md", "prompt.md"]:
            url = f"{RAW_BASE}/skills/{skill}/{fname}"
            try:
                with urllib.request.urlopen(url, timeout=10) as r:
                    result[fname] = r.read().decode("utf-8")
            except Exception as e:
                raise RuntimeError(f"Failed to fetch {url}: {e}") from e
        return result

def get_context_file(name: str) -> str:
    if SOURCE == "local":
        src = "CLAUDE.md" if name == "AGENTS.md" else name
        path = SCRIPT_DIR / src
        if path.exists():
            return path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Missing {src}")
    else:
        src = "CLAUDE.md" if name == "AGENTS.md" else name
        url = f"{RAW_BASE}/{src}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}") from e

# ─── Installation logic ───────────────────────────────────────────────────────

def backup_path(p: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return p.with_suffix(f".bak_{ts}")

def write_file(dest: Path, content: str, dry: bool) -> str:
    """Write file, backup if exists. Returns 'created' or 'updated'."""
    if dest.exists():
        if not dry:
            shutil.copy2(dest, backup_path(dest))
            dest.write_text(content, encoding="utf-8")
        return "updated"
    else:
        if not dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        return "created"

def install_tool(tool: dict, skills: list[str], base: Path, dry: bool) -> tuple[int, int, list[str]]:
    """Install skills + context file for one tool. Returns (created, updated, errors)."""
    created = updated = 0
    errors = []

    if tool.get("files_per_skill") and skills:
        for skill in skills:
            try:
                files = get_skill_files(skill)
            except Exception as e:
                errors.append(f"{skill}: {e}")
                continue
            for fname, content in files.items():
                status = write_file(base / skill / fname, content, dry)
                if status == "created": created += 1
                else: updated += 1

    if not tool.get("files_per_skill"):
        ctx = tool.get("context_file", "CLAUDE.md")
        try:
            content = get_context_file(ctx)
            status = write_file(base / ctx, content, dry)
            if status == "created": created += 1
            else: updated += 1
        except Exception as e:
            errors.append(f"{ctx}: {e}")

    return created, updated, errors

def uninstall_tool(tool: dict, skills: list[str], base: Path, dry: bool) -> tuple[int, list[str]]:
    """Remove skills + context file for one tool. Returns (removed, errors)."""
    removed = 0
    errors = []

    if tool.get("files_per_skill") and skills:
        for skill in skills:
            skill_dir = base / skill
            if skill_dir.exists():
                if not dry:
                    shutil.rmtree(skill_dir)
                removed += 1

    if not tool.get("files_per_skill"):
        ctx = tool.get("context_file", "CLAUDE.md")
        dest = base / ctx
        if dest.exists():
            if not dry:
                dest.unlink()
            removed += 1

    return removed, errors

# ─── Main ─────────────────────────────────────────────────────────────────────

def abort(msg: str = "Aborted."):
    print(f"\n  {msg}")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Dev Workflows installer")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run",   action="store_true")
    args = parser.parse_args()

    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       Dev Workflows Installer        ║")
    print("  ╚══════════════════════════════════════╝")
    mode = "uninstall" if args.uninstall else "install"
    dry_tag = "  [dry-run]" if args.dry_run else ""
    print(f"  source: {SOURCE}  |  mode: {mode}{dry_tag}\n")

    if SOURCE == "remote":
        ok = questionary.confirm(
            "Local skills/ not found. Download from GitHub?", default=True
        ).ask()
        if not ok:
            abort()

    # ── Step 1: Tools ────────────────────────────────────────────────────────
    tool_choices = [
        Choice(
            title=f"{t['name']}  ({'detected' if detect_tool(t) else 'not detected'})",
            value=t["id"],
            checked=detect_tool(t),
        )
        for t in TOOLS
    ]
    selected_ids = questionary.checkbox(
        "Select tools to install for:", choices=tool_choices
    ).ask()
    if not selected_ids:
        abort("No tools selected.")
    selected_tools = [t for t in TOOLS if t["id"] in selected_ids]

    # ── Step 2: Scope ────────────────────────────────────────────────────────
    global_paths  = "  ·  ".join(t.get("global_label",  "") for t in selected_tools)
    project_paths = "  ·  ".join(t.get("project_label", "") for t in selected_tools)

    scope_choice = questionary.select(
        "Where to install?",
        choices=[
            Choice(f"Global         ({global_paths})",  value="global"),
            Choice(f"This project   ({project_paths})", value="project_current"),
            Choice("Other path…",                       value="project_other"),
        ],
    ).ask()
    if scope_choice is None:
        abort()

    if scope_choice == "global":
        scope = "global"
        project_dir = None
    elif scope_choice == "project_current":
        scope = "project"
        project_dir = Path.cwd()
    else:
        scope = "project"
        raw = questionary.path("Project path:").ask()
        if not raw:
            abort()
        project_dir = Path(raw).expanduser().resolve()
        if not project_dir.exists():
            abort(f"Path not found: {project_dir}")

    # ── Step 3: Skills ───────────────────────────────────────────────────────
    skill_tools   = [t for t in selected_tools if t.get("files_per_skill")]
    context_tools = [t for t in selected_tools if not t.get("files_per_skill")]

    selected_skills: list[str] = []
    if skill_tools:
        skill_choices = [
            Choice(title=f"{name}  —  {desc}", value=name, checked=True)
            for name, desc in SKILLS
        ]
        selected_skills = questionary.checkbox(
            "Select skills to install:", choices=skill_choices
        ).ask() or []
        if not selected_skills and not context_tools:
            abort("No skills selected.")

    # ── Step 4: Confirm ──────────────────────────────────────────────────────
    scope_label = "global" if scope == "global" else str(project_dir)
    print(f"\n  Tools : {', '.join(t['name'] for t in selected_tools)}")
    print(f"  Scope : {scope_label}")
    if selected_skills:
        print(f"  Skills: {len(selected_skills)} selected")
    if args.dry_run:
        print("  [dry-run — no files will be written]")

    action = "Uninstall" if args.uninstall else "Install"
    ok = questionary.confirm(f"\n{action}?", default=True).ask()
    if not ok:
        abort()

    # ── Step 5: Execute ──────────────────────────────────────────────────────
    print()
    total_errors: list[str] = []

    for tool in selected_tools:
        if scope == "global":
            base = tool.get("global_dir")
            if base is None:
                print(f"  ⚠  {tool['name']}: global install not supported, skipped")
                continue
            dest_label = tool.get("global_label", str(base))
        else:
            base = project_dir / tool["project_subdir"]
            dest_label = tool.get("project_label", str(base))

        if args.uninstall:
            removed, errors = uninstall_tool(tool, selected_skills, base, args.dry_run)
            if errors:
                print(f"  ✗  {tool['name']}: {len(errors)} error(s)")
                for e in errors:
                    print(f"       {e}")
                total_errors.extend(errors)
            else:
                tag = "(dry-run)" if args.dry_run else ""
                print(f"  ✓  {tool['name']}  —  {removed} item(s) removed  {tag}")
        else:
            created, updated, errors = install_tool(tool, selected_skills, base, args.dry_run)
            if errors:
                print(f"  ✗  {tool['name']}: {len(errors)} error(s)")
                for e in errors:
                    print(f"       {e}")
                total_errors.extend(errors)
            else:
                tag = "(dry-run)" if args.dry_run else ""
                print(f"  ✓  {tool['name']}  →  {dest_label}  ({created} created, {updated} updated)  {tag}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    if total_errors:
        print(f"  Done with {len(total_errors)} error(s). Check output above.")
    else:
        verb = "Uninstalled" if args.uninstall else "Installed"
        print(f"  {verb} successfully.")

    if not args.uninstall and not args.dry_run and not total_errors:
        for t in selected_tools:
            if t["id"] == "claude":
                print("\n  Claude Code skills available as:")
                for skill in selected_skills:
                    print(f"    /dev-workflows:{skill}")
            elif t["id"] == "hermes":
                print("\n  Hermes Agent skills loaded. Use them by typing:")
                for skill in selected_skills:
                    print(f"    /skill dev-workflows:{skill}")
                print("\n  Or launch with: hermes -s dev-workflows:workflow-init")
        print("\n  Restart your agent to load new skills.")

if __name__ == "__main__":
    main()
