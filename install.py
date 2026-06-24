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
    # (name, description, category)
    # Category defaults to "dev-workflows" for all existing skills; document and other
    # categories set explicitly so the installer routes to the right Hermes subdirectory.
    ("workflow-init",     "Bootstrap a new multi-repo workspace",                    "dev-workflows"),
    ("workflow-continue", "Resume an existing workspace session",                    "dev-workflows"),
    ("workflow-add-repo", "Add a new repo to an existing workspace",                 "dev-workflows"),
    ("project-init",      "Bootstrap a new single-repo project",                     "dev-workflows"),
    ("project-continue",  "Start a session on an existing project",                  "dev-workflows"),
    ("project-handoff",   "Close a session cleanly for the next agent",              "dev-workflows"),
    ("project-audit",     "Assess a project with no or stale documentation",         "dev-workflows"),
    ("task-plan",         "Produce a detailed implementation plan",                  "dev-workflows"),
    ("task-do",           "Execute a planned task step by step",                     "dev-workflows"),
    ("task-review",       "Pre-PR code review (correctness, security, tests)",       "dev-workflows"),
    ("task-hotfix",       "Urgent production fix with controlled speed",             "dev-workflows"),
    ("create-qa-agent",       "Generate a professional QA/Test engineer agent prompt",       "dev-workflows"),
    ("create-architect-agent", "Generate a professional Software Architect agent prompt",     "dev-workflows"),
    ("create-backend-agent",   "Generate a professional Backend developer agent prompt",       "dev-workflows"),
    ("create-frontend-agent",  "Generate a professional Frontend developer agent prompt",      "dev-workflows"),
    ("create-database-agent",  "Generate a professional Database expert agent prompt",         "dev-workflows"),
    ("create-cloud-agent",     "Generate a professional Cloud architect agent prompt",         "dev-workflows"),
    ("create-devops-agent",    "Generate a professional DevOps/SRE agent prompt",              "dev-workflows"),
    ("create-security-agent",  "Generate a professional Security engineer agent prompt",       "dev-workflows"),
    ("workflow-status",    "Multi-repo workspace visibility in one glance",          "dev-workflows"),
    ("change-impact",      "Analyze blast radius of a proposed change before coding", "dev-workflows"),
    ("pr-description",     "Generate a structured PR description from the current diff", "dev-workflows"),
    ("deploy-plan",        "Plan a deployment with steps, rollback, and verification", "dev-workflows"),
    ("create-mobile-agent", "Generate a professional Mobile Developer agent prompt",  "dev-workflows"),
    ("project-review",   "Full project architecture, security, and quality review",          "dev-workflows"),
    ("dependency-audit", "Auditoría de dependencias: vulnerabilidades y versiones",          "dev-workflows"),
    ("release",          "End-to-end release workflow: tag, changelog, publish",              "dev-workflows"),
    ("task-compacting",  "Archive completed/cancelled tasks with monthly LLM-friendly summaries", "dev-workflows"),
    ("task-continue",    "Resume a partially completed task from the last phase",             "dev-workflows"),
    ("repo-cleanup",     "Limpieza segura de ramas git: propias automático, ajenas con permiso", "dev-workflows"),
    ("tag-create",       "Crea tags git semver: analiza cambios, sugiere versión, pide confirmación", "dev-workflows"),
    ("make-report",      "Generate structured markdown reports optimized for ClickUp Docs (tables, diagrams, formatting)", "document"),
]

SKILL_NAMES = [s[0] for s in SKILLS]
SKILL_CATEGORIES = {s[0]: s[2] for s in SKILLS}

# ─── Hook configuration ────────────────────────────────────────────────────────

NATIVE_HOOK_TOOLS = {"claude"}

HOOK_FALLBACK_START = "<!-- dev-workflows-session-start-hook-start -->"
HOOK_FALLBACK_END = "<!-- dev-workflows-session-start-hook-end -->"

HOOK_FALLBACK_TEMPLATE = """{start}
## Session-Start Hook

At startup, run the session-start hook to check .context8/ state:

    python3 {hook_path}

- If .context8/ is missing, follow the hook's instructions to run the correct init skill before user work.
- If active tasks are reported, load or mention them before starting new work.

For more detail see the Dev Workflows README or run the hook with `--help`.
{end}
"""

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
        "global_dir": Path.home() / ".hermes" / "skills",
        "project_subdir": Path(".hermes") / "skills",
        "files_per_skill": ["SKILL.md"],
        "global_label": "~/.hermes/skills/",
        "project_label": ".hermes/skills/",
    },
]

