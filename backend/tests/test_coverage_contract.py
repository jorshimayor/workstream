from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import coverage_policy as policy  # noqa: E402

HEAD = "0016_artifact_domain"
SHA = "a" * 40


def write_json(path: Path, value: dict, *, canonical: bool = False) -> Path:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n" if canonical else json.dumps(value)
    path.write_text(text, encoding="utf-8")
    return path


def evidence(**updates) -> dict:
    value = {
        "schema_version": 1, "base_merge_sha": SHA, "measured_tree_sha": "b" * 40,
        "covered_lines": 3, "num_statements": 4, "measured_percent": "75.000000",
        "configured_floor": "75.000000", "minimum_milestone": "75.000000",
        "python_version": "3.12.0", "coverage_version": "7.1.0",
        "pytest_cov_version": "7.1.0", "database_name": "workstream_test_012345abcdef",
        "alembic_head": HEAD,
    }
    value.update(updates)
    return value


def config_text(report: str = "", run: str = "", pin: str = "pytest-cov==7.1.0",
                precision: int = 6, floor: int = 75) -> str:
    return (
        f"[project.optional-dependencies]\ndev=['{pin}']\n[tool.coverage.run]\n{run}"
        f"\n[tool.coverage.report]\nprecision={precision}\nfail_under={floor}\n{report}"
    )


def coverage_file(tmp_path: Path, *, files: dict | None = None, covered=2, statements=3) -> tuple[Path, Path]:
    root = tmp_path / "backend"
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "app/a.py").write_text("x = 1\n", encoding="utf-8")
    data = {"files": files if files is not None else {"app/a.py": {}},
            "totals": {"covered_lines": covered, "num_statements": statements}}
    return write_json(tmp_path / "coverage.json", data), root


def test_compute_floor_validates_inventory_and_truncates(tmp_path: Path) -> None:
    path, root = coverage_file(tmp_path)
    assert policy.coverage_counts(path, root) == (2, 3)
    assert policy.six_place_percent(2, 3) == "66.666666"
    path, root = coverage_file(tmp_path, files={})
    with pytest.raises(policy.PolicyError, match="application_inventory_mismatch"):
        policy.coverage_counts(path, root)


@pytest.mark.parametrize(("covered", "statements"), [(-1, 3), (4, 3), (0, 0), (True, 3)])
def test_coverage_counts_reject_invalid_totals(tmp_path: Path, covered, statements) -> None:
    path, root = coverage_file(tmp_path, covered=covered, statements=statements)
    with pytest.raises(policy.PolicyError, match="invalid_coverage"):
        policy.coverage_counts(path, root)


def test_intended_config_returns_exact_floor(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(config_text(), encoding="utf-8")
    assert policy.config_floor(path) == Decimal("75.000000")


@pytest.mark.parametrize(("kwargs", "code"), [
    ({"pin": "pytest-cov>=7"}, "pytest_cov_pin_missing"),
    ({"precision": 5}, "coverage_precision_invalid"),
    ({"floor": 101}, "coverage_floor_invalid"),
    ({"report": "omit=[]\n"}, "coverage_exclusion_config"),
    ({"run": "source=['app']\n"}, "coverage_exclusion_config"),
    ({"run": "include=[]\n"}, "coverage_exclusion_config"),
    ({"report": "exclude_lines=[]\n"}, "coverage_exclusion_config"),
])
def test_config_fails_closed(tmp_path: Path, kwargs: dict, code: str) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(config_text(**kwargs), encoding="utf-8")
    with pytest.raises(policy.PolicyError, match=code):
        policy.config_floor(path)


def test_application_coverage_pragma_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "app/a.py").write_text("x = 1  # pragma: no cover\n", encoding="utf-8")
    with pytest.raises(policy.PolicyError, match="coverage_pragma"):
        policy.validate_sources(tmp_path)


def test_canonical_evidence_accepts_bounded_non_secret_schema(tmp_path: Path) -> None:
    path = write_json(tmp_path / "evidence.json", evidence(), canonical=True)
    assert policy.canonical_evidence(path, HEAD)["covered_lines"] == 3
    path.write_text(json.dumps(evidence()), encoding="utf-8")
    with pytest.raises(policy.PolicyError, match="evidence_not_canonical"):
        policy.canonical_evidence(path, HEAD)


@pytest.mark.parametrize(("updates", "code"), [
    ({"extra": 1}, "evidence_schema_invalid"),
    ({"schema_version": True}, "evidence_schema_invalid"),
    ({"base_merge_sha": "bad"}, "evidence_sha_invalid"),
    ({"covered_lines": 5}, "evidence_counts_invalid"),
    ({"measured_percent": "75"}, "evidence_decimal_invalid"),
    ({"configured_floor": "101.000000"}, "evidence_decimal_invalid"),
    ({"measured_percent": "74.000000"}, "evidence_percent_invalid"),
    ({"database_name": "workstream_test"}, "evidence_database_invalid"),
    ({"alembic_head": "old"}, "evidence_alembic_invalid"),
    ({"python_version": ""}, "evidence_version_invalid"),
    ({"python_version": "postgresql://secret"}, "evidence_secret"),
])
def test_evidence_schema_fails_closed(updates: dict, code: str) -> None:
    with pytest.raises(policy.PolicyError, match=code):
        policy.evidence_data(evidence(**updates), HEAD)


