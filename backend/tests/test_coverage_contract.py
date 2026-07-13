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
                precision: int = 6, floor: int | str = 75, dev: str | None = None) -> str:
    dependencies = dev if dev is not None else f"['{pin}']"
    return (
        f"[project.optional-dependencies]\ndev={dependencies}\n[tool.coverage.run]\n{run}"
        f"\n[tool.coverage.report]\nprecision={precision}\nfail_under={floor}\n{report}"
    )


def coverage_file(tmp_path: Path, *, files: dict | None = None, covered=2, statements=3) -> tuple[Path, Path]:
    root = tmp_path / "backend"
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "app/a.py").write_text("x = 1\n", encoding="utf-8")
    summary = {"summary": {"covered_lines": covered, "num_statements": statements}}
    data = {"files": files if files is not None else {"app/a.py": summary},
            "totals": {"covered_lines": covered, "num_statements": statements}}
    return write_json(tmp_path / "coverage.json", data), root


def test_compute_floor_validates_inventory_and_truncates(tmp_path: Path) -> None:
    path, root = coverage_file(tmp_path)
    assert policy.coverage_counts(path, root) == (2, 3)
    path, root = coverage_file(tmp_path, files={})
    with pytest.raises(policy.PolicyError, match="application_inventory_mismatch"):
        policy.coverage_counts(path, root)


@pytest.mark.parametrize(("covered", "statements", "expected"), [
    (0, 3, "0.000000"),
    (3, 3, "100.000000"),
    (2, 3, "66.666666"),
    (1, 7, "14.285714"),
    (10**100 - 1, 10**100, "99.999999"),
])
def test_six_place_percent_success_boundaries(covered: int, statements: int, expected: str) -> None:
    assert policy.six_place_percent(covered, statements) == expected


@pytest.mark.parametrize(("files", "code"), [
    ({"app/a.py": {}}, "invalid_file_coverage"),
    ({"app/a.py": {"summary": {"covered_lines": 1, "num_statements": 3}}}, "coverage_totals_mismatch"),
])
def test_coverage_counts_reconciles_file_summaries(tmp_path: Path, files: dict, code: str) -> None:
    path, root = coverage_file(tmp_path, files=files)
    with pytest.raises(policy.PolicyError, match=code):
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
    ({"pin": "pytest-cov==7.1.0-malicious"}, "pytest_cov_pin_missing"),
    ({"dev": "['pytest-cov==7.1.0','pytest-cov>=9']"}, "pytest_cov_pin_missing"),
    ({"dev": "['pytest-cov==7.1.0','PYTEST..COV>=9']"}, "pytest_cov_pin_missing"),
    ({"dev": "['pytest-cov==7.1.0',' pytest_cov>=9']"}, "pytest_cov_pin_missing"),
    ({"dev": "'pytest-cov==7.1.0'"}, "invalid_coverage_config"),
    ({"precision": 5}, "coverage_precision_invalid"),
    ({"floor": 101}, "coverage_floor_invalid"),
    ({"floor": "true"}, "coverage_floor_invalid"),
    ({"floor": "'75'"}, "coverage_floor_invalid"),
    ({"floor": "nan"}, "coverage_floor_invalid"),
    ({"floor": "inf"}, "coverage_floor_invalid"),
    ({"floor": "75.1234567"}, "coverage_floor_invalid"),
    ({"report": "omit=[]\n"}, "coverage_exclusion_config"),
    ({"run": "source=['app']\n"}, "coverage_exclusion_config"),
    ({"run": "source_pkgs=['app.modules.projects']\n"}, "coverage_exclusion_config"),
    ({"run": "source_dirs=['app/modules/projects']\n"}, "coverage_exclusion_config"),
    ({"run": "include=[]\n"}, "coverage_exclusion_config"),
    ({"report": "exclude_lines=[]\n"}, "coverage_exclusion_config"),
])
def test_config_fails_closed(tmp_path: Path, kwargs: dict, code: str) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(config_text(**kwargs), encoding="utf-8")
    with pytest.raises(policy.PolicyError, match=code):
        policy.config_floor(path)


@pytest.mark.parametrize("text", [
    "[project.optional-dependencies]\ndev=['pytest-cov==7.1.0']\n[tool.coverage]\nreport=[]",
    "[project.optional-dependencies]\ndev=['pytest-cov==7.1.0']\n[tool.coverage]\nrun='source'\n[tool.coverage.report]\nprecision=6\nfail_under=75",
])
def test_config_rejects_malformed_tables(tmp_path: Path, text: str) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(policy.PolicyError, match="invalid_coverage_config"):
        policy.config_floor(path)


