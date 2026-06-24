"""Tests for the session-start hook."""

import json
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hooks.context8_session_start import (
    build_output,
    classify_directory,
    scan_tasks,
    format_text,
    format_json,
    SESSION_START,
    HOOK_EVENT_KEY,
)


class TestClassifyDirectory(unittest.TestCase):
    def test_project_with_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / ".git").mkdir()
            self.assertEqual(classify_directory(tmpdir), "project")

    def test_project_with_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "pyproject.toml").touch()
            self.assertEqual(classify_directory(tmpdir), "project")

    def test_workspace_with_child_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "repo-a" / ".git").mkdir(parents=True)
            (tmpdir / "repo-b" / ".git").mkdir(parents=True)
            self.assertEqual(classify_directory(tmpdir), "workspace")

    def test_workspace_with_git_and_child_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / ".git").mkdir()
            (tmpdir / "repo-a" / ".git").mkdir(parents=True)
            self.assertEqual(classify_directory(tmpdir), "workspace")

    def test_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            self.assertEqual(classify_directory(tmpdir), "unknown")


class TestScanTasks(unittest.TestCase):
    def test_finds_active_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            (tasks_dir / "active.md").write_text(
                "# Task\n\n**Status**: In progress\n\nDo it.", encoding="utf-8"
            )
            (tasks_dir / "done.md").write_text(
                "# Task\n\n**Status**: Complete\n\nDone.", encoding="utf-8"
            )
            results = scan_tasks(tasks_dir)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["status"], "In progress")

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = scan_tasks(Path(tmp))
            self.assertEqual(results, [])

    def test_non_existent_dir(self):
        results = scan_tasks(Path("/nonexistent/.context8/tasks"))
        self.assertEqual(results, [])


class TestBuildOutput(unittest.TestCase):
    def test_missing_context8_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / ".git").mkdir()
            output = build_output(None, tmpdir)
            self.assertFalse(output["has_context8"])
            self.assertEqual(output["classification"], "project")
            self.assertIn("project-init", output["instructions"][0])

    def test_missing_context8_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "repo-a" / ".git").mkdir(parents=True)
            (tmpdir / "repo-b" / ".git").mkdir(parents=True)
            output = build_output(None, tmpdir)
            self.assertFalse(output["has_context8"])
            self.assertEqual(output["classification"], "workspace")
            self.assertIn("workflow-init", output["instructions"][0])

    def test_existing_context8(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / ".context8" / "tasks").mkdir(parents=True)
            (tmpdir / ".context8" / "PROJECT_OVERVIEW.md").write_text(
                "# Test\n\nStable.", encoding="utf-8"
            )
            (tmpdir / ".context8" / "tasks" / "active.md").write_text(
                "# Task\n\n**Status**: Planned\n\nDo it.", encoding="utf-8"
            )
            output = build_output(None, tmpdir)
            self.assertTrue(output["has_context8"])
            self.assertIn("PROJECT_OVERVIEW.md", output["context_summary"])
            self.assertEqual(len(output["active_tasks_local"]), 1)


class TestOutputFormat(unittest.TestCase):
    def test_text_format(self):
        output = {
            "cwd": "/test",
            "has_context8": True,
            "context_summary": {},
            "active_tasks_local": [],
            "active_tasks_child_repos": [],
        }
        text = format_text(output)
        self.assertIn(".context8/ found", text)

    def test_json_format_for_session_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / ".context8").mkdir()
            hook_data = {HOOK_EVENT_KEY: SESSION_START}
            output = build_output(hook_data, tmpdir)
            json_str = format_json(output)
            parsed = json.loads(json_str)
            self.assertIn("additionalContext", parsed)
            self.assertIn(".context8/ found", parsed["additionalContext"])


if __name__ == "__main__":
    unittest.main()
