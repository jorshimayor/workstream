# Chunk Contract: WS-QUAL-001-01B1B-R1 Lexical Binding Closure

Parent: `WS-QUAL-001` Backend Coverage Floor

Status: proposed corrective replacement after B1B's two-cycle circuit stop;
internal contract review pending.

## Goal And Scope

Complete the semantic delta guards using lexical binding rather than
file-global alias sets. Preserve all passing B1B repository, assertion-span,
rename, scope, size, and cwd behavior.

Risk: L1 test/CI integrity. SLA: P1. Allowed implementation files are
`backend/scripts/coverage_policy.py`, `backend/tests/test_coverage_contract.py`,
and WS-QUAL/global process evidence. Parser redesign, B2, docs, live config,
workflow/evidence mutation, `backend/app/**`, DB/API/product/AUTH behavior,
skips/xfails, exclusions, and coverage-raising tests remain forbidden.

The complete replacement candidate is capped at 300 non-memory lines from
merge base. Stop above 270 before remaining work, above 300, or on any
additional valid finding outside this exact corrective scope.

## Acceptance Criteria

- Resolve pytest/unittest modules, direct imports, and aliases by the lexical
  scope and statement binding applicable at each executable call.
- A local or parameter binding that shadows `pytest`, a module alias, or an
  imported `raises`/skip name must be treated as local, not framework behavior.
- Detect genuine pytest skip/xfail/importorskip and unittest skip decorators,
  exceptions, `self.skipTest`, `super().skipTest`, and proven TestCase-instance
  receivers without classifying arbitrary local `.skipTest()` methods.
- Base-AST deleted assertion detection must apply the same lexical resolution
  to direct/imported/module-aliased `pytest.raises` while preserving multiline
  native/self assertions and inert/local-lookalike acceptance.
- Preserve real committed rename rejection, root helper reuse, cwd restoration,
  exact global/WS-QUAL memory scope, and the implementation cap.
- Restore the local-lookalike test to its original non-weak expectation; tests
  may not be rewritten to accept broader guard behavior.

## Verification And Review

Run the complete B1B verification command set plus adversarial nested-scope,
parameter-shadow, assignment-shadow, and class/TestCase binding matrices.
Required reviewers: senior engineering, QA/test, security/auth, product/ops,
architecture, CI integrity, reuse/dedup, and test delta. Human focus: lexical
false positives/negatives, no weakened expectations, and no B2/AUTH spill.

Stop after R1. Do not start 01B2 or chunk 02. AUTH-02 may continue independently
in its already-authorized worktree.
