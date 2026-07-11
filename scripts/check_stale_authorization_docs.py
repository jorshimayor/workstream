#!/usr/bin/env python3
"""Reject obsolete authorization claims in active Workstream documentation."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_SUFFIXES = {".md", ".html", ".puml"}

# Exact reviewed history/archive paths. New files are active unless added here
# with an explicit rationale through normal review.
HISTORICAL_PATHS = {
    "docs/checker_trial_failure_catalog.md": "closed checker-trial evidence",
    "docs/internal_reviews/2026-06-11_chunk9_pre_review_gate.md": "closed internal review",
    "docs/internal_reviews/2026-06-11_revision_context_rebase.md": "closed internal review",
    "docs/internal_reviews/2026-06-12_chunk10_checker_trial.md": "closed internal review",
    "docs/internal_reviews/2026-06-12_week2_closeout_real_api_drill.md": "closed internal review",
    "docs/internal_reviews/2026-06-13_week1_week2_deterministic_hardening.md": "closed internal review",
    "docs/internal_reviews/2026-06-16_submission_artifact_policy_architecture.md": "closed internal review",
    "docs/reference_specs/WS-AUTH-001-actor-profile-role-and-authorization-service-specification.md": "immutable archival input",
    "docs/reference_specs/WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.md": "immutable archival input",
    "docs/reference_specs/WS-REV-001-review-lifecycle-specification.md": "immutable archival input",
    "docs/review_adversarial_quality_review.md": "closed review record",
    "docs/review_architecture_review.md": "closed review record",
    "docs/review_closure.md": "closed review record",
    "docs/review_final_adversarial_review.md": "closed review record",
    "docs/review_final_architecture_review.md": "closed review record",
    "docs/review_final_product_strategy_review.md": "closed review record",
    "docs/review_operations_review.md": "closed review record",
    "docs/review_process_baseline_operations_review.md": "closed review record",
    "docs/review_process_pattern_baseline_review.md": "closed review record",
    "docs/review_product_strategy_review.md": "closed review record",
    "docs/review_systems_architecture_review.md": "closed review record",
    "docs/roadmap_30_day_master_plan.md": "historical initial plan",
    "docs/roadmap_day_by_day_execution_plan.md": "historical execution plan",
    "docs/roadmap_pilot_plan.md": "historical pilot plan",
    "docs/roadmap_week1_backend_plan.md": "historical Week 1 plan",
    "docs/spec_chunk_1_backend_scaffold.md": "historical implemented chunk",
    "docs/spec_chunk_3_project_guide_foundation.md": "historical implemented chunk",
    "docs/spec_chunk_4_task_queue_assignment.md": "historical implemented chunk",
    "docs/spec_chunk_5_submission_packet_foundation.md": "historical implemented chunk",
    "docs/spec_chunk_6_checker_contract_records.md": "historical implemented chunk",
    "docs/spec_chunk_7_checker_runner_registry.md": "historical implemented chunk",
    "docs/spec_chunk_8_submission_artifact_policy_checkers.md": "historical implemented chunk",
    "docs/spec_chunk_9_pre_review_gate.md": "historical implemented chunk",
    "docs/spec_chunk_10_checker_trial.md": "historical implemented chunk",
    "docs/spec_week2_checker_framework.md": "historical implemented plan",
}


@dataclass(frozen=True)
class Rule:
    """One forbidden active-document pattern."""

    code: str
    pattern: re.Pattern[str]


RULES = (
    Rule("NON_CANONICAL_API_PREFIX", re.compile(r"(?<!/api)/v1(?:/|\b)")),
    Rule(
        "LEGACY_ADMIN_PROJECT_MANAGER_AUTHORITY",
        re.compile(r"`?admin`?\s*(?:/|or)\s*`?project_manager`?", re.IGNORECASE),
    ),
    Rule("LEGACY_ROLE_HELPER", re.compile(r"require_any_role", re.IGNORECASE)),
    Rule("TRUSTED_ROLE_CLAIM_AUTHORITY", re.compile(r"trusted role claims", re.IGNORECASE)),
    Rule(
        "CURRENT_TOKEN_ROLE_AUTHORITY",
        re.compile(r"role in the current verified token", re.IGNORECASE),
    ),
    Rule(
        "TOKEN_CARRIES_PRODUCT_ROLE",
        re.compile(r"token also carries an authorized Workstream role", re.IGNORECASE),
    ),
    Rule(
        "TYPED_PROFILE_AUTHORITY",
        re.compile(r"ActorProfile\s*\(\s*profile_type", re.IGNORECASE),
    ),
    Rule(
        "OBSOLETE_ROLE_ASSIGNMENT_MODEL",
        re.compile(r"WorkstreamRoleAssignment", re.IGNORECASE),
    ),
    Rule(
        "OPERATOR_NOT_A_ROLE",
        re.compile(r"Operator.{0,80}not a separate.{0,40}permission role", re.IGNORECASE),
    ),
    Rule(
        "BROAD_ADMIN_OVERRIDE",
        re.compile(r"\badmin\s+(?:can|may|must)\s+override", re.IGNORECASE),
    ),
    Rule("LEGACY_ADMIN_HEADING", re.compile(r"^#{2,4}\s+Admin\s*$", re.IGNORECASE | re.MULTILINE)),
    Rule(
        "LEGACY_ROLE_MATRIX",
        re.compile(r"\|\s*Admin\s*\|.*\|\s*(?:Finance|Auditor)\s*\|", re.IGNORECASE),
    ),
    Rule(
        "ROLE_NAME_APPROVAL_PROVENANCE",
        re.compile(r"approved_by_role.{0,40}project_manager", re.IGNORECASE),
    ),
    Rule(
        "GENERIC_ADMIN_PRODUCT_AUTHORITY",
        re.compile(
            r"\badmin\s+(?:can|may|must|is allowed to)\s+"
            r"(?:create|approve|activate|manage|claim|review|submit|grant|revoke|read|update|delete)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "TOKEN_ROLE_PRODUCT_AUTHORITY",
        re.compile(
            r"(?:token\s+roles?|roles?\s+(?:from|in)\s+(?:the\s+)?"
            r"(?:(?:current|verified|bearer)\s+)*token).{0,100}?"
            r"\b(?:grants?|authoriz(?:e[sd]?|ation)|permits?|allows?|approv(?:e[sd]?|al))\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "NAMED_ROLE_TOKEN_AUTHORITY",
        re.compile(
            r"\b(?:admin|project_manager|worker|reviewer|operator)\b.{0,24}?\btoken\b.{0,80}?"
            r"\b(?:can|may|must|grants?|authoriz(?:e[sd]?|ation)|permits?|allows?|approv(?:e[sd]?|al))\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "TYPED_PROFILE_PRODUCT_AUTHORITY",
        re.compile(
            r"ActorProfile.{0,60}?\b(?:profile_type|type)\b.{0,80}?"
            r"\b(?:grants?|authoriz(?:e[sd]?|ation)|permits?|allows?|approv(?:e[sd]?|al))\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "HUMAN_WORKER_VOCABULARY",
        re.compile(r"\bworkers?\b", re.IGNORECASE),
    ),
    Rule(
        "HUMAN_WORKER_IDENTIFIER",
        re.compile(
            r"\bworker_(?:id|attestation|message|suggested_fix|evidence_refs|"
            r"visible|claim_status|profile)\b|/api/v1/workers(?:/|\b)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "TECHNICAL_WORKER_HUMAN_AUTHORITY",
        re.compile(
            r"\b(?:celery|checker|setup|system|background|reconciliation)\s+"
            r"workers?\b.{0,120}\b(?:"
            r"claims?\s+(?:a\s+)?(?:human\s+|contributor\s+)?task|"
            r"submits?\s+(?:a\s+)?(?:contributor\s+)?(?:packet|submission)|"
            r"records?\s+(?:a\s+)?review\s+decision|"
            r"receives?\s+(?:a\s+)?(?:submitter|reviewer|both|contributor|"
            r"human\s+administrative)\s+grant|"
            r"is\s+(?:a\s+)?human\s+product\s+role)\b",
            re.IGNORECASE,
        ),
    ),
)

TECHNICAL_WORKER_PREFIX = re.compile(
    r"(?:celery(?:[- ]backed)?|checker|setup|system|background|reconciliation|"
    r"execution|"
    r"service|job|queue|durable|project[- ]setup|pre[- ]review|post[- ]submit)"
    r"[\s/-]+$",
    re.IGNORECASE,
)

MATCH_EXEMPTIONS = {
    (
        "docs/reference_specs/README.md",
        "NON_CANONICAL_API_PREFIX",
    ): re.compile(
        r"^archival input uses `/v1`\. WS-AUTH-001 takes precedence over the current$"
    ),
}


def git_lines(root: Path, *args: str) -> list[str]:
    """Return non-empty lines from a Git command in ``root``."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def discover_documents(root: Path = ROOT) -> list[Path]:
    """Auto-discover tracked and untracked active documentation."""
    raw_paths = git_lines(root, "ls-files")
    raw_paths.extend(git_lines(root, "ls-files", "--others", "--exclude-standard"))
    documents: list[Path] = []
    for raw_path in dict.fromkeys(raw_paths):
        if raw_path != "README.md" and not raw_path.startswith("docs/"):
            continue
        if Path(raw_path).suffix.lower() not in DOCUMENT_SUFFIXES:
            continue
        if raw_path in HISTORICAL_PATHS:
            continue
        path = root / raw_path
        if path.is_file():
            documents.append(path)
    return documents


