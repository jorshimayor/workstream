"""Regression tests for Workstream agent gate helpers.

Run with plain Python so the agent-gates workflow does not need test
dependencies installed before it can protect the repository process.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
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
