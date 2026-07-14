"""Validate merged loop memory is not left in a pre-merge state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKED_FILES = (
    ".agent-loop/LOOP_STATE.md",
    ".agent-loop/WORK_QUEUE.md",
    ".agent-loop/REVIEW_LOG.md",
)
INITIATIVE_STATUS_FILES = tuple(
    str(path.relative_to(ROOT))
    for path in (ROOT / ".agent-loop/initiatives").glob("*/STATUS.md")
)
FORBIDDEN_PATTERNS = (
    (re.compile(r"PR #\d+ open", re.IGNORECASE), "merged main cannot list an open PR"),
    (
        re.compile(r"awaiting human merge decision", re.IGNORECASE),
        "merged main cannot await a merge decision",
    ),
    (
        re.compile(r"human merge checkpoint", re.IGNORECASE),
        "merged main cannot remain at the human merge checkpoint",
    ),
    (
        re.compile(r"CI ready for final rerun", re.IGNORECASE),
        "merged main cannot wait for final CI rerun",
    ),
    (
        re.compile(r"Push the reviewed revision", re.IGNORECASE),
        "merged main cannot instruct pushing reviewed revision",
    ),
    (
        re.compile(
            r"CodeRabbit, then stop for the user-owned merge decision", re.IGNORECASE
        ),
        "merged main cannot wait for external review before merge",
    ),
    (
        re.compile(
            r"\|\s*`[^`]+`\s*\|[^|]+\|[^|]+\|\s*In progress\s*\|", re.IGNORECASE
        ),
        "merged main cannot keep a completed chunk in active In progress state",
    ),
)
GENERATED_FILES = (
    ".agent-loop/STATE.json",
    ".agent-loop/LOOP_STATE.md",
    ".agent-loop/MERGE_LOG.jsonl",
)


def checked_paths() -> list[Path]:
    """Return loop memory paths that must not contain pre-merge state."""
    paths = [ROOT / path for path in CHECKED_FILES]
    paths.extend(ROOT / path for path in INITIATIVE_STATUS_FILES)
    return paths


def generated_state_failures(root: Path) -> list[str]:
    """Return consistency failures for generated automation-branch state."""
    paths = [root / path for path in GENERATED_FILES]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        return [
            f"{path.relative_to(root)}: missing generated loop memory file"
            for path in missing
        ]
    try:
        state = json.loads(paths[0].read_text(encoding="utf-8"))
        ledger = [
            json.loads(line)
            for line in paths[2].read_text(encoding="utf-8").splitlines()
            if line
        ]
        rendered = paths[1].read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"generated loop memory is unreadable: {exc.__class__.__name__}"]
    if not isinstance(state, dict):
        return [".agent-loop/STATE.json: expected a JSON object"]
    failures: list[str] = []
    if state.get("schema_version") != 1:
        failures.append(".agent-loop/STATE.json: unsupported schema version")
    if state.get("state_branch") != "automation/loop-memory":
        failures.append(".agent-loop/STATE.json: unexpected state branch")
    previous_hash = None
    previous_main_sha = None
    ledger_records = []
    expected_keys = {
        "schema_version",
        "previous_entry_hash",
        "record",
        "entry_hash",
    }
    for entry in ledger:
        if not isinstance(entry, dict) or set(entry) != expected_keys:
            failures.append(".agent-loop/MERGE_LOG.jsonl: invalid entry schema")
            break
        record = entry.get("record")
        if not isinstance(record, dict):
            failures.append(
                ".agent-loop/MERGE_LOG.jsonl: entry record is not an object"
            )
            break
        payload = (
            f"{previous_hash or ''}\n"
            f"{json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=True)}"
        ).encode("utf-8")
        expected_hash = hashlib.sha256(payload).hexdigest()
        if (
            entry.get("previous_entry_hash") != previous_hash
            or entry.get("entry_hash") != expected_hash
        ):
            failures.append(".agent-loop/MERGE_LOG.jsonl: hash chain is invalid")
            break
        source = record.get("source", {})
        if (
            previous_main_sha is not None
            and source.get("first_parent_sha") != previous_main_sha
        ):
            failures.append(
                ".agent-loop/MERGE_LOG.jsonl: first-parent chain is invalid"
            )
            break
        previous_hash = expected_hash
        previous_main_sha = source.get("main_sha")
        ledger_records.append(record)
    if not ledger_records or ledger_records[-1] != state:
        failures.append(
            ".agent-loop/MERGE_LOG.jsonl: ledger tail does not match live state"
        )
    source = state.get("source", {})
    chunk = state.get("completed_chunk", {})
    for value, label in (
        (source.get("main_sha"), "merge SHA"),
        (chunk.get("chunk_id"), "completed chunk"),
    ):
        if not isinstance(value, str) or f"`{value}`" not in rendered:
            failures.append(f".agent-loop/LOOP_STATE.md: missing generated {label}")
    return failures


def build_parser() -> argparse.ArgumentParser:
    """Build the loop-memory validator parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate generated state or legacy main memory."""
    args = build_parser().parse_args([] if argv is None else argv)
    if args.state_root:
        failures = generated_state_failures(args.state_root)
        if failures:
            print("Generated loop memory state is invalid:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1
        print("Generated loop memory state check passed.")
        return 0

    failures: list[str] = []
    for path in checked_paths():
        if not path.exists():
            failures.append(f"{path.relative_to(ROOT)}: missing loop memory file")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, message in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: {message}")

    if failures:
        print("Loop memory state is stale:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Loop memory state check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
