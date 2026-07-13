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
EAGER_ITERATORS = {"all", "any", "bytearray", "bytes", "dict", "frozenset", "list", "max", "min", "next", "set", "sorted", "sum", "tuple"}
LAZY_ITERATORS = {"enumerate", "filter", "iter", "map", "reversed", "zip"}


class Bindings(ast.NodeVisitor):
    def __init__(self, table: symtable.SymbolTable, future_annotations: bool) -> None:
        self.tables, self.child_positions = [table], [0]
        self.scopes, self.types, self.cases = [{}], ["module"], [False]
        self.future_annotations, self.inline_depths, self.comp_writes = future_annotations, [0], []
        self.weak, self.raises, self.suppressed, self.consume_genexpr = False, set(), 0, 0

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
        self.inline_depths.append(0)
    def leave(self) -> None:
        if self.child_positions[-1] != len(self.tables[-1].get_children()):
            raise SyntaxError("unused symbol table")
        self.tables.pop()
        self.child_positions.pop()
        self.scopes.pop()
        self.types.pop()
        self.cases.pop()
        self.inline_depths.pop()
    def put(self, name: str, kind: str, offset: int = 0) -> None:
        if self.suppressed:
            return
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
    def builtin(self, node: ast.AST, names: set[str]) -> bool:
        if not isinstance(node, ast.Name) or node.id not in names:
            return False
        try:
            symbol = self.tables[-1].lookup(node.id)
        except KeyError:
            return True
        return not (symbol.is_assigned() or symbol.is_imported() or symbol.is_parameter())
    def visit_iterated(self, node: ast.AST) -> None:
        if isinstance(node, ast.GeneratorExp):
            previous, self.consume_genexpr = self.consume_genexpr, 1
            self.visit(node)
            self.consume_genexpr = previous
        elif isinstance(node, ast.Call) and self.builtin(node.func, LAZY_ITERATORS):
            self.visit(node.func)
            for index, argument in enumerate(node.args):
                (self.visit if node.func.id == "map" and index == 0 or node.func.id == "filter" and index == 0 else self.visit_iterated)(argument)
            for keyword in node.keywords:
                self.visit(keyword.value)
        else:
            self.visit(node)
    def kind(self, node: ast.AST, bindings: dict[str, str] | None = None) -> str:
        if isinstance(node, ast.Name):
            return (bindings or {}).get(node.id, self.get(node.id))
        if isinstance(node, ast.Starred):
            return self.kind(node.value, bindings)
        if isinstance(node, ast.IfExp):
            kinds = {self.kind(node.body, bindings), self.kind(node.orelse, bindings)}
            return kinds.pop() if len(kinds) == 1 else "ambiguous"
        if isinstance(node, ast.BoolOp):
            kinds = {self.kind(item, bindings) for item in node.values}
            return kinds.pop() if len(kinds) == 1 else "ambiguous"
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            kinds = {self.kind(item, bindings) for item in node.elts}
            return "local" if not kinds else kinds.pop() if len(kinds) == 1 else "ambiguous"
        if isinstance(node, ast.Dict):
            kinds = {self.kind(item or value, bindings) for item, value in zip(node.keys, node.values, strict=True)}
            return "local" if not kinds else kinds.pop() if len(kinds) == 1 else "ambiguous"
        if isinstance(node, ast.Call) and self.kind(node.func, bindings) in {"testcase", "ambiguous"}:
            return "case" if self.kind(node.func, bindings) == "testcase" else "ambiguous"
        if isinstance(node, ast.Attribute):
            owner = self.kind(node.value, bindings)
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
        (self.visit_iterated if any(isinstance(target, (ast.Tuple, ast.List)) for target in node.targets) else self.visit)(node.value)
        for target in node.targets:
            self.assign_target(target, node.value)
    def target_names(self, node: ast.AST) -> set[str]:
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, ast.Starred):
            return self.target_names(node.value)
        if isinstance(node, (ast.Tuple, ast.List)):
            return set().union(*(self.target_names(item) for item in node.elts))
        return set()
    def assign_target(self, target: ast.AST, value: ast.AST, bindings: dict[str, str] | None = None) -> None:
        if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)) and len(target.elts) == len(value.elts):
            for child, item in zip(target.elts, value.elts, strict=True):
                self.assign_target(child, item, bindings)
        else:
            self.bind_target(target, self.kind(value, bindings))
    def bind_target(self, node: ast.AST, kind: str, evaluate: bool = True) -> None:
        if isinstance(node, ast.Name):
            self.put(node.id, kind)
        elif isinstance(node, ast.Starred):
            self.bind_target(node.value, kind, evaluate)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for item in node.elts:
                self.bind_target(item, kind, evaluate)
        elif evaluate and isinstance(node, ast.Attribute):
            self.visit(node.value)
        elif evaluate and isinstance(node, ast.Subscript):
            self.visit(node.value)
            self.visit(node.slice)
    def target_bindings(self, target: ast.AST, value: ast.AST, bindings: dict[str, str]) -> None:
        if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)) and len(target.elts) == len(value.elts):
            for child, item in zip(target.elts, value.elts, strict=True):
                self.target_bindings(child, item, bindings)
        else:
            for name in self.target_names(target):
                bindings[name] = self.kind(value, bindings)
    def empty_iterable(self, node: ast.AST) -> bool:
        return isinstance(node, (ast.Tuple, ast.List, ast.Set)) and not node.elts or isinstance(node, ast.Dict) and not node.keys
    def element_provenance(self, node: ast.AST, bindings: dict[str, str] | None = None) -> tuple[ast.AST, dict[str, str]]:
        environment = dict(bindings or {})
        for item in ast.walk(node):
            if isinstance(item, ast.Name):
                environment.setdefault(item.id, self.get(item.id))
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and len(node.elts) == 1:
            return node.elts[0], environment
        if isinstance(node, ast.Dict) and len(node.keys) == 1 and node.keys[0]:
            return node.keys[0], environment
        if isinstance(node, ast.Dict) and len(node.keys) == 1 and node.keys[0] is None:
            return self.element_provenance(node.values[0], environment)
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for generator in node.generators:
                if self.empty_iterable(generator.iter):
                    return ast.Constant(None), environment
                value, source = self.element_provenance(generator.iter, environment)
                self.target_bindings(generator.target, value, source)
                environment.update(source)
            return (node.key if isinstance(node, ast.DictComp) else node.elt), environment
        return node, environment
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value:
            self.visit(node.value)
        self.assign_target(node.target, node.value) if node.value else self.bind_target(node.target, "local")
        if not self.future_annotations and self.types[-1] != "function":
            self.visit(node.annotation)
    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        prior = self.kind(node.target)
        self.bind_target(node.target, prior)
        self.visit(node.value)
        self.bind_target(node.target, "local" if prior == "local" else "ambiguous", False)
    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.put(node.target.id, self.kind(node.value), self.inline_depths[-1])
            if self.inline_depths[-1]:
                for writes in self.comp_writes:
                    writes.add(node.target.id)
    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.put(node.id, "local")
    def visit_Attribute(self, node: ast.Attribute) -> None:
        if not self.suppressed:
            self.weak |= self.kind(node) in {"blocked", "ambiguous"}
        self.generic_visit(node)
    def visit_Starred(self, node: ast.Starred) -> None:
        (self.visit_iterated if isinstance(node.ctx, ast.Load) else self.visit)(node.value)
    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self.visit_iterated(node.value)
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
    def state(self) -> list[dict[str, str]]:
        return [scope.copy() for scope in self.scopes]
    def join(self, states: list[list[dict[str, str]]]) -> None:
        self.scopes = [scope.copy() for scope in states[0]]
        self.merge(states)
    def loop_summary(self, nodes: list[ast.stmt]) -> set[str]:
        bindings: dict[str, str] = {}
        def record_kind(name: str, kind: str) -> None:
            previous = bindings.get(name, self.get(name))
            if kind != previous:
                bindings[name] = kind if previous == "local" and kind != "local" else "ambiguous"
        def record(target: ast.AST, value: ast.AST) -> None:
            if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)) and len(target.elts) == len(value.elts):
                for child, item in zip(target.elts, value.elts, strict=True):
                    record(child, item)
                return
            kind = self.kind(value, bindings)
            for name in self.target_names(target):
                record_kind(name, kind)
        def inspect_comp(expression: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp, consume: bool) -> None:
            for generator in expression.generators:
                inspect(generator.iter)
                if self.empty_iterable(generator.iter):
                    return
                if consume:
                    for condition in generator.ifs:
                        inspect(condition)
            if consume:
                for value in ((expression.key, expression.value) if isinstance(expression, ast.DictComp) else (expression.elt,)):
                    inspect(value)
        def inspect_iterated(node: ast.AST) -> None:
            if isinstance(node, ast.GeneratorExp):
                inspect_comp(node, True)
            elif isinstance(node, ast.Call) and self.builtin(node.func, LAZY_ITERATORS):
                for index, argument in enumerate(node.args):
                    (inspect if node.func.id in {"map", "filter"} and index == 0 else inspect_iterated)(argument)
            else:
                inspect(node)
        def inspect(node: ast.AST) -> None:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for item in (*node.args.defaults, *node.args.kw_defaults, *node.decorator_list):
                    if item:
                        inspect(item)
                if not self.future_annotations:
                    for item in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                        if item.annotation:
                            inspect(item.annotation)
                    if node.returns:
                        inspect(node.returns)
                return
            if isinstance(node, ast.Lambda):
                for item in (*node.args.defaults, *node.args.kw_defaults):
                    if item:
                        inspect(item)
                return
            if isinstance(node, ast.ClassDef):
                for item in (*node.decorator_list, *node.bases, *(keyword.value for keyword in node.keywords)):
                    inspect(item)
                if any(self.kind(base, bindings) in {"testcase", "ambiguous"} for base in node.bases):
                    record_kind(node.name, "testcase")
                def declarations(items: list[ast.stmt]) -> set[str]:
                    names: set[str] = set()
                    def collect(item: ast.AST) -> None:
                        if isinstance(item, ast.Global):
                            names.update(item.names)
                        elif not isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                            for child in ast.iter_child_nodes(item):
                                collect(child)
                    for item in items:
                        collect(item)
                    return names
                globals_, state = declarations(node.body), {name: bindings.get(name, self.get(name)) for name in declarations(node.body)}
                def set_target(target: ast.AST, value: ast.AST, current: dict[str, str]) -> None:
                    kind = self.kind(value, {**bindings, **current})
                    for name in self.target_names(target) & globals_:
                        current[name] = kind
                def transfer(items: list[ast.stmt], current: dict[str, str]) -> dict[str, str]:
                    for item in items:
                        if isinstance(item, ast.ClassDef):
                            inspect(item)
                            current.update({name: bindings.get(name, current[name]) for name in globals_})
                        elif isinstance(item, ast.Assign):
                            inspect(item.value)
                            for target in item.targets:
                                set_target(target, item.value, current)
                        elif isinstance(item, (ast.AnnAssign, ast.NamedExpr)) and item.value:
                            inspect(item.value)
                            set_target(item.target, item.value, current)
                        elif isinstance(item, ast.Import):
                            for alias in item.names:
                                name, root = alias.asname or alias.name.split(".", 1)[0], alias.name.split(".", 1)[0]
                                if name in globals_:
                                    current[name] = root if root in {"pytest", "unittest"} else "local"
                        elif isinstance(item, ast.ImportFrom):
                            root = (item.module or "").split(".", 1)[0]
                            for alias in item.names:
                                name = alias.asname or alias.name
                                if name in globals_:
                                    current[name] = ({"mark": "mark", "raises": "raises"}.get(alias.name, "blocked" if alias.name in BLOCKED else "local") if root == "pytest" else "testcase" if root == "unittest" and alias.name == "TestCase" else "blocked" if root == "unittest" and alias.name in BLOCKED else "local")
                        elif isinstance(item, ast.AugAssign) and self.target_names(item.target) & globals_:
                            inspect(item.value)
                            for name in self.target_names(item.target) & globals_:
                                current[name] = "local" if current[name] == self.kind(item.value, {**bindings, **current}) == "local" else "ambiguous"
                        elif isinstance(item, ast.If):
                            inspect(item.test)
                            left, right = transfer(item.body, current.copy()), transfer(item.orelse, current.copy())
                            current = {name: left[name] if left[name] == right[name] else "ambiguous" for name in globals_}
                        elif isinstance(item, (ast.For, ast.AsyncFor, ast.While)):
                            inspect(item.iter if isinstance(item, (ast.For, ast.AsyncFor)) else item.test)
                            body = transfer(item.body, current.copy())
                            current = {name: current[name] if current[name] == body[name] else "ambiguous" for name in globals_}
                            current = transfer(item.orelse, current)
                        elif isinstance(item, (ast.Try, ast.TryStar)):
                            success = transfer(item.orelse, transfer(item.body, current.copy()))
                            states = [success, current, *(transfer(handler.body, current.copy()) for handler in item.handlers)]
                            current = {name: states[0][name] if all(state[name] == states[0][name] for state in states) else "ambiguous" for name in globals_}
                            current = transfer(item.finalbody, current)
                        elif isinstance(item, (ast.With, ast.AsyncWith)):
                            for context in item.items:
                                inspect(context.context_expr)
                            current = transfer(item.body, current)
                        elif isinstance(item, ast.Match):
                            inspect(item.subject)
                            states = [current, *(transfer(case.body, current.copy()) for case in item.cases)]
                            current = {name: states[0][name] if all(state[name] == states[0][name] for state in states) else "ambiguous" for name in globals_}
                        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            inspect(item)
                        else:
                            for child in ast.iter_child_nodes(item):
                                if not isinstance(child, ast.stmt):
                                    inspect(child)
                    return current
                state = transfer(node.body, state)
                for name, kind in state.items():
                    record_kind(name, kind)
                return
            if isinstance(node, ast.Call):
                for argument in node.args:
                    expression = argument.value if isinstance(argument, ast.Starred) else argument
                    if self.builtin(node.func, EAGER_ITERATORS) or isinstance(argument, ast.Starred):
                        inspect_iterated(expression)
            if isinstance(node, (ast.For, ast.AsyncFor)):
                inspect_iterated(node.iter)
            if isinstance(node, (ast.Starred, ast.YieldFrom)):
                inspect_iterated(node.value)
                return
            if isinstance(node, ast.GeneratorExp):
                inspect_comp(node, False)
                return
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
                inspect_comp(node, True)
                return
            if isinstance(node, ast.AnnAssign) and self.types[-1] == "function":
                if node.value:
                    record(node.target, node.value)
                    inspect(node.value)
                return
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in {"pytest", "unittest"}:
                        record_kind(alias.asname or root, root)
            elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".", 1)[0] in {"pytest", "unittest"}:
                for alias in node.names:
                    kind = {"mark": "mark", "raises": "raises", "TestCase": "testcase"}.get(alias.name, "blocked" if alias.name in BLOCKED else "local")
                    record_kind(alias.asname or alias.name, kind)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    record(target, node.value)
            elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value:
                record(node.target, node.value)
            elif isinstance(node, ast.AugAssign):
                record(node.target, node.value)
            for child in ast.iter_child_nodes(node):
                inspect(child)
        previous = None
        while previous != bindings:
            previous = bindings.copy()
            for node in nodes:
                inspect(node)
        return {name for name, kind in bindings.items() if kind != "local"}

    def visit_For(self, node: ast.For) -> None:
        self.visit_iterated(node.iter)
        before = self.state()
        for name in self.loop_summary(node.body):
            self.put(name, "ambiguous")
        value, bindings = self.element_provenance(node.iter)
        self.assign_target(node.target, value, bindings)
        for item in node.body:
            self.visit(item)
        body = self.state()
        self.join([before, body])
        for item in node.orelse:
            self.visit(item)
        self.join([before, body, self.state()])

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        before = self.state()
        for name in self.loop_summary(node.body):
            self.put(name, "ambiguous")
        for item in node.body:
            self.visit(item)
        body = self.state()
        self.join([before, body])
        for item in node.orelse:
            self.visit(item)
        self.join([before, body, self.state()])

    def visit_Try(self, node: ast.Try) -> None:
        progress = [self.state()]
        for item in node.body:
            self.visit(item)
            progress.append(self.state())
        for item in node.orelse:
            self.visit(item)
        states = [self.state()]
        self.join(progress)
        handler_incoming = self.state()
        for handler in node.handlers:
            self.scopes = [scope.copy() for scope in handler_incoming]
            if handler.type:
                self.visit(handler.type)
            failed = self.state()
            if handler.name:
                self.put(handler.name, "local")
            for item in handler.body:
                self.visit(item)
            states.append(self.state())
            self.join([handler_incoming, failed])
            handler_incoming = self.state()
        self.join(states)
        for item in node.finalbody:
            self.visit(item)
    def visit_TryStar(self, node: ast.TryStar) -> None:
        progress = [self.state()]
        for item in node.body:
            self.visit(item)
            progress.append(self.state())
        success = self.state()
        for item in node.orelse:
            self.visit(item)
        success = self.state()
        self.join(progress)
        for handler in node.handlers:
            incoming = self.state()
            self.visit(handler)
            self.join([incoming, self.state()])
        self.join([success, self.state()])
        for item in node.finalbody:
            self.visit(item)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        incoming, states = self.state(), []
        for case in node.cases:
            self.scopes = [scope.copy() for scope in incoming]
            self.visit(case.pattern)
            if case.guard:
                self.visit(case.guard)
            failed = self.state()
            for item in case.body:
                self.visit(item)
            states.append(self.state())
            self.join([incoming, failed])
            incoming = self.state()
        self.join([incoming, *states])

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
        if node.type:
            self.visit(node.type)
        if node.name:
            self.put(node.name, "local")
        for item in node.body:
            self.visit(item)

    def visit_Call(self, node: ast.Call) -> None:
        kind = self.kind(node.func)
        if not self.suppressed:
            self.weak |= kind in {"blocked", "ambiguous"} or kind == "builtin" and isinstance(node.func, ast.Name) and node.func.id == "exec"
        if not self.suppressed and kind in {"raises", "ambiguous"}:
            self.raises.add((node.lineno, node.end_lineno))
        if not self.suppressed and isinstance(node.func, ast.Attribute) and node.func.attr == "skipTest":
            value = node.func.value
            self.weak |= self.kind(value) in {"case", "ambiguous"} or self.cases[-1] and (isinstance(value, ast.Name) and value.id == "self" or isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "super")
        self.visit(node.func)
        for argument in node.args:
            (self.visit_iterated if isinstance(argument, ast.Starred) or self.builtin(node.func, EAGER_ITERATORS) else self.visit)(argument)
        for keyword in node.keywords:
            self.visit(keyword.value)

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
        incoming = self.consume_genexpr
        consumed = not isinstance(node, ast.GeneratorExp) or bool(incoming)
        if isinstance(node, ast.GeneratorExp):
            self.consume_genexpr = 0
        (self.visit_iterated if consumed else self.visit)(generators[0].iter)
        first_value, first_bindings = self.element_provenance(generators[0].iter)
        names = set().union(*(self.target_names(generator.target) for generator in generators))
        expected = {ast.GeneratorExp: "genexpr", ast.ListComp: "listcomp", ast.SetComp: "setcomp", ast.DictComp: "dictcomp"}[type(node)]
        has_table = isinstance(node, ast.GeneratorExp)
        self.comp_writes.append(set())
        if has_table:
            child = self.next_child()
            self.enter(node, "function", expected, {name: "local" for name in child.get_locals()})
        else:
            self.scopes.append({name: "local" for name in names})
            self.types.append("function")
            self.cases.append(self.cases[-1])
            self.inline_depths[-1] += 1
        before, unreachable, lazy = self.state(), False, not consumed
        self.suppressed += lazy
        for index, generator in enumerate(generators):
            if generator is not generators[0]:
                self.suppressed += unreachable
                (self.visit_iterated if consumed else self.visit)(generator.iter)
                self.suppressed -= unreachable
            value, bindings, empty = (*self.element_provenance(generator.iter, first_bindings if index == 0 else None), self.empty_iterable(generator.iter))
            self.suppressed += unreachable or empty
            self.assign_target(generator.target, value, bindings)
            self.suppressed -= unreachable or empty
            unreachable |= empty
            self.suppressed += unreachable
            for condition in generator.ifs:
                self.visit(condition)
            self.suppressed -= unreachable
        self.suppressed += unreachable
        for value in ((node.key, node.value) if isinstance(node, ast.DictComp) else (node.elt,)):
            self.visit(value)
        self.suppressed -= unreachable
        self.suppressed -= lazy
        if has_table:
            self.leave()
        else:
            self.inline_depths[-1] -= 1
            self.scopes.pop()
            self.types.pop()
            self.cases.pop()
        writes = self.comp_writes.pop()
        after = self.state()
        self.join([before[:-1] if len(before) > len(after) else before, after])
        for name in writes:
            self.put(name, "ambiguous", self.inline_depths[-1])
        self.consume_genexpr = incoming
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
