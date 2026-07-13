# Chunk Contract: WS-QUAL-001-01B1B-R8 Syntactic Integrity Policy

Parent: `WS-QUAL-001` Backend Coverage Floor

## Goal And Rationale

Replace R7's attempted Python execution model with a bounded syntactic policy.
The gate protects changed tests from known pytest/unittest weakening constructs
and deleted assertion constructs; it does not predict runtime reachability,
iterator consumption, or arbitrary Python values.

Risk: L1. SLA: normal. The user's 2026-07-13 instruction to fix the blocking
coverage gate is the implementation start signal only after this contract passes
all required internal plan-review tracks.

## Scope

Allowed files:

- `backend/scripts/coverage_policy.py`
- `backend/tests/test_coverage_contract.py`
- WS-QUAL and global `.agent-loop/` memory

Not allowed: `backend/app/**`, coverage-raising tests, skips/xfails/exclusions,
configuration, workflows, evidence baselines, B2, chunk 02, AUTH-03, product
runtime, dependencies, public docs, or spreadsheet exports.

The implementation delta from merged main is capped at 700 added/deleted lines
across the policy and contract-test files. Checkpoint at 600. Tests must keep one
case per physical line, stay reviewable without generated/encoded fixtures, and
must not be compacted to satisfy the cap. Stop above 700.

## Acceptance Criteria

- Absolute `pytest` and `unittest` imports, aliases, and direct imports establish
  framework ownership. Relative imports such as `from .pytest` remain local.
- Python lexical scopes use stdlib `symtable`; local parameters and declarations
  shadow outer framework names, while explicit global/nonlocal ownership remains
  visible. Bounded direct aliases may propagate framework ownership, but no
  control-flow fixed point or runtime value model is permitted.
- Known skip/xfail/importorskip/SkipTest/skipTest/pytestmark constructs are
  rejected wherever they occur syntactically once their root is framework-owned.
  Reachability, generator laziness, async iteration, wrappers, qualified
  builtins, and consumer argument roles cannot change the result.
- Native `assert`, framework-owned `pytest.raises`/imported `raises`, and
  unittest `self.assert*` calls are recognized syntactically in the base file
  for deleted-assertion protection, independent of runtime reachability.
- Strings, comments, annotations under postponed evaluation, relative imports,
  local lookalikes, shadowed names, and unrelated methods remain clean.
- Preserve repository root/cwd behavior, committed rename checks, scope and size
  enforcement, metadata parsing, canonical coverage grammar, and all R2 tests.
- No test expectation is weakened merely to match broader detection.

## Verification And Review

Run:

```text
cd backend && .venv/bin/python -m pytest -q tests/test_coverage_contract.py
cd backend && .venv/bin/ruff check scripts/coverage_policy.py tests/test_coverage_contract.py
cd backend && .venv/bin/pip check
backend/.venv/bin/python scripts/check_stale_workstream_wording.py
backend/.venv/bin/python scripts/check_stale_authorization_docs.py
backend/.venv/bin/python scripts/check_loop_memory_state.py
backend/.venv/bin/python scripts/check_markdown_links.py
git diff --check
```

Required reviewers: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, docs, reuse/dedup, test delta, and circuit breaker.
Human review focus: the intentionally conservative syntax contract, local
lookalike precision, readable tests, no CI weakening, and bounded scope.

## Stop Conditions

Stop if the syntactic contract requires runtime reachability/consumption,
arbitrary call semantics, another abstract interpreter, unreadable tests, more
than two repair cycles, or more than 700 implementation lines. Do not start B2,
chunk 02, AUTH-03, or any other chunk after R8.