@pytest.mark.parametrize("pragma", ["pragma no cover", "PRAGMA:NO COVER", "pragma:   no   cover", "pragma:nocover"])
def test_application_coverage_pragma_is_rejected(tmp_path: Path, pragma: str) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "app/a.py").write_text(f"x = 1  # {pragma}\n", encoding="utf-8")
    with pytest.raises(policy.PolicyError, match="coverage_pragma"):
        policy.validate_sources(tmp_path)
    (tmp_path / "app/a.py").write_text("MESSAGE = 'pragma: no cover'\n\"\"\"pragma: no cover\"\"\"\n", encoding="utf-8")
    policy.validate_sources(tmp_path)
    (tmp_path / "app/a.py").write_text("# This documentation mentions pragma: no cover\n# notapragmanocover\nx = 1\n", encoding="utf-8")
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
    ({"python_version": "not-a-version"}, "evidence_version_invalid"),
    ({"python_version": "alice:hunter2@db.internal"}, "evidence_version_invalid"),
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


def test_runner_metadata_rejects_matching_malformed_expectations(tmp_path: Path) -> None:
    value = {"schema_version": 1, "database_name": "workstream_test_012345abcdef",
             "alembic_head": "../head", "tree_sha": "not-a-sha"}
    path = write_json(tmp_path / "metadata.json", value)
    with pytest.raises(policy.PolicyError, match="metadata_alembic_mismatch"):
        policy.runner_metadata(path, "not-a-sha", "../head")


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
    ("value = 'pytest.skip and xfail are inert'", False),
    ("import pytest\nwith pytest.raises(ValueError): raise ValueError", False),
    ("import pytest as pt\nwith pt.raises(ValueError): raise ValueError", False),
    ("from pytest import raises as expect\nwith expect(ValueError): raise ValueError", False),
    ("import pytest\npytest.skip('disabled')", True),
    ("import pytest\n@pytest.mark.xfail\ndef test_x(): pass", True),
    ("def test_x():\n from pytest import skip\n skip('disabled')", True),
    ("if True:\n from pytest import mark as m\n @m.skip\n def test_x(): pass", True),
    ("import pytest as pt\npt.importorskip('optional')", True),
    ("import unittest as ut\n@ut.skipUnless(True, 'reason')\ndef test_x(): pass", True),
    ("from unittest import expectedFailure\n@expectedFailure\ndef test_x(): pass", True),
    ("class T:\n def test_x(self): self.skipTest('disabled')", False),
    ("import unittest\nraise unittest.SkipTest('disabled')", True),
    ("from unittest import SkipTest\nraise SkipTest('disabled')", True),
    ("from unittest.case import SkipTest as ST\nraise ST('disabled')", True),
    ("import unittest.case as uc\nraise uc.SkipTest('disabled')", True),
    ("class Local:\n def skip(self): pass\npytest = Local()\npytest.skip()", False),
    ("class Local:\n def skipTest(self): pass\nlocal = Local()\nlocal.skipTest()", False),
    ("import pytest\ndef test_x(pytest): pytest.skip('local')", False),
    ("import pytest\ndef test_x():\n pytest.skip('local')\n pytest = object()", False),
    ("import pytest\ndef outer():\n def test_x(): pytest.skip('disabled')", True),
    ("import pytest\ndef outer():\n pytest = object()\n def test_x(): pytest.skip('local')", False),
    ("import pytest\nclass T:\n pytest = object()\n def test_x(self): pytest.skip('disabled')", True),
    ("import pytest\ndef test_x():\n global pytest\n pytest.skip('disabled')\n pytest = object()", True),
    ("def outer():\n import pytest\n def test_x():\n  nonlocal pytest\n  pytest.skip('disabled')\n  pytest = object()", True),
    ("import pytest\nif ready: pytest = object()\npytest.skip('ambiguous')", True),
    ("from pytest import skip\nif ready: skip = print\nskip('ambiguous')", True),
    ("import pytest\nif ready: pytest = object()\nelse: pytest = object()\npytest.skip('local')", False),
    ("import pytest\ndef test_x(*pytest, **options): pytest.skip('local')", False),
    ("import pytest\ntest_x = lambda pytest: pytest.skip('local')", False),
    ("import pytest\nvalues = [pytest.skip() for pytest in ()]", False),
    ("import pytest\nvalues = [pytest for pytest in ()]\npytest.skip('disabled')", True),
    ("import pytest\ntry: pass\nexcept Exception as pytest: pytest.skip('local')", False),
    ("import pytest\nfor _ in (): pytest = object()\npytest.skip('ambiguous')", True),
    ("import pytest\ntry: pytest = object()\nexcept Exception: pass\npytest.skip('ambiguous')", True),
    ("import pytest\nmatch value:\n case 1: pytest = object()\npytest.skip('ambiguous')", True),
    ("import pytest\nwith manager() as pytest: pytest.skip('local')", False),
    ("import pytest\nvalue: pytest.mark.skip = 1", True),
    ("import pytest\npytest.foo = object()\npytest.skip()", True),
    ("import pytest\npytest[0] = object()\npytest.skip()", True),
    ("import pytest\npytest += object()\npytest.skip()", True),
    ("p = object()\ntry:\n import pytest as p\nexcept Exception: p = object()\np.skip()", True),
    ("p = object()\ntry:\n import pytest as p\n raise Error\nexcept Exception: p.skip()", True),
    ("import pytest\ntry: pytest = object()\nexcept: pass\nfinally: pytest = object()\npytest.skip()", False),
    ("p = object()\nmatch value:\n case 1: import pytest as p\n case _: p = object()\np.skip()", True),
    ("p = object()\nfor x in xs: import pytest as p\nelse: p = object()\np.skip()", True),
    ("import pytest\np = pytest\nif ready: p = object()\npytestmark = p.mark.skip", True),
    ("import unittest\nu = unittest\nif ready: u = object()\ncase = u.TestCase()\ncase.skipTest()", True),
    ("from __future__ import annotations\nimport pytest\ndef f(x: (lambda: pytest.skip())): pass\nclass C:\n x: (lambda: pytest.skip())", False),
    ("import pytest\nmatch value:\n case pytest: pytest.skip()", False),
    ("import pytest\ndef f():\n [[y for y in () if (pytest := object())] for x in ()]\n pytest.skip()", True),
    ("for x in xs:\n def local(): pass", False),
    ("while ready:\n local = lambda: 1", False),
    ("try: pass\nexcept Exception:\n def local(): pass", False),
    ("p = object()\nfor x in xs:\n p.skip()\n import pytest as p", True),
    ("p = object()\nwhile ready:\n p.skip()\n import pytest as p", True),
    ("p = object()\nfor x in xs:\n p.skip()\n import os, pytest as p", True),
    ("import pytest\np = object()\nfor x in xs:\n p.skip()\n p += pytest", True),
    ("import pytest\npytest.skip().field = 1", True),
    ("import pytest\ntarget[pytest.skip()] = 1", True),
    ("import pytest\n[pytest.skip() for pytest.field in xs]", True),
    ("import pytest\n[x for target[pytest.skip()] in xs]", True),
    ("import pytest\np, = (pytest,)\np.skip()", True),
    ("import pytest\n(p, (q,)) = (pytest, (pytest,))\nq.skip()", True),
    ("import pytest\n[(pytest := object()) for _ in ()]\npytest.skip()", True),
    ("import pytest\n((pytest := object()) for _ in ())\npytest.skip()", True),
    ("import pytest\n[lambda: ((p := pytest), p.skip()) for _ in xs]", True),
    ("import pytest as pa\np = object()\nmatch x:\n case 1 if (p := pa) and False: pass\n case _: p.skip()", True),
    ("import pytest\ndef f():\n value: pytest.mark.skip", False),
    ("import pytest\nvalue: pytest.mark.skip", True),
    ("from pytest import mark\npytestmark = mark.skip", True),
    ("import pytest\npytestmark = [pytest.mark.xfail]", True),
    ("def test_x(exec): exec('local')", False),
    ("import pytest\nclass A:\n pytest = object()\n class B:\n  pytest.skip('disabled')", True),
    ("import pytest\na = (pytest for pytest in ()); b = (pytest.skip() for _ in ())", True),
    ("import pytest\na = lambda pytest: pytest.skip(); b = lambda: pytest.skip()", True),
    ("import pytest\ndef test_x(pytest): pytest.skip()\ndef test_x(): pytest.skip()", True),
    ("import unittest\nclass T(unittest.TestCase):\n def test_x(self): super().skipTest('disabled')", True),
    ("import unittest\ncase: unittest.TestCase = unittest.TestCase()\ncase.skipTest('disabled')", True),
    ("import unittest\ncase = unittest.TestCase()\nif ready: case = object()\ncase.skipTest('ambiguous')", True),
    ("from unittest import TestCase as Case\ncase = Case()\ncase.skipTest('disabled')", True),
    ("import unittest\ncase = unittest.TestCase()\ncase.skipTest('disabled')", True),
    ("def invalid(", True),
])
def test_python_weakening_is_syntax_aware(tmp_path: Path, source: str, weak: bool) -> None:
    path = tmp_path / "test_policy.py"
    path.write_text(source, encoding="utf-8")
    assert policy.weak_python(path) is weak


