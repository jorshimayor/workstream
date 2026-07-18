# WS-REV-001-01 External Review Response

## PR

- PR: `#145`
- Initial published head: `9ad0420e4c8f3ce0933a85fc75f133a340f91fcd`
- Reviewed repair candidate: `5af0adcec3cc184c4455292ec2f04e7505a90857`
- Trusted base: `a10d9018007d2e847b4870e9b26cbd24e24c7bb4`

## Comments Addressed

- GitHub Agent Gates failed in `validate-merge-intent` because the declared
  successor title did not match the first heading of the existing
  `WS-REV-001-02` chunk contract.
- The successor heading now uses the canonical schema-v2 form and exactly
  matches `Locked Review Policy And Task Lifecycle Alignment` from
  `.agent-loop/merge-intents/WS-REV-001-01.json`.
- CodeRabbit's nine actionable comments were addressed: explicit pinned
  PlantUML precondition; four-source `--all` rendering; FinalAcceptance as an
  accept side effect; exact durable/final/current CheckerRun transition guards;
  complete TaskAssignment attribution; both ART v2 storage passages; exact
  checker routing outcomes; valid Markdown table cells; and explicit
  `auto_reject_after_limit=false` configuration with runtime enforcement owned
  by `WS-REV-001-02`.
- Its Markdown lint nit was addressed by reflowing the PR reference so a line
  no longer begins with `#143`.
- The revision scanner now permits the required false configuration while
  rejecting unquoted, quoted, JSON, and backticked truthy forms. The first
  repair candidate's Ruff formatting failure was also corrected.
- ART-02A3 PR #141 later advanced main. The branch merged it, resolved the sole
  glossary overlap by preserving both exact byte-store operations and narrow
  typed product capabilities, and corrected Ruff formatting in four merged ART
  gate assertions. Fresh exact-SHA internal review passed.
- CodeRabbit's later scope-verification comment was valid in requiring a
  fail-closed comparison. The repair intentionally retains trusted current main
  as the PR-scope base, documents why the original planning base is reserved
  for archival immutability, and compares exact added/modified statuses against
  a committed 71-entry manifest with rename detection disabled.
- Internal repair review then found that the first path-only manifest could not
  distinguish an approved modification from deleting the same path. The final
  status-aware manifest closes that gap; adversarial status-change, removal,
  rename-as-delete-plus-add, and unreviewed-addition probes all fail.

## Comments Deferred

- None. The ART comment's highlighted lower passage was already correct, but
  its body identified an earlier raw `ArtifactStore` stack bullet; that earlier
  occurrence was also updated rather than dismissing the finding as stale.

## Human Decisions Needed

- None. The repairs preserve the approved Chunk 01 contract and do not start
  or implement Chunk 02.

## Commands Rerun

- `python3 scripts/update_post_merge_memory.py validate-merge-intent --base-ref origin/main`
- `python3 scripts/test_agent_gates.py`
- Ruff format/lint for both changed Python gate files.
- Stale artifact, authorization, review, and Workstream wording scanners.
- Markdown links, reference checksums, pinned PlantUML rendering, table-column
  checks, scope checks, and `git diff --check`.
- Exact `--name-status --no-renames` manifest comparison plus adversarial
  status-change, removal, rename, and addition probes.
- Exact-SHA plan gate and all nine required internal reviewer tracks.

## Remaining Risks

- Replacement GitHub checks and any CodeRabbit follow-up on the final repaired
  PR head remain required after push.
- Runtime concurrency, rollback, and AUTH/ART/CON integration remain owned by
  later implementation chunks.
