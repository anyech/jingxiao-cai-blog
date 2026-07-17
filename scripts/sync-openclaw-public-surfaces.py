#!/usr/bin/env python3
"""Synchronize reviewed OpenClaw contribution proof across both public sites.

The personal-site updater remains the only GitHub fetcher and KNOWN_SCOPE
registry. This coordinator prepares and validates both sites before publishing,
fails closed on unknown PRs, and uses the blog's source -> dist -> main flow.
"""

from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import urllib.request


BLOG_REPO = Path(__file__).resolve().parents[1]
PERSONAL_REPO = BLOG_REPO.parent / "jingxiao-cai"
PERSONAL_SCRIPT = PERSONAL_REPO / "scripts" / "update_openclaw_contrib.py"
BLOG_UPDATER = BLOG_REPO / "scripts" / "update-openclaw-contrib.py"
BLOG_SOURCE_BRANCH = "eleventy-migration-hardening-20260520"
BLOG_SNAPSHOT = BLOG_REPO / "src" / "_data" / "openclawContrib.json"
BLOG_URL = "https://anyech.github.io/jingxiao-cai-blog/"
LOCK_PATH = Path("/tmp/jingxiao-cai-openclaw-public-surfaces.lock")
PRESERVED_MAIN_PATHS = (".github", "DEPLOYMENT.md", "LICENSE")


