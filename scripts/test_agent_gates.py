"""Regression tests for Workstream agent gate helpers.

Run with plain Python so the agent-gates workflow does not need test
dependencies installed before it can protect the repository process.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_COVERAGE_PHASE = "foundation"
ARTIFACT_COVERAGE_ORDER = (
    "foundation",
    "02A1",
    "02A2",
    "02A3",
    "02B1",
    "02B2",
    "02B3",
    "02C1",
    "02C2",
    "02D",
    "03",
    "04A",
    "04B",
    "05",
    "06A",
    "06B",
    "07",
)


def artifact_contract_phase_for(coverage_phase: str) -> str:
    """Map an implementation chunk to the stale-contract phase it owns."""
    active_index = ARTIFACT_COVERAGE_ORDER.index(coverage_phase)
    phase = "foundation"
    if active_index >= ARTIFACT_COVERAGE_ORDER.index("02A3"):
        phase = "artifact_store_cutover"
    if active_index >= ARTIFACT_COVERAGE_ORDER.index("03"):
        phase = "guide_source_cutover"
    if active_index >= ARTIFACT_COVERAGE_ORDER.index("04B"):
        phase = "upload_admission"
    if active_index >= ARTIFACT_COVERAGE_ORDER.index("05"):
        phase = "submission_cutover"
    if active_index >= ARTIFACT_COVERAGE_ORDER.index("06B"):
        phase = "checker_cutover"
    return phase


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
    gate = load_module("review_gate_backend_paths", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_relevance", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_statements", "scripts/check_internal_review_evidence.py")
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
            assert gate.validate_evidence(strong, required, enforce_reviewed_revision=False) == []
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
            assert gate.validate_evidence(evidence, required, enforce_reviewed_revision=False) == []
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
            missing = gate.validate_evidence(evidence, required, enforce_reviewed_revision=False)
            assert any("qa/test reviewer result must be one of" in item for item in missing)
            assert "qa/test blocking findings must be none" in missing
    finally:
        gate.changed_files = original_changed_files


def test_evidence_accepts_exact_pass_and_approved_na_results() -> None:
    """Reviewer result values are exact, with explicit N/A reason support."""
    gate = load_module("review_gate_exact_results", "scripts/check_internal_review_evidence.py")
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
    assert any("senior engineering reviewer result must be one of" in item for item in missing)

    optional_bad_text = (
        "| Reviewer | Result | Blocking findings | Notes |\n"
        "|---|---:|---|---|\n"
        "| senior engineering | PASS | None | checked |\n"
        "| docs | Pending / N/A - with approved reason | None | |\n"
        "| ci integrity | N/A | None | |\n"
    )
    missing = gate.validate_reviewer_rows(optional_bad_text.lower(), required)
    assert any("docs reviewer result must be one of" in item for item in missing)
    assert any("ci integrity reviewer result must be one of" in item for item in missing)

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
    gate = load_module("review_gate_required_na", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_revision_binding", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_revision_rejects_late_changes", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_revision_rejects_dirty", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_revision_blank_provenance", "scripts/check_internal_review_evidence.py")
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
        text = f"Reviewed code SHA: {reviewed}\nReviewed at:\nReviewer run IDs:\n".lower()
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
    gate = load_module("review_gate_base_ref", "scripts/check_internal_review_evidence.py")
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
    gate = load_module("review_gate_main_complete", "scripts/check_internal_review_evidence.py")
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
        ROOT
        / ".agent-loop/initiatives/test-agent-gate/"
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
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
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
    gate = load_module("review_gate_external_response_only", "scripts/check_internal_review_evidence.py")
    original_env = os.environ.get("INTERNAL_REVIEW_BASE_REF")
    original_git = gate.git
    original_git_ok = gate.git_ok
    original_changed_files = gate.changed_files
    external_response = (
        ROOT
        / ".agent-loop/initiatives/test-agent-gate/"
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
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
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
    gate = load_module("review_gate_missing_evidence_file", "scripts/check_internal_review_evidence.py")
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
    matches = [pattern.pattern for pattern in stale.FORBIDDEN_PATTERNS if pattern.search(sample)]
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
        pattern.pattern for pattern in stale.FORBIDDEN_PATTERNS if pattern.search(case_variant_sample)
    ]
    assert {
        "Approved" + "TaskArtifactBinding",
        "Effective" + "TaskSubmissionArtifactPolicy",
        "Project" + "PreSubmitCheckerSpec",
    }.issubset(set(case_variant_matches))
    failures = stale.forbidden_path_failures([Path(".claude/settings.json"), Path("CLAUDE.md")])
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
        (root / "docs/internal_reviews/archive.md").write_text("old review\n", encoding="utf-8")
        (root / "other/internal_reviews/file.md").write_text("active review\n", encoding="utf-8")
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
    checker = load_module("loop_memory_state_rejects", "scripts/check_loop_memory_state.py")
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
    checker = load_module("loop_memory_state_accepts", "scripts/check_loop_memory_state.py")
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
        (
            "The system worker receives a reviewer grant and records a review "
            "decision."
        ),
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
        assert gate.scan(root) == [
            "docs/new_active_doc.md:1: NON_CANONICAL_API_PREFIX"
        ]

        active.write_text("POST /api/v1/projects\n", encoding="utf-8")
        assert gate.scan(root) == []

        active.write_text(
            "The worker role from the verified token authorizes task claims.\n"
            "ActorProfile with type worker authorizes task claim.\n",
            encoding="utf-8",
        )
        failures = gate.scan(root)
        assert any(item.endswith("TOKEN_ROLE_PRODUCT_AUTHORITY") for item in failures)
        assert any(item.endswith("TYPED_PROFILE_PRODUCT_AUTHORITY") for item in failures)

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
    marker = (
        "archival input uses `/v1`. WS-AUTH-001 takes precedence over the current"
    )
    assert gate.scan_text("docs/reference_specs/README.md", marker) == []
    failures = gate.scan_text(
        "docs/reference_specs/README.md",
        marker + "\nClients call POST /v1/projects.\n",
    )
    assert failures == [
        "docs/reference_specs/README.md:2: NON_CANONICAL_API_PREFIX"
    ]


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
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/agent-gates.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["agent-gates"]["steps"]
    scanner_steps = [
        step
        for step in steps
        if step.get("run") == "python3 scripts/check_stale_artifact_contracts.py"
    ]
    assert scanner_steps == [
        {
            "name": "Stale artifact contract check",
            "run": "python3 scripts/check_stale_artifact_contracts.py",
        }
    ]
    assert all("continue-on-error" not in step for step in steps)
    assert all(step.get("if") not in {False, "false", "${{ false }}"} for step in steps)


def test_agent_gate_dependencies_and_workflow_are_pinned() -> None:
    """The YAML parser dependency and its installation remain deterministic."""
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/agent-gates.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["agent-gates"]["steps"]
    assert any(
        step.get("uses")
        == "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
        and step.get("with", {}).get("python-version") == "3.12"
        for step in steps
    )
    assert sum(
        step.get("run")
        == "python -m pip install --require-hashes -r scripts/agent-gate-requirements.txt"
        for step in steps
    ) == 1
    assert all("continue-on-error" not in step for step in steps)
    requirements = (ROOT / "scripts/agent-gate-requirements.txt").read_text(
        encoding="utf-8"
    )
    assert requirements == (
        "PyYAML==6.0.3 "
        "--hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc\n"
    )


def test_backend_coverage_thresholds_are_regression_protected() -> None:
    """Keep both the approved global floor and stricter artifact floor fail closed."""
    workflow = (ROOT / ".github/workflows/backend.yml").read_text(encoding="utf-8")
    assert workflow.count("--cov-fail-under=78") == 1
    assert (
        "--cov=app --cov-report=term-missing --cov-fail-under=78"
    ) in workflow
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
    assert gate.scan_text(
        "backend/app/modules/tasks/schemas.py",
        "package_uri content_cid artifact_manifest_hash",
        "foundation",
    ) == []
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


def test_stale_artifact_contracts_rejects_obsolete_v01_provider_plans() -> None:
    """Active v0.1 docs cannot restore R2-only or Flow Node-first storage."""
    gate = load_module(
        "stale_artifact_contracts_object_storage",
        "scripts/check_stale_artifact_contracts.py",
    )
    path = "docs/spec_artifact_storage_service.md"
    failures = gate.scan_text(
        path,
        "S3ArtifactStore; Cloudflare R2 is the production provider; "
        "Flow Node is the production provider",
        "foundation",
    )
    assert failures == [
        f"{path}:1: AMBIGUOUS_S3_ADAPTER_NAME",
        f"{path}:1: R2_ONLY_PRODUCTION",
        f"{path}:1: OBSOLETE_FLOW_NODE_PLAN",
    ]
    assert gate.scan_text(
        path,
        "S3CompatibleArtifactStore supports AWS S3 and Cloudflare R2",
        "foundation",
    ) == []
    assert gate.scan_text(
        path,
        "Cloudflare R2 is not the only production object storage provider.",
        "foundation",
    ) == []
    assert gate.scan_text(
        "backend/app/adapters/artifacts/s3.py",
        "class S3ArtifactStore: pass",
        "foundation",
    ) == [
        "backend/app/adapters/artifacts/s3.py:1: AMBIGUOUS_S3_ADAPTER_NAME"
    ]


def test_stale_artifact_contracts_scans_active_plan_but_skips_history() -> None:
    """All current initiatives are scanned without rewriting review evidence."""
    gate = load_module(
        "stale_artifact_contracts_active_plans",
        "scripts/check_stale_artifact_contracts.py",
    )
    active = ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/PLAN.md"
    history = (
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/"
        "reviews/WS-ART-001-PLAN-pr-trust-bundle.md"
    )
    assert gate.path_is_scannable(active)
    assert not gate.path_is_scannable(
        ".agent-loop/initiatives/WS-ART-999-future/PLAN.md"
    )
    assert not gate.path_is_scannable(
        ".agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/STATUS.md"
    )
    assert not gate.path_is_scannable(history)
    assert gate.path_is_scannable("docs/reviews/artifact_operations.md")
    assert gate.path_is_scannable("backend/app/modules/reviews/artifacts.py")
    assert gate.path_is_scannable("docs/new_artifact_contract.rst")
    assert gate.path_is_scannable("deploy/r2/credentials")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".agent-loop/initiatives/WS-ART-001-storage").mkdir(parents=True)
        (root / ".agent-loop/initiatives/WS-AUTH-001-auth").mkdir(parents=True)
        (root / ".agent-loop/WORK_QUEUE.md").write_text(
            "## In Progress\n\n"
            "| Chunk | Title | Risk | Status |\n"
            "|---|---|---:|---|\n"
            "| `WS-ART-001-02A1` | Storage | L1 | Active |\n"
            "| `WS-AUTH-001-05` | Auth | L1 | Active |\n"
            "\n## Planned Next\n",
            encoding="utf-8",
        )
        assert gate.active_initiative_prefixes(root) == (
            ".agent-loop/initiatives/WS-ART-001-storage/",
            ".agent-loop/initiatives/WS-AUTH-001-auth/",
        )


def test_stale_artifact_contracts_discovers_new_active_docs() -> None:
    """A new active architecture doc cannot bypass provider-neutral wording rules."""
    gate = load_module(
        "stale_artifact_contracts_dynamic_docs",
        "scripts/check_stale_artifact_contracts.py",
    )
    path = "docs/new_artifact_architecture.md"
    assert gate.path_is_scannable(path)
    assert gate.scan_text(path, "R2 is the sole production backend", "foundation") == [
        f"{path}:1: R2_ONLY_PRODUCTION"
    ]
    historical = "docs/internal_reviews/old_artifact_review.md"
    assert not gate.path_is_scannable(historical)
    assert gate.ACTIVE_INITIATIVE_PREFIXES == (
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/",
    )


def test_stale_artifact_contracts_scans_plantuml_and_active_loop_ledgers() -> None:
    """New diagrams and durable loop state cannot bypass artifact wording gates."""
    gate = load_module(
        "stale_artifact_contracts_diagrams_and_ledgers",
        "scripts/check_stale_artifact_contracts.py",
    )
    diagram = "docs/diagrams/new_artifact_architecture.puml"
    work_queue = ".agent-loop/WORK_QUEUE.md"
    assert gate.path_is_scannable(diagram)
    assert gate.scan_text(
        diagram,
        "R2 is the sole production store",
        "foundation",
    ) == [f"{diagram}:1: R2_ONLY_PRODUCTION"]
    assert gate.path_is_scannable(work_queue)
    assert gate.scan_text(
        work_queue,
        "Flow Node is the production store",
        "foundation",
    ) == [f"{work_queue}:1: OBSOLETE_FLOW_NODE_PLAN"]


def test_stale_artifact_contracts_rejects_caller_storage_uris_at_cutover() -> None:
    """Caller-owned provider URIs remain legal only before submission cutover."""
    gate = load_module(
        "stale_artifact_contracts_caller_storage_uris",
        "scripts/check_stale_artifact_contracts.py",
    )
    path = "docs/template_submission_artifact_policy.md"
    text = "Clients may send local://fixture or s3://bucket/key references."
    assert gate.scan_text(path, text, "foundation") == []
    assert gate.scan_text(path, text, "submission_cutover") == [
        f"{path}:1: LEGACY_CALLER_STORAGE_SCHEME",
        f"{path}:1: LEGACY_CALLER_STORAGE_SCHEME",
    ]


def test_stale_artifact_contracts_future_phases_ignore_immutable_history() -> None:
    """Full-repository phase scans target live owners, not migrations or fixtures."""
    gate = load_module(
        "stale_artifact_contracts_future_phase_repository",
        "scripts/check_stale_artifact_contracts.py",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        files = {
            "backend/app/modules/projects/models.py": "content_cid = 'old'\n",
            "backend/app/modules/tasks/schemas.py": "package_uri = 'old'\n",
            "backend/app/modules/checkers/models.py": "artifact_manifest_hash = 'old'\n",
            "docs/live_artifact_contract.md": "allowed: local://fixture\n",
            "backend/alembic/versions/0001_history.py": (
                "content_cid package_uri artifact_manifest_hash\n"
            ),
            "backend/tests/test_history.py": (
                "content_cid package_uri artifact_manifest_hash local://fixture\n"
            ),
            "docs/internal_reviews/history.md": (
                "content_cid package_uri artifact_manifest_hash local://fixture\n"
            ),
        }
        for relative_path, contents in files.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)

        assert gate.scan(root, "foundation") == []
        assert gate.scan(root, "guide_source_cutover") == [
            "backend/app/modules/projects/models.py:1: LEGACY_GUIDE_CONTENT_CID"
        ]
        assert set(gate.scan(root, "checker_cutover")) == {
            "backend/app/modules/projects/models.py:1: LEGACY_GUIDE_CONTENT_CID",
            "backend/app/modules/tasks/schemas.py:1: LEGACY_SUBMISSION_TRANSPORT",
            "backend/app/modules/checkers/models.py:1: LEGACY_CHECKER_ARTIFACT_COPY",
            "docs/live_artifact_contract.md:1: LEGACY_CALLER_STORAGE_SCHEME",
        }

        for relative_path in (
            "backend/app/modules/projects/models.py",
            "backend/app/modules/tasks/schemas.py",
            "backend/app/modules/checkers/models.py",
            "docs/live_artifact_contract.md",
        ):
            (root / relative_path).write_text("current_contract = True\n", encoding="utf-8")
        assert gate.scan(root, "checker_cutover") == []


def test_stale_artifact_contracts_rejects_r2_static_and_manager_setup_resume() -> None:
    """Active storage docs preserve credential and recovery ownership."""
    gate = load_module(
        "stale_artifact_contracts_storage_ownership",
        "scripts/check_stale_artifact_contracts.py",
    )
    path = "docs/spec_artifact_storage_service.md"
    failures = gate.scan_text(
        path,
        "R2 supports injected static credentials. "
        "A Project Manager may use the setup-run resume command.",
        "foundation",
    )
    assert failures == [
        f"{path}:1: R2_STATIC_PRODUCTION_CREDENTIALS",
        f"{path}:1: PROJECT_MANAGER_SETUP_RESUME",
    ]
    assert gate.scan_text(
        path,
        "Project Manager can restart project setup after storage recovery.",
        "foundation",
    ) == [f"{path}:1: PROJECT_MANAGER_SETUP_RESUME"]
    assert gate.scan_text(
        path,
        "Project Manager can restart\nproject setup after storage recovery.",
        "foundation",
    ) == [f"{path}:1: PROJECT_MANAGER_SETUP_RESUME"]
    assert gate.scan_text(
        path,
        "Project Manager may use project setup\nrestart after recovery.",
        "foundation",
    ) == [f"{path}:1: PROJECT_MANAGER_SETUP_RESUME"]
    for allowed in (
        "Project Manager cannot restart project setup after storage recovery.",
        "Project Manager must not use setup-run retry after recovery.",
        "Project Manager observes recovery. Operator can restart project setup.",
    ):
        assert gate.scan_text(path, allowed, "foundation") == []
    assert gate.scan_text(
        path,
        "Operator is not required, and a Project Manager may restart project setup.",
        "foundation",
    ) == [f"{path}:1: PROJECT_MANAGER_SETUP_RESUME"]
    for positive_authority in (
        "Project Manager does not need Operator approval and may restart project setup.",
        "Project Manager is not blocked and may restart project setup.",
        "Project Manager is not prohibited from restarting project setup.",
    ):
        assert gate.scan_text(path, positive_authority, "foundation") == [
            f"{path}:1: PROJECT_MANAGER_SETUP_RESUME"
        ]
    assert gate.scan_text(
        path,
        "AWS is not enabled, but R2 is the sole production backend.",
        "foundation",
    ) == [f"{path}:1: R2_ONLY_PRODUCTION"]
    for stale_architecture in (
        "Cloudflare R2 is our production object storage.",
        "Production artifact bytes are stored only in Cloudflare R2.",
        "Only Cloudflare R2 is supported for production deployments.",
    ):
        assert gate.scan_text(path, stale_architecture, "foundation") == [
            f"{path}:1: R2_ONLY_PRODUCTION"
        ]
    for stale_flow_node in (
        "The v0.1 production artifact store uses Flow Node.",
        "Flow Node will handle v0.1 production artifact bytes.",
    ):
        assert gate.scan_text(path, stale_flow_node, "foundation") == [
            f"{path}:1: OBSOLETE_FLOW_NODE_PLAN"
        ]
    assert gate.scan_text(
        path,
        "The adapter dependency remains WS-ART-001-01C.",
        "foundation",
    ) == [f"{path}:1: OBSOLETE_ARTIFACT_CHUNK_DEPENDENCY"]
    for wording in (
        "Cloudflare R2 production credentials are static.",
        "Configure static credentials for R2 production.",
        "R2 relies on long-lived credentials.",
        "Static credentials are supported for the Cloudflare R2 production profile.",
        "R2 uses static access keys in production.",
        (
            "R2 reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from the "
            "environment in production."
        ),
    ):
        assert gate.scan_text(path, wording, "foundation") == [
            f"{path}:1: R2_STATIC_PRODUCTION_CREDENTIALS"
        ]
    assert gate.scan_text(
        "backend/app/core/config.py",
        'R2 production credentials are static',
        "foundation",
    ) == [
        "backend/app/core/config.py:1: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    assert gate.scan_text(
        "backend/app/adapters/artifacts/s3_compatible.py",
        'R2 uses long-lived credentials',
        "foundation",
    ) == [
        "backend/app/adapters/artifacts/s3_compatible.py:1: "
        "R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    mixed_provider_config = (
        "profiles:\n  cloudflare_r2:\n    credential_mode: container_temporary\n"
        "  minio:\n    credential_mode: local_static\n"
        "    AWS_ACCESS_KEY_ID: ${MINIO_ACCESS_KEY}\n"
    )
    assert gate.scan_text("docker-compose.yml", mixed_provider_config, "foundation") == []
    for deployment_path, static_config in (
        (
            "deploy/r2/config.yaml",
            "profiles:\n  cloudflare_r2:\n    endpoint: "
            "https://account.r2.cloudflarestorage.com\n"
            + "    note: safe\n" * 80
            + "    credential_mode: local_static\n",
        ),
        (
            "infra/r2/.env.example",
            "ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "ARTIFACT_CREDENTIAL_MODE=static\n",
        ),
        (
            "infra/r2/reversed.env",
            "ARTIFACT_CREDENTIAL_MODE=local_static\n"
            "ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n",
        ),
        (
            "deployment/r2/config.toml",
            "[profiles.cloudflare_r2]\ncredential_mode = 'long_lived'\n",
        ),
        (
            "docker-compose.r2.yml",
            "services:\n  workstream:\n    environment:\n"
            "      - ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "      - AWS_ACCESS_KEY_ID=forbidden\n"
            "      - AWS_SECRET_ACCESS_KEY=forbidden\n",
        ),
        (
            "compose.yaml",
            "services:\n  workstream:\n    environment:\n"
            "      - ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "      - AWS_ACCESS_KEY_ID\n",
        ),
        (
            "compose.r2.yml",
            "services:\n  workstream:\n    environment:\n"
            "      - 'ARTIFACT_PROVIDER_PROFILE=cloudflare_r2'\n"
            "      - \"AWS_SECRET_ACCESS_KEY=forbidden\"\n",
        ),
        (
            "deploy/r2/compose.yml",
            "services:\n  workstream:\n    environment: "
            "[ARTIFACT_PROVIDER_PROFILE=cloudflare_r2, AWS_ACCESS_KEY_ID]\n",
        ),
        (
            "k8s/r2-deployment.yaml",
            "spec:\n  containers:\n    - name: workstream\n      env:\n"
            "        - name: ARTIFACT_PROVIDER_PROFILE\n          value: cloudflare_r2\n"
            "        - name: AWS_ACCESS_KEY_ID\n          valueFrom:\n"
            "            secretKeyRef:\n              name: forbidden\n              key: access\n",
        ),
        (
            "deploy/r2/config.json",
            '{"environment":{"ARTIFACT_PROVIDER_PROFILE":"cloudflare_r2",'
            '"AWS_ACCESS_KEY_ID":"forbidden"}}\n',
        ),
        (
            "deployment/r2/entrypoint.sh",
            "export ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "export AWS_ACCESS_KEY_ID\n",
        ),
        (
            "deploy/r2/Dockerfile.runtime",
            "ENV ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "ENV AWS_SECRET_ACCESS_KEY=forbidden\n",
        ),
        (
            "Dockerfile",
            "FROM python:3.12 AS runtime\n"
            "ENV PROFILE=r2 "
            "AWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            ".env.production",
            "ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n"
            "AWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            "deployment/r2/compound.sh",
            "export PROFILE=r2 "
            "AWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            "deploy/r2/nested.yaml",
            "provider_profile: cloudflare_r2\ncredentials:\n"
            "  AWS_ACCESS_KEY_ID: forbidden\n",
        ),
        (
            "compose.inherited.yml",
            "services:\n  workstream:\n    environment:\n"
            "      ARTIFACT_PROVIDER_PROFILE: cloudflare_r2\n"
            "      AWS_ACCESS_KEY_ID:\n",
        ),
        (
            "compose.merged.yml",
            "x-credentials: &credentials\n  AWS_ACCESS_KEY_ID:\n"
            "services:\n  workstream:\n    environment:\n"
            "      <<: *credentials\n"
            "      ARTIFACT_PROVIDER_PROFILE: cloudflare_r2\n",
        ),
        (
            "k8s/r2-envfrom.yaml",
            "spec:\n  containers:\n    - name: workstream\n      env:\n"
            "        - name: ARTIFACT_PROVIDER_PROFILE\n          value: cloudflare_r2\n"
            "      envFrom:\n        - secretRef:\n            name: forbidden\n",
        ),
        (
            "infra/r2/.env",
            "AWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            "Dockerfile.r2",
            "FROM python:3.12\nENV AWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            ".env.production",
            "ARTIFACT_PROVIDER_PROFILE\nAWS_ACCESS_KEY_ID\n",
        ),
        (
            "ops/storage.yaml",
            "provider_profile: cloudflare_r2\n"
            "AWS_ACCESS_KEY_ID: forbidden\n",
        ),
        (
            "compose.dynamic.yml",
            "services:\n  workstream:\n    environment:\n"
            "      ARTIFACT_PROVIDER_PROFILE: ${ARTIFACT_PROVIDER_PROFILE}\n"
            "      AWS_ACCESS_KEY_ID: forbidden\n",
        ),
        (
            "deployment/r2/config.toml",
            "provider_profile = 'cloudflare_r2'\n"
            "credentials = { aws_access_key_id = 'forbidden' }\n",
        ),
        (
            "backend/app/core/settings.py",
            "artifact_provider_profile = 'cloudflare_r2'\n"
            "artifact_r2_access_key_id = 'forbidden'\n",
        ),
        (
            "deploy/r2/credentials",
            "AWS_SECRET_ACCESS_KEY=forbidden\n",
        ),
        (
            "compose.env-file.yml",
            "services:\n  workstream:\n    environment:\n"
            "      ARTIFACT_PROVIDER_PROFILE: cloudflare_r2\n"
            "    env_file: .env.r2\n",
        ),
        (
            "deploy/main.tf",
            "provider \"cloudflare_r2\" {\n"
            "  credentials {\n"
            "    aws_access_key_id = \"forbidden\"\n"
            "  }\n"
            "}\n",
        ),
        (
            "infra/prod.tfvars",
            "artifact_provider_profile = \"r2\"\n"
            "AWS_ACCESS_KEY_ID = \"forbidden\"\n",
        ),
        (
            "config/r2.env",
            "ARTIFACT_PROVIDER_PROFILE=r2\nAWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            "production.env",
            "ARTIFACT_PROVIDER_PROFILE=r2\nAWS_ACCESS_KEY_ID=forbidden\n",
        ),
        (
            "deploy/indirect.tf",
            "artifact_provider_profile = var.artifact_provider_profile\n"
            "AWS_ACCESS_KEY_ID = \"forbidden\"\n",
        ),
        (
            "deploy/env-command.sh",
            "env ARTIFACT_PROVIDER_PROFILE=r2 AWS_ACCESS_KEY_ID=forbidden exec app\n",
        ),
        (
            "Dockerfile.r2",
            "FROM python:3.12\nARG AWS_ACCESS_KEY_ID\n",
        ),
        (
            "Dockerfile",
            "FROM python:3.12\n"
            "RUN env ARTIFACT_PROVIDER_PROFILE=r2 AWS_ACCESS_KEY_ID=forbidden app\n",
        ),
        (
            "compose.parent-secret.yml",
            "services:\n  workstream:\n    environment:\n"
            "      ARTIFACT_PROVIDER_PROFILE: r2\n"
            "      R2_PARENT_SECRET: forbidden\n",
        ),
        (
            "ops/storage.yaml",
            "artifact.provider: r2\nartifact.aws_profile: forbidden\n",
        ),
        (
            "ops/storage.yaml",
            "artifact-provider: r2\n"
            "artifact-aws-shared-credentials-file: forbidden\n",
        ),
        (
            "ops/storage.json",
            '{"artifactProvider":"r2","accessKeyId":"forbidden"}\n',
        ),
        (
            "ops/storage.ini",
            "[profile workstream-r2]\naws_access_key_id = forbidden\n",
        ),
        (
            "compose.environment-scalar.yml",
            "services:\n  workstream:\n    environment: ${R2_ENVIRONMENT}\n",
        ),
        (
            "compose.environment-template.yml",
            "services:\n  workstream:\n    environment:\n"
            "      - ${R2_CREDENTIAL_ASSIGNMENT}\n",
        ),
        (
            "compose.env-file-only.yml",
            "services:\n  workstream:\n    env_file: .env.r2\n",
        ),
        (
            "deploy/source.sh",
            '. "$R2_ENV_FILE"\n',
        ),
    ):
        assert gate.path_is_scannable(deployment_path)
        failures = gate.scan_text(deployment_path, static_config, "foundation")
        assert len(failures) == 1
        assert failures[0].endswith("R2_STATIC_PRODUCTION_CREDENTIALS")
    compose_with_local_minio = (
        "services:\n"
        "  workstream:\n"
        "    environment:\n"
        "      ARTIFACT_PROVIDER_PROFILE: cloudflare_r2\n"
        "      ARTIFACT_CREDENTIAL_MODE: container_temporary\n"
        "  minio:\n"
        "    environment:\n"
        "      ARTIFACT_PROVIDER_PROFILE: minio\n"
        "      AWS_ACCESS_KEY_ID: local-dev-only\n"
        "      AWS_SECRET_ACCESS_KEY: local-dev-only\n"
    )
    assert gate.scan_text("compose.yml", compose_with_local_minio, "foundation") == []
    assert gate.scan_text(
        "ops/storage.yaml",
        "provider_profile: cloudflare_r2\nasset_mode: static\nretention: long_lived\n",
        "foundation",
    ) == []
    assert gate.scan_text(
        "ops/storage.yaml",
        "provider_profile: cloudflare_r2\naws_config_file: /dev/null\n",
        "foundation",
    ) == []
    assert gate.scan_text(
        "ops/email.yaml",
        "provider: ${EMAIL_PROVIDER}\nAWS_ACCESS_KEY_ID: aws-only\n",
        "foundation",
    ) == []
    assert gate.scan_text(
        ".env.example",
        "ARTIFACT_PROVIDER_PROFILE=r2\n"
        "ARTIFACT_CREDENTIAL_MODE=container_temporary\n"
        "MINIO_ACCESS_KEY=local-only\nMINIO_SECRET_KEY=local-only\n",
        "foundation",
    ) == []
    assert gate.scan_text(
        "ops/storage.yaml",
        "provider_profile: r2\nsentry_access_key: unrelated\n",
        "foundation",
    ) == []
    dockerfile_with_local_minio = (
        "FROM minio/minio:latest AS minio\n"
        "ENV ARTIFACT_PROVIDER_PROFILE=minio AWS_ACCESS_KEY_ID=local-only\n"
        "FROM python:3.12 AS workstream\n"
        "ENV ARTIFACT_PROVIDER_PROFILE=cloudflare_r2 "
        "ARTIFACT_CREDENTIAL_MODE=container_temporary\n"
    )
    assert gate.scan_text("Dockerfile", dockerfile_with_local_minio, "foundation") == []
    dockerfile_parent_r2 = (
        "FROM python:3.12 AS r2base\n"
        "ENV PROFILE=r2\n"
        "FROM r2base AS runtime\n"
        "ENV AWS_ACCESS_KEY_ID=forbidden\n"
    )
    assert gate.scan_text("Dockerfile", dockerfile_parent_r2, "foundation") == [
        "Dockerfile:4: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    dockerfile_parent_static = (
        "FROM python:3.12 AS base\n"
        "ENV AWS_ACCESS_KEY_ID=forbidden\n"
        "FROM base AS runtime\n"
        "ENV PROFILE=r2\n"
    )
    assert gate.scan_text("Dockerfile", dockerfile_parent_static, "foundation") == [
        "Dockerfile:2: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    terraform_peer_resources = (
        'resource "artifact_profile" "r2" {\n'
        '  provider_profile = "r2"\n'
        "}\n"
        'resource "artifact_profile" "minio" {\n'
        '  provider_profile = "minio"\n'
        '  AWS_ACCESS_KEY_ID = "local-only"\n'
        "}\n"
    )
    assert gate.scan_text("deploy/storage.tf", terraform_peer_resources, "foundation") == []
    terraform_peer_resources_reversed = (
        'resource "artifact_profile" "minio" {\n'
        '  provider_profile = "minio"\n'
        '  AWS_ACCESS_KEY_ID = "local-only"\n'
        "}\n"
        'resource "artifact_profile" "r2" {\n'
        '  provider_profile = "r2"\n'
        "}\n"
    )
    assert (
        gate.scan_text(
            "deploy/storage.tf",
            terraform_peer_resources_reversed,
            "foundation",
        )
        == []
    )
    unnamed_dockerfile_stage = (
        "FROM python:3.12\n"
        "ENV PROFILE=r2 AWS_ACCESS_KEY_ID=forbidden\n"
    )
    assert gate.scan_text("Dockerfile", unnamed_dockerfile_stage, "foundation") == [
        "Dockerfile:2: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    dockerfile_child_minio_override = (
        "FROM python:3.12 AS base\n"
        "ENV PROFILE=r2\n"
        "FROM base AS local\n"
        "ENV PROFILE=minio AWS_ACCESS_KEY_ID=local-only\n"
    )
    assert (
        gate.scan_text("Dockerfile", dockerfile_child_minio_override, "foundation")
        == []
    )
    shell_with_local_minio = (
        "minio_config() {\n"
        "  export ARTIFACT_PROVIDER_PROFILE=minio AWS_ACCESS_KEY_ID=local-only\n"
        "}\n"
        "r2_config() {\n"
        "  export ARTIFACT_PROVIDER_PROFILE=cloudflare_r2 "
        "ARTIFACT_CREDENTIAL_MODE=container_temporary\n"
        "}\n"
    )
    assert gate.scan_text("deploy/storage.sh", shell_with_local_minio, "foundation") == []
    shell_root_inheritance = (
        "export AWS_ACCESS_KEY_ID=forbidden\n"
        "r2_config() { export PROFILE=r2; }\n"
        "r2_config\n"
    )
    assert gate.scan_text("deploy/storage.sh", shell_root_inheritance, "foundation") == [
        "deploy/storage.sh:1: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    shell_local_then_export = (
        "r2_config()\n{\n"
        "  PROFILE=r2\n"
        "  export PROFILE\n"
        "  export AWS_ACCESS_KEY_ID\n"
        "}\n"
    )
    assert gate.scan_text("deploy/storage.sh", shell_local_then_export, "foundation") == [
        "deploy/storage.sh:5: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    shell_called_minio_then_r2 = shell_with_local_minio + "minio_config\nr2_config\n"
    assert gate.scan_text(
        "deploy/storage.sh", shell_called_minio_then_r2, "foundation"
    ) == ["deploy/storage.sh:2: R2_STATIC_PRODUCTION_CREDENTIALS"]
    shell_function_with_arguments = (
        "export AWS_ACCESS_KEY_ID=forbidden\n"
        "configure() { export ARTIFACT_PROVIDER_PROFILE=r2; }\n"
        "configure production\n"
    )
    assert gate.scan_text(
        "deploy/storage.sh",
        shell_function_with_arguments,
        "foundation",
    ) == ["deploy/storage.sh:1: R2_STATIC_PRODUCTION_CREDENTIALS"]
    shell_control_flow = (
        "if use_minio; then\n"
        "  export PROFILE=minio AWS_ACCESS_KEY_ID=local-only\n"
        "else\n"
        "  export PROFILE=r2 ARTIFACT_CREDENTIAL_MODE=container_temporary\n"
        "fi\n"
    )
    assert gate.scan_text("deploy/storage.sh", shell_control_flow, "foundation") == [
        "deploy/storage.sh:1: R2_CONFIG_PARSE_ERROR"
    ]
    yaml_complex_key = (
        "? [one, two]\n"
        ": value\n"
        "profile: r2\n"
        "AWS_ACCESS_KEY_ID: forbidden\n"
    )
    assert gate.scan_text("ops/r2.yaml", yaml_complex_key, "foundation") == [
        "ops/r2.yaml:1: R2_CONFIG_PARSE_ERROR"
    ]
    inherited_parent_overridden_by_minio = (
        "provider_profile: cloudflare_r2\n"
        "profiles:\n"
        "  local:\n"
        "    provider_profile: minio\n"
        "    AWS_ACCESS_KEY_ID: local-only\n"
    )
    assert gate.scan_text(
        "deploy/storage.yaml",
        inherited_parent_overridden_by_minio,
        "foundation",
    ) == []
    exact_line_config = (
        "services:\n"
        "  minio:\n"
        "    environment:\n"
        "      ARTIFACT_PROVIDER_PROFILE: minio\n"
        "      AWS_ACCESS_KEY_ID: local-only\n"
        "  workstream:\n"
        "    environment:\n"
        "      ARTIFACT_PROVIDER_PROFILE: cloudflare_r2\n"
        "      AWS_ACCESS_KEY_ID: forbidden\n"
    )
    assert gate.scan_text("compose.yml", exact_line_config, "foundation") == [
        "compose.yml:9: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    repeated_toml_keys = (
        "[profiles.minio]\n"
        "provider_profile = 'minio'\n"
        "aws_access_key_id = 'local-only'\n"
        "\n"
        "[profiles.r2]\n"
        "provider_profile = 'r2'\n"
        "aws_access_key_id = 'forbidden'\n"
    )
    assert gate.scan_text("deploy/storage.toml", repeated_toml_keys, "foundation") == [
        "deploy/storage.toml:7: R2_STATIC_PRODUCTION_CREDENTIALS"
    ]
    issuer_parent_secret = (
        "services:\n"
        "  r2-credential-issuer:\n"
        "    environment:\n"
        "      ARTIFACT_PROVIDER_PROFILE: r2\n"
        "      R2_PARENT_SECRET: issuer-owned\n"
    )
    assert gate.scan_text("compose.r2.yml", issuer_parent_secret, "foundation") == []
    workstream_docker_secret_mount = (
        "FROM python:3.12 AS workstream\n"
        "RUN --mount=type=secret,id=R2_PARENT_SECRET python -m app\n"
    )
    assert gate.scan_text(
        "backend/Dockerfile",
        workstream_docker_secret_mount,
        "foundation",
    ) == ["backend/Dockerfile:2: R2_STATIC_PRODUCTION_CREDENTIALS"]
    issuer_docker_secret_mount = (
        "FROM python:3.12 AS issuer\n"
        "RUN --mount=type=secret,id=R2_PARENT_SECRET python -m issuer\n"
    )
    assert gate.scan_text(
        "services/r2_credential_issuer/Dockerfile",
        issuer_docker_secret_mount,
        "foundation",
    ) == []
    rejection_code = (
        'if provider_profile == "cloudflare_r2" and "AWS_ACCESS_KEY_ID" in env:\n'
        '    raise ValueError("ambient credential source rejected")\n'
    )
    assert gate.scan_text("backend/app/core/config.py", rejection_code, "foundation") == []
    for forbidden_source in (
        "AWS_SESSION_TOKEN",
        "AWS_SECURITY_TOKEN",
        "AWS_PROFILE",
        "AWS_SHARED_CREDENTIALS_FILE",
        "AWS_CREDENTIAL_FILE",
        "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
        "AWS_CONTAINER_AUTHORIZATION_TOKEN",
        "credential_process",
        "login_session",
    ):
        config = f"ARTIFACT_PROVIDER_PROFILE=cloudflare_r2\n{forbidden_source}=forbidden\n"
        failures = gate.scan_text("infra/r2/.env", config, "foundation")
        assert len(failures) == 1, (forbidden_source, failures)
        assert failures[0].endswith("R2_STATIC_PRODUCTION_CREDENTIALS")
    for deployment_path in (
        "deploy/r2-policy.tf",
        "deployment/r2-entrypoint.sh",
        "infra/r2/.env",
        "deploy/r2/Dockerfile",
    ):
        assert gate.path_is_scannable(deployment_path)
        assert gate.scan_text(
            deployment_path,
            "R2 uses static access keys in production.",
            "foundation",
        ) == [f"{deployment_path}:1: R2_STATIC_PRODUCTION_CREDENTIALS"]


def test_stale_artifact_contracts_fail_closed_on_unreadable_text() -> None:
    """A tracked non-UTF8 active file cannot silently bypass contract scanning."""
    gate = load_module(
        "stale_artifact_contracts_unreadable",
        "scripts/check_stale_artifact_contracts.py",
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "docs/active.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\xfe")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        assert gate.scan(root, "foundation") == ["docs/active.md:0: UNREADABLE_TEXT"]


def test_stale_artifact_contracts_remove_flow_node_at_store_cutover() -> None:
    """The dormant runtime provider is rejected from its owning cutover onward."""
    gate = load_module(
        "stale_artifact_contracts_flow_node_cutover",
        "scripts/check_stale_artifact_contracts.py",
    )
    path = "backend/app/core/config.py"
    assert gate.scan_text(path, 'backend = "flow_node"', "foundation") == []
    assert gate.scan_text(path, 'backend = "flow_node"', "artifact_store_cutover") == [
        f"{path}:1: LEGACY_FLOW_NODE_RUNTIME"
    ]


def test_artifact_chunk_contracts_accumulate_exact_ci_coverage_gates() -> None:
    """All artifact chunks define exact cumulative fail-closed coverage gates."""
    artifact_report = (
        "coverage report --include='app/adapters/artifacts/*,"
        "app/interfaces/artifacts.py,app/modules/artifacts/*' --precision=2 "
        "--fail-under=90"
    )
    external_service_report = (
        "coverage report --include='app/interfaces/external_services.py' "
        "--precision=2 --fail-under=90"
    )
    config_report = (
        "coverage report --include='app/core/config.py' --precision=2 "
        "--fail-under=90"
    )
    worker_report = (
        "coverage report --include='app/workers/*' --precision=2 --fail-under=90"
    )
    api_router_report = (
        "coverage report --include='app/api/router.py' --precision=2 "
        "--fail-under=90"
    )
    project_report = (
        "coverage report --include='app/modules/projects/*' --precision=2 "
        "--fail-under=90"
    )
    task_report = (
        "coverage report --include='app/modules/tasks/*' --precision=2 "
        "--fail-under=90"
    )
    checker_report = (
        "coverage report --include='app/modules/checkers/*' --precision=2 "
        "--fail-under=90"
    )
    project_agent_report = (
        "coverage report --include='app/adapters/project_agents/*,"
        "app/interfaces/project_agents.py' --precision=2 --fail-under=90"
    )
    issuer_report = (
        "python -m pytest services/r2_credential_issuer/tests -q "
        "--cov=services/r2_credential_issuer/src --cov-report=term-missing "
        "--cov-fail-under=90"
    )
    example_report = (
        "python -m pytest examples/artifact_lifecycle/tests -q "
        "--cov=examples/artifact_lifecycle/proof_tools "
        "--cov-report=term-missing --cov-fail-under=90"
    )
    base_reports = (artifact_report, external_service_report, config_report)
    coverage_plan = (
        (
            "02A1",
            "WS-ART-001-02A1-external-service-adapter-foundation.md",
            (artifact_report, external_service_report),
        ),
        (
            "02A2",
            "WS-ART-001-02A2-committed-source-local-preparation.md",
            base_reports,
        ),
        (
            "02A3",
            "WS-ART-001-02A3-artifact-store-v2-local-clean-cut.md",
            base_reports + (worker_report,),
        ),
        (
            "02B1",
            "WS-ART-001-02B1-s3-compatible-minio-aws.md",
            base_reports + (worker_report,),
        ),
        (
            "02B2",
            "WS-ART-001-02B2-r2-credential-issuer.md",
            base_reports + (worker_report, issuer_report),
        ),
        (
            "02B3",
            "WS-ART-001-02B3-r2-credential-delivery.md",
            base_reports + (worker_report, issuer_report),
        ),
        (
            "02C1",
            "WS-ART-001-02C1-verification-publication-fencing.md",
            base_reports + (worker_report, issuer_report),
        ),
        (
            "02C2",
            "WS-ART-001-02C2-recovery-attempt-idempotency.md",
            base_reports + (worker_report, issuer_report),
        ),
        (
            "02D",
            "WS-ART-001-02D-operator-artifact-operations.md",
            base_reports + (worker_report, api_router_report, issuer_report),
        ),
        (
            "03",
            "WS-ART-001-03-guide-source-cutover.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "04A",
            "WS-ART-001-04A-upload-inspection-sealing.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "04B",
            "WS-ART-001-04B-pre-submit-admission.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                task_report,
                checker_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "05",
            "WS-ART-001-05-submission-artifact-cutover.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                task_report,
                checker_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "06A",
            "WS-ART-001-06A-checker-input-materialization.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                task_report,
                checker_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "06B",
            "WS-ART-001-06B-checker-output-routing.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                task_report,
                checker_report,
                project_agent_report,
                issuer_report,
            ),
        ),
        (
            "07",
            "WS-ART-001-07-recovery-live-proof.md",
            base_reports
            + (
                worker_report,
                api_router_report,
                project_report,
                task_report,
                checker_report,
                project_agent_report,
                issuer_report,
                example_report,
            ),
        ),
    )
    chunk_root = (
        ROOT
        / ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks"
    )
    assert len(coverage_plan) == 16
    for _phase, filename, expected_commands in coverage_plan:
        contract = (chunk_root / filename).read_text(encoding="utf-8")
        normalized_contract = " ".join(contract.split())
        assert ".github/workflows/backend.yml" in contract
        assert "scripts/test_agent_gates.py" in contract
        assert "python3 scripts/check_stale_artifact_contracts.py" in contract
        assert "preserves every earlier scoped 90 percent gate" in normalized_contract
        assert contract.count("--cov-fail-under=78") == 1
        assert (
            "--cov=app --cov-report=term-missing --cov-fail-under=78"
            in normalized_contract
        )
        heading = next(
            candidate
            for candidate in ("## Exact CI Coverage Gates", "## Exact CI Coverage Gate")
            if candidate in contract
        )
        section = contract.split(heading, maxsplit=1)[1].split("## Verification", maxsplit=1)[0]
        fenced = section.split("```bash", maxsplit=1)[1].split("```", maxsplit=1)[0]
        actual_commands = tuple(
            " ".join(line.split()) for line in fenced.splitlines() if line.strip()
        )
        assert actual_commands == expected_commands, (
            f"{filename} exact CI commands changed: {actual_commands!r}"
        )
        for command in actual_commands:
            threshold_count = command.count("--cov-fail-under=90") + command.count(
                "--fail-under=90"
            )
            assert threshold_count == 1
            assert command.startswith(("coverage report ", "python -m pytest "))
            assert "|| true" not in command

    phases = ("foundation",) + tuple(item[0] for item in coverage_plan)
    assert ARTIFACT_COVERAGE_PHASE in phases
    active_index = phases.index(ARTIFACT_COVERAGE_PHASE)
    workflow = (ROOT / ".github/workflows/backend.yml").read_text(encoding="utf-8")
    workflow_document = yaml.safe_load(workflow)
    assert isinstance(workflow_document, dict)
    assert "env" not in workflow_document
    assert "defaults" not in workflow_document
    jobs = workflow_document.get("jobs")
    assert isinstance(jobs, dict)
    test_job = jobs.get("test")
    assert isinstance(test_job, dict)
    assert set(test_job) == {"runs-on", "timeout-minutes", "services", "steps"}
    steps = test_job.get("steps")
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)

    isolated_steps = [step for step in steps if step.get("name") == "Isolated database runner test"]
    assert isolated_steps == [
        {
            "name": "Isolated database runner test",
            "working-directory": "backend",
            "env": {
                "WORKSTREAM_TEST_ADMIN_DATABASE_URL": (
                    "postgresql+asyncpg://workstream:workstream@localhost:5433/postgres"
                )
            },
            "run": "python -m pytest -q tests/test_isolated_database_runner.py",
        }
    ]

    global_coverage_command = (
        "python scripts/run_isolated_tests.py --metadata-json "
        "/tmp/workstream-database.json "
        "--timeout-seconds 12600 -- python -m pytest -q "
        "--ignore=tests/test_isolated_database_runner.py --cov=app "
        "--cov-report=term-missing --cov-fail-under=78"
    )
    global_steps = [
        (index, step)
        for index, step in enumerate(steps)
        if step.get("run") == global_coverage_command
    ]
    assert len(global_steps) == 1
    global_index, global_step = global_steps[0]
    assert set(global_step) == {"name", "working-directory", "env", "run"}
    assert global_step["working-directory"] == "backend"
    assert global_step["env"] == {
        "WORKSTREAM_TEST_ADMIN_DATABASE_URL": (
            "postgresql+asyncpg://workstream:workstream@localhost:5433/postgres"
        )
    }
    all_run_commands = [step.get("run") for step in steps if isinstance(step.get("run"), str)]
    assert sum("--cov-fail-under=78" in command for command in all_run_commands) == 1
    forbidden_coverage_controls = (
        "$GITHUB_ENV",
        "PYTEST_ADDOPTS",
        "COVERAGE_FILE",
        "COVERAGE_PROCESS_START",
        "coverage erase",
        "coverage combine",
        "--cov-append",
    )
    assert not any(
        token in command
        for command in all_run_commands
        for token in forbidden_coverage_controls
    )

    expected_active = (
        (artifact_report,)
        if ARTIFACT_COVERAGE_PHASE == "foundation"
        else coverage_plan[active_index - 1][2]
    )
    executable_90_steps = [
        (index, step)
        for index, step in enumerate(steps)
        if isinstance(step.get("run"), str)
        and ("--fail-under=90" in step["run"] or "--cov-fail-under=90" in step["run"])
    ]
    assert len(executable_90_steps) == len(expected_active)
    coverage_sequence = steps[global_index + 1 : global_index + 1 + len(expected_active)]
    assert tuple(step.get("run") for step in coverage_sequence) == expected_active
    for command, step in zip(expected_active, coverage_sequence, strict=True):
        expected_workdir = "backend" if command.startswith("coverage report ") else None
        expected_keys = {"name", "run"}
        if expected_workdir is not None:
            expected_keys.add("working-directory")
        assert set(step) == expected_keys
        assert step.get("working-directory") == expected_workdir


def test_artifact_coverage_phase_is_bound_to_active_chunk() -> None:
    """Coverage and stale-contract phases follow the durable active chunk."""
    queue = (ROOT / ".agent-loop/WORK_QUEUE.md").read_text(encoding="utf-8")
    in_progress = queue.split("## In Progress", maxsplit=1)[1].split(
        "## Planned Next", maxsplit=1
    )[0]
    active_chunks = [
        chunk
        for chunk in re.findall(r"\| `([^`]+)` \|", in_progress)
        if chunk.startswith("WS-ART-001-")
    ]
    assert len(active_chunks) == 1
    expected_chunk = (
        "WS-ART-001-OBJECT-STORAGE-AMENDMENT"
        if ARTIFACT_COVERAGE_PHASE == "foundation"
        else f"WS-ART-001-{ARTIFACT_COVERAGE_PHASE}"
    )
    assert active_chunks[0] == expected_chunk

    stale_gate = load_module(
        "stale_artifact_phase_binding",
        "scripts/check_stale_artifact_contracts.py",
    )
    active_index = ARTIFACT_COVERAGE_ORDER.index(ARTIFACT_COVERAGE_PHASE)
    expected_contract_phase = artifact_contract_phase_for(ARTIFACT_COVERAGE_PHASE)
    assert stale_gate.ARTIFACT_CONTRACT_PHASE == expected_contract_phase
    assert artifact_contract_phase_for("04A") == "guide_source_cutover"
    assert artifact_contract_phase_for("04B") == "upload_admission"
    cutover_contract = (
        ROOT
        / ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
        "WS-ART-001-02A3-artifact-store-v2-local-clean-cut.md"
    ).read_text(encoding="utf-8")
    assert "scripts/check_stale_artifact_contracts.py" in cutover_contract
    assert "`artifact_store_cutover`" in cutover_contract

    changed = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.splitlines()
    if ARTIFACT_COVERAGE_PHASE == "foundation":
        runtime_prefixes = (
            "backend/app/",
            "backend/alembic/",
            "services/r2_credential_issuer/",
            "examples/artifact_lifecycle/",
        )
        assert not any(path.startswith(runtime_prefixes) for path in changed)

    ownership_phases = (
        ("backend/app/interfaces/external_services.py", "02A1"),
        ("backend/app/modules/artifacts/preparation", "02A2"),
        ("backend/app/workers/artifact_scratch", "02A3"),
        ("backend/app/adapters/artifacts/s3_compatible", "02B1"),
        ("services/r2_credential_issuer/", "02B2"),
        ("examples/artifact_lifecycle/", "07"),
    )
    for changed_path in changed:
        for owned_prefix, minimum_phase in ownership_phases:
            if changed_path.startswith(owned_prefix):
                assert active_index >= ARTIFACT_COVERAGE_ORDER.index(minimum_phase), (
                    f"{changed_path} requires artifact phase {minimum_phase}"
                )


def test_r2_contract_distinguishes_parent_secret_from_access_key_id() -> None:
    """R2 planning must not treat its reused access-key ID as secret signing key."""
    contract_paths = (
        "docs/spec_artifact_storage_service.md",
        "docs/decision_0013_immutable_artifact_storage_boundary.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/DECISIONS.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/DISCOVERY.md",
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-02B3-r2-credential-delivery.md"
        ),
    )
    for relative_path in contract_paths:
        contract = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "parent credential" not in contract.lower()
        assert "parent secret" in contract.lower()
        assert "parent access-key ID" in contract
    spec = (ROOT / "docs/spec_artifact_storage_service.md").read_text(encoding="utf-8")
    r2_chunk = (ROOT / contract_paths[-1]).read_text(encoding="utf-8")
    for required in (
        "AWS_CREDENTIAL_FILE",
        "OriginalEC2Provider",
        "login_session",
        "ec2-credentials-file",
        "container-role",
    ):
        assert required in spec
        assert required in r2_chunk


def test_artifact_operations_use_registered_authorization_permissions() -> None:
    """Artifact routes consume exact AUTH-owned permissions without local authority."""
    auth_spec = (ROOT / "docs/spec_authorization_service.md").read_text(
        encoding="utf-8"
    )
    artifact_chunk = (
        ROOT
        / ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
        "WS-ART-001-02D-operator-artifact-operations.md"
    ).read_text(encoding="utf-8")
    for permission in (
        "artifact.binding.read",
        "artifact.replica.read",
        "artifact.receipt.read",
        "artifact.verification_job.read",
        "artifact.verification_job.retry",
        "artifact.recovery_attempt.read",
        "artifact.recovery_attempt.execute",
        "artifact.audit.read",
        "artifact.verification.execute",
        "artifact.reconciliation.execute",
        "artifact.pending_work.scan",
    ):
        assert permission in auth_spec
        assert permission in artifact_chunk
    auth_chunk = (
        ROOT
        / ".agent-loop/initiatives/WS-AUTH-001-workstream-authorization-service/chunks/"
        "WS-AUTH-001-07-authorization-kernel.md"
    ).read_text(encoding="utf-8")
    assert "broad `operations.*` permissions are\n  not aliases" in auth_chunk
    assert "registers no permission" in artifact_chunk
    for prerequisite in ("AUTH-07", "AUTH-08", "AUTH-09"):
        assert prerequisite in artifact_chunk
    adr = (ROOT / "docs/decision_0013_immutable_artifact_storage_boundary.md").read_text(
        encoding="utf-8"
    )
    assert "The Authorization Service alone owns" in adr
    assert "PostgreSQL records its evidence but grants no authority" in adr


def test_checker_phases_share_one_verified_scratch_materializer() -> None:
    """Pre-submit and post-submit cannot diverge into separate byte paths."""
    contract_paths = (
        "docs/spec_artifact_storage_service.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/PLAN.md",
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-04B-pre-submit-admission.md"
        ),
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-06A-checker-input-materialization.md"
        ),
    )
    for relative_path in contract_paths:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        normalized = " ".join(text.split()).lower()
        assert "canonical" in normalized
        assert "materializer" in normalized
        assert "recomput" in normalized
        assert "digest" in normalized or "sha-256" in normalized
        assert "byte count" in normalized
        assert "read-only" in normalized
        assert "pre-submit" in normalized
        assert "post-submit" in normalized
    post_submit = (ROOT / contract_paths[-1]).read_text(encoding="utf-8")
    assert "never a\n  second workspace manager" in post_submit
    assert "tests/test_artifact_scratch_manager.py" in post_submit


def test_r2_contract_locks_scope_and_shared_network_namespace() -> None:
    """R2 issuer authority and loopback topology remain concrete and bounded."""
    contract_paths = (
        "docs/spec_artifact_storage_service.md",
        "docs/decision_0013_immutable_artifact_storage_boundary.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/PLAN.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/RISKS.md",
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-02B2-r2-credential-issuer.md"
        ),
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-02B3-r2-credential-delivery.md"
        ),
    )
    for relative_path in contract_paths:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        normalized = " ".join(text.split()).lower()
        assert "exact cloudflare account" in normalized
        assert "artifact bucket" in normalized
        assert "non-admin" in normalized
        assert "rotation" in normalized
        assert "revocation" in normalized
        assert "network_mode: service:<workstream-service>" in text
        assert "same pod" in normalized
        assert "bridge" in normalized


def test_aws_contract_allows_only_selected_workload_identity_provider() -> None:
    """AWS production cannot fall back to the ambient SDK credential chain."""
    contract_paths = (
        "docs/spec_artifact_storage_service.md",
        "docs/decision_0013_immutable_artifact_storage_boundary.md",
        ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/PLAN.md",
        (
            ".agent-loop/initiatives/WS-ART-001-immutable-artifact-storage/chunks/"
            "WS-ART-001-02B1-s3-compatible-minio-aws.md"
        ),
    )
    required_methods = (
        "assume-role-with-web-identity",
        "container-role",
        "iam-role",
    )
    for relative_path in contract_paths:
        contract = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "aws_workload_identity" in contract
        assert "aws_default_chain" not in contract
        for method in required_methods:
            assert method in contract
        assert "selected" in contract.lower()
        assert "unselected" in contract.lower()


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
        test_stale_authorization_rule_examples_are_rejected,
        test_stale_authorization_discovery_includes_new_untracked_docs,
        test_stale_authorization_precedence_exemption_is_line_scoped,
        test_stale_authorization_history_allowlist_is_exact,
        test_agent_gates_runs_stale_authorization_docs_fail_closed,
        test_agent_gates_runs_stale_artifact_contracts_fail_closed,
        test_agent_gate_dependencies_and_workflow_are_pinned,
        test_backend_coverage_thresholds_are_regression_protected,
        test_stale_artifact_contracts_foundation_keeps_later_terms_inactive,
        test_stale_artifact_contracts_active_later_phase_owns_only_reached_terms,
        test_stale_artifact_contracts_malformed_phase_fails_closed,
        test_stale_artifact_contracts_rejects_obsolete_v01_provider_plans,
        test_stale_artifact_contracts_scans_active_plan_but_skips_history,
        test_stale_artifact_contracts_discovers_new_active_docs,
        test_stale_artifact_contracts_scans_plantuml_and_active_loop_ledgers,
        test_stale_artifact_contracts_rejects_caller_storage_uris_at_cutover,
        test_stale_artifact_contracts_future_phases_ignore_immutable_history,
        test_stale_artifact_contracts_rejects_r2_static_and_manager_setup_resume,
        test_stale_artifact_contracts_fail_closed_on_unreadable_text,
        test_stale_artifact_contracts_remove_flow_node_at_store_cutover,
        test_artifact_chunk_contracts_accumulate_exact_ci_coverage_gates,
        test_artifact_coverage_phase_is_bound_to_active_chunk,
        test_r2_contract_distinguishes_parent_secret_from_access_key_id,
        test_artifact_operations_use_registered_authorization_permissions,
        test_checker_phases_share_one_verified_scratch_materializer,
        test_r2_contract_locks_scope_and_shared_network_namespace,
        test_aws_contract_allows_only_selected_workload_identity_provider,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} agent gate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
