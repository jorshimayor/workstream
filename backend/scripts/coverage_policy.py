#!/usr/bin/env python3
"""Read-only core for Workstream's complete-backend coverage policy."""

from __future__ import annotations

import argparse
import ast
from decimal import Decimal, InvalidOperation
from io import StringIO
import json
import os
from pathlib import Path
import re
import sys
import tokenize
import tomllib

from coverage.config import DEFAULT_EXCLUDE
from run_isolated_tests import NAME_RE

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent
sys.path.insert(0, str(REPO / "scripts"))
from workstream_agent_gate import changed_files, diff_text, maybe_run, numstat  # noqa: E402

SHA_RE = re.compile(r"[a-f0-9]{40}")
DECIMAL_RE = re.compile(r"\d+\.\d{6}")
VERSION_RE = re.compile(r"[0-9]+(?:\.[0-9]+){1,3}(?:[a-z0-9.+-]{0,20})?")
ALEMBIC_RE = re.compile(r"[a-z0-9_]{1,64}")
EVIDENCE_KEYS = set(
    "schema_version base_merge_sha measured_tree_sha covered_lines num_statements "
    "measured_percent configured_floor minimum_milestone python_version coverage_version "
    "pytest_cov_version database_name alembic_head".split()
)
GLOBAL_MEMORY = {".agent-loop/LOOP_STATE.md", ".agent-loop/REVIEW_LOG.md", ".agent-loop/WORK_QUEUE.md"}
QUAL_MEMORY = ".agent-loop/initiatives/WS-QUAL-001-backend-coverage-floor/"


