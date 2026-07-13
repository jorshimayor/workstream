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


BLOCKED = {"skip", "skipif", "skipIf", "skipUnless", "xfail", "expectedFailure", "importorskip", "SkipTest"}


def scope_bindings(nodes: list[ast.stmt]) -> tuple[set[str], dict[str, str]]:
    names, routes = set(), {}
    def collect(node: ast.AST) -> None:
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            routes.update({name: type(node).__name__.lower() for name in node.names})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        else:
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names.update(alias.asname or alias.name.split(".", 1)[0] for alias in node.names)
            for child in ast.iter_child_nodes(node):
                collect(child)
    for node in nodes:
        collect(node)
    return names, routes


class Bindings(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scopes, self.types, self.cases, self.routes = [{}], ["module"], [False], [{}]
        self.weak, self.raises = False, set()
    def put(self, name: str, kind: str) -> None:
        route = self.routes[-1].get(name)
        if route == "global":
            self.scopes[0][name] = kind
        elif route == "nonlocal":
            for index in range(len(self.scopes) - 2, 0, -1):
                if self.types[index] == "function" and name in self.scopes[index]:
                    self.scopes[index][name] = kind
                    return
        else:
            self.scopes[-1][name] = kind
    def get(self, name: str) -> str:
        for index in range(len(self.scopes) - 1, -1, -1):
            if self.types[index] != "class" or "function" not in self.types[index + 1:]:
                if name in self.scopes[index]:
                    return self.scopes[index][name]
        return "local"
    def kind(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return self.get(node.id)
        if isinstance(node, ast.Call) and self.kind(node.func) == "testcase":
            return "case"
        if isinstance(node, ast.Attribute):
            owner = self.kind(node.value)
            if (owner, node.attr) == ("pytest", "mark"):
                return "mark"
            if owner in {"pytest", "ambiguous"} and node.attr == "raises":
                return "raises"
            if owner == "unittest" and node.attr in {"case", "TestCase"}:
                return "unittest" if node.attr == "case" else "testcase"
            if owner in {"pytest", "unittest", "mark", "ambiguous"} and node.attr in BLOCKED:
                return "blocked"
        return "local"
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            self.put(alias.asname or root, root if root in {"pytest", "unittest"} else "local")
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".", 1)[0]
        for alias in node.names:
            name = alias.asname or alias.name
            if alias.name == "*" and root in {"pytest", "unittest"}:
                self.weak = True
            elif root == "pytest":
                self.put(name, {"mark": "mark", "raises": "raises"}.get(alias.name, "blocked" if alias.name in BLOCKED else "local"))
            elif root == "unittest":
                self.put(name, "testcase" if alias.name == "TestCase" else "blocked" if alias.name in BLOCKED else "local")
    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            for item in ast.walk(target):
                if isinstance(item, ast.Name):
                    self.put(item.id, self.kind(node.value))
    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.put(node.id, "local")
    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        before = self.scopes[-1].copy()
        for item in node.body:
            self.visit(item)
        left = self.scopes[-1].copy()
        self.scopes[-1] = before.copy()
        for item in node.orelse:
            self.visit(item)
        right = self.scopes[-1]
        self.scopes[-1] = {name: left.get(name, before.get(name, "local")) if left.get(name, before.get(name)) == right.get(name, before.get(name)) else "ambiguous" for name in before.keys() | left.keys() | right.keys()}
    def visit_Call(self, node: ast.Call) -> None:
        kind = self.kind(node.func)
        self.weak |= kind in {"blocked", "ambiguous"} or isinstance(node.func, ast.Name) and node.func.id == "exec"
        if kind in {"raises", "ambiguous"}:
            self.raises.add((node.lineno, node.end_lineno))
        if isinstance(node.func, ast.Attribute) and node.func.attr == "skipTest":
            value = node.func.value
            self.weak |= self.kind(value) == "case" or self.cases[-1] and (isinstance(value, ast.Name) and value.id == "self" or isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "super")
        self.generic_visit(node)
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for item in (*node.decorator_list, *node.args.defaults, *node.args.kw_defaults):
            if item:
                self.visit(item)
        self.weak |= any(self.kind(item) in {"blocked", "ambiguous"} for item in node.decorator_list)
        self.put(node.name, "local")
        args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
        names, routes = scope_bindings(node.body)
        self.scopes.append({name: "local" for name in (names | {arg.arg for arg in args}) - routes.keys()})
        self.types.append("function")
        self.cases.append(self.cases[-1])
        self.routes.append(routes)
        for item in node.body:
            self.visit(item)
        self.scopes.pop()
        self.types.pop()
        self.cases.pop()
        self.routes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for item in (*node.decorator_list, *node.bases):
            self.visit(item)
        self.weak |= any(self.kind(item) in {"blocked", "ambiguous"} for item in node.decorator_list)
        is_case = any(self.kind(base) == "testcase" for base in node.bases)
        self.put(node.name, "testcase" if is_case else "local")
        self.scopes.append({})
        self.types.append("class")
        self.cases.append(is_case)
        self.routes.append({})
        for item in node.body:
            self.visit(item)
        self.scopes.pop()
        self.types.pop()
        self.cases.pop()
        self.routes.pop()


def analyze_python(source: str) -> tuple[ast.Module, Bindings]:
    tree, bindings = ast.parse(source), Bindings()
    bindings.visit(tree)
    return tree, bindings


def weak_python(path: Path) -> bool:
    try:
        return analyze_python(path.read_text(encoding="utf-8"))[1].weak
    except (OSError, SyntaxError):
        return True


def has_deleted_assertion(diff: str, base_source: str) -> bool:
    deleted, old_line = set(), 0
    for line in diff.splitlines():
        match = re.match(r"^@@ -(\d+)(?:,\d+)? \+", line)
        if match:
            old_line = int(match.group(1))
        elif line.startswith("-") and not line.startswith("---"):
            deleted.add(old_line)
            old_line += 1
        elif not line.startswith("+"):
            old_line += 1
    try:
        tree, analysis = analyze_python(base_source)
    except SyntaxError:
        return bool(deleted)
    for node in ast.walk(tree):
        assertion = isinstance(node, ast.Assert)
        if isinstance(node, ast.Call):
            assertion = (node.lineno, node.end_lineno) in analysis.raises or (isinstance(node.func, ast.Attribute) and ast.unparse(node.func.value) == "self" and node.func.attr.startswith("assert"))
        if assertion and deleted.intersection(range(node.lineno, node.end_lineno + 1)):
            return True
    return False


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
