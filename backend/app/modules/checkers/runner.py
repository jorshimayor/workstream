"""Checker registry, structural checkers, and manifest hashing."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Awaitable
from typing import Protocol

from app.modules.tasks.models import Submission, WorkstreamTask
from app.modules.tasks.schemas import SubmissionCreate

CHECKER_STATUS_PASSED = "passed"
CHECKER_STATUS_WARNING = "warning"
CHECKER_STATUS_FAILED = "failed"

CHECKER_SEVERITY_INFO = "info"
CHECKER_SEVERITY_LOW = "low"
CHECKER_SEVERITY_MEDIUM = "medium"
CHECKER_SEVERITY_HIGH = "high"
CHECKER_SEVERITY_CRITICAL = "critical"

BLOCKING_SEVERITIES = {CHECKER_SEVERITY_HIGH, CHECKER_SEVERITY_CRITICAL}


class CheckerNameConflict(ValueError):
    """Raised when duplicate checker names are registered."""


class UnknownChecker(ValueError):
    """Raised when a policy references an unregistered checker."""


class ArtifactManifestError(ValueError):
    """Raised when an artifact manifest cannot be canonicalized."""


@dataclass(frozen=True)
class CheckerOutcome:
    """In-memory checker result before persistence."""

    checker_name: str
    status: str
    severity: str
    message: str
    blocks_review: bool = False
    worker_message: str | None = None
    worker_suggested_fix: str | None = None
    worker_evidence_refs: list[str] = field(default_factory=list)
    worker_visible: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CheckerContext:
    """Data available to structural checkers."""

    task: WorkstreamTask
    submission: Submission
    required_checker_names: frozenset[str]
    warning_checker_names: frozenset[str]
    blocking_severities: frozenset[str]


class Checker(Protocol):
    """Protocol implemented by registered checkers."""

    name: str

    async def run(self, context: CheckerContext) -> CheckerOutcome:
        """Run the checker against a locked submission context."""


CheckerHandler = Callable[[CheckerContext], Awaitable[CheckerOutcome]]


class FunctionChecker:
    """Checker adapter around a plain callable."""

    def __init__(self, name: str, handler: "CheckerHandler") -> None:
        """Create a named checker.

        Args:
            name: Canonical checker name referenced by checker policies.
            handler: Function that evaluates a checker context.
        """
        self.name = name
        self._handler = handler

    async def run(self, context: CheckerContext) -> CheckerOutcome:
        """Run the wrapped checker handler."""
        return await self._handler(context)


class CheckerRegistry:
    """Registry of canonical checker implementations."""

    def __init__(self) -> None:
        """Create an empty checker registry."""
        self._checkers: dict[str, Checker] = {}

    def register(self, checker: Checker) -> None:
        """Register one checker implementation by canonical name.

        Args:
            checker: Checker implementation to register.

        Raises:
            CheckerNameConflict: If another checker already owns the same name.
        """
        if checker.name in self._checkers:
            raise CheckerNameConflict(f"checker already registered: {checker.name}")
        self._checkers[checker.name] = checker

    def require_registered(self, checker_names: set[str]) -> None:
        """Validate that all policy checker names have implementations.

        Args:
            checker_names: Checker names from locked checker policy.

        Raises:
            UnknownChecker: If any checker name is not registered.
        """
        missing = sorted(checker_names.difference(self._checkers))
        if missing:
            raise UnknownChecker(f"unregistered checker policy names: {', '.join(missing)}")

    async def run(
        self,
        context: CheckerContext,
        checker_names: list[str],
    ) -> list[CheckerOutcome]:
        """Run checkers in policy order.

        Args:
            context: Locked checker context.
            checker_names: Canonical checker names to execute.

        Returns:
            Checker outcomes in the same order as ``checker_names``.
        """
        self.require_registered(set(checker_names))
        return [await self._checkers[name].run(context) for name in checker_names]

    def names(self) -> set[str]:
        """Return all registered checker names."""
        return set(self._checkers)


def canonical_artifact_manifest_hash(manifest: list[dict]) -> str:
    """Hash a submission artifact manifest using Workstream canonical JSON.

    Args:
        manifest: Artifact hash entries persisted on a submission.

    Returns:
        SHA-256 digest prefixed with ``sha256:``.

    Raises:
        ArtifactManifestError: If duplicate artifacts or invalid entries are present.
    """
    seen_artifacts: set[str] = set()
    canonical_entries: list[dict] = []
    for entry in manifest:
        artifact = str(entry.get("artifact", "")).strip()
        artifact_hash = str(entry.get("hash", "")).strip()
        if not artifact or not artifact_hash:
            raise ArtifactManifestError("artifact manifest entries require artifact and hash")
        if artifact in seen_artifacts:
            raise ArtifactManifestError(f"duplicate artifact in manifest: {artifact}")
        seen_artifacts.add(artifact)
        canonical_entries.append(
            {
                "artifact": artifact,
                "hash": artifact_hash,
                "notes": entry.get("notes"),
                "size_bytes": entry.get("size_bytes"),
            }
        )
    encoded = json.dumps(
        sorted(canonical_entries, key=lambda item: (item["artifact"], item["hash"])),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


async def pre_submit_static_feedback(
    task: WorkstreamTask,
    payload: SubmissionCreate,
) -> list[CheckerOutcome]:
    """Run non-authoritative structural checks before a submission is created.

    Args:
        task: Task receiving the draft packet.
        payload: Draft submission packet payload.

    Returns:
        Worker-facing checker feedback items. These are not durable gate records.
    """
    outcomes: list[CheckerOutcome] = []
    manifest = [entry.model_dump() for entry in payload.artifact_hash_manifest]
    outcomes.append(_packet_shape_outcome(payload.summary, payload.package_hash, manifest))
    outcomes.append(_artifact_manifest_outcome(manifest))
    outcomes.append(_evidence_reference_outcome(len(payload.evidence_items), task.required_evidence))
    return outcomes


def _pass(name: str, message: str, *, metadata: dict | None = None) -> CheckerOutcome:
    """Build a passing checker outcome."""
    return CheckerOutcome(
        checker_name=name,
        status=CHECKER_STATUS_PASSED,
        severity=CHECKER_SEVERITY_INFO,
        message=message,
        worker_message=message,
        metadata=metadata or {},
    )


def _fail(
    name: str,
    message: str,
    suggested_fix: str,
    *,
    metadata: dict | None = None,
    worker_visible: bool = True,
) -> CheckerOutcome:
    """Build a worker-fixable failing checker outcome."""
    return CheckerOutcome(
        checker_name=name,
        status=CHECKER_STATUS_FAILED,
        severity=CHECKER_SEVERITY_HIGH,
        message=message,
        blocks_review=True,
        worker_message=message if worker_visible else None,
        worker_suggested_fix=suggested_fix if worker_visible else None,
        worker_visible=worker_visible,
        metadata=metadata or {},
    )


def _packet_shape_outcome(summary: str, package_hash: str, manifest: list[dict]) -> CheckerOutcome:
    """Validate required packet fields shared by pre-submit and durable checks."""
    missing: list[str] = []
    if not summary.strip():
        missing.append("summary")
    if not package_hash.strip():
        missing.append("package_hash")
    if not manifest:
        missing.append("artifact_hash_manifest")
    if missing:
        return _fail(
            "check_submission_packet",
            f"Submission packet is missing required fields: {', '.join(missing)}.",
            "Add the missing packet fields before submitting.",
            metadata={"missing_fields": missing},
        )
    return _pass("check_submission_packet", "Submission packet contains required fields.")


def _artifact_manifest_outcome(manifest: list[dict]) -> CheckerOutcome:
    """Validate manifest canonicalization and expose the derived hash."""
    try:
        manifest_hash = canonical_artifact_manifest_hash(manifest)
    except ArtifactManifestError as exc:
        return _fail(
            "check_artifact_manifest_integrity",
            str(exc),
            "Use one unique artifact entry per artifact and include its hash.",
        )
    return _pass(
        "check_artifact_manifest_integrity",
        "Artifact manifest is canonical and hashable.",
        metadata={"artifact_manifest_hash": manifest_hash},
    )


def _evidence_reference_outcome(
    evidence_count: int,
    required_evidence: list[str],
) -> CheckerOutcome:
    """Validate that required-evidence tasks include evidence rows."""
    if required_evidence and evidence_count == 0:
        return _fail(
            "check_evidence_references_present",
            "Submission is missing required evidence references.",
            "Attach evidence items required by the task before submitting.",
            metadata={"required_evidence": required_evidence},
        )
    return _pass("check_evidence_references_present", "Submission includes evidence references.")


async def check_submission_packet(context: CheckerContext) -> CheckerOutcome:
    """Validate required submission packet fields after the packet is locked."""
    return _packet_shape_outcome(
        context.submission.summary,
        context.submission.package_hash,
        context.submission.artifact_hash_manifest,
    )


async def check_policy_context_present(context: CheckerContext) -> CheckerOutcome:
    """Validate that the submission carries all locked guide and policy versions."""
    missing = [
        name
        for name, value in {
            "locked_guide_version": context.submission.locked_guide_version,
            "locked_checker_policy_version": context.submission.locked_checker_policy_version,
            "locked_review_policy_version": context.submission.locked_review_policy_version,
            "locked_revision_policy_version": context.submission.locked_revision_policy_version,
            "locked_payment_policy_version": context.submission.locked_payment_policy_version,
        }.items()
        if not value
    ]
    if missing:
        return _fail(
            "check_policy_context_present",
            f"Submission is missing locked policy context: {', '.join(missing)}.",
            "Ask a project manager to re-screen the task before submitting.",
            metadata={"missing_context": missing},
        )
    return _pass("check_policy_context_present", "Submission has locked guide and policy context.")


async def check_artifact_manifest_integrity(context: CheckerContext) -> CheckerOutcome:
    """Validate artifact manifest uniqueness and canonical hashability."""
    return _artifact_manifest_outcome(context.submission.artifact_hash_manifest)


async def check_evidence_references_present(context: CheckerContext) -> CheckerOutcome:
    """Validate that evidence references exist when the task requires evidence."""
    return _evidence_reference_outcome(
        len(context.submission.evidence_items),
        context.task.required_evidence,
    )


def default_checker_registry() -> CheckerRegistry:
    """Create the built-in checker registry for v0.1 structural checks."""
    registry = CheckerRegistry()
    registry.register(FunctionChecker("check_submission_packet", check_submission_packet))
    registry.register(FunctionChecker("check_policy_context_present", check_policy_context_present))
    registry.register(
        FunctionChecker("check_artifact_manifest_integrity", check_artifact_manifest_integrity)
    )
    registry.register(
        FunctionChecker("check_evidence_references_present", check_evidence_references_present)
    )
    return registry