# ─── Hook helpers ──────────────────────────────────────────────────────────────

def get_hook_script_content() -> str:
    """Return the hook script content from local or remote source."""
    if SOURCE == "local":
        path = SCRIPT_DIR / "hooks" / "context8_session_start.py"
        if path.exists():
            return path.read_text(encoding="utf-8")
        raise FileNotFoundError("Missing hooks/context8_session_start.py")
    else:
        url = f"{RAW_BASE}/hooks/context8_session_start.py"
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.read().decode("utf-8")


def get_hook_config_content() -> str:
    """Return hooks.json content from local or remote source."""
    if SOURCE == "local":
        path = SCRIPT_DIR / "hooks" / "hooks.json"
        if path.exists():
            return path.read_text(encoding="utf-8")
        raise FileNotFoundError("Missing hooks/hooks.json")
    else:
        url = f"{RAW_BASE}/hooks/hooks.json"
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.read().decode("utf-8")


def install_hook_assets(tool: dict, base: Path, dry: bool) -> tuple[int, int, list[str]]:
    """Install hook script and (for native hook tools) hooks.json.
    Returns (created, updated, errors).
    Hook script goes to base/hooks/context8_session_start.py.
    hooks.json (native) goes to base.parent/hooks/hooks.json.
    """
    created = updated = 0
    errors = []

    # Hook script goes in base/hooks/
    hooks_dir = base / "hooks"
    try:
        script_content = get_hook_script_content()
        script_dest = hooks_dir / "context8_session_start.py"
        status = write_file(script_dest, script_content, dry)
        if status == "created":
            created += 1
        else:
            updated += 1
    except Exception as e:
        errors.append(f"hook script: {e}")

    # hooks.json for native hook tools goes in plugin_root/hooks/
    if tool["id"] in NATIVE_HOOK_TOOLS:
        try:
            config_content = get_hook_config_content()
            plugin_root = base.parent  # skills dir is child of plugin root
            config_dest = plugin_root / "hooks" / "hooks.json"
            status = write_file(config_dest, config_content, dry)
            if status == "created":
                created += 1
            else:
                updated += 1
        except Exception as e:
            errors.append(f"hooks.json: {e}")

    return created, updated, errors


def remove_hook_assets(tool: dict, base: Path, dry: bool) -> tuple[int, list[str]]:
    """Remove hook assets. Returns (removed, errors)."""
    removed = 0
    errors = []

    hooks_dir = base / "hooks"
    script_dest = hooks_dir / "context8_session_start.py"
    if script_dest.exists():
        if not dry:
            script_dest.unlink()
        removed += 1

    if tool["id"] in NATIVE_HOOK_TOOLS:
        plugin_root = base.parent
        config_dest = plugin_root / "hooks" / "hooks.json"
        if config_dest.exists():
            if not dry:
                config_dest.unlink()
            removed += 1

    # Remove empty hooks dir
    if hooks_dir.exists() and not dry:
        try:
            hooks_dir.rmdir()  # only if empty
        except OSError:
            pass

    return removed, errors


def managed_context_path(tool: dict, base: Path) -> Path | None:
    """Return the path of the managed context file for this tool, if any."""
    ctx = tool.get("context_file")
    if not ctx:
        return None
    return base / ctx


def inject_hook_fallback_block(ctx_dest: Path, hook_path: str, dry: bool) -> tuple[str, str]:
    """Inject or update the managed hook fallback block in a context file.
    Returns (action, detail)."""
    block = HOOK_FALLBACK_TEMPLATE.format(
        start=HOOK_FALLBACK_START,
        end=HOOK_FALLBACK_END,
        hook_path=hook_path,
    )

    if not ctx_dest.exists():
        return "skipped", "context file does not exist"

    content = ctx_dest.read_text(encoding="utf-8")

    if HOOK_FALLBACK_START in content and HOOK_FALLBACK_END in content:
        start_idx = content.index(HOOK_FALLBACK_START)
        end_idx = content.index(HOOK_FALLBACK_END) + len(HOOK_FALLBACK_END)
        new_content = content[:start_idx] + block + content[end_idx:]
        action = "updated"
    else:
        new_content = content.rstrip() + "\n" + block + "\n"
        action = "created"

    if not dry:
        shutil.copy2(ctx_dest, backup_path(ctx_dest))
        ctx_dest.write_text(new_content, encoding="utf-8")

    return action, "hook fallback block"


