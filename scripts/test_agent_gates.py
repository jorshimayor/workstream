"""Regression tests for Workstream agent gate helpers.

Run with plain Python so the agent-gates workflow does not need test
dependencies installed before it can protect the repository process.
"""

from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: str):
    """Load a script module by path."""
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_required_tracks_expand_for_loop_and_ci_paths() -> None:
    """Loop, Codex, script, and workflow paths require focused reviewers."""
    gate = load_module("review_gate", "scripts/check_internal_review_evidence.py")
    tracks = gate.required_tracks_for(
        [
            ".agent-loop/policies/engineering-review-policy.md",
            ".agents/skills/qa-review/SKILL.md",
            ".codex/agents/qa-reviewer.toml",
            ".github/workflows/agent-gates.yml",
            "scripts/workstream_agent_gate.py",
        ]
    )
    assert tracks == (
        "senior engineering",
        "qa/test",
        "security/auth",
        "product/ops",
        "architecture",
        "docs",
        "reuse/dedup",
        "ci integrity",
    )


def test_backend_config_paths_require_review_evidence() -> None:
    """Migration and backend tooling paths cannot bypass review evidence."""
    gate = load_module(
        "review_gate_backend_paths", "scripts/check_internal_review_evidence.py"
    )
    assert gate.is_relevant("backend/alembic/versions/0001_init.py")
    assert gate.is_relevant("backend/alembic.ini")
    assert gate.is_relevant("backend/pyproject.toml")

    backend_tracks = gate.required_tracks_for(["backend/alembic/versions/0001_init.py"])
    assert "architecture" in backend_tracks
    assert "ci integrity" not in backend_tracks

    backend_config_tracks = gate.required_tracks_for(["backend/pyproject.toml"])
    assert "ci integrity" in backend_config_tracks


def test_review_evidence_files_are_not_relevant_changes() -> None:
    """Review evidence files satisfy the gate without requiring more evidence."""
    gate = load_module(
        "review_gate_relevance", "scripts/check_internal_review_evidence.py"
    )
    assert not gate.is_relevant(".agent-loop/initiatives/example/reviews/review.md")
    assert not gate.is_relevant("docs/internal_reviews/example.md")
    assert not gate.is_internal_review_evidence_path("docs/internal_reviews/example.md")
    assert gate.is_internal_review_evidence_path(
        ".agent-loop/initiatives/example/reviews/example-internal-review-evidence.md"
    )
    assert not gate.is_internal_review_evidence_path(
        ".agent-loop/initiatives/example/reviews/example-external-review-response.md"
    )


def test_evidence_requires_completed_yes_statements() -> None:
    """Evidence must contain affirmative completion statements."""
    gate = load_module(
        "review_gate_statements", "scripts/check_internal_review_evidence.py"
    )
    original_changed_files = gate.changed_files
    gate.changed_files = lambda: []
    required = ("senior engineering", "qa/test")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            weak = Path(tmpdir) / "weak.md"
            weak.write_text(
                "| Reviewer | Result | Blocking findings |\n"
                "|---|---:|---|\n"
                "| senior engineering | PASS | None |\n"
                "| qa/test | PASS | None |\n"
                "open sub-agent sessions: none\nvalid findings addressed: no\n",
                encoding="utf-8",
            )
            assert "valid findings addressed: yes" in gate.validate_evidence(
                weak,
                required,
                enforce_reviewed_revision=False,
            )

            strong = Path(tmpdir) / "strong.md"
            strong.write_text(
                "| Reviewer | Result | Blocking findings |\n"
                "|---|---:|---|\n"
                "| senior engineering | PASS | None |\n"
                "| qa/test | PASS | None |\n"
                "open sub-agent sessions: none\nvalid findings addressed: yes\n",
                encoding="utf-8",
            )
            assert (
                gate.validate_evidence(
                    strong, required, enforce_reviewed_revision=False
                )
                == []
            )
    finally:
        gate.changed_files = original_changed_files


def test_evidence_must_reference_changed_chunk() -> None:
    """Evidence must mention the changed chunk contract when one exists."""
    gate = load_module("review_gate_chunk", "scripts/check_internal_review_evidence.py")
    original_changed_files = gate.changed_files
    gate.changed_files = lambda: [
        ".agent-loop/initiatives/WS-ENG-001-codex-zero-trust-loop-bootstrap/"
        "chunks/WS-ENG-001-01-codex-loop-bootstrap.md"
    ]
    required = ("senior engineering",)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence = Path(tmpdir) / "review.md"
            evidence.write_text(
                "| Reviewer | Result | Blocking findings |\n"
                "|---|---:|---|\n"
                "| senior engineering | PASS | None |\n"
                "open sub-agent sessions: none\nvalid findings addressed: yes\n",
                encoding="utf-8",
            )
            assert "chunk id: one of ws-eng-001-01" in gate.validate_evidence(
                evidence,
                required,
                enforce_reviewed_revision=False,
            )

            evidence.write_text(
                "WS-ENG-001-01\n"
                "| Reviewer | Result | Blocking findings |\n"
                "|---|---:|---|\n"
                "| senior engineering | PASS | None |\n"
                "open sub-agent sessions: none\nvalid findings addressed: yes\n",
                encoding="utf-8",
            )
            assert (
                gate.validate_evidence(
                    evidence, required, enforce_reviewed_revision=False
                )
                == []
            )
    finally:
        gate.changed_files = original_changed_files


def test_evidence_rejects_pending_or_blocking_reviewer_rows() -> None:
    """Evidence table rows must show passing reviewers and no blocking findings."""
    gate = load_module("review_gate_rows", "scripts/check_internal_review_evidence.py")
    original_changed_files = gate.changed_files
    gate.changed_files = lambda: []
    required = ("senior engineering", "qa/test")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence = Path(tmpdir) / "review.md"
            evidence.write_text(
                "| Reviewer | Result | Blocking findings |\n"
                "|---|---:|---|\n"
                "| senior engineering | PASS | None |\n"
                "| qa/test | Pending | High finding |\n"
                "open sub-agent sessions: none\nvalid findings addressed: yes\n",
                encoding="utf-8",
            )
            missing = gate.validate_evidence(
                evidence, required, enforce_reviewed_revision=False
            )
            assert any(
                "qa/test reviewer result must be one of" in item for item in missing
            )
            assert "qa/test blocking findings must be none" in missing
    finally:
        gate.changed_files = original_changed_files


def test_evidence_accepts_exact_pass_and_approved_na_results() -> None:
    """Reviewer result values are exact, with explicit N/A reason support."""
    gate = load_module(
        "review_gate_exact_results", "scripts/check_internal_review_evidence.py"
    )
    required = ("senior engineering",)
    text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | PASS WITH LOW RISKS | None | checked |\n"
        "| qa/test | N/A - with approved reason | None | explicitly unrelated because docs only |\n"
    )
    assert gate.validate_reviewer_rows(text.lower(), required) == []

    bad_text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | bypass | None | malformed |\n"
    )
    missing = gate.validate_reviewer_rows(bad_text.lower(), required)
    assert any(
        "senior engineering reviewer result must be one of" in item for item in missing
    )

    optional_bad_text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | PASS | None | checked |\n"
        "| docs | Pending / N/A - with approved reason | None | |\n"
        "| ci integrity | N/A | None | |\n"
    )
    missing = gate.validate_reviewer_rows(optional_bad_text.lower(), required)
    assert any("docs reviewer result must be one of" in item for item in missing)
    assert any(
        "ci integrity reviewer result must be one of" in item for item in missing
    )

    unrelated_table_text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | PASS | None | checked |\n"
        "| Finding | Severity | Status |\n"
        "|---|---:|---|\n"
        "| F-001 | high | closed |\n"
    )
    assert gate.validate_reviewer_rows(unrelated_table_text.lower(), required) == []

    missing_note_text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | PASS | None | checked |\n"
        "| docs | N/A - with approved reason | None | pending |\n"
    )
    missing = gate.validate_reviewer_rows(missing_note_text.lower(), required)
    assert "docs n/a result requires notes" in missing


def test_evidence_rejects_na_for_required_tracks() -> None:
    """Required reviewer tracks must pass and cannot be bypassed with N/A."""
    gate = load_module(
        "review_gate_required_na", "scripts/check_internal_review_evidence.py"
    )
    required = ("security/auth", "architecture")
    text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| security/auth | N/A - with approved reason | None | claimed unrelated |\n"
        "| architecture | N/A - with approved reason | None | claimed unrelated |\n"
    )
    missing = gate.validate_reviewer_rows(text.lower(), required)
    assert "security/auth reviewer result cannot be n/a when required" in missing
    assert "architecture reviewer result cannot be n/a when required" in missing


