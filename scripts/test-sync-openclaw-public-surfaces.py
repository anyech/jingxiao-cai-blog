#!/usr/bin/env python3
"""Focused regression tests for the public-surface sync coordinator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("sync-openclaw-public-surfaces.py")
SPEC = importlib.util.spec_from_file_location("sync_openclaw_public_surfaces", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
coordinator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coordinator)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


class PublicSurfaceSyncCoordinatorTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Coordinator Test")
        git(repo, "config", "user.email", "coordinator-test@example.invalid")
        (repo / "src" / "posts").mkdir(parents=True)
        (repo / "src" / "index.njk").write_text("tracked\n")
        (repo / ".gitignore").write_text("src/assets/*.tmp\n")
        git(repo, "add", ".gitignore", "src/index.njk")
        git(repo, "commit", "-q", "-m", "fixture")
        return repo

    def test_tracked_source_allows_unrelated_untracked_artifact(self) -> None:
        repo = self.make_repo()
        (repo / "review").mkdir()
        (repo / "review" / "local-notes.md").write_text("not a build input\n")

        coordinator.ensure_blog_build_inputs_tracked(repo)

    def test_nontracked_eleventy_inputs_fail_closed(self) -> None:
        repo = self.make_repo()
        (repo / "src" / "posts" / "draft.md").write_text("unreviewed\n")
        (repo / "src" / "assets").mkdir()
        (repo / "src" / "assets" / "preview.tmp").write_text("ignored but public\n")

        with self.assertRaisesRegex(RuntimeError, "non-tracked Eleventy inputs") as caught:
            coordinator.ensure_blog_build_inputs_tracked(repo)

        self.assertIn("src/posts/draft.md", str(caught.exception))
        self.assertIn("src/assets/preview.tmp", str(caught.exception))

    def test_guard_failure_precedes_build_and_publish(self) -> None:
        blocker = RuntimeError("non-tracked Eleventy inputs")
        with mock.patch.object(coordinator, "ensure_repo_ready") as ready, mock.patch.object(
            coordinator,
            "ensure_blog_build_inputs_tracked",
            side_effect=blocker,
        ), mock.patch.object(coordinator, "load_module") as load_module, mock.patch.object(
            coordinator,
            "run",
        ) as run, mock.patch.object(coordinator, "commit_blog_source") as commit_source, mock.patch.object(
            coordinator,
            "publish_blog_main",
        ) as publish_main:
            with self.assertRaisesRegex(RuntimeError, "non-tracked Eleventy inputs"):
                coordinator.synchronize(pull=False, commit_push=True, max_age_days=30)

        self.assertEqual(ready.call_count, 2)
        load_module.assert_not_called()
        run.assert_not_called()
        commit_source.assert_not_called()
        publish_main.assert_not_called()


if __name__ == "__main__":
    unittest.main()
