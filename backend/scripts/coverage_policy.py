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
import symtable
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


class Bindings(ast.NodeVisitor):
    def __init__(self, table: symtable.SymbolTable, future_annotations: bool) -> None:
        self.tables, self.child_positions = [table], [0]
        self.scopes, self.types, self.cases = [{}], ["module"], [False]
        self.future_annotations, self.inline_depth = future_annotations, 0
        self.weak, self.raises = False, set()

    def next_child(self) -> symtable.SymbolTable:
        position = self.child_positions[-1]
        if position >= len(self.tables[-1].get_children()):
            raise SyntaxError("missing symbol table")
        return self.tables[-1].get_children()[position]
    def enter(self, node: ast.AST, table_type: str, name: str, initial: dict[str, str]) -> None:
        children, position = self.tables[-1].get_children(), self.child_positions[-1]
        if position >= len(children):
            raise SyntaxError("missing symbol table")
        child = children[position]
        if (child.get_type(), child.get_name(), child.get_lineno()) != (table_type, name, node.lineno):
            raise SyntaxError("symbol table mismatch")
        self.child_positions[-1] += 1
        self.tables.append(child)
        self.child_positions.append(0)
        self.scopes.append(initial)
        self.types.append(table_type)
        self.cases.append(self.cases[-1])
    def leave(self) -> None:
        if self.child_positions[-1] != len(self.tables[-1].get_children()):
            raise SyntaxError("unused symbol table")
        self.tables.pop()
        self.child_positions.pop()
        self.scopes.pop()
        self.types.pop()
        self.cases.pop()
    def put(self, name: str, kind: str, offset: int = 0) -> None:
        try:
            symbol = self.tables[-1].lookup(name)
        except KeyError:
            symbol = None
        if len(self.tables) > 1 and symbol and symbol.is_global():
            self.scopes[0][name] = kind
        elif symbol and symbol.is_nonlocal():
            for index in range(len(self.scopes) - 2, 0, -1):
                if self.types[index] == "function" and name in self.scopes[index]:
                    self.scopes[index][name] = kind
                    return
        else:
            self.scopes[-1 - offset][name] = kind
    def get(self, name: str) -> str:
        for index in range(len(self.scopes) - 1, -1, -1):
            if self.types[index] != "class" or index == len(self.scopes) - 1:
                if name in self.scopes[index]:
                    return self.scopes[index][name]
        return "builtin" if name == "exec" else "local"
    def kind(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return self.get(node.id)
        if isinstance(node, ast.Call) and self.kind(node.func) in {"testcase", "ambiguous"}:
            return "case" if self.kind(node.func) == "testcase" else "ambiguous"
        if isinstance(node, ast.Attribute):
            owner = self.kind(node.value)
            if (owner, node.attr) == ("pytest", "mark"):
                return "mark"
            if owner == "ambiguous" and node.attr in {"mark", "TestCase", "case"}:
                return "ambiguous"
            if owner in {"pytest", "ambiguous"} and node.attr == "raises":
                return "raises"
            if owner == "unittest" and node.attr in {"case", "TestCase"}:
                return "unittest" if node.attr == "case" else "testcase"
            if owner in {"pytest", "unittest", "mark", "ambiguous"} and node.attr in BLOCKED:
                return "blocked"
        return "local"
    def merge(self, states: list[list[dict[str, str]]]) -> None:
        for index, scope in enumerate(self.scopes):
            keys = set().union(*(state[index] for state in states))
            for name in keys:
                values = {state[index].get(name, "local") for state in states}
                scope[name] = values.pop() if len(values) == 1 else "ambiguous"
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
            self.bind_target(target, self.kind(node.value))
    def bind_target(self, node: ast.AST, kind: str) -> None:
        if isinstance(node, ast.Name):
            self.put(node.id, kind)
        elif isinstance(node, ast.Starred):
            self.bind_target(node.value, kind)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for item in node.elts:
                self.bind_target(item, kind)
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self.future_annotations:
            self.visit(node.annotation)
        if node.value:
            self.visit(node.value)
        self.bind_target(node.target, self.kind(node.value) if node.value else "local")
    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        prior = self.kind(node.target)
        self.visit(node.value)
        self.bind_target(node.target, "local" if prior == "local" else "ambiguous")
    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.put(node.target.id, self.kind(node.value), self.inline_depth)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.put(node.id, "local")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.weak |= self.kind(node) in {"blocked", "ambiguous"}
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        before = [scope.copy() for scope in self.scopes]
        for item in node.body:
            self.visit(item)
        left = [scope.copy() for scope in self.scopes]
        self.scopes = [scope.copy() for scope in before]
        for item in node.orelse:
            self.visit(item)
        self.merge([left, self.scopes])

    def run_path(self, items: list[ast.AST], start: list[dict[str, str]]) -> list[dict[str, str]]:
        self.scopes = [scope.copy() for scope in start]
        for item in items:
            self.visit(item)
        return [scope.copy() for scope in self.scopes]

    def visit_For(self, node: ast.For) -> None:
        self.visit(node.iter)
        before = [scope.copy() for scope in self.scopes]
        body = [node.target, *node.body]
        self.merge([self.run_path(node.orelse, before), self.run_path([*body, *node.orelse], before), self.run_path(body, before)])

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        before = [scope.copy() for scope in self.scopes]
        self.merge([self.run_path(node.orelse, before), self.run_path([*node.body, *node.orelse], before), self.run_path(node.body, before)])

    def visit_Try(self, node: ast.Try) -> None:
        before = [scope.copy() for scope in self.scopes]
        progress = [before]
        for item in node.body:
            progress.append(self.run_path([item], progress[-1]))
        states = [self.run_path(node.orelse, progress[-1])]
        states.extend(self.run_path([handler], incoming) for handler in node.handlers for incoming in progress)
        self.scopes = [scope.copy() for scope in before]
        self.merge(states)
        for item in node.finalbody:
            self.visit(item)

    visit_TryStar = visit_Try

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        before = [scope.copy() for scope in self.scopes]
        paths = [[case.pattern, *([case.guard] if case.guard else []), *case.body] for case in node.cases]
        self.merge([before, *(self.run_path(path, before) for path in paths)])

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name:
            self.put(node.name, "local")
        if node.pattern:
            self.visit(node.pattern)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name:
            self.put(node.name, "local")

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest:
            self.put(node.rest, "local")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self.put(node.name, "local")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        kind = self.kind(node.func)
        self.weak |= kind in {"blocked", "ambiguous"} or kind == "builtin" and isinstance(node.func, ast.Name) and node.func.id == "exec"
        if kind in {"raises", "ambiguous"}:
            self.raises.add((node.lineno, node.end_lineno))
        if isinstance(node.func, ast.Attribute) and node.func.attr == "skipTest":
            value = node.func.value
            self.weak |= self.kind(value) in {"case", "ambiguous"} or self.cases[-1] and (isinstance(value, ast.Name) and value.id == "self" or isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "super")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for item in (*node.args.defaults, *node.args.kw_defaults, *node.decorator_list):
            if item:
                self.visit(item)
        if not self.future_annotations:
            for item in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                if item.annotation:
                    self.visit(item.annotation)
            if node.returns:
                self.visit(node.returns)
        self.weak |= any(self.kind(item) in {"blocked", "ambiguous"} for item in node.decorator_list)
        self.put(node.name, "local")
        child = self.next_child()
        self.enter(node, "function", node.name, {name: "local" for name in child.get_locals()})
        for item in node.body:
            self.visit(item)
        self.leave()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for item in (*node.args.defaults, *node.args.kw_defaults):
            if item:
                self.visit(item)
        child = self.next_child()
        self.enter(node, "function", "lambda", {name: "local" for name in child.get_locals()})
        self.visit(node.body)
        self.leave()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for item in (*node.decorator_list, *node.bases, *(keyword.value for keyword in node.keywords)):
            self.visit(item)
        self.weak |= any(self.kind(item) in {"blocked", "ambiguous"} for item in node.decorator_list)
        is_case = any(self.kind(base) == "testcase" for base in node.bases)
        self.put(node.name, "testcase" if is_case else "local")
        self.enter(node, "class", node.name, {})
        self.cases[-1] = is_case
        for item in node.body:
            self.visit(item)
        self.leave()

    def visit_comprehension_scope(self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp) -> None:
        generators = node.generators
        self.visit(generators[0].iter)
        names = {item.id for generator in generators for item in ast.walk(generator.target) if isinstance(item, ast.Name)}
        expected = {ast.GeneratorExp: "genexpr", ast.ListComp: "listcomp", ast.SetComp: "setcomp", ast.DictComp: "dictcomp"}[type(node)]
        has_table = isinstance(node, ast.GeneratorExp)
        if has_table:
            child = self.next_child()
            self.enter(node, "function", expected, {name: "local" for name in child.get_locals()})
        else:
            self.scopes.append({name: "local" for name in names})
            self.types.append("function")
            self.cases.append(self.cases[-1])
            self.inline_depth += 1
        for generator in generators:
            if generator is not generators[0]:
                self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        for value in ((node.key, node.value) if isinstance(node, ast.DictComp) else (node.elt,)):
            self.visit(value)
        if has_table:
            self.leave()
        else:
            self.inline_depth -= 1
            self.scopes.pop()
            self.types.pop()
            self.cases.pop()
    visit_ListComp = visit_comprehension_scope
    visit_SetComp = visit_comprehension_scope
    visit_DictComp = visit_comprehension_scope
    visit_GeneratorExp = visit_comprehension_scope


def analyze_python(source: str) -> tuple[ast.Module, Bindings]:
    tree = ast.parse(source)
    future_annotations = any(isinstance(node, ast.ImportFrom) and node.module == "__future__" and any(alias.name == "annotations" for alias in node.names) for node in tree.body)
    bindings = Bindings(symtable.symtable(source, "<test>", "exec"), future_annotations)
    bindings.visit(tree)
    if bindings.child_positions != [len(bindings.tables[0].get_children())]:
        raise SyntaxError("unused symbol table")
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
