#!/usr/bin/env python3
"""Refresh the blog's reviewed OpenClaw contribution snapshot.

The personal-site updater remains the canonical GitHub fetcher and reviewed
scope-label registry. This wrapper only exports its verified result into the
Eleventy data file; unknown PRs fail closed before public copy can change.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "src" / "_data" / "openclawContrib.json"
DEFAULT_SOURCE = REPO_ROOT.parent / "jingxiao-cai" / "scripts" / "update_openclaw_contrib.py"
CONTRIBUTIONS_URL = (
    "https://github.com/openclaw/openclaw/pulls"
    "?q=is%3Apr+author%3Aanyech+is%3Amerged"
)
WRITING_URL = "/jingxiao-cai-blog/topics/openclaw-self-hosting.html"
SCOPE = "Runtime reliability · delivery · document tooling"
DEFAULT_MAX_AGE_DAYS = 30


def load_source(path: Path):
    if not path.is_file():
        raise RuntimeError(f"canonical updater not found: {path}")
    spec = importlib.util.spec_from_file_location("personal_site_openclaw_contrib", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load canonical updater: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_snapshot(
    source,
    *,
    prs: list[dict[str, object]] | None = None,
    verified_date: str | None = None,
) -> dict[str, object]:
    prs = source.fetch_merged_prs() if prs is None else prs
    if not prs:
        raise RuntimeError("GitHub returned zero merged OpenClaw PRs; refusing to replace snapshot")
    unknown = source.unknown_scope_prs(prs)
    if unknown:
        numbers = ", ".join(f"#{int(pr['number'])}" for pr in unknown)
        raise RuntimeError(f"unreviewed merged PR scope(s): {numbers}; refusing public update")

    latest = prs[0]
    number = int(latest["number"])
    return {
        "mergedPrCount": len(prs),
        "scope": SCOPE,
        "latest": {
            "number": number,
            "label": source.KNOWN_SCOPE[number],
            "url": str(latest["url"]),
            "mergedAt": str(latest["merged_at"]),
        },
        "contributionsUrl": CONTRIBUTIONS_URL,
        "writingUrl": WRITING_URL,
        "verifiedDate": verified_date or datetime.now(timezone.utc).date().isoformat(),
        "source": "personal-site OpenClaw contribution updater",
    }


def load_existing() -> dict[str, object] | None:
    if not OUTPUT.exists():
        return None
    try:
        value = json.loads(OUTPUT.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def semantic_snapshot(snapshot: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in snapshot.items() if key != "verifiedDate"}


def choose_verified_date(
    candidate: dict[str, object],
    existing: dict[str, object] | None,
    *,
    today: date,
    max_age_days: int,
) -> str:
    """Avoid daily republishing while bounding public snapshot staleness."""

    if existing and semantic_snapshot(existing) == semantic_snapshot(candidate):
        raw = existing.get("verifiedDate")
        if isinstance(raw, str):
            try:
                previous = date.fromisoformat(raw)
            except ValueError:
                previous = None
            if previous is not None:
                age = (today - previous).days
                if 0 <= age < max_age_days:
                    return raw
    return today.isoformat()


def refreshed_snapshot(
    source,
    *,
    prs: list[dict[str, object]] | None = None,
    today: date | None = None,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
) -> dict[str, object]:
    if max_age_days < 1:
        raise ValueError("max_age_days must be at least 1")
    current_day = today or datetime.now(timezone.utc).date()
    candidate = build_snapshot(source, prs=prs, verified_date=current_day.isoformat())
    candidate["verifiedDate"] = choose_verified_date(
        candidate,
        load_existing(),
        today=current_day,
        max_age_days=max_age_days,
    )
    return candidate


def rendered(snapshot: dict[str, object]) -> str:
    return json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-script", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true", help="exit nonzero when the committed snapshot differs")
    parser.add_argument("--json", action="store_true", help="print the refreshed snapshot")
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    args = parser.parse_args()

    snapshot = refreshed_snapshot(
        load_source(args.source_script.resolve()),
        max_age_days=args.max_age_days,
    )
    content = rendered(snapshot)
    changed = not OUTPUT.exists() or OUTPUT.read_text() != content

    if args.check:
        if changed:
            print("OpenClaw contribution snapshot is stale", file=sys.stderr)
            return 1
    elif changed:
        OUTPUT.write_text(content)

    if args.json:
        print(json.dumps({"changed": changed, "snapshot": snapshot}, ensure_ascii=False))
    else:
        print(f"OpenClaw contribution snapshot {'would change' if args.check and changed else 'updated' if changed else 'current'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