@pytest.mark.parametrize(("files", "rows", "diff", "source", "max_lines", "code"), [
    (["backend/app/a.py"], [], "", "", 5, "scope_violation"),
    ([".agent-loop/initiatives/WS-AUTH-001/PLAN.md"], [], "", "", 5, "scope_violation"),
    (["backend/tests/test_ok.py"], [("backend/tests/test_ok.py", 6, 0)], "", "", 5, "implementation_size_exceeded"),
    (["backend/tests/test_ok.py"], [("backend/tests/test_ok.py", 1, 0)], "@@ -1 +0,0 @@\n-assert value", "assert value", 5, "deleted_assertion"),
])
def test_delta_fails_closed(monkeypatch, tmp_path: Path, files, rows, diff, source, max_lines, code) -> None:
    test = tmp_path / "backend/tests/test_ok.py"
    test.parent.mkdir(parents=True)
    test.write_text("value = 'skip xfail'\nassert value", encoding="utf-8")
    monkeypatch.setattr(policy, "REPO", tmp_path)
    monkeypatch.setattr(policy, "changed_files", lambda *_: files)
    monkeypatch.setattr(policy, "numstat", lambda *_: (0, 0, rows))
    monkeypatch.setattr(policy, "diff_text", lambda *_: diff)
    monkeypatch.setattr(policy, "maybe_run", lambda *_: source)
    with pytest.raises(policy.PolicyError, match=code):
        policy.validate_delta("base", max_lines, {"backend/tests/test_ok.py"})


