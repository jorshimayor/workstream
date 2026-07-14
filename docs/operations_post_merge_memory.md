# Post-Merge Memory Operations

## Purpose

Managers review and approve each implementation PR once. Workstream then
records merge state automatically without a second bookkeeping PR or repeated
reviewer fanout.

## Trust Boundary

`.github/workflows/loop-memory.yml` runs only after a push to protected `main`
or an explicit operator replay. It executes the updater already present on
`main`; it never checks out pull-request-head code with write credentials. Its
only write target is `automation/loop-memory`.

The generated branch contains:

- `.agent-loop/STATE.json` - canonical live state
- `.agent-loop/LOOP_STATE.md` - generated human view
- `.agent-loop/MERGE_LOG.jsonl` - append-only merge history

## PR Metadata

Every PR carries exactly one marker:

```text
<!-- workstream-loop-state
{"schema_version":1,"initiative_id":"WS-AUTH-001","chunk_id":"WS-AUTH-001-06","chunk_title":"Canonical Actor Profile And Identity Link","next_chunk_id":"WS-AUTH-001-07","next_chunk_title":"Authorization Kernel And Permission Registry","next_requires_explicit_start":true}
-->
```

Agent Gates rejects missing, duplicate, malformed, unknown-key, mismatched
initiative/chunk, or incomplete next-chunk metadata before merge.

## Normal Operation

1. The manager reviews and merges the normal PR.
2. `Loop Memory` resolves the exact merged PR from the protected-main SHA.
3. The updater validates the PR marker and records observed Backend, Agent
   Gates, and CodeRabbit conclusions from the final PR head.
4. The workflow commits generated files directly to `automation/loop-memory`.
5. Work stops. A next chunk starts only under the generated explicit gate.

## Read Current State

```bash
git fetch origin automation/loop-memory
git show origin/automation/loop-memory:.agent-loop/STATE.json
git show origin/automation/loop-memory:.agent-loop/LOOP_STATE.md
```

## Recovery

If the workflow fails, correct the PR marker or repository permission that
caused the fail-closed result, then run `Loop Memory` with `workflow_dispatch`
and the exact 40-character merge SHA. Replays are idempotent. Older merges and
conflicting duplicate records are rejected; generated files must not be edited
by hand.

## Review Policy

Implementation, specification, generator, workflow, policy, and hand-edited
memory changes retain all normal review requirements. Only deterministic output
committed by `Loop Memory` to `automation/loop-memory` skips the second review
and PR cycle.
