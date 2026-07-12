#!/usr/bin/env python3
"""Reject artifact contract vocabulary after each owning cutover activates."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# ARTIFACT_CONTRACT_PHASE: foundation
ARTIFACT_CONTRACT_PHASE = "foundation"

PHASES = (
    "foundation",
    "guide_source_cutover",
    "upload_admission",
    "submission_cutover",
    "checker_cutover",
)

SKIP_PREFIXES = (
    ".agent-loop/",
    "docs/internal_reviews/",
    "docs/reference_specs/",
)
TEXT_SUFFIXES = {".html", ".json", ".md", ".py", ".toml", ".yaml", ".yml"}
FOUNDATION_INTERFACE_PATHS = {
    "backend/app/interfaces/artifacts.py",
    "backend/app/modules/artifacts/contracts.py",
}
FOUNDATION_INTERFACE_PREFIXES = ("contracts/artifact-store/",)


@dataclass(frozen=True)
class Rule:
    """One obsolete term and the phase that begins rejecting it."""

    code: str
    active_from: str
    pattern: re.Pattern[str]


RULES = (
    Rule(
        "PROVIDER_SPECIFIC_GENERIC_INTERFACE",
        "foundation",
        re.compile(r"\b(?:cid|dag|pins?|pinned|pinning)\b", re.IGNORECASE),
    ),
    Rule("LEGACY_GUIDE_CONTENT_CID", "guide_source_cutover", re.compile(r"\bcontent_cid\b")),
    Rule(
        "LEGACY_SUBMISSION_TRANSPORT",
        "submission_cutover",
        re.compile(
            r"\b(?:package_uri|package_hash|artifact_hash_manifest|worker_attestation)\b"
        ),
    ),
    Rule(
        "LEGACY_PROJECT_STORAGE_POLICY",
        "submission_cutover",
        re.compile(
            r"\b(?:manifest_required|artifact_hash_required|artifact_hash_algorithm|"
            r"allowed_storage_schemes)\b"
        ),
    ),
    Rule(
        "LEGACY_STORAGE_COMPILER_PRIMITIVE",
        "submission_cutover",
        re.compile(r"\b(?:enforce_storage_scheme|verify_hash|require_manifest_field)\b"),
    ),
    Rule(
        "LEGACY_CHECKER_ARTIFACT_COPY",
        "checker_cutover",
        re.compile(r"\b(?:artifact_manifest_hash|checker_artifact_manifest)\b"),
    ),
)


def phase_index(phase: str) -> int:
    """Return the phase index or fail closed for an unknown marker."""
    if not isinstance(phase, str) or phase not in PHASES:
        raise ValueError(f"malformed artifact contract phase: {phase!r}")
    return PHASES.index(phase)


def rules_for_phase(phase: str) -> tuple[Rule, ...]:
    """Return rules whose owning phase is active at ``phase``."""
    current = phase_index(phase)
    return tuple(rule for rule in RULES if phase_index(rule.active_from) <= current)


def path_is_scannable(relative_path: str) -> bool:
    """Return whether an active source or document path should be scanned."""
    path = Path(relative_path)
    return (
        path.suffix.lower() in TEXT_SUFFIXES
        and not relative_path.startswith(SKIP_PREFIXES)
        and relative_path != "scripts/check_stale_artifact_contracts.py"
    )


def rule_applies_to_path(rule: Rule, relative_path: str) -> bool:
    """Limit foundation neutrality checks to generic artifact contracts."""
    if rule.code != "PROVIDER_SPECIFIC_GENERIC_INTERFACE":
        return True
    return relative_path in FOUNDATION_INTERFACE_PATHS or relative_path.startswith(
        FOUNDATION_INTERFACE_PREFIXES
    )


def scan_text(relative_path: str, text: str, phase: str) -> list[str]:
    """Return deterministic stale-contract failures for one text file."""
    failures: list[str] = []
    for rule in rules_for_phase(phase):
        if not rule_applies_to_path(rule, relative_path):
            continue
        for match in rule.pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{relative_path}:{line}: {rule.code}")
    return failures


def git_lines(root: Path, *args: str) -> list[str]:
    """Return non-empty path lines from Git."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def discover_paths(root: Path = ROOT) -> list[Path]:
    """Discover tracked and untracked active text files."""
    relative_paths = git_lines(root, "ls-files")
    relative_paths.extend(git_lines(root, "ls-files", "--others", "--exclude-standard"))
    paths: list[Path] = []
    for relative_path in dict.fromkeys(relative_paths):
        if not path_is_scannable(relative_path):
            continue
        path = root / relative_path
        if path.is_file():
            paths.append(path)
    return paths


def scan(root: Path = ROOT, phase: str | None = None) -> list[str]:
    """Scan the repository at an explicitly validated artifact phase."""
    if phase is None:
        phase = ARTIFACT_CONTRACT_PHASE
    phase_index(phase)
    failures: list[str] = []
    for path in discover_paths(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        failures.extend(scan_text(path.relative_to(root).as_posix(), text, phase))
    return failures


def main() -> int:
    """Run the phased stale artifact contract check."""
    try:
        failures = scan()
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"Stale artifact contract check failed closed: {exc}", file=sys.stderr)
        return 1

    if failures:
        print(
            f"Stale artifact contract check failed at phase {ARTIFACT_CONTRACT_PHASE}:",
            file=sys.stderr,
        )
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Stale artifact contract check passed at phase {ARTIFACT_CONTRACT_PHASE}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