def test_delta_accepts_approved_memory_without_counting_it(monkeypatch, tmp_path: Path) -> None:
    test = tmp_path / "backend/tests/test_ok.py"
    test.parent.mkdir(parents=True)
    test.write_text("value = 'skip and xfail are inert'\nassert value", encoding="utf-8")
    files = ["backend/tests/test_ok.py", ".agent-loop/LOOP_STATE.md", f"{policy.QUAL_MEMORY}STATUS.md"]
    monkeypatch.setattr(policy, "REPO", tmp_path)
    monkeypatch.setattr(policy, "changed_files", lambda *_: files)
    monkeypatch.setattr(policy, "numstat", lambda *_: (199, 0, [(files[0], 2, 0), (files[1], 97, 0), (files[2], 100, 0)]))
    monkeypatch.setattr(policy, "diff_text", lambda *_: "+assert value")
    monkeypatch.setattr(policy, "maybe_run", lambda *_: "")
    policy.validate_delta("base", 2, {files[0]})


@pytest.mark.parametrize(("source", "replacement", "blocked"), [
    ("import pytest\n\ndef test_x():\n    with pytest.raises(ValueError):\n        raise ValueError\n", "def test_x():\n    raise ValueError\n", True),
    ("import pytest as pt\n\ndef test_x():\n    with (\n        pt\n        .raises(ValueError)\n    ):\n        raise ValueError\n", "def test_x():\n    raise ValueError\n", True),
    ("from pytest import raises as expect\n\ndef test_x():\n    with (\n        expect\n        (ValueError)\n    ):\n        raise ValueError\n", "def test_x():\n    raise ValueError\n", True),
    ("def test_x():\n    if ready: assert result\n", "def test_x():\n    raise ValueError\n", True),
    ("class TestX:\n    def test_x(self):\n        value = (\n            self\n            .assertEqual(1, 1)\n        )\n", "def test_x():\n    raise ValueError\n", True),
    ("MESSAGE = 'pytest.raises(ValueError)'\n# pytest.raises(ValueError)\ndef test_x():\n    assert True\n", "def test_x():\n    assert True\n", False),
    ("class Local:\n    def raises(self, value): return value\npytest = Local()\npytest.raises(ValueError)\n", "class Local:\n    pass\n", False),
    ("import pytest\ndef test_x(pytest):\n    with pytest.raises(ValueError): raise ValueError\n", "import pytest\ndef test_x(pytest): raise ValueError\n", False),
    ("from pytest import raises\ndef test_x(raises):\n    with raises(ValueError): raise ValueError\n", "from pytest import raises\ndef test_x(raises): raise ValueError\n", False),
    ("from pytest import raises\nif ready: raises = print\nwith raises(ValueError): raise ValueError\n", "raise ValueError\n", True),
    ("import pytest\ntest_x = lambda pytest: pytest.raises(ValueError)\n", "import pytest\ntest_x = lambda pytest: None\n", False),
    ("import pytest\ndef test_x(*pytest): pytest.raises(ValueError)\n", "import pytest\ndef test_x(*pytest): pass\n", False),
    ("import pytest\nvalues = [pytest.raises(ValueError) for pytest in ()]\n", "import pytest\nvalues = []\n", False),
    ("import pytest\ntry: pass\nexcept Exception as pytest: pytest.raises(ValueError)\n", "import pytest\ntry: pass\nexcept Exception: pass\n", False),
    ("from __future__ import annotations\nimport pytest\ndef f(x: (lambda: pytest.raises(ValueError))): pass\n", "from __future__ import annotations\nimport pytest\ndef f(x): pass\n", False),
    ("p = object()\ntry:\n import pytest as p\nexcept Exception: p = object()\nwith p.raises(ValueError): raise ValueError\n", "raise ValueError\n", True),
    ("import pytest\nr, = (pytest.raises,)\nwith r(ValueError): raise ValueError\n", "raise ValueError\n", True),
    ("r = print\nfor x in xs:\n with r(ValueError): raise ValueError\n from pytest import raises as r\n", "raise ValueError\n", True),
    ("import pytest\n[(pytest := object()) for _ in ()]\nwith pytest.raises(ValueError): raise ValueError\n", "raise ValueError\n", True),
])
def test_delta_checks_committed_assertion_constructs(monkeypatch, tmp_path: Path, source: str, replacement: str, blocked: bool) -> None:
    repo = tmp_path / "repo"
    test = repo / "backend/tests/test_sample.py"
    test.parent.mkdir(parents=True)
    test.write_text(source, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Coverage Test"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    base = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, text=True, capture_output=True,
    ).stdout.strip()
    test.write_text(replacement, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "remove assertion"], check=True)
    monkeypatch.setattr(policy, "REPO", repo)
    monkeypatch.chdir(repo / "backend")
    if blocked:
        with pytest.raises(policy.PolicyError, match="deleted_assertion"):
            policy.validate_delta(base, 300, {"backend/tests/test_sample.py"})
    else:
        policy.validate_delta(base, 300, {"backend/tests/test_sample.py"})
    assert Path.cwd() == repo / "backend"