def load_module(name: str, path: Path):
    if not path.is_file():
        raise RuntimeError(f"required updater is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load updater: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(
    argv: list[str],
    *,
    cwd: Path,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()[-2000:]
        raise RuntimeError(f"{' '.join(argv)} exited {proc.returncode}: {detail}")
    return proc


def git(repo: Path, *args: str, timeout: int = 120) -> str:
    return run(["git", *args], cwd=repo, timeout=timeout).stdout.strip()


def ensure_repo_ready(repo: Path, branch: str, *, pull: bool) -> None:
    actual = git(repo, "branch", "--show-current")
    if actual != branch:
        raise RuntimeError(f"{repo}: expected branch {branch!r}, found {actual!r}")
    if git(repo, "status", "--porcelain=v1", "--untracked-files=no"):
        raise RuntimeError(f"{repo}: tracked worktree is dirty; refusing automated publish")
    if pull:
        git(repo, "pull", "--ff-only", "origin", branch, timeout=180)
    counts = git(repo, "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}").split()
    if counts != ["0", "0"]:
        raise RuntimeError(f"{repo}: branch is not synchronized with origin/{branch}: {counts}")


def write_blog_snapshot(blog_updater, snapshot: dict[str, object]) -> bool:
    content = blog_updater.rendered(snapshot)
    changed = not BLOG_SNAPSHOT.exists() or BLOG_SNAPSHOT.read_text() != content
    if changed:
        BLOG_SNAPSHOT.write_text(content)
    return changed


def restore_text(path: Path, original: str) -> None:
    if path.read_text() != original:
        path.write_text(original)


def blog_main_matches(snapshot: dict[str, object]) -> bool:
    git(BLOG_REPO, "fetch", "origin", "main", timeout=180)
    proc = subprocess.run(
        ["git", "show", "origin/main:index.html"],
        cwd=BLOG_REPO,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        return False
    latest = snapshot["latest"]
    assert isinstance(latest, dict)
    markers = (
        f"<strong>{snapshot['mergedPrCount']}</strong>",
        str(latest["url"]),
        str(latest["label"]),
        f'datetime="{snapshot["verifiedDate"]}"',
    )
    return all(marker in proc.stdout for marker in markers)


def commit_blog_source() -> str:
    git(BLOG_REPO, "add", str(BLOG_SNAPSHOT.relative_to(BLOG_REPO)))
    git(BLOG_REPO, "commit", "-m", "Refresh OpenClaw contribution snapshot")
    git(BLOG_REPO, "push", "origin", BLOG_SOURCE_BRANCH, timeout=180)
    return git(BLOG_REPO, "rev-parse", "--short", "HEAD")


def sanitize_generated_homepage() -> None:
    homepage = (BLOG_REPO / "dist" / "index.html").read_text()
    forbidden = ("/home/ubuntu", "channel:", "MOLTBOOK_API_KEY", "GITHUB_TOKEN=", "TODO", "TBD")
    hits = [value for value in forbidden if value in homepage]
    if hits:
        raise RuntimeError(f"generated homepage failed sanitization guard: {hits}")


def publish_blog_main() -> str | None:
    git(BLOG_REPO, "fetch", "origin", "main", timeout=180)
    temp_root = Path(tempfile.mkdtemp(prefix="blog-openclaw-publish-"))
    worktree = temp_root / "main"
    added = False
    try:
        git(BLOG_REPO, "worktree", "add", "--detach", str(worktree), "origin/main", timeout=180)
        added = True
        run(
            [
                "rsync",
                "-a",
                "--delete",
                "--exclude=.git",
                "--exclude=.github",
                "--exclude=DEPLOYMENT.md",
                "--exclude=LICENSE",
                f"{BLOG_REPO / 'dist'}/",
                f"{worktree}/",
            ],
            cwd=BLOG_REPO,
            timeout=180,
        )
        missing = [name for name in PRESERVED_MAIN_PATHS if not (worktree / name).exists()]
        if missing:
            raise RuntimeError(f"publish worktree lost preserved support paths: {missing}")
        git(worktree, "diff", "--check")
        if not git(worktree, "status", "--porcelain=v1"):
            return None
        git(worktree, "add", "-A")
        git(worktree, "commit", "-m", "Publish OpenClaw contribution snapshot")
        commit = git(worktree, "rev-parse", "--short", "HEAD")
        git(worktree, "push", "origin", "HEAD:main", timeout=180)
        return commit
    finally:
        if added:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=BLOG_REPO,
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
            )
        shutil.rmtree(temp_root, ignore_errors=True)


def fetch_text(url: str) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "jingxiao-cai-openclaw-public-surface-live-verify"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        status = getattr(response, "status", response.getcode())
        return int(status), response.read().decode("utf-8", errors="replace")


def verify_blog_live(snapshot: dict[str, object], timeout_seconds: int = 150) -> dict[str, object]:
    latest = snapshot["latest"]
    assert isinstance(latest, dict)
    deadline = time.monotonic() + timeout_seconds
    attempts = 0
    checks: dict[str, bool] = {}
    error = ""
    while True:
        attempts += 1
        try:
            status, body = fetch_text(BLOG_URL)
            css_status, _ = fetch_text(BLOG_URL + "assets/site.css")
            pagefind_status, _ = fetch_text(BLOG_URL + "pagefind/pagefind.js")
            checks = {
                "http_200": status == 200,
                "expected_count": f"<strong>{snapshot['mergedPrCount']}</strong>" in body,
                "latest_pr_link": str(latest["url"]) in body,
                "latest_scope_label": str(latest["label"]) in body,
                "verified_date": f'datetime="{snapshot["verifiedDate"]}"' in body,
                "css_200": css_status == 200,
                "pagefind_200": pagefind_status == 200,
            }
            if all(checks.values()):
                return {"ok": True, "url": BLOG_URL, "attempts": attempts, "checks": checks}
            error = "failed checks: " + ", ".join(key for key, value in checks.items() if not value)
        except Exception as exc:  # pragma: no cover - exercised by live cron
            error = str(exc)
        if time.monotonic() >= deadline:
            return {
                "ok": False,
                "url": BLOG_URL,
                "attempts": attempts,
                "checks": checks,
                "error": error,
            }
        time.sleep(10)


def synchronize(*, pull: bool, commit_push: bool, max_age_days: int) -> dict[str, object]:
    ensure_repo_ready(PERSONAL_REPO, "main", pull=pull)
    ensure_repo_ready(BLOG_REPO, BLOG_SOURCE_BRANCH, pull=pull)
    personal = load_module("personal_site_openclaw_contrib", PERSONAL_SCRIPT)
    blog_updater = load_module("blog_openclaw_contrib", BLOG_UPDATER)

    prs = personal.fetch_merged_prs()
    if not prs:
        raise RuntimeError("GitHub returned zero merged OpenClaw PRs; refusing public update")
    unknown = personal.unknown_scope_prs(prs)
    if unknown:
        return {
            "ok": True,
            "reviewNeeded": True,
            "reason": "unknown_pr_scope",
            "mergedPrCount": len(prs),
            "latestPr": prs[0],
            "unknownPrs": unknown,
            "changed": False,
            "pushed": False,
            "personalSite": {"changed": False, "pushed": False},
            "blog": {"changed": False, "pushed": False},
        }

    personal_changed = personal.update_index(prs)
    personal_original = personal.INDEX_HTML.read_text()
    if personal_changed:
        # update_index already wrote the generated form, so recover the exact
        # pre-run version from git for pre-publish rollback.
        personal_original = git(PERSONAL_REPO, "show", "HEAD:index.html")
    blog_original = BLOG_SNAPSHOT.read_text()
    try:
        personal.basic_validate()
        snapshot = blog_updater.refreshed_snapshot(
            personal,
            prs=prs,
            max_age_days=max_age_days,
        )
        blog_changed = write_blog_snapshot(blog_updater, snapshot)
        blog_publish_needed = not blog_main_matches(snapshot)

        run(["npm", "run", "check:openclaw-contrib"], cwd=BLOG_REPO, timeout=90)
        if blog_changed or blog_publish_needed:
            run(["npm", "run", "verify"], cwd=BLOG_REPO, timeout=240)
            sanitize_generated_homepage()
    except Exception:
        restore_text(personal.INDEX_HTML, personal_original)
        restore_text(BLOG_SNAPSHOT, blog_original)
        raise

    personal_pushed = False
    personal_commit = None
    personal_live = None
    blog_source_commit = None
    blog_publish_commit = None
    blog_live = None
    if commit_push:
        if personal_changed:
            personal_pushed, personal_commit = personal.commit_and_push()
            personal_live = personal.verify_live_site(prs)
            if not personal_live.get("ok"):
                raise RuntimeError(f"personal-site live verification failed: {personal_live}")
        if blog_changed:
            blog_source_commit = commit_blog_source()
        if blog_publish_needed:
            blog_publish_commit = publish_blog_main()
            if not blog_publish_commit:
                raise RuntimeError("blog publish was required but generated main had no diff")
            blog_live = verify_blog_live(snapshot)
            if not blog_live.get("ok"):
                raise RuntimeError(f"blog live verification failed: {blog_live}")
    else:
        restore_text(personal.INDEX_HTML, personal_original)
        restore_text(BLOG_SNAPSHOT, blog_original)

    pushed = personal_pushed or bool(blog_publish_commit)
    return {
        "ok": True,
        "reviewNeeded": False,
        "mergedPrCount": len(prs),
        "latestPr": prs[0],
        "changed": personal_changed or blog_changed or blog_publish_needed,
        "pushed": pushed,
        "personalSite": {
            "changed": personal_changed,
            "pushed": personal_pushed,
            "commit": personal_commit,
            "liveVerification": personal_live,
        },
        "blog": {
            "changed": blog_changed,
            "publishNeeded": blog_publish_needed,
            "pushed": bool(blog_publish_commit),
            "sourceCommit": blog_source_commit,
            "publishCommit": blog_publish_commit,
            "liveVerification": blog_live,
            "snapshot": snapshot,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull", action="store_true", help="Fast-forward both source repositories first")
    parser.add_argument("--commit-push", action="store_true", help="Publish validated changes to both sites")
    parser.add_argument("--json", action="store_true", help="Emit a compact machine-readable summary")
    parser.add_argument("--max-age-days", type=int, default=30)
    args = parser.parse_args()

    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            result = {"ok": False, "error": "another public-surface sync is already running"}
            print(json.dumps(result, ensure_ascii=False) if args.json else result)
            return 3
        try:
            result = synchronize(
                pull=args.pull,
                commit_push=args.commit_push,
                max_age_days=args.max_age_days,
            )
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
            print(json.dumps(result, ensure_ascii=False) if args.json else result)
            return 1

    print(json.dumps(result, ensure_ascii=False) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
