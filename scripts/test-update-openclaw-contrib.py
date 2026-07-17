#!/usr/bin/env python3
"""Focused regression tests for the OpenClaw contribution snapshot updater."""

from __future__ import annotations

from datetime import date
import importlib.util
import json
from pathlib import Path
import tempfile


SCRIPT = Path(__file__).with_name("update-openclaw-contrib.py")
SPEC = importlib.util.spec_from_file_location("blog_openclaw_contrib_test", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeSource:
    KNOWN_SCOPE = {123: "reviewed runtime fix", 124: "reviewed delivery fix"}

    @staticmethod
    def unknown_scope_prs(prs):
        return [pr for pr in prs if int(pr["number"]) not in FakeSource.KNOWN_SCOPE]


def prs(number: int = 123):
    return [
        {
            "number": number,
            "url": f"https://github.com/openclaw/openclaw/pull/{number}",
            "merged_at": "2026-07-17T00:00:00Z",
        }
    ]


def with_output(existing: dict[str, object] | None, callback):
    original = MODULE.OUTPUT
    with tempfile.TemporaryDirectory() as temp:
        MODULE.OUTPUT = Path(temp) / "openclawContrib.json"
        if existing is not None:
            MODULE.OUTPUT.write_text(json.dumps(existing))
        try:
            return callback()
        finally:
            MODULE.OUTPUT = original


def test_preserves_recent_date_without_semantic_change() -> None:
    candidate = MODULE.build_snapshot(FakeSource, prs=prs(), verified_date="2026-07-17")
    candidate["verifiedDate"] = "2026-07-01"
    result = with_output(
        candidate,
        lambda: MODULE.refreshed_snapshot(
            FakeSource,
            prs=prs(),
            today=date(2026, 7, 17),
            max_age_days=30,
        ),
    )
    assert result["verifiedDate"] == "2026-07-01"


def test_refreshes_date_at_staleness_boundary() -> None:
    candidate = MODULE.build_snapshot(FakeSource, prs=prs(), verified_date="2026-06-17")
    result = with_output(
        candidate,
        lambda: MODULE.refreshed_snapshot(
            FakeSource,
            prs=prs(),
            today=date(2026, 7, 17),
            max_age_days=30,
        ),
    )
    assert result["verifiedDate"] == "2026-07-17"


def test_semantic_change_refreshes_date_immediately() -> None:
    existing = MODULE.build_snapshot(FakeSource, prs=prs(), verified_date="2026-07-01")
    result = with_output(
        existing,
        lambda: MODULE.refreshed_snapshot(
            FakeSource,
            prs=prs(124),
            today=date(2026, 7, 17),
            max_age_days=30,
        ),
    )
    assert result["verifiedDate"] == "2026-07-17"
    assert result["latest"]["number"] == 124


def test_unknown_scope_fails_closed() -> None:
    try:
        MODULE.build_snapshot(FakeSource, prs=prs(999), verified_date="2026-07-17")
    except RuntimeError as exc:
        assert "unreviewed merged PR" in str(exc)
    else:
        raise AssertionError("unknown PR scope did not fail closed")


def main() -> None:
    test_preserves_recent_date_without_semantic_change()
    test_refreshes_date_at_staleness_boundary()
    test_semantic_change_refreshes_date_immediately()
    test_unknown_scope_fails_closed()
    print("OPENCLAW_CONTRIB_UPDATER_TESTS_OK")


if __name__ == "__main__":
    main()