def test_delta_rejects_committed_test_rename(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    old = repo / "backend/tests/test_old.py"
    old.parent.mkdir(parents=True)
    filler = "\n".join(f"VALUE_{index} = {index}" for index in range(30))
    old.write_text(f"import pytest as pt\n{filler}\nwith pt.raises(ValueError):\n    raise ValueError\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Coverage Test"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()
    new = old.with_name("test_new.py")
    subprocess.run(["git", "-C", str(repo), "mv", str(old.relative_to(repo)), str(new.relative_to(repo))], check=True)
    new.write_text(f"{filler}\ndef test_x():\n    raise ValueError\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "rename test"], check=True)
    monkeypatch.setattr(policy, "REPO", repo)
    with pytest.raises(policy.PolicyError, match="test_rename"):
        policy.validate_delta(base, 300, {"backend/tests/test_new.py"})


def test_compute_cli_is_read_only_and_stable(tmp_path: Path) -> None:
    files = {
        item.relative_to(policy.BACKEND).as_posix():
            {"summary": {"covered_lines": 0, "num_statements": 0}}
        for item in (policy.BACKEND / "app").rglob("*.py")
    }
    files[next(iter(files))]["summary"] = {"covered_lines": 2, "num_statements": 3}
    path = write_json(tmp_path / "coverage.json", {"files": files, "totals": {"covered_lines": 2, "num_statements": 3}})
    command = [sys.executable, str(SCRIPTS / "coverage_policy.py"), "--coverage-json", str(path)]
    result = subprocess.run([*command, "--compute-floor"], text=True, capture_output=True, check=False)
    assert (result.returncode, result.stdout, result.stderr) == (0, "66.666666\n", "")
    assert list(tmp_path.iterdir()) == [path]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    assert result.returncode == 2
    assert result.stderr == "coverage-policy: mode_required\n"