def remove_hook_fallback_block(ctx_dest: Path, dry: bool) -> tuple[bool, str]:
    """Remove the managed hook fallback block from a context file."""
    if not ctx_dest.exists():
        return False, "not found"

    content = ctx_dest.read_text(encoding="utf-8")

    if HOOK_FALLBACK_START not in content or HOOK_FALLBACK_END not in content:
        return False, "no fallback block found"

    start_idx = content.index(HOOK_FALLBACK_START)
    end_idx = content.index(HOOK_FALLBACK_END) + len(HOOK_FALLBACK_END)
    new_content = content[:start_idx] + content[end_idx:]

    if not dry:
        shutil.copy2(ctx_dest, backup_path(ctx_dest))
        ctx_dest.write_text(new_content, encoding="utf-8")

    return True, "removed fallback block"


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

def install_skill_for_tool(tool: dict, skill: str, base: Path, dry: bool) -> tuple[int, int, list[str]]:
    """Install one skill for one tool. Returns (created, updated, errors)."""
    created = updated = 0
    errors = []

    try:
        files = get_skill_files(skill)
    except Exception as e:
        return 0, 0, [f"{skill}: {e}"]

    category = SKILL_CATEGORIES.get(skill, "dev-workflows")

    for fname, content in files.items():
        if tool["id"] == "hermes":
            # Hermes uses category subdirectories: skills/<category>/<name>/SKILL.md
            dest = base / category / skill / fname
        else:
            # All other agents use flat structure: skills/<name>/SKILL.md
            dest = base / skill / fname
        status = write_file(dest, content, dry)
        if status == "created":
            created += 1
        else:
            updated += 1

    return created, updated, errors

def install_tool(tool: dict, skills: list[str], base: Path, dry: bool) -> tuple[int, int, list[str]]:
    """Install skills + context file + hook assets for one tool. Returns (created, updated, errors)."""
    created = updated = 0
    errors = []

    if tool.get("files_per_skill") and skills:
        for skill in skills:
            c, u, e = install_skill_for_tool(tool, skill, base, dry)
            created += c
            updated += u
            errors.extend(e)

    if not tool.get("files_per_skill"):
        ctx = tool.get("context_file", "CLAUDE.md")
        try:
            content = get_context_file(ctx)
            status = write_file(base / ctx, content, dry)
            if status == "created": created += 1
            else: updated += 1
        except Exception as e:
            errors.append(f"{ctx}: {e}")

    # Install hook assets
    if not errors:
        c, u, e = install_hook_assets(tool, base, dry)
        created += c
        updated += u
        errors.extend(e)

    # Inject fallback block into context file for non-native-hook tools
    if tool["id"] not in NATIVE_HOOK_TOOLS:
        ctx_dest = managed_context_path(tool, base)
        if ctx_dest:
            hook_path = base / "hooks" / "context8_session_start.py"
            action, detail = inject_hook_fallback_block(ctx_dest, str(hook_path), dry)
            if action in ("created", "updated"):
                updated += 1

    return created, updated, errors

def uninstall_tool(tool: dict, skills: list[str], base: Path, dry: bool) -> tuple[int, list[str]]:
    """Remove skills + context file + hook assets for one tool. Returns (removed, errors)."""
    removed = 0
    errors = []

    if tool.get("files_per_skill") and skills:
        for skill in skills:
            category = SKILL_CATEGORIES.get(skill, "dev-workflows")
            if tool["id"] == "hermes":
                skill_dir = base / category / skill
            else:
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

    # Remove hook assets
    r, e = remove_hook_assets(tool, base, dry)
    removed += r
    errors.extend(e)

    # Remove fallback block from context file
    ctx_dest = managed_context_path(tool, base)
    if ctx_dest and ctx_dest.exists():
        ok, _ = remove_hook_fallback_block(ctx_dest, dry)
        if ok:
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
            for name, desc, _cat in SKILLS
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
                    cat = SKILL_CATEGORIES.get(skill, "dev-workflows")
                    print(f"    /{cat}:{skill}")
            elif t["id"] == "hermes":
                print("\n  Hermes Agent skills loaded. Use them by typing:")
                for skill in selected_skills:
                    cat = SKILL_CATEGORIES.get(skill, "dev-workflows")
                    print(f"    /skill {cat}:{skill}")
        print("\n  Restart your agent to load new skills.")

if __name__ == "__main__":
    main()
