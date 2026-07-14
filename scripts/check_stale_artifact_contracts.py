#!/usr/bin/env python3
"""Reject stale artifact contracts after each owning cutover activates."""

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
    "artifact_store_cutover",
    "guide_source_cutover",
    "upload_admission",
    "submission_cutover",
    "checker_cutover",
)

HISTORICAL_PREFIXES = (
    "docs/internal_reviews/",
    "docs/reference_specs/",
)
AGENT_LOOP_INITIATIVE_PREFIX = ".agent-loop/initiatives/"
ACTIVE_LOOP_PATHS = {
    ".agent-loop/LOOP_STATE.md",
    ".agent-loop/MEMORY.md",
    ".agent-loop/REVIEW_LOG.md",
    ".agent-loop/WORK_QUEUE.md",
}
TEXT_SUFFIXES = {
    ".html",
    ".json",
    ".md",
    ".puml",
    ".py",
    ".rst",
    ".sh",
    ".tf",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
FOUNDATION_INTERFACE_PATHS = {
    "backend/app/interfaces/artifacts.py",
    "backend/app/modules/artifacts/contracts.py",
}
FOUNDATION_INTERFACE_PREFIXES = ("contracts/artifact-store/",)
R2_RUNTIME_PREFIXES = (
    "backend/app/core/",
    "backend/app/adapters/artifacts/",
    "services/r2_credential_issuer/",
    "deploy/",
    "deployment/",
    "infra/",
    "infrastructure/",
    "k8s/",
    "helm/",
    "charts/",
)
R2_RUNTIME_FILENAMES = (
    "compose.",
    "docker-compose.",
    "Dockerfile",
)
LIVE_RULE_PATHS = {
    "LEGACY_FLOW_NODE_RUNTIME": (
        "backend/app/core/config.py",
        "backend/app/interfaces/",
        "backend/app/adapters/artifacts/",
    ),
    "LEGACY_GUIDE_CONTENT_CID": (
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
    ),
    "LEGACY_SUBMISSION_TRANSPORT": (
        "backend/app/modules/tasks/",
        "backend/app/modules/checkers/",
    ),
    "LEGACY_PROJECT_STORAGE_POLICY": (
        "backend/app/adapters/project_agents/",
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
        "backend/app/modules/checkers/",
        "backend/app/modules/tasks/",
    ),
    "LEGACY_STORAGE_COMPILER_PRIMITIVE": (
        "backend/app/adapters/project_agents/",
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
        "backend/app/modules/checkers/",
        "backend/app/modules/tasks/",
    ),
    "LEGACY_CHECKER_ARTIFACT_COPY": (
        "backend/app/modules/tasks/",
        "backend/app/modules/checkers/",
    ),
}


def active_initiative_prefixes(root: Path = ROOT) -> tuple[str, ...]:
    """Derive live initiative directories from every in-progress queue row."""
    queue_path = root / ".agent-loop/WORK_QUEUE.md"
    if not queue_path.is_file():
        return ()
    queue = queue_path.read_text(encoding="utf-8")
    try:
        in_progress = queue.split("## In Progress", maxsplit=1)[1].split(
            "## Planned Next",
            maxsplit=1,
        )[0]
    except IndexError as exc:
        raise ValueError("malformed Work Queue headings") from exc
    initiative_ids = {
        match.group(1)
        for chunk in re.findall(r"\| `([^`]+)` \|", in_progress)
        if (match := re.match(r"([A-Z]+-[A-Z]+-\d+)", chunk))
    }
    initiative_root = root / AGENT_LOOP_INITIATIVE_PREFIX
    if not initiative_root.is_dir():
        return ()
    return tuple(
        f"{AGENT_LOOP_INITIATIVE_PREFIX}{path.name}/"
        for path in sorted(initiative_root.iterdir())
        if path.is_dir() and any(path.name.startswith(item) for item in initiative_ids)
    )


@dataclass(frozen=True)
class Rule:
    """One obsolete term and the phase that begins rejecting it."""

    code: str
    active_from: str
    pattern: re.Pattern[str]


RULES = (
    Rule(
        "AMBIGUOUS_S3_ADAPTER_NAME",
        "foundation",
        re.compile(r"\bS3ArtifactStore\b"),
    ),
    Rule(
        "ACTIVE_R2_V01_PLAN",
        "foundation",
        re.compile(
            r"(?:\bWS-ART-001-02B[23]\b|"
            r"AWS S3\s+(?:or|and)\s+(?:Cloudflare\s+)?R2"
            r"[^.!?\n]{0,100}\bproduction\b|"
            r"\bproduction\b[^.!?\n]{0,100}AWS S3\s+(?:or|and)\s+"
            r"(?:Cloudflare\s+)?R2|"
            r"(?:Cloudflare\s+)?R2[^.!?\n]{0,80}\bproduction\s+"
            r"(?:provider|profile|option|backend|store)|"
            r"\bproduction\s+(?:provider|profile|option|backend|store)"
            r"[^.!?\n]{0,80}(?:Cloudflare\s+)?R2\b)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "OBSOLETE_FLOW_NODE_PLAN",
        "foundation",
        re.compile(
            r"(?:\bFN-ART-001\b|\bWS-ART-001-02-flow-node-adapter|"
            r"Flow Node[^.!?\n]{0,80}\b(?:v0\.1|production)\b|"
            r"\b(?:v0\.1|production)\b[^.!?\n]{0,80}Flow Node)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "PROVIDER_SPECIFIC_GENERIC_INTERFACE",
        "foundation",
        re.compile(r"\b(?:cid|dag|pins?|pinned|pinning)\b", re.IGNORECASE),
    ),
    Rule(
        "LEGACY_FLOW_NODE_RUNTIME",
        "artifact_store_cutover",
        re.compile(r"\bflow_node\b", re.IGNORECASE),
    ),
    Rule(
        "LEGACY_GUIDE_CONTENT_CID",
        "guide_source_cutover",
        re.compile(r"\bcontent_cid\b"),
    ),
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
        "LEGACY_CALLER_STORAGE_SCHEME",
        "submission_cutover",
        re.compile(r"\b(?:local|s3|r2)://", re.IGNORECASE),
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


def path_is_scannable(relative_path: str, root: Path = ROOT) -> bool:
    """Return whether a live source or document path should be scanned."""
    active_prefixes = active_initiative_prefixes(root)
    path = Path(relative_path)
    is_review_history = (
        relative_path.startswith(AGENT_LOOP_INITIATIVE_PREFIX)
        and "/reviews/" in relative_path
    )
    return (
        path.suffix.lower() in TEXT_SUFFIXES
        and not relative_path.startswith(HISTORICAL_PREFIXES)
        and not is_review_history
        and (
            not relative_path.startswith(".agent-loop/")
            or relative_path in ACTIVE_LOOP_PATHS
            or relative_path.startswith(active_prefixes)
        )
        and relative_path != "scripts/check_stale_artifact_contracts.py"
    )


def path_is_active_contract(relative_path: str, root: Path = ROOT) -> bool:
    """Return whether a path carries current artifact architecture wording."""
    if relative_path in {"AGENTS.md", "README.md", *ACTIVE_LOOP_PATHS}:
        return True
    if relative_path.startswith("docs/"):
        return not relative_path.startswith(HISTORICAL_PREFIXES)
    return relative_path.startswith(active_initiative_prefixes(root)) and "/reviews/" not in (
        relative_path
    )


def rule_applies_to_path(rule: Rule, relative_path: str, root: Path = ROOT) -> bool:
    """Limit each rule to its owning active contract or runtime boundary."""
    if rule.code == "PROVIDER_SPECIFIC_GENERIC_INTERFACE":
        return relative_path in FOUNDATION_INTERFACE_PATHS or relative_path.startswith(
            FOUNDATION_INTERFACE_PREFIXES
        )
    if rule.code == "ACTIVE_R2_V01_PLAN":
        return path_is_active_contract(relative_path, root)
    if rule.code == "OBSOLETE_FLOW_NODE_PLAN":
        return path_is_active_contract(relative_path, root)
    if rule.code in LIVE_RULE_PATHS:
        return (
            relative_path.startswith("docs/")
            and path_is_active_contract(relative_path, root)
        ) or relative_path.startswith(LIVE_RULE_PATHS[rule.code])
    if rule.code == "LEGACY_CALLER_STORAGE_SCHEME":
        return (
            relative_path.startswith("docs/")
            and path_is_active_contract(relative_path, root)
        ) or relative_path.startswith(
            (
                "backend/app/modules/projects/",
                "backend/app/modules/tasks/",
                "backend/app/modules/checkers/",
            )
        )
    return True


def scan_text(relative_path: str, text: str, phase: str, root: Path = ROOT) -> list[str]:
    """Return deterministic stale-contract failures for one text file."""
    failures: list[str] = []
    for rule in rules_for_phase(phase):
        if not rule_applies_to_path(rule, relative_path, root):
            continue
        for match in rule.pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            line_text = text.splitlines()[line - 1]
            if rule.code == "ACTIVE_R2_V01_PLAN" and re.search(
                r"\b(?:defer(?:red|s)?|no active|not a v0\.1|outside v0\.1)\b",
                line_text,
                re.IGNORECASE,
            ):
                continue
            if rule.code == "OBSOLETE_FLOW_NODE_PLAN" and re.search(
                r"\b(?:defer(?:red|s)?|supersed(?:ed|es)?|preserv(?:ed|es)?|"
                r"not (?:a )?v0\.1|cannot block|outside v0\.1)\b",
                line_text,
                re.IGNORECASE,
            ):
                continue
            failures.append(f"{relative_path}:{line}: {rule.code}")
    if relative_path.startswith(R2_RUNTIME_PREFIXES) or Path(relative_path).name.startswith(
        R2_RUNTIME_FILENAMES
    ):
        for match in re.finditer(
            r"\b(?:cloudflare_r2|r2_credential|r2-credential)\b",
            text,
            re.IGNORECASE,
        ):
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{relative_path}:{line}: DEFERRED_R2_RUNTIME")
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
        if not path_is_scannable(relative_path, root):
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
        except (OSError, UnicodeDecodeError) as exc:
            relative_path = path.relative_to(root).as_posix()
            failures.append(f"{relative_path}:0: UNREADABLE_ACTIVE_TEXT ({type(exc).__name__})")
            continue
        failures.extend(scan_text(path.relative_to(root).as_posix(), text, phase, root))
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