class PolicyError(RuntimeError):
    """A stable coverage-policy violation."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise PolicyError(code)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError("invalid_json") from exc
    require(isinstance(data, dict), "invalid_json")
    return data


def six_place_percent(covered: int, statements: int) -> str:
    scaled = covered * 100_000_000 // statements
    return f"{scaled // 1_000_000}.{scaled % 1_000_000:06d}"


def coverage_counts(path: Path, root: Path = BACKEND) -> tuple[int, int]:
    data = load_json(path)
    totals, files = data.get("totals"), data.get("files")
    require(isinstance(totals, dict) and isinstance(files, dict), "invalid_coverage")
    covered, statements = totals.get("covered_lines"), totals.get("num_statements")
    require(type(covered) is int and type(statements) is int, "invalid_coverage")
    require(statements > 0 and 0 <= covered <= statements, "invalid_coverage")
    expected = {item.relative_to(root).as_posix() for item in (root / "app").rglob("*.py")}
    require(set(files) == expected, "application_inventory_mismatch")
    sums = [0, 0]
    for value in files.values():
        summary = value.get("summary") if isinstance(value, dict) else None
        require(isinstance(summary, dict), "invalid_file_coverage")
        pair = summary.get("covered_lines"), summary.get("num_statements")
        require(all(type(item) is int for item in pair) and 0 <= pair[0] <= pair[1], "invalid_file_coverage")
        sums = [sums[index] + pair[index] for index in range(2)]
    require(tuple(sums) == (covered, statements), "coverage_totals_mismatch")
    return covered, statements


def config_floor(path: Path) -> Decimal:
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
        coverage = config["tool"]["coverage"]
        require(isinstance(coverage, dict), "invalid_coverage_config")
        report = coverage["report"]
        run = coverage.get("run", {})
        dev = config["project"]["optional-dependencies"]["dev"]
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        raise PolicyError("invalid_coverage_config") from exc
    require(isinstance(report, dict) and isinstance(run, dict), "invalid_coverage_config")
    require(isinstance(dev, list) and all(isinstance(item, str) for item in dev), "invalid_coverage_config")
    pins = [item for item in dev if re.sub(r"[-_.]+", "-", re.split(r"[<>=!~\s;\[]", item.strip(), 1)[0].lower()) == "pytest-cov"]
    require(pins == ["pytest-cov==7.1.0"], "pytest_cov_pin_missing")
    forbidden = {"omit", "include", "source", "source_pkgs", "source_dirs", "exclude_lines", "exclude_also"}
    require(not forbidden.intersection(run), "coverage_exclusion_config")
    require(not forbidden.intersection(report), "coverage_exclusion_config")
    require(report.get("precision") == 6, "coverage_precision_invalid")
    try:
        raw = report["fail_under"]
        require(type(raw) in {int, float}, "coverage_floor_invalid")
        value = Decimal(str(raw))
        floor = value.quantize(Decimal("0.000001"))
        require(value.is_finite() and value == floor, "coverage_floor_invalid")
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise PolicyError("coverage_floor_invalid") from exc
    require(Decimal("0") <= floor <= Decimal("100"), "coverage_floor_invalid")
    return floor


def validate_sources(root: Path) -> None:
    for path in (root / "app").rglob("*.py"):
        tokens = tokenize.generate_tokens(StringIO(path.read_text(encoding="utf-8")).readline)
        require(not any(token.type == tokenize.COMMENT and re.search(DEFAULT_EXCLUDE[0], token.string) for token in tokens), "coverage_pragma")


def evidence_data(data: dict, expected_head: str) -> dict:
    require(set(data) == EVIDENCE_KEYS and type(data.get("schema_version")) is int and data["schema_version"] == 1, "evidence_schema_invalid")
    for key in ("base_merge_sha", "measured_tree_sha"):
        require(isinstance(data.get(key), str) and SHA_RE.fullmatch(data[key]), "evidence_sha_invalid")
    covered, statements = data.get("covered_lines"), data.get("num_statements")
    require(type(covered) is int and type(statements) is int, "evidence_counts_invalid")
    require(statements > 0 and 0 <= covered <= statements, "evidence_counts_invalid")
    for key in ("measured_percent", "configured_floor", "minimum_milestone"):
        require(isinstance(data.get(key), str) and DECIMAL_RE.fullmatch(data[key]), "evidence_decimal_invalid")
        require(Decimal("0") <= Decimal(data[key]) <= Decimal("100"), "evidence_decimal_invalid")
    require(data["measured_percent"] == six_place_percent(covered, statements), "evidence_percent_invalid")
    require(isinstance(data.get("database_name"), str) and NAME_RE.fullmatch(data["database_name"]), "evidence_database_invalid")
    require(ALEMBIC_RE.fullmatch(expected_head) and data.get("alembic_head") == expected_head, "evidence_alembic_invalid")
    for key in ("python_version", "coverage_version", "pytest_cov_version"):
        require(isinstance(data.get(key), str) and VERSION_RE.fullmatch(data[key]), "evidence_version_invalid")
    serialized = json.dumps(data).lower()
    require(not any(token in serialized for token in ("://", "password", "secret", "workstream_role_")), "evidence_secret")
    return data


def canonical_evidence(path: Path, expected_head: str) -> dict:
    data = evidence_data(load_json(path), expected_head)
    require(path.read_text(encoding="utf-8") == json.dumps(data, indent=2, sort_keys=True) + "\n", "evidence_not_canonical")
    return data


def runner_metadata(path: Path, expected_tree: str, expected_head: str) -> dict:
    data = load_json(path)
    require(set(data) == {"schema_version", "database_name", "alembic_head", "tree_sha"}, "metadata_invalid")
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1, "metadata_invalid")
    require(isinstance(data.get("database_name"), str) and NAME_RE.fullmatch(data["database_name"]), "metadata_invalid")
    require(ALEMBIC_RE.fullmatch(expected_head) and data.get("alembic_head") == expected_head, "metadata_alembic_mismatch")
    require(SHA_RE.fullmatch(expected_tree) and data.get("tree_sha") == expected_tree, "metadata_tree_mismatch")
    require("://" not in json.dumps(data), "metadata_secret")
    return data


def weak_python(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return True
    blocked = {"skip", "skipif", "skipIf", "skipUnless", "xfail", "expectedFailure", "importorskip", "skipTest", "SkipTest"}
    modules, marks, names = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.asname or alias.name.split(".", 1)[0] for alias in node.names if alias.name.split(".", 1)[0] in {"pytest", "unittest"})
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".", 1)[0] in {"pytest", "unittest"}:
            for alias in node.names:
                target = alias.asname or alias.name
                if alias.name == "mark":
                    marks.add(target)
                elif alias.name in blocked:
                    names.add(target)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in names:
            return True
        if isinstance(node, ast.Attribute) and node.attr in blocked:
            root = ast.unparse(node.value).split(".", 1)[0]
            if (node.attr == "skipTest" and root == "self") or root in modules | marks:
                return True
    return False


def raises_aliases(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"pytest.raises"}
    aliases = {"pytest.raises"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            aliases.update(f"{alias.asname}.raises" for alias in node.names if alias.name == "pytest" and alias.asname)
        if isinstance(node, ast.ImportFrom) and node.module == "pytest":
            aliases.update(alias.asname or alias.name for alias in node.names if alias.name == "raises")
    return aliases


def has_deleted_assertion(diff: str, base_source: str) -> bool:
    deleted = [line for line in diff.splitlines() if line.startswith("-") and not line.startswith("---")]
    targets = "|".join(re.escape(target) for target in sorted(raises_aliases(base_source)))
    raises = re.compile(rf"^-.*(?<![\w.])(?:{targets})\s*\(")
    return any(line_has_assertion(line[1:]) or raises.search(line) for line in deleted)


def line_has_assertion(source: str) -> bool:
    tokens = []
    try:
        tokens.extend(tokenize.generate_tokens(StringIO(source).readline))
    except tokenize.TokenError:
        pass
    values = [token.string for token in tokens if token.type not in {tokenize.STRING, tokenize.COMMENT}]
    return "assert" in values or any(index > 0 and values[index - 1] == "self" and values[index] == "." and values[index + 1].startswith("assert") and values[index + 2] == "(" for index in range(len(values) - 2))


def approved_memory(path: str) -> bool:
    return path in GLOBAL_MEMORY or path.startswith(QUAL_MEMORY)


def has_test_rename(statuses: str) -> bool:
    return any(parts[0].startswith("R") and any(path.startswith("backend/tests/") and path.endswith(".py") for path in parts[1:]) for parts in (line.split("\t") for line in statuses.splitlines()) if parts)


def validate_delta(base: str, max_lines: int, allowed: set[str]) -> None:
    previous = Path.cwd()
    try:
        os.chdir(REPO)
        files = changed_files(base, "HEAD")
        _, _, rows = numstat(base, "HEAD")
        tests = [path for path in files if path.startswith("backend/tests/") and path.endswith(".py")]
        statuses = "\n".join(
            (maybe_run(["git", "diff", "--name-status", "--find-renames", f"{base}...HEAD"]),
             maybe_run(["git", "diff", "--name-status", "--find-renames", "--cached"]),
             maybe_run(["git", "diff", "--name-status", "--find-renames"]))
        )
        diffs = {path: diff_text(base, "HEAD", [path]) for path in tests}
        sources = {path: maybe_run(["git", "show", f"{base}:{path}"]) for path in tests}
    finally:
        os.chdir(previous)
    require(all(path in allowed or approved_memory(path) for path in files), "scope_violation")
    require(not has_test_rename(statuses), "test_rename")
    require(sum(add + delete for path, add, delete in rows if not approved_memory(path)) <= max_lines, "implementation_size_exceeded")
    require(not any(weak_python(REPO / path) for path in tests), "test_skip_or_xfail")
    require(not any(has_deleted_assertion(diffs[path], sources[path]) for path in tests), "deleted_assertion")


def main() -> int:
    """Compute a candidate floor without configuring policy or writing evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-json", required=True, type=Path)
    parser.add_argument("--compute-floor", action="store_true")
    args = parser.parse_args()
    try:
        require(args.compute_floor, "mode_required")
        print(six_place_percent(*coverage_counts(args.coverage_json)))
    except (PolicyError, OSError, ValueError) as exc:
        code = exc.args[0] if isinstance(exc, PolicyError) else "policy_runtime_error"
        print(f"coverage-policy: {code}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
