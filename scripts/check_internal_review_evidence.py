"""Require internal reviewer evidence when PRs change Workstream contracts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

RELEVANT_PREFIXES = (
    ".github/workflows/",
    "AGENTS.md",
    "README.md",
    "backend/app/",
    "backend/tests/",
    "docs/",
)
IGNORED_PREFIXES = (
    "docs/internal_reviews/",
    "docs/diagrams/rendered/",
)
EVIDENCE_PREFIX = "docs/internal_reviews/"
REQUIRED_TRACKS = (
    "senior engineering",
    "qa/test",
    "security/auth",
    "product/ops",
)
REQUIRED_PHRASES = (
    "open sub-agent sessions: none",
    "valid findings addressed",
)


def git(*args: str) -> str:
    """Run git and return stdout."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def changed_files() -> list[str]:
    """Return files changed by this PR or local branch."""
    paths: list[str] = []

    def add(output: str) -> None:
        for line in output.splitlines():
            if line and line not in paths:
                paths.append(line)

    base_ref = os.environ.get("INTERNAL_REVIEW_BASE_REF") or os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        candidates = [f"origin/{base_ref}", base_ref]
        for candidate in candidates:
            try:
                add(git("diff", "--name-only", f"{candidate}...HEAD"))
                break
            except subprocess.CalledProcessError:
                continue
    else:
        try:
            add(git("diff", "--name-only", "HEAD~1...HEAD"))
        except subprocess.CalledProcessError:
            pass

    add(git("diff", "--name-only", "--cached"))
    add(git("diff", "--name-only"))
    add(git("ls-files", "--others", "--exclude-standard"))
    return paths


def is_relevant(path: str) -> bool:
    """Return whether a changed path requires internal review evidence."""
    if path.startswith(IGNORED_PREFIXES):
        return False
    return path.startswith(RELEVANT_PREFIXES)


def validate_evidence(path: Path) -> list[str]:
    """Validate one internal review evidence file."""
    text = path.read_text(encoding="utf-8").lower()
    missing = [track for track in REQUIRED_TRACKS if track not in text]
    missing.extend(phrase for phrase in REQUIRED_PHRASES if phrase not in text)
    return missing


def main() -> int:
    """Check that changed contract files include complete review evidence."""
    changed = changed_files()
    relevant = [path for path in changed if is_relevant(path)]
    if not relevant:
        print("No internal review evidence required for this change.")
        return 0

    evidence_paths = [
        Path(path)
        for path in changed
        if path.startswith(EVIDENCE_PREFIX) and path.endswith(".md")
    ]
    if not evidence_paths:
        print(
            "Internal review evidence is required for Workstream contract changes.\n"
            "Add a changed docs/internal_reviews/*.md file with senior engineering, "
            "QA/test, security/auth, and product/ops results before opening the PR.",
            file=sys.stderr,
        )
        return 1

    failures: list[str] = []
    for path in evidence_paths:
        missing = validate_evidence(path)
        if missing:
            failures.append(f"{path}: missing {', '.join(missing)}")

    if failures:
        print("Internal review evidence is incomplete:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Internal review evidence gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