def line_number(text: str, offset: int) -> int:
    """Return a one-based line number for ``offset``."""
    return text.count("\n", 0, offset) + 1


def containing_line(text: str, offset: int) -> str:
    """Return the full line containing ``offset``."""
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return text[start:] if end == -1 else text[start:end]


def exempt_match(relative_path: str, rule: Rule, text: str, offset: int) -> bool:
    """Return whether one exact reviewed archival marker match is allowed."""
    exemption = MATCH_EXEMPTIONS.get((relative_path, rule.code))
    return bool(exemption and exemption.fullmatch(containing_line(text, offset)))


def technical_worker_match(text: str, match: re.Match[str]) -> bool:
    """Return whether the matched worker token is service-qualified."""
    token = re.search(
        r"\bworkers?(?:_(?:id|attestation|message|suggested_fix|evidence_refs|"
        r"visible|claim_status|profile))?\b",
        match.group(0),
        re.IGNORECASE,
    )
    if token is None:
        return False
    worker_offset = match.start() + token.start()
    prefix = text[max(0, worker_offset - 120) : worker_offset]
    token_end = worker_offset + len(token.group(0))
    suffix = text[token_end : token_end + 20]
    exact_code_path = token.group(0).lower() == "workers" and (
        (prefix.endswith("backend/app/") and suffix.startswith("/"))
        or (prefix.endswith("app.") and suffix.startswith("."))
    )
    exact_celery_cli = bool(
        re.search(
            r"(?:^|\n)[^;\n]*\bcelery\s+-A\s+[^;\n]+$",
            prefix,
            re.IGNORECASE,
        )
        and suffix.startswith(" --")
    )
    return bool(
        TECHNICAL_WORKER_PREFIX.search(prefix)
        or exact_code_path
        or exact_celery_cli
    )


def scan_text(relative_path: str, text: str) -> list[str]:
    """Return deterministic rule failures for one active document."""
    failures: list[str] = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            if exempt_match(relative_path, rule, text, match.start()):
                continue
            if rule.code in {
                "HUMAN_WORKER_VOCABULARY",
                "HUMAN_WORKER_IDENTIFIER",
            } and technical_worker_match(text, match):
                continue
            failures.append(
                f"{relative_path}:{line_number(text, match.start())}: {rule.code}"
            )
    return failures


def scan(root: Path = ROOT) -> list[str]:
    """Scan every discovered active document."""
    failures: list[str] = []
    for path in discover_documents(root):
        relative_path = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            failures.append(f"{relative_path}: unreadable active document: {exc}")
            continue
        failures.extend(scan_text(relative_path, text))
    return failures


def main() -> int:
    """Run the stale authorization documentation gate."""
    failures = scan()
    if failures:
        print("Stale authorization documentation check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Stale authorization documentation check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