def test_evidence_reviewed_revision_allows_only_evidence_status_changes() -> None:
    """Evidence must be bound to a reviewed SHA and only status files may follow."""
    gate = load_module(
        "review_gate_revision_binding", "scripts/check_internal_review_evidence.py"
    )
    original_git = gate.git
    original_git_ok = gate.git_ok
    reviewed = "a" * 40

    def fake_git(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return "b" * 40
        if args == ("diff", "--name-only", f"{reviewed}..{'b' * 40}"):
            return (
                ".agent-loop/LOOP_STATE.md\n"
                ".agent-loop/initiatives/example/reviews/review.md\n"
                "docs/internal_reviews/review.md"
            )
        if args in {
            ("diff", "--name-only", "--cached"),
            ("diff", "--name-only"),
            ("ls-files", "--others", "--exclude-standard"),
        }:
            return ""
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    try:
        text = (
            f"Reviewed code SHA: {reviewed}\n"
            "Reviewed at: 2026-06-18T00:00:00Z\n"
            "Reviewer run IDs: local\n"
        ).lower()
        assert gate.validate_reviewed_revision(text) == []
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok


def test_evidence_reviewed_revision_rejects_late_implementation_changes() -> None:
    """Implementation changes after the reviewed SHA invalidate evidence."""
    gate = load_module(
        "review_gate_revision_rejects_late_changes",
        "scripts/check_internal_review_evidence.py",
    )
    original_git = gate.git
    original_git_ok = gate.git_ok
    reviewed = "a" * 40

    def fake_git(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return "b" * 40
        if args == ("diff", "--name-only", f"{reviewed}..{'b' * 40}"):
            return "scripts/check_internal_review_evidence.py"
        if args in {
            ("diff", "--name-only", "--cached"),
            ("diff", "--name-only"),
            ("ls-files", "--others", "--exclude-standard"),
        }:
            return ""
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    try:
        text = (
            f"Reviewed code SHA: {reviewed}\n"
            "Reviewed at: 2026-06-18T00:00:00Z\n"
            "Reviewer run IDs: local\n"
        ).lower()
        missing = gate.validate_reviewed_revision(text)
        assert any("reviewed code sha is stale" in item for item in missing)
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok


def test_evidence_reviewed_revision_rejects_dirty_tree_changes() -> None:
    """Staged, unstaged, and untracked implementation changes invalidate evidence."""
    gate = load_module(
        "review_gate_revision_rejects_dirty",
        "scripts/check_internal_review_evidence.py",
    )
    original_git = gate.git
    original_git_ok = gate.git_ok
    reviewed = "a" * 40

    def fake_git(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return reviewed
        if args == ("diff", "--name-only", f"{reviewed}..{reviewed}"):
            return ""
        if args == ("diff", "--name-only", "--cached"):
            return "scripts/staged_change.py"
        if args == ("diff", "--name-only"):
            return "scripts/check_internal_review_evidence.py"
        if args == ("ls-files", "--others", "--exclude-standard"):
            return "scripts/untracked_change.py"
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    try:
        text = (
            f"Reviewed code SHA: {reviewed}\n"
            "Reviewed at: 2026-06-18T00:00:00Z\n"
            "Reviewer run IDs: local\n"
        ).lower()
        missing = gate.validate_reviewed_revision(text)
        assert any("reviewed code sha is stale" in item for item in missing)
        stale = next(item for item in missing if "reviewed code sha is stale" in item)
        assert "scripts/staged_change.py" in stale
        assert "scripts/check_internal_review_evidence.py" in stale
        assert "scripts/untracked_change.py" in stale
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok


def test_evidence_reviewed_revision_rejects_invalid_provenance() -> None:
    """Reviewed at and reviewer run IDs must contain concrete values."""
    gate = load_module(
        "review_gate_revision_blank_provenance",
        "scripts/check_internal_review_evidence.py",
    )
    original_git = gate.git
    original_git_ok = gate.git_ok
    reviewed = "a" * 40

    def fake_git(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return reviewed
        if args == ("diff", "--name-only", f"{reviewed}..{reviewed}"):
            return ""
        if args in {
            ("diff", "--name-only", "--cached"),
            ("diff", "--name-only"),
            ("ls-files", "--others", "--exclude-standard"),
        }:
            return ""
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    try:
        text = (
            f"Reviewed code SHA: {reviewed}\nReviewed at:\nReviewer run IDs:\n".lower()
        )
        missing = gate.validate_reviewed_revision(text)
        assert "reviewed at" in missing
        assert "reviewer run ids" in missing

        placeholder_text = (
            f"Reviewed code SHA: `{reviewed}`\n"
            "Reviewed at: `<UTC timestamp>`\n"
            "Reviewer run IDs: `<agent ids, CI run IDs, or local reviewer run references>`\n"
        ).lower()
        missing = gate.validate_reviewed_revision(placeholder_text)
        assert "reviewed at" in missing
        assert "reviewer run ids" in missing

        bad_timestamp_text = (
            f"Reviewed code SHA: {reviewed}\n"
            "Reviewed at: 2026-06-18 00:00:00\n"
            "Reviewer run IDs: 019eda06-0848-7131-8895-48f8ea720fb9\n"
        ).lower()
        assert "reviewed at" in gate.validate_reviewed_revision(bad_timestamp_text)
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok


def test_evidence_main_fails_closed_on_unresolved_base_ref() -> None:
    """Configured base refs must resolve before the evidence gate can pass."""
    gate = load_module(
        "review_gate_base_ref", "scripts/check_internal_review_evidence.py"
    )
    original_env = os.environ.get("INTERNAL_REVIEW_BASE_REF")
    original_git_ok = gate.git_ok
    os.environ["INTERNAL_REVIEW_BASE_REF"] = "missing-base"
    gate.git_ok = lambda *args: False
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            assert gate.main() == 1
    finally:
        gate.git_ok = original_git_ok
        if original_env is None:
            os.environ.pop("INTERNAL_REVIEW_BASE_REF", None)
        else:
            os.environ["INTERNAL_REVIEW_BASE_REF"] = original_env


def test_evidence_main_passes_with_complete_evidence_and_pr_head() -> None:
    """The full evidence gate passes when evidence is complete and bound to PR_HEAD_SHA."""
    gate = load_module(
        "review_gate_main_complete", "scripts/check_internal_review_evidence.py"
    )
    original_env = {
        "INTERNAL_REVIEW_BASE_REF": os.environ.get("INTERNAL_REVIEW_BASE_REF"),
        "INTERNAL_REVIEW_CHUNK_ID": os.environ.get("INTERNAL_REVIEW_CHUNK_ID"),
        "PR_HEAD_SHA": os.environ.get("PR_HEAD_SHA"),
    }
    original_git = gate.git
    original_git_ok = gate.git_ok
    original_changed_files = gate.changed_files
    reviewed = "a" * 40
    local_head = "b" * 40
    evidence = (
        ROOT / ".agent-loop/initiatives/test-agent-gate/"
        "reviews/test-agent-gate-internal-review-evidence.md"
    )

    def fake_git(*args: str) -> str:
        if args == ("merge-base", "--is-ancestor", "origin/main", "HEAD"):
            return ""
        if args == ("rev-parse", "HEAD"):
            return local_head
        if args == ("diff", "--name-only", f"{reviewed}..{reviewed}"):
            return ""
        if args in {
            ("diff", "--name-only", "--cached"),
            ("diff", "--name-only"),
            ("ls-files", "--others", "--exclude-standard"),
        }:
            return ""
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    gate.changed_files = lambda: [
        "scripts/check_internal_review_evidence.py",
        ".agent-loop/initiatives/test-agent-gate/"
        "reviews/test-agent-gate-internal-review-evidence.md",
        "docs/internal_reviews/historical-note.md",
        ".agent-loop/initiatives/example/reviews/example-external-review-response.md",
    ]
    try:
        os.environ.pop("INTERNAL_REVIEW_BASE_REF", None)
        os.environ["INTERNAL_REVIEW_CHUNK_ID"] = "WS-ENG-001-01"
        os.environ["PR_HEAD_SHA"] = reviewed
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(
            "WS-ENG-001-01\n"
            "open sub-agent sessions: none\n"
            "valid findings addressed: yes\n"
            f"Reviewed code SHA: {reviewed}\n"
            "Reviewed at: 2026-06-18T00:00:00Z\n"
            "Reviewer run IDs: 019eda83-6476-7230-895b-1877790c407b\n"
            "| Reviewer | Result | Blocking findings | Notes |\n"
            "|---|---:|---|---|\n"
            "| senior engineering | PASS | None | checked |\n"
            "| qa/test | PASS WITH LOW RISKS | None | checked |\n"
            "| security/auth | PASS | None | checked |\n"
            "| product/ops | PASS | None | checked |\n"
            "| ci integrity | PASS | None | checked |\n"
            "| reuse/dedup | PASS | None | checked |\n",
            encoding="utf-8",
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            assert gate.main() == 0
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok
        gate.changed_files = original_changed_files
        evidence.unlink(missing_ok=True)
        evidence.parent.rmdir()
        evidence.parent.parent.rmdir()
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_evidence_main_rejects_external_response_without_internal_evidence() -> None:
    """External review responses do not satisfy required internal evidence."""
    gate = load_module(
        "review_gate_external_response_only",
        "scripts/check_internal_review_evidence.py",
    )
    original_env = os.environ.get("INTERNAL_REVIEW_BASE_REF")
    original_git = gate.git
    original_git_ok = gate.git_ok
    original_changed_files = gate.changed_files
    external_response = (
        ROOT / ".agent-loop/initiatives/test-agent-gate/"
        "reviews/test-agent-gate-external-review-response.md"
    )

    def fake_git(*args: str) -> str:
        if args == ("merge-base", "--is-ancestor", "origin/main", "HEAD"):
            return ""
        return ""

    gate.git = fake_git
    gate.git_ok = lambda *args: True
    gate.changed_files = lambda: [
        "scripts/check_internal_review_evidence.py",
        ".agent-loop/initiatives/test-agent-gate/"
        "reviews/test-agent-gate-external-review-response.md",
    ]
    try:
        os.environ.pop("INTERNAL_REVIEW_BASE_REF", None)
        external_response.parent.mkdir(parents=True, exist_ok=True)
        external_response.write_text(
            "# External Review Response\n\n## Source\n\nCodeRabbit\n",
            encoding="utf-8",
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            assert gate.main() == 1
    finally:
        gate.git = original_git
        gate.git_ok = original_git_ok
        gate.changed_files = original_changed_files
        external_response.unlink(missing_ok=True)
        external_response.parent.rmdir()
        external_response.parent.parent.rmdir()
        if original_env is None:
            os.environ.pop("INTERNAL_REVIEW_BASE_REF", None)
        else:
            os.environ["INTERNAL_REVIEW_BASE_REF"] = original_env


def test_evidence_main_reports_missing_evidence_file() -> None:
    """Changed evidence paths that no longer exist produce structured failure."""
    gate = load_module(
        "review_gate_missing_evidence_file", "scripts/check_internal_review_evidence.py"
    )
    original_changed_files = gate.changed_files
    gate.changed_files = lambda: [
        "scripts/workstream_agent_gate.py",
        ".agent-loop/initiatives/example/reviews/deleted-internal-review-evidence.md",
    ]
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            assert gate.main() == 1
    finally:
        gate.changed_files = original_changed_files


def test_static_sensor_counts_untracked_text_lines() -> None:
    """The static sensor includes untracked text files in line totals."""
    sensor = load_module("agent_sensor", "scripts/workstream_agent_gate.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = Path(tmpdir) / "new.md"
        sample.write_text("one\ntwo\n", encoding="utf-8")
        assert sensor.count_text_lines(str(sample)) == 2


def test_static_sensor_requires_resolved_base_ref() -> None:
    """The static sensor must not silently pass when no base ref resolves."""
    sensor = load_module("agent_sensor_base_ref", "scripts/workstream_agent_gate.py")
    original_ref_exists = sensor.ref_exists
    original_first_existing_ref = sensor.first_existing_ref
    sensor.ref_exists = lambda ref: False
    sensor.first_existing_ref = lambda *refs: None

    try:
        report = sensor.analyze("missing-base", "HEAD")
        assert report["result"] == "REVIEW_REQUIRED"
        assert report["findings"][0]["code"] == "BASE_REF_UNRESOLVED"
    finally:
        sensor.ref_exists = original_ref_exists
        sensor.first_existing_ref = original_first_existing_ref


def test_static_sensor_accumulates_numstat_for_duplicate_paths() -> None:
    """Line totals include committed, staged, and dirty changes to one file."""
    sensor = load_module("agent_sensor_numstat", "scripts/workstream_agent_gate.py")
    original_maybe_run = sensor.maybe_run

    def fake_maybe_run(cmd: list[str]) -> str:
        joined = " ".join(cmd)
        if "diff --numstat origin/main...HEAD" in joined:
            return "3\t1\tscripts/workstream_agent_gate.py"
        if cmd == ["git", "diff", "--numstat", "--cached"]:
            return "2\t0\tscripts/workstream_agent_gate.py"
        if cmd == ["git", "diff", "--numstat"]:
            return "1\t4\tscripts/workstream_agent_gate.py"
        if "ls-files --others --exclude-standard" in joined:
            return ""
        return ""

    sensor.maybe_run = fake_maybe_run
    try:
        added, deleted, rows = sensor.numstat("origin/main", "HEAD")
        assert added == 6
        assert deleted == 5
        assert rows == [("scripts/workstream_agent_gate.py", 6, 5)]
    finally:
        sensor.maybe_run = original_maybe_run


def test_static_sensor_flags_backend_config_as_ci_surface() -> None:
    """Backend config and migration-control paths are CI/build sensitive."""
    sensor = load_module("agent_sensor_ci_paths", "scripts/workstream_agent_gate.py")
    assert sensor.CI_PATTERNS.search("backend/pyproject.toml")
    assert sensor.CI_PATTERNS.search("backend/alembic.ini")
    assert sensor.CI_PATTERNS.search("backend/alembic/versions/0001_init.py")


def test_markdown_link_checker_collects_base_cached_dirty_and_untracked() -> None:
    """Markdown link collection uses PR refs plus local dirty-tree paths."""
    checker = load_module("markdown_link_checker", "scripts/check_markdown_links.py")
    original_check_output = checker.subprocess.check_output
    original_run = checker.subprocess.run

    def fake_check_output(cmd: list[str], text: bool) -> str:
        joined = " ".join(cmd)
        if "diff --name-only origin/main...HEAD" in joined:
            return "README.md\nbackend/app/main.py\n"
        if "diff --name-only --cached" in joined:
            return ".agent-loop/README.md\n"
        if cmd == ["git", "diff", "--name-only"]:
            return "docs/glossary.md\n"
        if "ls-files --others --exclude-standard" in joined:
            return "new.md\n"
        return ""

    checker.subprocess.check_output = fake_check_output
    checker.subprocess.run = lambda *args, **kwargs: SimpleNamespace(returncode=0)
    try:
        assert [str(path) for path in checker.changed_markdown_files()] == [
            "README.md",
            ".agent-loop/README.md",
            "docs/glossary.md",
            "new.md",
        ]
    finally:
        checker.subprocess.check_output = original_check_output
        checker.subprocess.run = original_run


def test_stale_wording_patterns_catch_variants() -> None:
    """Stale wording patterns catch case and separator variants."""
    stale = load_module("stale_wording", "scripts/check_stale_workstream_wording.py")
    sample = "\n".join(
        [
            "Garden " + "Roadmap",
            "task-" + "production control plane",
            "This repository does not use auto-" + "merge.",
            "Claude " + "Code support is not configured here.",
            "Approved" + "TaskArtifactBinding",
            "Effective" + "TaskSubmissionArtifactPolicy",
            "Effective" + "SubmissionArtifactPolicy",
            "Project" + "PreSubmitCheckerSpec",
            "locked_" + "task_" + "artifact_binding_id",
            "locked_" + "effective_" + "task_submission_artifact_policy_hash",
            "task artifact " + "binding",
            "effective task submission artifact " + "policy",
            "effective task " + "policy",
            "effective_" + "project_policy_hash",
            "effective project policy " + "hash",
            "effective policy " + "hashes",
            "generated task " + "pre-submit checker",
            "task-level " + "PreSubmitCheckerPolicy",
            "task-level " + "pre-submit",
            "project/task " + "policy",
            "profile-" + "scoped",
            "project/" + "profile",
            "pre-submit checker policy " + "hash",
            "pre_submit_checker_" + "policy_hash",
            "project pre-submit checker policy " + "hashes",
            "project checker " + "hash",
            "PreSubmitCheckerPolicy " + "hash",
            "PreSubmitCheckerPolicy snapshot/" + "hash",
        ]
    )
    matches = [
        pattern.pattern
        for pattern in stale.FORBIDDEN_PATTERNS
        if pattern.search(sample)
    ]
    assert set(matches) == {
        "task-" + "production control plane",
        "garden " + "roadmap",
        "Approved" + "TaskArtifactBinding",
        "Effective" + "TaskSubmissionArtifactPolicy",
        "Effective" + "SubmissionArtifactPolicy",
        "Project" + "PreSubmitCheckerSpec",
        "task_" + "artifact_binding",
        "effective_" + "task_submission",
        "task artifact " + "binding",
        "effective task submission artifact " + "policy",
        "effective task " + "policy",
        "effective_" + "project_policy_hash",
        "effective project policy " + "hash(?:es)?",
        "effective policy " + "hash(?:es)?",
        "locked_" + "task_" + "artifact_binding_id",
        "locked_" + "effective_" + "task_submission_artifact_policy_hash",
        "generated task " + "pre-submit",
        "task-level " + "PreSubmitCheckerPolicy",
        "task-level " + "pre-submit",
        "project/task " + "policy",
        "profile-" + "scoped",
        "project/" + "profile",
        "pre-submit checker policy " + "hash(?:es)?",
        "pre_submit_checker_" + "policy_hash",
        "project pre-submit checker policy " + "hash(?:es)?",
        "project checker " + "hash(?:es)?",
        "PreSubmitCheckerPolicy " + "hash(?:es)?",
        "PreSubmitCheckerPolicy snapshot/" + "hash(?:es)?",
    }
    case_variant_sample = "\n".join(
        [
            "approved" + "taskartifactbinding",
            "effective" + "TaskSubmissionArtifactPolicy",
            "PROJECT" + "PRESUBMITCHECKERSPEC",
        ]
    )
    case_variant_matches = [
        pattern.pattern
        for pattern in stale.FORBIDDEN_PATTERNS
        if pattern.search(case_variant_sample)
    ]
    assert {
        "Approved" + "TaskArtifactBinding",
        "Effective" + "TaskSubmissionArtifactPolicy",
        "Project" + "PreSubmitCheckerSpec",
    }.issubset(set(case_variant_matches))
    failures = stale.forbidden_path_failures(
        [Path(".claude/settings.json"), Path("CLAUDE.md")]
    )
    assert len(failures) == 2


def test_stale_wording_skips_only_docs_internal_reviews_prefix() -> None:
    """Historical review archives are skipped without hiding other folders."""
    stale = load_module(
        "stale_wording_skip_prefix",
        "scripts/check_stale_workstream_wording.py",
    )
    original_check_output = stale.subprocess.check_output
    original_cwd = Path.cwd()

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "docs/internal_reviews").mkdir(parents=True)
        (root / "other/internal_reviews").mkdir(parents=True)
        (root / "active").mkdir()
        (root / "docs/internal_reviews/archive.md").write_text(
            "old review\n", encoding="utf-8"
        )
        (root / "other/internal_reviews/file.md").write_text(
            "active review\n", encoding="utf-8"
        )
        (root / "active/file.md").write_text("active doc\n", encoding="utf-8")

        def fake_check_output(cmd: list[str], text: bool) -> str:
            if cmd == ["git", "ls-files"]:
                return "\n".join(
                    [
                        "docs/internal_reviews/archive.md",
                        "other/internal_reviews/file.md",
                        "active/file.md",
                    ]
                )
            if cmd == ["git", "ls-files", "--others", "--exclude-standard"]:
                return ""
            return ""

        stale.subprocess.check_output = fake_check_output
        os.chdir(root)
        try:
            scanned = {path.as_posix() for path in stale.tracked_and_new_files()}
        finally:
            os.chdir(original_cwd)
            stale.subprocess.check_output = original_check_output

    assert "docs/internal_reviews/archive.md" not in scanned
    assert "other/internal_reviews/file.md" in scanned
    assert "active/file.md" in scanned


def test_stale_wording_catches_multiline_legacy_status_reconstruction() -> None:
    """The stale wording gate catches split legacy status construction."""
    stale = load_module(
        "stale_wording_multiline_legacy_status",
        "scripts/check_stale_workstream_wording.py",
    )
    sample = 'LEGACY = "auto" \\\n    + "_checking"\n'
    pattern = next(
        pattern
        for pattern in stale.FORBIDDEN_PATTERNS
        if pattern.pattern == r"auto\s*[\"']?\s*\\?\s*\+\s*[\"']?_checking"
    )

    match = pattern.search(sample)

    assert match is not None
    assert stale.line_number_for_offset(sample, match.start()) == 1


def test_loop_memory_state_rejects_pre_merge_status() -> None:
    """Main loop memory must not keep pre-merge checkpoint language."""
    checker = load_module(
        "loop_memory_state_rejects", "scripts/check_loop_memory_state.py"
    )
    original_root = checker.ROOT
    original_status_files = checker.INITIATIVE_STATUS_FILES
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".agent-loop/initiatives/example").mkdir(parents=True)
        (root / ".agent-loop/LOOP_STATE.md").write_text(
            "Status: PR #23 open; awaiting human merge decision\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/WORK_QUEUE.md").write_text(
            "| `WS-ENG-001-01` | Bootstrap | L1 | In progress |\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/REVIEW_LOG.md").write_text(
            "Status: internal reviewer fanout complete.\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/initiatives/example/STATUS.md").write_text(
            "Current gate: human merge checkpoint\n",
            encoding="utf-8",
        )
        checker.ROOT = root
        checker.INITIATIVE_STATUS_FILES = (".agent-loop/initiatives/example/STATUS.md",)
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                assert checker.main() == 1
        finally:
            checker.ROOT = original_root
            checker.INITIATIVE_STATUS_FILES = original_status_files


def test_loop_memory_state_accepts_merged_fixture() -> None:
    """Merged loop memory fixtures should pass the main-only guard."""
    checker = load_module(
        "loop_memory_state_accepts", "scripts/check_loop_memory_state.py"
    )
    original_root = checker.ROOT
    original_status_files = checker.INITIATIVE_STATUS_FILES
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".agent-loop/initiatives/example").mkdir(parents=True)
        (root / ".agent-loop/LOOP_STATE.md").write_text(
            "Status: `WS-ENG-001-01` merged through PR #23; no active chunk\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/WORK_QUEUE.md").write_text(
            "| None | No active chunk | - | Inactive |\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/REVIEW_LOG.md").write_text(
            "Status: merged through PR #23.\n",
            encoding="utf-8",
        )
        (root / ".agent-loop/initiatives/example/STATUS.md").write_text(
            "Current gate: stopped after merge memory update\n",
            encoding="utf-8",
        )
        checker.ROOT = root
        checker.INITIATIVE_STATUS_FILES = (".agent-loop/initiatives/example/STATUS.md",)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                assert checker.main() == 0
        finally:
            checker.ROOT = original_root
            checker.INITIATIVE_STATUS_FILES = original_status_files


def valid_loop_intent() -> str:
    """Return one valid committed merge-intent JSON fixture."""
    return (
        '{"schema_version":1,"initiative_id":"WS-AUTH-001",'
        '"chunk_id":"WS-AUTH-001-06","chunk_title":"Canonical Actor Profile",'
        '"next_chunk_id":"WS-AUTH-001-07","next_chunk_title":"Authorization Kernel",'
        '"next_requires_explicit_start":true}\n'
    )


def updater_base64(value: str) -> str:
    """Return GitHub-contents-style base64 text."""
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def loop_record(
    module,
    *,
    sha: str = "a" * 40,
    first_parent_sha: str = "0" * 40,
    merged_at: str = "2026-07-14T20:00:00Z",
    pr_number: int = 120,
) -> dict:
    """Return one complete generated-state fixture."""
    metadata = module.parse_loop_metadata(valid_loop_intent())
    return {
        "schema_version": 1,
        "repository": "Flow-Research/workstream",
        "state_branch": "automation/loop-memory",
        "updated_at": merged_at,
        "source": {
            "main_sha": sha,
            "first_parent_sha": first_parent_sha,
            "pr_number": pr_number,
            "pr_url": f"https://github.com/Flow-Research/workstream/pull/{pr_number}",
            "pr_title": "Canonical actor profile",
            "head_sha": "b" * 40,
            "head_ref": "codex/ws-auth-001-06",
            "merged_at": merged_at,
            "merged_by": "manager",
            "intent_path": ".agent-loop/merge-intents/WS-AUTH-001-06.json",
            "intent_blob_sha": "d" * 40,
        },
        "completed_chunk": module.asdict(metadata),
        "active": {"planning_chunk": None, "implementation_chunk": None},
        "gate": {
            "status": "stopped_after_merge",
            "next_chunk_id": metadata.next_chunk_id,
            "next_chunk_title": metadata.next_chunk_title,
            "next_requires_explicit_start": True,
        },
        "checks": {
            "required": {
                name: {"kind": "check_run", "conclusion": "success", "url": None}
                for name in module.REQUIRED_CHECKS
            },
            "all_required_passed": True,
        },
    }


def test_post_merge_metadata_is_strict_and_bounded() -> None:
    """PR metadata rejects ambiguity, unknown keys, and inconsistent chunk facts."""
    updater = load_module("post_merge_metadata", "scripts/update_post_merge_memory.py")
    metadata = updater.parse_loop_metadata(valid_loop_intent())
    assert metadata.initiative_id == "WS-AUTH-001"
    assert metadata.chunk_id == "WS-AUTH-001-06"
    assert metadata.next_requires_explicit_start is True

    invalid_bodies = [
        "",
        valid_loop_intent() + valid_loop_intent(),
        valid_loop_intent().replace('"schema_version":1', '"schema_version":2'),
        valid_loop_intent().replace(
            '"chunk_id":"WS-AUTH-001-06"', '"chunk_id":"WS-POL-002-04"'
        ),
        valid_loop_intent().replace(
            '"next_chunk_title":"Authorization Kernel"', '"next_chunk_title":null'
        ),
        valid_loop_intent().replace(
            '"schema_version":1', '"schema_version":1,"unexpected":true'
        ),
    ]
    for body in invalid_bodies:
        try:
            updater.parse_loop_metadata(body)
        except updater.LoopMemoryError:
            continue
        raise AssertionError(f"invalid merge intent passed: {body}")


def test_post_merge_state_is_idempotent_and_monotonic() -> None:
    """Generated state accepts one merge, replays exactly, and rejects older/conflicting data."""
    updater = load_module("post_merge_state", "scripts/update_post_merge_memory.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        record = loop_record(updater)
        assert updater.apply_merge_record(root, record) is True
        assert updater.apply_merge_record(root, record) is False
        updater.validate_generated_state(root)

        conflict = json.loads(json.dumps(record))
        conflict["source"]["pr_title"] = "Conflicting title"
        try:
            updater.apply_merge_record(root, conflict)
        except updater.LoopMemoryError as exc:
            assert "different state" in str(exc)
        else:
            raise AssertionError("conflicting replay passed")

        successor = loop_record(
            updater,
            sha="c" * 40,
            first_parent_sha="a" * 40,
            merged_at="2026-07-14T20:00:00Z",
            pr_number=121,
        )
        assert updater.apply_merge_record(root, successor) is True
        updater.validate_generated_state(root)

        older = loop_record(
            updater,
            sha="e" * 40,
            first_parent_sha="0" * 40,
            merged_at="2026-07-14T19:59:59Z",
            pr_number=119,
        )
        try:
            updater.apply_merge_record(root, older)
        except updater.LoopMemoryError as exc:
            assert "direct first-parent successor" in str(exc)
        else:
            raise AssertionError("older merge replaced live state")


def test_post_merge_collection_binds_exact_pr_and_checks() -> None:
    """The collector binds one main merge SHA and final-head check evidence."""
    updater = load_module(
        "post_merge_collection", "scripts/update_post_merge_memory.py"
    )
    merge_sha = "a" * 40
    head_sha = "b" * 40
    responses = {
        f"/repos/Flow-Research/workstream/commits/{merge_sha}/pulls?per_page=100": [
            {
                "number": 120,
                "state": "closed",
                "merged_at": "2026-07-14T20:00:00Z",
                "merge_commit_sha": merge_sha,
                "html_url": "https://github.com/Flow-Research/workstream/pull/120",
                "title": "Canonical actor profile",
                "base": {"ref": "main"},
                "head": {"sha": head_sha, "ref": "codex/ws-auth-001-06"},
                "merged_by": {"login": "manager"},
            }
        ],
        "/repos/Flow-Research/workstream/pulls/120": {
            "number": 120,
            "state": "closed",
            "merged_at": "2026-07-14T20:00:00Z",
            "merge_commit_sha": merge_sha,
            "html_url": "https://github.com/Flow-Research/workstream/pull/120",
            "title": "Canonical actor profile",
            "base": {"ref": "main"},
            "head": {"sha": head_sha, "ref": "codex/ws-auth-001-06"},
            "merged_by": {"login": "manager"},
        },
        "/repos/Flow-Research/workstream/pulls/120/files?per_page=100&page=1": [
            {
                "filename": ".agent-loop/merge-intents/WS-AUTH-001-06.json",
                "status": "added",
            }
        ],
        (
            "/repos/Flow-Research/workstream/contents/"
            ".agent-loop/merge-intents/WS-AUTH-001-06.json"
            f"?ref={head_sha}"
        ): {
            "encoding": "base64",
            "sha": "d" * 40,
            "content": updater_base64(valid_loop_intent()),
        },
        f"/repos/Flow-Research/workstream/commits/{merge_sha}": {
            "parents": [{"sha": "0" * 40}]
        },
        f"/repos/Flow-Research/workstream/commits/{head_sha}/check-runs?per_page=100": {
            "check_runs": [
                {
                    "name": "agent-gates",
                    "conclusion": "success",
                    "started_at": "2026-07-14T19:49:00Z",
                    "completed_at": "2026-07-14T19:50:00Z",
                    "details_url": "https://example.test/gates",
                },
                {
                    "name": "test",
                    "conclusion": "success",
                    "started_at": "2026-07-14T19:50:00Z",
                    "completed_at": "2026-07-14T19:51:00Z",
                    "details_url": "https://example.test/test",
                },
            ]
        },
        f"/repos/Flow-Research/workstream/commits/{head_sha}/status?per_page=100": {
            "statuses": [
                {
                    "context": "CodeRabbit",
                    "state": "success",
                    "updated_at": "2026-07-14T19:52:00Z",
                    "target_url": "https://example.test/review",
                }
            ]
        },
    }

    class FakeClient:
        def get_json(self, path: str):
            return responses[path]

        def get_paginated(self, path: str):
            return responses[f"{path}?per_page=100&page=1"]

    record = updater.collect_merge_record(
        FakeClient(), "Flow-Research/workstream", merge_sha
    )
    assert record["source"]["main_sha"] == merge_sha
    assert record["source"]["head_sha"] == head_sha
    assert record["source"]["first_parent_sha"] == "0" * 40
    assert record["source"]["intent_blob_sha"] == "d" * 40
    assert record["completed_chunk"]["chunk_id"] == "WS-AUTH-001-06"
    assert record["checks"]["all_required_passed"] is True


def test_generated_loop_memory_validator_detects_drift() -> None:
    """The independent validator detects ledger and rendered-state drift."""
    updater = load_module(
        "post_merge_validator_updater", "scripts/update_post_merge_memory.py"
    )
    checker = load_module("post_merge_validator", "scripts/check_loop_memory_state.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        updater.apply_merge_record(root, loop_record(updater))
        assert checker.generated_state_failures(root) == []
        (root / updater.RENDERED_PATH).write_text("stale\n", encoding="utf-8")
        failures = checker.generated_state_failures(root)
        assert any("merge SHA" in failure for failure in failures)
        assert any("completed chunk" in failure for failure in failures)


def test_generated_loop_memory_escapes_markdown_metadata() -> None:
    """PR and chunk titles cannot inject generated Markdown structure."""
    updater = load_module(
        "post_merge_markdown_escape", "scripts/update_post_merge_memory.py"
    )
    record = loop_record(updater)
    record["source"]["pr_title"] = "Title [link](https://unsafe.test) `code`"
    record["completed_chunk"]["chunk_title"] = "Chunk <unsafe>"
    rendered = updater.render_state(record)
    assert "Title \\[link\\](https://unsafe.test) \\`code\\`" in rendered
    assert "Chunk &lt;unsafe&gt;" in rendered


def test_loop_memory_workflow_isolated_write_boundary() -> None:
    """The write-capable workflow runs on trusted main and targets only the state branch."""
    workflow = (ROOT / ".github/workflows/loop-memory.yml").read_text(encoding="utf-8")
    agent_gates = (ROOT / ".github/workflows/agent-gates.yml").read_text(
        encoding="utf-8"
    )
    assert "pull_request_target" not in workflow
    assert "workflow_dispatch" not in workflow
    assert "repository_dispatch" in workflow
    assert "persist-credentials: false" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: read" in workflow
    assert "HEAD:refs/heads/${STATE_BRANCH}" in workflow
    assert "HEAD:refs/heads/main" not in workflow
    assert "gh pr create" not in workflow
    assert "git rev-list --reverse --first-parent" in workflow
    assert 'git merge-base --is-ancestor "${MERGE_SHA}" "${current_sha}"' in workflow
    assert "validate-merge-intent" in agent_gates
    assert "github.event.pull_request.body" not in agent_gates


def assert_loop_error(module, callback, expected: str) -> None:
    """Assert one loop-memory operation fails with a bounded diagnostic."""
    try:
        callback()
    except module.LoopMemoryError as exc:
        assert expected in str(exc)
        return
    raise AssertionError(f"expected LoopMemoryError containing {expected!r}")


def test_post_merge_input_and_check_validation_fail_closed() -> None:
    """Untrusted identifiers, payload types, and incomplete checks remain bounded."""
    updater = load_module(
        "post_merge_input_validation", "scripts/update_post_merge_memory.py"
    )
    assert_loop_error(
        updater, lambda: updater.parse_loop_metadata(None), "must be text"
    )
    assert_loop_error(
        updater,
        lambda: updater.parse_loop_metadata(
            valid_loop_intent().replace(
                '"chunk_title":"Canonical Actor Profile"', '"chunk_title":7'
            )
        ),
        "chunk_title must be a string",
    )
    assert_loop_error(
        updater,
        lambda: updater.parse_loop_metadata(
            valid_loop_intent().replace("Canonical Actor Profile", "Bad\\nTitle")
        ),
        "single-line string",
    )
    assert_loop_error(
        updater,
        lambda: updater.parse_loop_metadata(
            valid_loop_intent().replace("WS-AUTH-001-06", "bad id")
        ),
        "canonical lifecycle identifier",
    )
    assert_loop_error(
        updater,
        lambda: updater.parse_loop_metadata(
            valid_loop_intent().replace(
                '"next_requires_explicit_start":true',
                '"next_requires_explicit_start":"yes"',
            )
        ),
        "must be a boolean",
    )
    assert_loop_error(
        updater,
        lambda: updater._validate_repository_and_sha("invalid", "a" * 40),
        "owner/name",
    )
    assert_loop_error(
        updater,
        lambda: updater._validate_repository_and_sha(
            "Flow-Research/workstream", "A" * 40
        ),
        "lowercase hexadecimal",
    )

    evidence = updater._check_evidence(
        [
            {
                "name": "test",
                "conclusion": "success",
                "status": "completed",
                "started_at": "2026-01-01T00:00:00Z",
            },
            {
                "name": "test",
                "conclusion": None,
                "status": "in_progress",
                "started_at": "2026-01-01T00:01:00Z",
            },
        ],
        [],
    )
    assert evidence["required"]["test"]["conclusion"] == "in_progress"
    assert evidence["required"]["agent-gates"]["kind"] == "missing"
    assert evidence["all_required_passed"] is False


def test_github_client_bounds_success_and_network_failure() -> None:
    """The stdlib client authenticates JSON requests and hides transport detail on failure."""
    updater = load_module(
        "post_merge_github_client", "scripts/update_post_merge_memory.py"
    )
    assert_loop_error(updater, lambda: updater.GitHubClient(""), "token is required")
    original_urlopen = updater.urllib.request.urlopen

    class Response(io.StringIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    captured = {}

    def successful(request, timeout):
        captured["authorization"] = request.headers["Authorization"]
        captured["timeout"] = timeout
        return Response('{"ok":true}')

    try:
        updater.urllib.request.urlopen = successful
        client = updater.GitHubClient("secret", "https://api.example.test/")
        assert client.get_json("/state") == {"ok": True}
        assert captured == {"authorization": "Bearer secret", "timeout": 30}

        def failed(_request, timeout=None):
            assert timeout == 30
            raise updater.urllib.error.URLError("secret transport detail")

        updater.urllib.request.urlopen = failed
        assert_loop_error(
            updater, lambda: client.get_json("/state"), "GitHub API request failed"
        )
    finally:
        updater.urllib.request.urlopen = original_urlopen


def test_github_client_pagination_is_complete_and_bounded() -> None:
    """List collection follows every page and rejects invalid or unbounded payloads."""
    updater = load_module(
        "post_merge_github_pagination", "scripts/update_post_merge_memory.py"
    )
    client = updater.GitHubClient("secret")
    requested = []

    def two_pages(path: str):
        requested.append(path)
        return list(range(100)) if path.endswith("page=1") else ["last"]

    client.get_json = two_pages
    assert client.get_paginated("/pulls?state=closed")[-1] == "last"
    assert requested == [
        "/pulls?state=closed&per_page=100&page=1",
        "/pulls?state=closed&per_page=100&page=2",
    ]

    client.get_json = lambda _path: {"items": []}
    assert_loop_error(
        client_module := updater, lambda: client.get_paginated("/pulls"), "not a list"
    )

    calls = 0

    def endless(_path: str):
        nonlocal calls
        calls += 1
        return [None] * 100

    client.get_json = endless
    assert_loop_error(
        client_module,
        lambda: client.get_paginated("/pulls"),
        "exceeded 100 pages",
    )
    assert calls == 100


def test_committed_merge_intent_fails_closed_on_untrusted_github_payloads() -> None:
    """The reviewed-head intent loader rejects ambiguous, corrupt, and mismatched files."""
    updater = load_module(
        "post_merge_intent_payloads", "scripts/update_post_merge_memory.py"
    )
    repository = "Flow-Research/workstream"
    head_sha = "b" * 40
    canonical_path = ".agent-loop/merge-intents/WS-AUTH-001-06.json"

    class FakeClient:
        def __init__(self, files, content=None):
            self.files = files
            self.content = content

        def get_paginated(self, _path: str):
            return self.files

        def get_json(self, _path: str):
            return self.content

    added = [{"filename": canonical_path, "status": "added"}]
    valid_content = {
        "encoding": "base64",
        "sha": "d" * 40,
        "content": "\n".join(
            textwrap.wrap(updater_base64(valid_loop_intent()), width=60)
        ),
    }
    metadata, path, blob_sha = updater.load_committed_merge_intent(
        FakeClient(added, valid_content), repository, 120, head_sha
    )
    assert metadata.chunk_id == "WS-AUTH-001-06"
    assert (path, blob_sha) == (canonical_path, "d" * 40)

    cases = [
        ([], valid_content, "exactly one"),
        (
            [{"filename": canonical_path, "status": "modified"}],
            valid_content,
            "exactly one",
        ),
        (added, [], "invalid shape"),
        (added, {**valid_content, "sha": "bad"}, "canonical SHA"),
        (added, {**valid_content, "content": 7}, "no encoded content"),
        (added, {**valid_content, "content": "not base64"}, "base64 UTF-8"),
        (
            added,
            {**valid_content, "content": base64.b64encode(b"\xff").decode("ascii")},
            "base64 UTF-8",
        ),
        (
            added,
            {**valid_content, "content": base64.b64encode(b"x" * 8193).decode("ascii")},
            "exceeds 8192 bytes",
        ),
        (
            [
                {
                    "filename": ".agent-loop/merge-intents/WS-AUTH-001-07.json",
                    "status": "added",
                }
            ],
            valid_content,
            "path does not match",
        ),
    ]
    for files, content, expected in cases:
        assert_loop_error(
            updater,
            lambda files=files, content=content: updater.load_committed_merge_intent(
                FakeClient(files, content), repository, 120, head_sha
            ),
            expected,
        )


def test_post_merge_collection_rejects_ambiguous_or_mismatched_prs() -> None:
    """Collector errors never guess across missing, ambiguous, or inconsistent PR facts."""
    updater = load_module(
        "post_merge_collection_errors", "scripts/update_post_merge_memory.py"
    )
    repository = "Flow-Research/workstream"
    merge_sha = "a" * 40
    association_path = f"/repos/{repository}/commits/{merge_sha}/pulls?per_page=100"
    valid_association = {
        "number": 120,
        "state": "closed",
        "merged_at": "2026-07-14T20:00:00Z",
        "merge_commit_sha": merge_sha,
        "base": {"ref": "main"},
    }

    class FakeClient:
        def __init__(self, responses):
            self.responses = responses

        def get_json(self, path: str):
            return self.responses[path]

    for payload, expected in (
        ({}, "not a list"),
        ([], "exactly one"),
        ([valid_association, valid_association], "exactly one"),
    ):
        client = FakeClient({association_path: payload})
        assert_loop_error(
            updater,
            lambda client=client: updater.collect_merge_record(
                client, repository, merge_sha
            ),
            expected,
        )

    no_number = dict(valid_association)
    no_number["number"] = 0
    assert_loop_error(
        updater,
        lambda: updater.collect_merge_record(
            FakeClient({association_path: [no_number]}), repository, merge_sha
        ),
        "positive number",
    )
    assert_loop_error(
        updater,
        lambda: updater.collect_merge_record(
            FakeClient(
                {
                    association_path: [valid_association],
                    f"/repos/{repository}/pulls/120": [],
                }
            ),
            repository,
            merge_sha,
        ),
        "not an object",
    )
    mismatched = dict(valid_association)
    mismatched.update(
        {
            "merge_commit_sha": "c" * 40,
            "body": valid_loop_intent(),
            "head": {"sha": "b" * 40},
        }
    )
    assert_loop_error(
        updater,
        lambda: updater.collect_merge_record(
            FakeClient(
                {
                    association_path: [valid_association],
                    f"/repos/{repository}/pulls/120": mismatched,
                }
            ),
            repository,
            merge_sha,
        ),
        "do not match",
    )


def test_post_merge_state_rejects_corrupt_files_and_cli_misuse() -> None:
    """Corrupt generated files and wrong-branch CLI writes fail closed."""
    updater = load_module(
        "post_merge_corrupt_state", "scripts/update_post_merge_memory.py"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assert_loop_error(
            updater,
            lambda: updater.validate_generated_state(root),
            "state file is missing",
        )

        state_path = root / updater.STATE_PATH
        state_path.parent.mkdir(parents=True)
        state_path.write_text("[]\n", encoding="utf-8")
        assert_loop_error(
            updater, lambda: updater.validate_generated_state(root), "JSON object"
        )
        state_path.write_text("{invalid\n", encoding="utf-8")
        assert_loop_error(
            updater,
            lambda: updater.validate_generated_state(root),
            "cannot read generated state",
        )

        state_path.write_text(json.dumps(loop_record(updater)), encoding="utf-8")
        ledger_path = root / updater.LEDGER_PATH
        ledger_path.write_text("[]\n", encoding="utf-8")
        assert_loop_error(
            updater, lambda: updater.validate_generated_state(root), "JSON objects"
        )
        ledger_path.write_text("{invalid\n", encoding="utf-8")
        assert_loop_error(
            updater,
            lambda: updater.validate_generated_state(root),
            "cannot read merge ledger",
        )

        subprocess.run(
            ["git", "init", "--initial-branch", "wrong", str(root)],
            check=True,
            stdout=subprocess.PIPE,
        )
        assert_loop_error(
            updater, lambda: updater._assert_state_branch(root), "must be checked out"
        )

        intent_repo = root / "intent-repo"
        subprocess.run(
            ["git", "init", "--initial-branch", "main", str(intent_repo)],
            check=True,
            stdout=subprocess.PIPE,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(intent_repo),
                "config",
                "user.email",
                "test@example.test",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(intent_repo), "config", "user.name", "Test"],
            check=True,
        )
        (intent_repo / "README.md").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(intent_repo), "add", "README.md"], check=True)
        subprocess.run(
            ["git", "-C", str(intent_repo), "commit", "-m", "base"],
            check=True,
            stdout=subprocess.PIPE,
        )
        subprocess.run(
            ["git", "-C", str(intent_repo), "switch", "-c", "feature"],
            check=True,
            stdout=subprocess.PIPE,
        )
        intent_path = intent_repo / ".agent-loop/merge-intents/WS-AUTH-001-06.json"
        intent_path.parent.mkdir(parents=True)
        intent_path.write_text(valid_loop_intent(), encoding="utf-8")
        subprocess.run(
            [
                "git",
                "-C",
                str(intent_repo),
                "add",
                intent_path.relative_to(intent_repo),
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(intent_repo), "commit", "-m", "intent"],
            check=True,
            stdout=subprocess.PIPE,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            assert (
                updater.main(
                    [
                        "validate-merge-intent",
                        "--repository-root",
                        str(intent_repo),
                        "--base-ref",
                        "main",
                    ]
                )
                == 0
            )
        with contextlib.redirect_stderr(io.StringIO()):
            assert (
                updater.main(
                    [
                        "validate-merge-intent",
                        "--repository-root",
                        str(intent_repo),
                        "--base-ref",
                        "missing",
                    ]
                )
                == 1
            )
        with contextlib.redirect_stderr(io.StringIO()):
            assert updater.main(["validate-state", "--state-root", str(root)]) == 1


def test_post_merge_cli_updates_and_shows_generated_state() -> None:
    """The CLI update, validation, and display modes operate on the dedicated branch."""
    updater = load_module("post_merge_cli", "scripts/update_post_merge_memory.py")
    original_client = updater.GitHubClient
    original_collect = updater.collect_merge_record
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        subprocess.run(
            ["git", "init", "--initial-branch", updater.STATE_BRANCH, str(root)],
            check=True,
            stdout=subprocess.PIPE,
        )
        os.environ["TEST_GITHUB_TOKEN"] = "secret"
        updater.GitHubClient = lambda _token, _api_url: SimpleNamespace()
        updater.collect_merge_record = lambda _client, _repository, _sha: loop_record(
            updater
        )
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                assert (
                    updater.main(
                        [
                            "update",
                            "--repository",
                            "Flow-Research/workstream",
                            "--merge-sha",
                            "a" * 40,
                            "--state-root",
                            str(root),
                            "--token-env",
                            "TEST_GITHUB_TOKEN",
                        ]
                    )
                    == 0
                )
            assert "updated for PR #120" in output.getvalue()
            with contextlib.redirect_stdout(io.StringIO()):
                assert updater.main(["validate-state", "--state-root", str(root)]) == 0
            with contextlib.redirect_stdout(io.StringIO()) as output:
                assert updater.main(["show", "--state-root", str(root)]) == 0
            assert "Generated Workstream Loop State" in output.getvalue()
        finally:
            updater.GitHubClient = original_client
            updater.collect_merge_record = original_collect
            os.environ.pop("TEST_GITHUB_TOKEN", None)


def test_generated_loop_memory_validator_covers_corruption_matrix() -> None:
    """Independent state validation reports each generated-file corruption family."""
    updater = load_module(
        "post_merge_corruption_updater", "scripts/update_post_merge_memory.py"
    )
    checker = load_module(
        "post_merge_corruption_checker", "scripts/check_loop_memory_state.py"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assert len(checker.generated_state_failures(root)) == 3
        (root / ".agent-loop").mkdir()
        for relative in checker.GENERATED_FILES:
            (root / relative).write_text("not-json\n", encoding="utf-8")
        assert "unreadable" in checker.generated_state_failures(root)[0]

        (root / checker.GENERATED_FILES[0]).write_text("[]\n", encoding="utf-8")
        (root / checker.GENERATED_FILES[2]).write_text("{}\n", encoding="utf-8")
        assert "expected a JSON object" in checker.generated_state_failures(root)[0]

        valid_root = root / "valid"
        updater.apply_merge_record(valid_root, loop_record(updater))
        with contextlib.redirect_stdout(io.StringIO()):
            assert checker.main(["--state-root", str(valid_root)]) == 0

        state_path = valid_root / updater.STATE_PATH
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["schema_version"] = 2
        state["state_branch"] = "main"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        failures = checker.generated_state_failures(valid_root)
        assert any("schema version" in failure for failure in failures)
        assert any("unexpected state branch" in failure for failure in failures)
        assert any("ledger tail" in failure for failure in failures)
        with contextlib.redirect_stderr(io.StringIO()):
            assert checker.main(["--state-root", str(valid_root)]) == 1

    original_root = checker.ROOT
    original_status_files = checker.INITIATIVE_STATUS_FILES
    with tempfile.TemporaryDirectory() as tmpdir:
        checker.ROOT = Path(tmpdir)
        checker.INITIATIVE_STATUS_FILES = ()
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                assert checker.main() == 1
        finally:
            checker.ROOT = original_root
            checker.INITIATIVE_STATUS_FILES = original_status_files


def test_full_merge_ledger_hash_chain_detects_history_tampering() -> None:
    """Mutation or deletion of a non-tail ledger entry is detected independently."""
    updater = load_module(
        "post_merge_history_updater", "scripts/update_post_merge_memory.py"
    )
    checker = load_module(
        "post_merge_history_checker", "scripts/check_loop_memory_state.py"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        first = loop_record(updater)
        second = loop_record(
            updater,
            sha="c" * 40,
            first_parent_sha="a" * 40,
            merged_at="2026-07-14T20:01:00Z",
            pr_number=121,
        )
        updater.apply_merge_record(root, first)
        updater.apply_merge_record(root, second)
        ledger_path = root / updater.LEDGER_PATH
        original_lines = ledger_path.read_text(encoding="utf-8").splitlines()

        tampered = [json.loads(line) for line in original_lines]
        tampered[0]["record"]["source"]["pr_title"] = "tampered"
        ledger_path.write_text(
            "".join(f"{json.dumps(entry)}\n" for entry in tampered),
            encoding="utf-8",
        )
        assert_loop_error(
            updater,
            lambda: updater.validate_generated_state(root),
            "entry hash is invalid",
        )
        assert any(
            "hash chain" in failure
            for failure in checker.generated_state_failures(root)
        )

        ledger_path.write_text(f"{original_lines[1]}\n", encoding="utf-8")
        assert_loop_error(
            updater,
            lambda: updater.validate_generated_state(root),
            "previous hash chain is invalid",
        )
        assert any(
            "hash chain" in failure
            for failure in checker.generated_state_failures(root)
        )


def test_merge_ledger_rejects_schema_record_and_ancestry_corruption() -> None:
    """Every ledger envelope and first-parent link is validated before state changes."""
    updater = load_module(
        "post_merge_ledger_corruption", "scripts/update_post_merge_memory.py"
    )
    assert_loop_error(
        updater,
        lambda: updater._validate_ledger_entries([{}]),
        "invalid schema",
    )
    invalid_record = {
        "schema_version": 1,
        "previous_entry_hash": None,
        "record": [],
        "entry_hash": "bad",
    }
    assert_loop_error(
        updater,
        lambda: updater._validate_ledger_entries([invalid_record]),
        "JSON object",
    )

    bad_sha_record = loop_record(updater)
    bad_sha_record["source"]["main_sha"] = "not-a-sha"
    assert_loop_error(
        updater,
        lambda: updater._validate_ledger_entries(
            [updater._ledger_entry(bad_sha_record, None)]
        ),
        "canonical main SHA",
    )

    first = loop_record(updater)
    second = loop_record(
        updater,
        sha="c" * 40,
        first_parent_sha="f" * 40,
        pr_number=121,
    )
    first_entry = updater._ledger_entry(first, None)
    second_entry = updater._ledger_entry(second, first_entry["entry_hash"])
    assert_loop_error(
        updater,
        lambda: updater._validate_ledger_entries([first_entry, second_entry]),
        "first-parent chain",
    )


def test_stale_authorization_rule_examples_are_rejected() -> None:
    """Independent fixtures cover each required stale-authority family."""
    gate = load_module(
        "stale_authorization_docs_rules",
        "scripts/check_stale_authorization_docs.py",
    )
    fixtures = {
        "NON_CANONICAL_API_PREFIX": "POST /v1/projects",
        "LEGACY_ADMIN_PROJECT_MANAGER_AUTHORITY": "An admin or project_manager approves.",
        "LEGACY_ROLE_HELPER": "Call require_any_role for this route.",
        "TRUSTED_ROLE_CLAIM_AUTHORITY": "Routes use trusted role claims.",
        "CURRENT_TOKEN_ROLE_AUTHORITY": "Require the role in the current verified token.",
        "TOKEN_CARRIES_PRODUCT_ROLE": "The token also carries an authorized Workstream role.",
        "TYPED_PROFILE_AUTHORITY": 'ActorProfile(profile_type="worker") grants access.',
        "OBSOLETE_ROLE_ASSIGNMENT_MODEL": "Persist a WorkstreamRoleAssignment.",
        "OPERATOR_NOT_A_ROLE": "Operator is not a separate permission role.",
        "BROAD_ADMIN_OVERRIDE": "An admin can override a checker failure.",
        "LEGACY_ADMIN_HEADING": "### Admin",
        "LEGACY_ROLE_MATRIX": "| Admin | Project Manager | Finance | Auditor |",
        "ROLE_NAME_APPROVAL_PROVENANCE": '"approved_by_role": "project_manager"',
        "GENERIC_ADMIN_PRODUCT_AUTHORITY": "An admin can create projects.",
        "TOKEN_ROLE_PRODUCT_AUTHORITY": "A token role grants project access.",
        "NAMED_ROLE_TOKEN_AUTHORITY": "A project_manager token may approve this request.",
        "TYPED_PROFILE_PRODUCT_AUTHORITY": (
            "ActorProfile with type worker authorizes task claim."
        ),
        "HUMAN_WORKER_VOCABULARY": "## Flow 3: Worker Submits Work",
        "HUMAN_WORKER_IDENTIFIER": "worker_claim_status: fixed",
        "TECHNICAL_WORKER_HUMAN_AUTHORITY": (
            "The checker worker submits a contributor packet."
        ),
    }
    for code, sample in fixtures.items():
        failures = gate.scan_text("docs/new_active_doc.md", sample)
        assert any(failure.endswith(code) for failure in failures), (code, failures)

    unambiguous_canonical_statements = (
        "Product authority comes only from local Workstream grants.",
        "Bearer-token role metadata is identity provenance only.",
        "Typed workflow profiles are eligibility metadata only.",
        "An Access Administrator may grant administrative roles.",
    )
    for sample in unambiguous_canonical_statements:
        assert gate.scan_text("docs/new_active_doc.md", sample) == [], sample

    fail_closed_authority_shapes = (
        "No current token role grants Workstream authority.",
        "Roles from the bearer token do not permit this request.",
        "ActorProfile with type worker does not authorize task claim.",
        "A token role grants project access, but email does not.",
        "A token role grants project access, not a typed profile.",
        (
            "ActorProfile with type worker authorizes task claim, but does not "
            "authorize review."
        ),
        "A token role, not email, grants project access.",
        "A token role does not merely provide context; it grants project access.",
        "ActorProfile with type worker, not reviewer, authorizes task claim.",
        "A token role does not grant profile access but authorizes project access.",
        (
            "ActorProfile with type worker does not authorize read access but "
            "permits task claim."
        ),
        (
            "A worker role from the token does not allow profile reads but may "
            "approve projects."
        ),
        "A token role does not record email but grants project access.",
        "A worker token does not carry profile metadata but authorizes task claim.",
        "ActorProfile with type worker does not store secrets but permits task claim.",
    )
    for sample in fail_closed_authority_shapes:
        assert gate.scan_text("docs/new_active_doc.md", sample), sample

    technical_worker_statements = (
        "The Celery worker runs project setup jobs.",
        "Checker execution uses a durable worker boundary.",
        "The setup worker reloads current authority before commit.",
        "The Celery worker identity is recorded for audit.",
        "The checker worker writes results.",
        "The setup worker resumes a failed job.",
        "The system worker completed reconciliation.",
        "The Celery worker submission is retried.",
        "The checker worker claim status is internal.",
        "Celery workers submit jobs.",
        "Celery worker_id identifies the background process.",
        "The checker worker_id is included in internal telemetry.",
        "See backend/app/workers/tasks.py.",
    )
    for sample in technical_worker_statements:
        assert gate.scan_text("docs/new_active_doc.md", sample) == [], sample

    human_worker_statements = (
        "A qualified worker claims the task.",
        "The worker opens an assigned task.",
        "Maximum active tasks per worker.",
        "Worker attestation is required.",
        "A worker submits the packet.",
        "Workers submit packets.",
        "A worker can claim a task.",
        "Persist worker_id on the assignment.",
        "POST /api/v1/workers/me/profile",
        "Celery schedules background jobs; a worker submits the packet.",
        "Celery is configured here; workers submit task packets.",
        "Celery is installed; a worker submits human work.",
        "Celery supports queues, but human workers submit tasks.",
        "Human workers use Celery.",
        "The Celery worker claims a human task using submitter authority.",
        ("The system worker receives a reviewer grant and records a review decision."),
        "The setup worker is a human product role.",
        "The system worker has a reviewer grant.",
        "The Celery worker may review a contributor submission.",
        "The checker worker is a Contributor.",
        "The setup worker uses submitter authority.",
        "The background worker approves project work.",
        "The Celery worker approves a project guide.",
        "The system worker reviews the submission.",
        "The checker worker grants itself project access.",
        "The setup worker manages contributor grants.",
        "The background worker creates a project.",
        "The system worker records a review decision.",
        "The checker worker issues a submitter grant.",
        "The setup worker revokes a reviewer grant.",
        "The Celery worker accepts the submission.",
        "The background worker rejects project work.",
        "The checker worker requests revision.",
    )
    for sample in human_worker_statements:
        assert gate.scan_text("docs/new_active_doc.md", sample), sample


def test_stale_authorization_discovery_includes_new_untracked_docs() -> None:
    """A new active doc fails without being added to a hardcoded corpus."""
    gate = load_module(
        "stale_authorization_docs_discovery",
        "scripts/check_stale_authorization_docs.py",
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "docs").mkdir()
        active = root / "docs" / "new_active_doc.md"
        diagram = root / "docs" / "new_active_diagram.puml"
        active.write_text("POST /v1/projects\n", encoding="utf-8")
        diagram.write_text(
            "Workstream --> API : POST /api/v1/projects\n", encoding="utf-8"
        )
        assert active in gate.discover_documents(root)
        assert diagram in gate.discover_documents(root)
        assert gate.scan(root) == ["docs/new_active_doc.md:1: NON_CANONICAL_API_PREFIX"]

        active.write_text("POST /api/v1/projects\n", encoding="utf-8")
        assert gate.scan(root) == []

        active.write_text(
            "The worker role from the verified token authorizes task claims.\n"
            "ActorProfile with type worker authorizes task claim.\n",
            encoding="utf-8",
        )
        failures = gate.scan(root)
        assert any(item.endswith("TOKEN_ROLE_PRODUCT_AUTHORITY") for item in failures)
        assert any(
            item.endswith("TYPED_PROFILE_PRODUCT_AUTHORITY") for item in failures
        )

        active.write_text("POST /api/v1/projects\n", encoding="utf-8")
        diagram.write_text("Workstream --> API : POST /v1/projects\n", encoding="utf-8")
        assert gate.scan(root) == [
            "docs/new_active_diagram.puml:1: NON_CANONICAL_API_PREFIX"
        ]


def test_stale_authorization_precedence_exemption_is_line_scoped() -> None:
    """The active archive marker exempts one line, not its entire document."""
    gate = load_module(
        "stale_authorization_docs_precedence",
        "scripts/check_stale_authorization_docs.py",
    )
    marker = "archival input uses `/v1`. WS-AUTH-001 takes precedence over the current"
    assert gate.scan_text("docs/reference_specs/README.md", marker) == []
    failures = gate.scan_text(
        "docs/reference_specs/README.md",
        marker + "\nClients call POST /v1/projects.\n",
    )
    assert failures == ["docs/reference_specs/README.md:2: NON_CANONICAL_API_PREFIX"]


def test_stale_authorization_history_allowlist_is_exact() -> None:
    """Only reviewed exact history paths bypass active-document scanning."""
    gate = load_module(
        "stale_authorization_docs_history",
        "scripts/check_stale_authorization_docs.py",
    )
    assert "docs/spec_chunk_3_project_guide_foundation.md" in gate.HISTORICAL_PATHS
    assert "docs/spec_chunk_999_future.md" not in gate.HISTORICAL_PATHS


def test_agent_gates_runs_stale_authorization_docs_fail_closed() -> None:
    """The Agent Gates workflow must retain the authorization-doc scanner."""
    workflow = (ROOT / ".github/workflows/agent-gates.yml").read_text(encoding="utf-8")
    command = "run: python3 scripts/check_stale_authorization_docs.py"
    assert workflow.count(command) == 1
    assert "continue-on-error" not in workflow


def test_agent_gates_runs_stale_artifact_contracts_fail_closed() -> None:
    """The Agent Gates workflow must retain the artifact-contract scanner."""
    workflow = (ROOT / ".github/workflows/agent-gates.yml").read_text(encoding="utf-8")
    command = "run: python3 scripts/check_stale_artifact_contracts.py"
    assert workflow.count(command) == 1
    assert "continue-on-error" not in workflow


def test_backend_coverage_thresholds_are_regression_protected() -> None:
    """Keep both the approved global floor and stricter artifact floor fail closed."""
    workflow = (ROOT / ".github/workflows/backend.yml").read_text(encoding="utf-8")
    assert workflow.count("--cov-fail-under=78") == 1
    assert workflow.count("--fail-under=90") == 1
    assert (
        "--include='app/adapters/artifacts/*,app/interfaces/artifacts.py,"
        "app/modules/artifacts/*'"
    ) in workflow
    assert "continue-on-error" not in workflow


def test_stale_artifact_contracts_foundation_keeps_later_terms_inactive() -> None:
    """Foundation checks generic neutrality without preempting later cutovers."""
    gate = load_module(
        "stale_artifact_contracts_foundation",
        "scripts/check_stale_artifact_contracts.py",
    )
    assert gate.ARTIFACT_CONTRACT_PHASE == "foundation"
    assert (
        gate.scan_text(
            "backend/app/modules/tasks/schemas.py",
            "package_uri content_cid artifact_manifest_hash",
            "foundation",
        )
        == []
    )
    failures = gate.scan_text(
        "contracts/artifact-store/version_1/schema/example.json",
        '{"cid": "provider-specific"}',
        "foundation",
    )
    assert failures == [
        "contracts/artifact-store/version_1/schema/example.json:1: "
        "PROVIDER_SPECIFIC_GENERIC_INTERFACE"
    ]


def test_stale_artifact_contracts_active_later_phase_owns_only_reached_terms() -> None:
    """A later phase rejects reached legacy terms while leaving future ones alone."""
    gate = load_module(
        "stale_artifact_contracts_later",
        "scripts/check_stale_artifact_contracts.py",
    )
    guide_failures = gate.scan_text(
        "backend/app/modules/projects/schemas.py",
        "content_cid package_uri artifact_manifest_hash",
        "guide_source_cutover",
    )
    assert guide_failures == [
        "backend/app/modules/projects/schemas.py:1: LEGACY_GUIDE_CONTENT_CID"
    ]
    submission_failures = gate.scan_text(
        "backend/app/modules/tasks/schemas.py",
        "package_uri allowed_storage_schemes artifact_manifest_hash",
        "submission_cutover",
    )
    assert submission_failures == [
        "backend/app/modules/tasks/schemas.py:1: LEGACY_SUBMISSION_TRANSPORT",
        "backend/app/modules/tasks/schemas.py:1: LEGACY_PROJECT_STORAGE_POLICY",
    ]


def test_stale_artifact_contracts_malformed_phase_fails_closed() -> None:
    """Unknown or non-string phase markers cannot disable scanner rules."""
    gate = load_module(
        "stale_artifact_contracts_malformed",
        "scripts/check_stale_artifact_contracts.py",
    )
    for phase in ("", "submission", "foundation ", None, 1):
        try:
            gate.rules_for_phase(phase)
        except ValueError as exc:
            assert "malformed artifact contract phase" in str(exc)
        else:
            raise AssertionError(f"malformed phase was accepted: {phase!r}")

    original_phase = gate.ARTIFACT_CONTRACT_PHASE
    gate.ARTIFACT_CONTRACT_PHASE = "unknown"
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            assert gate.main() == 1
    finally:
        gate.ARTIFACT_CONTRACT_PHASE = original_phase


def main() -> int:
    """Run all local test functions."""
    tests = [
        test_required_tracks_expand_for_loop_and_ci_paths,
        test_backend_config_paths_require_review_evidence,
        test_review_evidence_files_are_not_relevant_changes,
        test_evidence_requires_completed_yes_statements,
        test_evidence_must_reference_changed_chunk,
        test_evidence_rejects_pending_or_blocking_reviewer_rows,
        test_evidence_accepts_exact_pass_and_approved_na_results,
        test_evidence_rejects_na_for_required_tracks,
        test_evidence_reviewed_revision_allows_only_evidence_status_changes,
        test_evidence_reviewed_revision_rejects_late_implementation_changes,
        test_evidence_reviewed_revision_rejects_dirty_tree_changes,
        test_evidence_reviewed_revision_rejects_invalid_provenance,
        test_evidence_main_fails_closed_on_unresolved_base_ref,
        test_evidence_main_passes_with_complete_evidence_and_pr_head,
        test_evidence_main_rejects_external_response_without_internal_evidence,
        test_evidence_main_reports_missing_evidence_file,
        test_static_sensor_counts_untracked_text_lines,
        test_static_sensor_requires_resolved_base_ref,
        test_static_sensor_accumulates_numstat_for_duplicate_paths,
        test_static_sensor_flags_backend_config_as_ci_surface,
        test_markdown_link_checker_collects_base_cached_dirty_and_untracked,
        test_stale_wording_patterns_catch_variants,
        test_stale_wording_skips_only_docs_internal_reviews_prefix,
        test_stale_wording_catches_multiline_legacy_status_reconstruction,
        test_loop_memory_state_rejects_pre_merge_status,
        test_loop_memory_state_accepts_merged_fixture,
        test_post_merge_metadata_is_strict_and_bounded,
        test_post_merge_state_is_idempotent_and_monotonic,
        test_post_merge_collection_binds_exact_pr_and_checks,
        test_generated_loop_memory_validator_detects_drift,
        test_generated_loop_memory_escapes_markdown_metadata,
        test_loop_memory_workflow_isolated_write_boundary,
        test_post_merge_input_and_check_validation_fail_closed,
        test_github_client_bounds_success_and_network_failure,
        test_github_client_pagination_is_complete_and_bounded,
        test_committed_merge_intent_fails_closed_on_untrusted_github_payloads,
        test_post_merge_collection_rejects_ambiguous_or_mismatched_prs,
        test_post_merge_state_rejects_corrupt_files_and_cli_misuse,
        test_post_merge_cli_updates_and_shows_generated_state,
        test_generated_loop_memory_validator_covers_corruption_matrix,
        test_full_merge_ledger_hash_chain_detects_history_tampering,
        test_merge_ledger_rejects_schema_record_and_ancestry_corruption,
        test_stale_authorization_rule_examples_are_rejected,
        test_stale_authorization_discovery_includes_new_untracked_docs,
        test_stale_authorization_precedence_exemption_is_line_scoped,
        test_stale_authorization_history_allowlist_is_exact,
        test_agent_gates_runs_stale_authorization_docs_fail_closed,
        test_agent_gates_runs_stale_artifact_contracts_fail_closed,
        test_backend_coverage_thresholds_are_regression_protected,
        test_stale_artifact_contracts_foundation_keeps_later_terms_inactive,
        test_stale_artifact_contracts_active_later_phase_owns_only_reached_terms,
        test_stale_artifact_contracts_malformed_phase_fails_closed,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} agent gate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