def test_runner_metadata_accepts_only_expected_tree_and_head(tmp_path: Path) -> None:
    value = {"schema_version": 1, "database_name": "workstream_test_012345abcdef",
             "alembic_head": HEAD, "tree_sha": SHA}
    path = write_json(tmp_path / "metadata.json", value)
    assert policy.runner_metadata(path, SHA, HEAD) == value
    value["tree_sha"] = "b" * 40
    write_json(path, value)
    with pytest.raises(policy.PolicyError, match="metadata_tree_mismatch"):
        policy.runner_metadata(path, SHA, HEAD)


@pytest.mark.parametrize(("updates", "code"), [
    ({"database_name": "workstream_test"}, "metadata_invalid"),
    ({"schema_version": True}, "metadata_invalid"),
    ({"alembic_head": "old"}, "metadata_alembic_mismatch"),
    ({"extra": "secret"}, "metadata_invalid"),
])
def test_runner_metadata_fails_closed(tmp_path: Path, updates: dict, code: str) -> None:
    value = {"schema_version": 1, "database_name": "workstream_test_012345abcdef",
             "alembic_head": HEAD, "tree_sha": SHA, **updates}
    path = write_json(tmp_path / "metadata.json", value)
    with pytest.raises(policy.PolicyError, match=code):
        policy.runner_metadata(path, SHA, HEAD)


@pytest.mark.parametrize(("source", "weak"), [
    ("value = 'pytest.skip and xfail are inert fixtures'", False),
    ("import pytest\npytest.skip('disabled')", True),
    ("import pytest\n@pytest.mark.xfail\ndef test_x(): pass", True),
    ("import pytest\npytestmark = pytest.mark.skipif(True)", True),
    ("def invalid(", True),
])
def test_python_weakening_is_syntax_aware(tmp_path: Path, source: str, weak: bool) -> None:
    path = tmp_path / "test_policy.py"
    path.write_text(source, encoding="utf-8")
    assert policy.weak_python(path) is weak


@pytest.mark.parametrize(("files", "rows", "diff", "max_lines", "code"), [
    (["backend/app/a.py"], [], "", 5, "scope_violation"),
    (["backend/tests/test_ok.py"], [("backend/tests/test_ok.py", 6, 0)], "", 5, "implementation_size_exceeded"),
    (["backend/tests/test_ok.py"], [("backend/tests/test_ok.py", 1, 0)], "-assert value", 5, "deleted_assertion"),
])
def test_delta_fails_closed(monkeypatch, tmp_path: Path, files, rows, diff, max_lines, code) -> None:
    test = tmp_path / "backend/tests/test_ok.py"
    test.parent.mkdir(parents=True)
    test.write_text("value = 'skip xfail'\nassert value", encoding="utf-8")
    monkeypatch.setattr(policy, "REPO", tmp_path)
    monkeypatch.setattr(policy, "changed_files", lambda *_: files)
    monkeypatch.setattr(policy, "numstat", lambda *_: (0, 0, rows))
    monkeypatch.setattr(policy, "diff_text", lambda *_: diff)
    with pytest.raises(policy.PolicyError, match=code):
        policy.validate_delta("base", max_lines, {"backend/tests/test_ok.py"})


def test_delta_accepts_inert_fixtures_and_agent_memory(monkeypatch, tmp_path: Path) -> None:
    test = tmp_path / "backend/tests/test_ok.py"
    test.parent.mkdir(parents=True)
    test.write_text("value = 'skip xfail'\nassert value", encoding="utf-8")
    files = ["backend/tests/test_ok.py", ".agent-loop/LOOP_STATE.md"]
    monkeypatch.setattr(policy, "REPO", tmp_path)
    monkeypatch.setattr(policy, "changed_files", lambda *_: files)
    monkeypatch.setattr(policy, "numstat", lambda *_: (99, 0, [(files[0], 2, 0), (files[1], 97, 0)]))
    monkeypatch.setattr(policy, "diff_text", lambda *_: "-value = 'assert fixture'\n+assert value")
    policy.validate_delta("base", 2, {files[0]})


def test_compute_cli_is_read_only_and_stable(tmp_path: Path) -> None:
    files = {item.relative_to(policy.BACKEND).as_posix(): {} for item in (policy.BACKEND / "app").rglob("*.py")}
    path = write_json(tmp_path / "coverage.json", {"files": files, "totals": {"covered_lines": 2, "num_statements": 3}})
    command = [sys.executable, str(SCRIPTS / "coverage_policy.py"), "--coverage-json", str(path)]
    result = subprocess.run([*command, "--compute-floor"], text=True, capture_output=True, check=False)
    assert (result.returncode, result.stdout, result.stderr) == (0, "66.666666\n", "")
    assert list(tmp_path.iterdir()) == [path]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    assert result.returncode == 2
    assert result.stderr == "coverage-policy: mode_required\n"
