"""Record trusted merged-PR loop state on the automation memory branch."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATE_BRANCH = "automation/loop-memory"
STATE_PATH = Path(".agent-loop/STATE.json")
RENDERED_PATH = Path(".agent-loop/LOOP_STATE.md")
LEDGER_PATH = Path(".agent-loop/MERGE_LOG.jsonl")
SIGNATURE_PATH = Path(".agent-loop/STATE.sig")
INTENT_PREFIX = ".agent-loop/merge-intents/"
BOOTSTRAP_INTENT_PATH = f"{INTENT_PREFIX}WS-ENG-001-02.json"
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_CHECKS = ("agent-gates", "test", "CodeRabbit")
REQUIRED_METADATA_KEYS = {
    "schema_version",
    "initiative_id",
    "chunk_id",
    "chunk_title",
    "next_chunk_id",
    "next_chunk_title",
    "next_requires_explicit_start",
}


class LoopMemoryError(RuntimeError):
    """Raised when merge memory cannot be derived without guessing."""


@dataclass(frozen=True)
class LoopMetadata:
    """Machine-readable lifecycle metadata supplied by the merged PR."""

    schema_version: int
    initiative_id: str
    chunk_id: str
    chunk_title: str
    next_chunk_id: str | None
    next_chunk_title: str | None
    next_requires_explicit_start: bool


class GitHubClient:
    """Minimal authenticated GitHub JSON client."""

    def __init__(self, token: str, api_url: str = "https://api.github.com") -> None:
        if not token:
            raise LoopMemoryError("GitHub token is required")
        self._token = token
        self._api_url = api_url.rstrip("/")

    def get_json(self, path: str) -> Any:
        """Return decoded JSON for one GitHub API path."""
        request = urllib.request.Request(
            f"{self._api_url}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "workstream-loop-memory/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            status = getattr(exc, "code", "network")
            raise LoopMemoryError(
                f"GitHub API request failed ({status}) for {path}"
            ) from exc

    def get_paginated(self, path: str) -> list[Any]:
        """Return all items from a bounded GitHub list endpoint."""
        items: list[Any] = []
        separator = "&" if "?" in path else "?"
        for page in range(1, 101):
            payload = self.get_json(f"{path}{separator}per_page=100&page={page}")
            if not isinstance(payload, list):
                raise LoopMemoryError("paginated GitHub response is not a list")
            items.extend(payload)
            if len(payload) < 100:
                return items
        raise LoopMemoryError("paginated GitHub response exceeded 100 pages")


def _bounded_text(value: Any, field: str, maximum: int = 160) -> str:
    """Validate one bounded single-line metadata string."""
    if not isinstance(value, str):
        raise LoopMemoryError(f"{field} must be a string")
    normalized = value.strip()
    if (
        not normalized
        or len(normalized) > maximum
        or any(ord(char) < 32 for char in normalized)
    ):
        raise LoopMemoryError(f"{field} must be a non-empty bounded single-line string")
    return normalized


def _optional_id(value: Any, field: str) -> str | None:
    """Validate an optional lifecycle identifier."""
    if value is None:
        return None
    normalized = _bounded_text(value, field, maximum=80)
    if not ID_PATTERN.fullmatch(normalized):
        raise LoopMemoryError(f"{field} is not a canonical lifecycle identifier")
    return normalized


def parse_loop_metadata(intent_text: str) -> LoopMetadata:
    """Parse and strictly validate one committed merge-intent document."""
    if not isinstance(intent_text, str):
        raise LoopMemoryError("merge intent must be text")
    try:
        payload = json.loads(intent_text)
    except json.JSONDecodeError as exc:
        raise LoopMemoryError("merge intent must contain valid JSON") from exc
    if not isinstance(payload, dict) or set(payload) != REQUIRED_METADATA_KEYS:
        raise LoopMemoryError("merge intent has missing or unexpected keys")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise LoopMemoryError(
            f"unsupported loop-state schema version: {payload['schema_version']!r}"
        )

    initiative_id = _optional_id(payload["initiative_id"], "initiative_id")
    chunk_id = _optional_id(payload["chunk_id"], "chunk_id")
    if initiative_id is None or chunk_id is None:
        raise LoopMemoryError("initiative_id and chunk_id are required")
    if not chunk_id.startswith(f"{initiative_id}-"):
        raise LoopMemoryError("chunk_id must belong to initiative_id")

    chunk_title = _bounded_text(payload["chunk_title"], "chunk_title")
    next_chunk_id = _optional_id(payload["next_chunk_id"], "next_chunk_id")
    next_title_value = payload["next_chunk_title"]
    next_chunk_title = (
        None
        if next_title_value is None
        else _bounded_text(
            next_title_value,
            "next_chunk_title",
        )
    )
    if (next_chunk_id is None) != (next_chunk_title is None):
        raise LoopMemoryError(
            "next_chunk_id and next_chunk_title must both be null or both be set"
        )
    explicit_start = payload["next_requires_explicit_start"]
    if not isinstance(explicit_start, bool):
        raise LoopMemoryError("next_requires_explicit_start must be a boolean")

    return LoopMetadata(
        schema_version=SCHEMA_VERSION,
        initiative_id=initiative_id,
        chunk_id=chunk_id,
        chunk_title=chunk_title,
        next_chunk_id=next_chunk_id,
        next_chunk_title=next_chunk_title,
        next_requires_explicit_start=explicit_start,
    )


def _validate_sha(merge_sha: str) -> None:
    """Validate one untrusted Git commit identifier."""
    if not SHA_PATTERN.fullmatch(merge_sha):
        raise LoopMemoryError(
            "merge SHA must contain 40 lowercase hexadecimal characters"
        )


def _validate_repository_and_sha(repository: str, merge_sha: str) -> None:
    """Validate untrusted workflow inputs before constructing API paths."""
    if not REPOSITORY_PATTERN.fullmatch(repository):
        raise LoopMemoryError("repository must be owner/name")
    _validate_sha(merge_sha)


def _intent_path(metadata: LoopMetadata) -> str:
    """Return the only canonical repository path for one merge intent."""
    return f"{INTENT_PREFIX}{metadata.chunk_id}.json"


def load_committed_merge_intent(
    client: GitHubClient,
    repository: str,
    pr_number: int,
    head_sha: str,
) -> tuple[LoopMetadata, str, str]:
    """Load the one newly added merge intent from the reviewed PR head."""
    files = client.get_paginated(f"/repos/{repository}/pulls/{pr_number}/files")
    intent_changes = [
        item
        for item in files
        if isinstance(item, dict)
        and isinstance(item.get("filename"), str)
        and item["filename"].startswith(INTENT_PREFIX)
    ]
    if len(intent_changes) != 1 or intent_changes[0].get("status") != "added":
        raise LoopMemoryError(
            "merged pull request must add exactly one merge-intent file"
        )
    path = intent_changes[0]["filename"]
    encoded_path = urllib.parse.quote(path, safe="/")
    payload = client.get_json(
        f"/repos/{repository}/contents/{encoded_path}?ref={head_sha}"
    )
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise LoopMemoryError("merge-intent content response has an invalid shape")
    blob_sha = payload.get("sha")
    content = payload.get("content")
    if not isinstance(blob_sha, str) or not SHA_PATTERN.fullmatch(blob_sha):
        raise LoopMemoryError("merge-intent blob has no canonical SHA")
    if not isinstance(content, str):
        raise LoopMemoryError("merge-intent blob has no encoded content")
    try:
        normalized_content = re.sub(r"[ \t\r\n]", "", content)
        raw = base64.b64decode(normalized_content, validate=True)
        if len(raw) > 8192:
            raise LoopMemoryError("merge-intent document exceeds 8192 bytes")
        text = raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise LoopMemoryError("merge-intent content is not valid base64 UTF-8") from exc
    metadata = parse_loop_metadata(text)
    if path != _intent_path(metadata):
        raise LoopMemoryError("merge-intent path does not match its chunk_id")
    return metadata, path, blob_sha


def validate_local_merge_intent(repository_root: Path, base_ref: str) -> LoopMetadata:
    """Validate one newly added merge intent in the local PR diff."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "diff",
            "--name-status",
            f"{base_ref}...HEAD",
            "--",
            INTENT_PREFIX,
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise LoopMemoryError(f"cannot resolve merge-intent base ref {base_ref!r}")
    changes = [line.split("\t", 1) for line in result.stdout.splitlines() if line]
    if len(changes) != 1 or len(changes[0]) != 2 or changes[0][0] != "A":
        raise LoopMemoryError("pull request must add exactly one merge-intent file")
    path = changes[0][1]
    intent_path = repository_root / path
    try:
        metadata = parse_loop_metadata(intent_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise LoopMemoryError("cannot read local merge-intent file") from exc
    if path != _intent_path(metadata):
        raise LoopMemoryError("merge-intent path does not match its chunk_id")
    return metadata


def _git_lines(repository_root: Path, arguments: list[str], failure: str) -> list[str]:
    """Run one read-only Git query and return its non-empty output lines."""
    result = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise LoopMemoryError(failure)
    return [line for line in result.stdout.splitlines() if line]


def _is_ancestor(repository_root: Path, ancestor: str, descendant: str) -> bool:
    """Return whether one commit is an ancestor, failing on an invalid Git query."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in (0, 1):
        raise LoopMemoryError("cannot resolve main commit ancestry")
    return result.returncode == 0


def plan_reconciliation_commits(
    repository_root: Path, target_sha: str, current_sha: str | None
) -> list[str]:
    """List every first-parent commit needed to reach one protected-main target."""
    _validate_sha(target_sha)
    if current_sha:
        _validate_sha(current_sha)
        if _is_ancestor(repository_root, target_sha, current_sha):
            return []
        if not _is_ancestor(repository_root, current_sha, target_sha):
            raise LoopMemoryError("canonical state is not on the target main ancestry")
        return _git_lines(
            repository_root,
            ["rev-list", "--reverse", "--first-parent", f"{current_sha}..{target_sha}"],
            "cannot enumerate unrecorded main commits",
        )

    bootstrap_commits = _git_lines(
        repository_root,
        [
            "rev-list",
            "--reverse",
            "--first-parent",
            target_sha,
            "--",
            BOOTSTRAP_INTENT_PATH,
        ],
        "cannot resolve the loop-memory bootstrap commit",
    )
    if len(bootstrap_commits) != 1 or not SHA_PATTERN.fullmatch(bootstrap_commits[0]):
        raise LoopMemoryError("target main history has no unique loop-memory bootstrap")
    bootstrap_sha = bootstrap_commits[0]
    successors = _git_lines(
        repository_root,
        ["rev-list", "--reverse", "--first-parent", f"{bootstrap_sha}..{target_sha}"],
        "cannot enumerate commits after the loop-memory bootstrap",
    )
    return [bootstrap_sha, *successors]


def _latest_named(
    items: list[dict[str, Any]], name_key: str, time_key: str
) -> dict[str, dict[str, Any]]:
    """Return the latest observed result for each named check or status."""
    latest: dict[str, dict[str, Any]] = {}
    for item in items:
        name = item.get(name_key)
        if not isinstance(name, str) or not name:
            continue
        current = latest.get(name)
        if current is None or str(item.get(time_key) or "") >= str(
            current.get(time_key) or ""
        ):
            latest[name] = item
    return latest


def _check_evidence(
    check_runs: list[dict[str, Any]], statuses: list[dict[str, Any]]
) -> dict[str, Any]:
    """Build bounded required-check evidence without treating it as merge authority."""
    latest_checks = _latest_named(check_runs, "name", "started_at")
    latest_statuses = _latest_named(statuses, "context", "updated_at")
    observed: dict[str, dict[str, str | None]] = {}
    for name in REQUIRED_CHECKS:
        if name in latest_checks:
            item = latest_checks[name]
            observed[name] = {
                "kind": "check_run",
                "conclusion": item.get("conclusion") or item.get("status"),
                "url": item.get("details_url"),
            }
        elif name in latest_statuses:
            item = latest_statuses[name]
            observed[name] = {
                "kind": "status",
                "conclusion": item.get("state"),
                "url": item.get("target_url"),
            }
        else:
            observed[name] = {"kind": "missing", "conclusion": None, "url": None}
    passed = all(item["conclusion"] == "success" for item in observed.values())
    return {"required": observed, "all_required_passed": passed}


def collect_merge_record(
    client: GitHubClient,
    repository: str,
    merge_sha: str,
) -> dict[str, Any]:
    """Collect one exact merged PR and its bounded loop metadata from GitHub."""
    _validate_repository_and_sha(repository, merge_sha)
    associated = client.get_json(
        f"/repos/{repository}/commits/{merge_sha}/pulls?per_page=100"
    )
    if not isinstance(associated, list):
        raise LoopMemoryError("associated pull request response is not a list")
    matches = [
        pr
        for pr in associated
        if pr.get("merge_commit_sha") == merge_sha
        and pr.get("merged_at")
        and pr.get("base", {}).get("ref") == "main"
        and pr.get("state") == "closed"
    ]
    if len(matches) != 1:
        raise LoopMemoryError(
            "merge SHA must resolve to exactly one merged pull request targeting main"
        )
    associated_pr = matches[0]
    pr_number = associated_pr.get("number")
    if not isinstance(pr_number, int) or pr_number <= 0:
        raise LoopMemoryError("merged pull request has no positive number")
    pr = client.get_json(f"/repos/{repository}/pulls/{pr_number}")
    if not isinstance(pr, dict):
        raise LoopMemoryError("merged pull request response is not an object")
    if (
        pr.get("merge_commit_sha") != merge_sha
        or pr.get("merged_at") != associated_pr.get("merged_at")
        or pr.get("base", {}).get("ref") != "main"
    ):
        raise LoopMemoryError(
            "full pull request facts do not match the associated merge"
        )
    head_sha = pr.get("head", {}).get("sha")
    if not isinstance(head_sha, str) or not SHA_PATTERN.fullmatch(head_sha):
        raise LoopMemoryError("merged pull request has no canonical head SHA")
    metadata, intent_path, intent_blob_sha = load_committed_merge_intent(
        client,
        repository,
        pr_number,
        head_sha,
    )

    commit_payload = client.get_json(f"/repos/{repository}/commits/{merge_sha}")
    parents = (
        commit_payload.get("parents") if isinstance(commit_payload, dict) else None
    )
    if (
        not isinstance(parents, list)
        or not parents
        or not isinstance(parents[0], dict)
        or not isinstance(parents[0].get("sha"), str)
        or not SHA_PATTERN.fullmatch(parents[0]["sha"])
    ):
        raise LoopMemoryError("merged main commit has no canonical first parent")
    first_parent_sha = parents[0]["sha"]

    check_payload = client.get_json(
        f"/repos/{repository}/commits/{head_sha}/check-runs?per_page=100"
    )
    status_payload = client.get_json(
        f"/repos/{repository}/commits/{head_sha}/status?per_page=100"
    )
    check_runs = (
        check_payload.get("check_runs", []) if isinstance(check_payload, dict) else []
    )
    statuses = (
        status_payload.get("statuses", []) if isinstance(status_payload, dict) else []
    )
    if not isinstance(check_runs, list) or not isinstance(statuses, list):
        raise LoopMemoryError("GitHub check evidence has an invalid shape")

    merged_at = pr["merged_at"]
    _parse_timestamp(merged_at, "merged_at")
    merged_by = pr.get("merged_by", {}).get("login")
    if not isinstance(merged_by, str) or not merged_by:
        raise LoopMemoryError("merged pull request has no merged_by identity")
    expected_pr_url = f"https://github.com/{repository}/pull/{pr_number}"
    if pr.get("html_url") != expected_pr_url:
        raise LoopMemoryError(
            "merged pull request URL does not match repository and number"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": repository,
        "state_branch": STATE_BRANCH,
        "updated_at": merged_at,
        "source": {
            "main_sha": merge_sha,
            "first_parent_sha": first_parent_sha,
            "pr_number": pr_number,
            "pr_url": expected_pr_url,
            "pr_title": _bounded_text(
                pr.get("title"), "pull request title", maximum=240
            ),
            "head_sha": head_sha,
            "head_ref": _bounded_text(
                pr.get("head", {}).get("ref"), "head ref", maximum=240
            ),
            "merged_at": merged_at,
            "merged_by": merged_by,
            "intent_path": intent_path,
            "intent_blob_sha": intent_blob_sha,
        },
        "completed_chunk": asdict(metadata),
        "active": {"planning_chunk": None, "implementation_chunk": None},
        "gate": {
            "status": "stopped_after_merge",
            "next_chunk_id": metadata.next_chunk_id,
            "next_chunk_title": metadata.next_chunk_title,
            "next_requires_explicit_start": metadata.next_requires_explicit_start,
        },
        "checks": _check_evidence(check_runs, statuses),
    }


def _parse_timestamp(value: Any, field: str) -> datetime:
    """Parse one UTC GitHub timestamp."""
    if not isinstance(value, str):
        raise LoopMemoryError(f"{field} must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LoopMemoryError(f"{field} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise LoopMemoryError(f"{field} must include a timezone")
    return parsed


def render_state(state: dict[str, Any]) -> str:
    """Render the canonical JSON state as a concise human-readable view."""
    source = state["source"]
    completed = state["completed_chunk"]
    gate = state["gate"]
    checks = state["checks"]
    next_line = "- Next chunk: none recorded."
    if gate["next_chunk_id"]:
        start = (
            "requires a separate explicit start"
            if gate["next_requires_explicit_start"]
            else "may use an existing start signal"
        )
        next_line = (
            f"- Next chunk: `{gate['next_chunk_id']}` - "
            f"{_markdown_text(gate['next_chunk_title'])}; {start}."
        )
    check_lines = []
    for name in REQUIRED_CHECKS:
        result = checks["required"][name]
        check_lines.append(f"  - `{name}`: `{result['conclusion'] or 'missing'}`")
    integrity = "passed" if checks["all_required_passed"] else "attention required"
    return "\n".join(
        [
            "# Generated Workstream Loop State",
            "",
            "> Canonical generated view. Do not edit this branch by hand.",
            "",
            f"- Repository: `{state['repository']}`",
            f"- Last merged PR: [#{source['pr_number']}]({source['pr_url']}) - "
            f"{_markdown_text(source['pr_title'])}",
            f"- Merge commit: `{source['main_sha']}`",
            f"- Final PR head: `{source['head_sha']}`",
            f"- Merged at: `{source['merged_at']}` by `{source['merged_by']}`",
            f"- Merge intent: `{source['intent_path']}` at blob `{source['intent_blob_sha']}`",
            f"- Completed chunk: `{completed['chunk_id']}` - "
            f"{_markdown_text(completed['chunk_title'])}",
            "- Active planning chunk: none",
            "- Active implementation chunk: none",
            f"- Current gate: `{gate['status']}`",
            next_line,
            f"- Required check evidence: {integrity}",
            *check_lines,
            "",
            f"Machine-readable state: `{STATE_PATH.as_posix()}`",
            f"Append-only merge ledger: `{LEDGER_PATH.as_posix()}`",
            "",
        ]
    )


def _canonical_json(value: Any, *, pretty: bool = False) -> str:
    """Return deterministic JSON text."""
    if pretty:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _markdown_text(value: str) -> str:
    """Escape bounded metadata before rendering it into Markdown."""
    return (
        value.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _atomic_write(path: Path, content: str) -> None:
    """Write one generated file atomically within its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    """Load an optional JSON object."""
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LoopMemoryError(f"cannot read generated state at {path}") from exc
    if not isinstance(value, dict):
        raise LoopMemoryError("generated state must be a JSON object")
    return value


def _load_ledger(path: Path) -> list[dict[str, Any]]:
    """Load and validate the optional JSONL merge ledger."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise LoopMemoryError("merge ledger entries must be JSON objects")
                records.append(value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LoopMemoryError(f"cannot read merge ledger at {path}") from exc
    return records


def _ledger_hash(previous_hash: str | None, record: dict[str, Any]) -> str:
    """Return the deterministic hash for one chained ledger entry."""
    payload = f"{previous_hash or ''}\n{_canonical_json(record)}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _ledger_entry(record: dict[str, Any], previous_hash: str | None) -> dict[str, Any]:
    """Wrap a merge record in one append-only hash-chain entry."""
    return {
        "schema_version": SCHEMA_VERSION,
        "previous_entry_hash": previous_hash,
        "record": record,
        "entry_hash": _ledger_hash(previous_hash, record),
    }


def _validate_ledger_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate the full ledger hash and first-parent chains."""
    records: list[dict[str, Any]] = []
    previous_hash: str | None = None
    previous_main_sha: str | None = None
    expected_keys = {
        "schema_version",
        "previous_entry_hash",
        "record",
        "entry_hash",
    }
    for entry in entries:
        if set(entry) != expected_keys or entry.get("schema_version") != SCHEMA_VERSION:
            raise LoopMemoryError("merge ledger entry has an invalid schema")
        record = entry.get("record")
        if not isinstance(record, dict):
            raise LoopMemoryError("merge ledger entry record must be a JSON object")
        if entry.get("previous_entry_hash") != previous_hash:
            raise LoopMemoryError("merge ledger previous hash chain is invalid")
        expected_hash = _ledger_hash(previous_hash, record)
        if entry.get("entry_hash") != expected_hash:
            raise LoopMemoryError("merge ledger entry hash is invalid")
        source = record.get("source", {})
        if (
            previous_main_sha is not None
            and source.get("first_parent_sha") != previous_main_sha
        ):
            raise LoopMemoryError("merge ledger first-parent chain is invalid")
        main_sha = source.get("main_sha")
        if not isinstance(main_sha, str) or not SHA_PATTERN.fullmatch(main_sha):
            raise LoopMemoryError("merge ledger record has no canonical main SHA")
        records.append(record)
        previous_hash = expected_hash
        previous_main_sha = main_sha
    return records


def apply_merge_record(state_root: Path, record: dict[str, Any]) -> bool:
    """Apply one monotonic, idempotent merge record to a state directory."""
    state_path = state_root / STATE_PATH
    ledger_path = state_root / LEDGER_PATH
    rendered_path = state_root / RENDERED_PATH
    existing = _load_json(state_path)
    ledger = _load_ledger(ledger_path)
    records = _validate_ledger_entries(ledger)
    merge_sha = record["source"]["main_sha"]

    if existing is not None and (
        not records or _canonical_json(records[-1]) != _canonical_json(existing)
    ):
        raise LoopMemoryError("canonical state does not match the merge ledger tail")

    duplicate = next(
        (
            entry
            for entry in records
            if entry.get("source", {}).get("main_sha") == merge_sha
        ),
        None,
    )
    if duplicate is not None:
        same_identity = (
            duplicate.get("source") == record.get("source")
            and duplicate.get("completed_chunk") == record.get("completed_chunk")
            and duplicate.get("gate") == record.get("gate")
        )
        if not same_identity:
            raise LoopMemoryError("merge SHA already exists with different state")
        return False

    if existing is not None:
        if record.get("source", {}).get("first_parent_sha") != existing.get(
            "source", {}
        ).get("main_sha"):
            raise LoopMemoryError(
                "merge record is not the direct first-parent successor"
            )

    previous_hash = ledger[-1]["entry_hash"] if ledger else None
    ledger.append(_ledger_entry(record, previous_hash))
    _atomic_write(state_path, _canonical_json(record, pretty=True))
    _atomic_write(rendered_path, render_state(record))
    _atomic_write(
        ledger_path, "".join(f"{_canonical_json(entry)}\n" for entry in ledger)
    )
    return True


def validate_generated_state(state_root: Path) -> None:
    """Validate JSON, rendered Markdown, and ledger agreement."""
    state = _load_json(state_root / STATE_PATH)
    if state is None:
        raise LoopMemoryError("generated state file is missing")
    if (
        state.get("schema_version") != SCHEMA_VERSION
        or state.get("state_branch") != STATE_BRANCH
    ):
        raise LoopMemoryError("generated state schema or branch is invalid")
    _validate_repository_and_sha(
        state.get("repository", ""), state.get("source", {}).get("main_sha", "")
    )
    ledger = _load_ledger(state_root / LEDGER_PATH)
    records = _validate_ledger_entries(ledger)
    if not records or _canonical_json(records[-1]) != _canonical_json(state):
        raise LoopMemoryError("merge ledger tail does not match canonical state")
    rendered_path = state_root / RENDERED_PATH
    if not rendered_path.exists() or rendered_path.read_text(
        encoding="utf-8"
    ) != render_state(state):
        raise LoopMemoryError("rendered loop state does not match canonical JSON")


def _signature_payload(state_root: Path) -> bytes:
    """Return an unambiguous payload covering every canonical generated file."""
    payload = bytearray(b"workstream-loop-memory-signature-v1\0")
    for relative_path in (STATE_PATH, RENDERED_PATH, LEDGER_PATH):
        path_bytes = relative_path.as_posix().encode("ascii")
        content = (state_root / relative_path).read_bytes()
        payload.extend(len(path_bytes).to_bytes(4, "big"))
        payload.extend(path_bytes)
        payload.extend(len(content).to_bytes(8, "big"))
        payload.extend(content)
    return bytes(payload)


def sign_generated_state(state_root: Path, private_key: Path) -> None:
    """Sign validated generated state with the Actions-only Ed25519 key."""
    validate_generated_state(state_root)
    with tempfile.NamedTemporaryFile() as payload_file:
        payload_file.write(_signature_payload(state_root))
        payload_file.flush()
        result = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-rawin",
                "-inkey",
                str(private_key),
                "-in",
                payload_file.name,
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    if result.returncode != 0 or len(result.stdout) != 64:
        raise LoopMemoryError("cannot sign generated loop memory")
    _atomic_write(
        state_root / SIGNATURE_PATH,
        base64.b64encode(result.stdout).decode("ascii") + "\n",
    )


def verify_generated_state_signature(
    state_root: Path,
    public_key: Path,
    expected_main_sha: str | None = None,
) -> None:
    """Verify canonical generated files, signature, and optional main freshness."""
    validate_generated_state(state_root)
    try:
        encoded_signature = (state_root / SIGNATURE_PATH).read_text(encoding="ascii")
        signature = base64.b64decode(encoded_signature.strip(), validate=True)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise LoopMemoryError("generated loop-memory signature is unreadable") from exc
    if len(signature) != 64:
        raise LoopMemoryError("generated loop-memory signature has an invalid length")
    with (
        tempfile.NamedTemporaryFile() as signature_file,
        tempfile.NamedTemporaryFile() as payload_file,
    ):
        signature_file.write(signature)
        signature_file.flush()
        payload_file.write(_signature_payload(state_root))
        payload_file.flush()
        result = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-verify",
                "-rawin",
                "-pubin",
                "-inkey",
                str(public_key),
                "-sigfile",
                signature_file.name,
                "-in",
                payload_file.name,
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    if result.returncode != 0:
        raise LoopMemoryError("generated loop-memory signature verification failed")
    if expected_main_sha is not None:
        _validate_sha(expected_main_sha)
        state = _load_json(state_root / STATE_PATH)
        if (
            state is None
            or state.get("source", {}).get("main_sha") != expected_main_sha
        ):
            raise LoopMemoryError(
                "generated loop memory is not current for protected main"
            )


def _assert_state_branch(state_root: Path) -> None:
    """Refuse to write generated memory outside its dedicated branch."""
    result = subprocess.run(
        ["git", "-C", str(state_root), "branch", "--show-current"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0 or result.stdout.strip() != STATE_BRANCH:
        raise LoopMemoryError(f"state root must be checked out on {STATE_BRANCH}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_intent = subparsers.add_parser("validate-merge-intent")
    validate_intent.add_argument("--repository-root", type=Path, default=Path("."))
    validate_intent.add_argument("--base-ref", required=True)

    plan_commits = subparsers.add_parser("plan-commits")
    plan_commits.add_argument("--repository-root", type=Path, default=Path("."))
    plan_commits.add_argument("--target-sha", required=True)
    plan_commits.add_argument("--current-sha")

    update = subparsers.add_parser("update")
    update.add_argument("--repository", required=True)
    update.add_argument("--merge-sha", required=True)
    update.add_argument("--state-root", type=Path, required=True)
    update.add_argument("--token-env", default="GITHUB_TOKEN")
    update.add_argument("--api-url", default="https://api.github.com")

    validate_state = subparsers.add_parser("validate-state")
    validate_state.add_argument("--state-root", type=Path, required=True)

    sign_state = subparsers.add_parser("sign-state")
    sign_state.add_argument("--state-root", type=Path, required=True)
    sign_state.add_argument("--private-key", type=Path, required=True)

    verify_state = subparsers.add_parser("verify-state")
    verify_state.add_argument("--state-root", type=Path, required=True)
    verify_state.add_argument("--public-key", type=Path, required=True)
    verify_state.add_argument("--expected-main-sha")

    show = subparsers.add_parser("show")
    show.add_argument("--state-root", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run metadata validation, state update, validation, or display."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-merge-intent":
            metadata = validate_local_merge_intent(
                args.repository_root,
                args.base_ref,
            )
            print(f"Merge intent passed for {metadata.chunk_id}.")
        elif args.command == "plan-commits":
            for merge_sha in plan_reconciliation_commits(
                args.repository_root,
                args.target_sha,
                args.current_sha,
            ):
                print(merge_sha)
        elif args.command == "update":
            _assert_state_branch(args.state_root)
            token = os.environ.get(args.token_env, "")
            record = collect_merge_record(
                GitHubClient(token, args.api_url),
                args.repository,
                args.merge_sha,
            )
            changed = apply_merge_record(args.state_root, record)
            validate_generated_state(args.state_root)
            result = "updated" if changed else "already current"
            print(f"Loop memory {result} for PR #{record['source']['pr_number']}.")
        elif args.command == "validate-state":
            validate_generated_state(args.state_root)
            print("Generated loop memory state passed.")
        elif args.command == "sign-state":
            sign_generated_state(args.state_root, args.private_key)
            print("Generated loop memory state signed.")
        elif args.command == "verify-state":
            verify_generated_state_signature(
                args.state_root,
                args.public_key,
                args.expected_main_sha,
            )
            print("Generated loop memory state signature passed.")
        elif args.command == "show":
            validate_generated_state(args.state_root)
            print((args.state_root / RENDERED_PATH).read_text(encoding="utf-8"), end="")
        else:  # pragma: no cover - argparse enforces the command set.
            raise LoopMemoryError("unsupported command")
    except (LoopMemoryError, OSError, UnicodeDecodeError) as exc:
        print(f"Post-merge memory failed closed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
