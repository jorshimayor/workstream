# Post-Merge Memory Operations

## Purpose

Managers review and approve each implementation PR once. Workstream then
records merge state automatically without a second bookkeeping PR or repeated
reviewer fanout.

## Trust Boundary

`.github/workflows/loop-memory.yml` runs only after a push to protected `main`
or an explicit operator replay. It executes the updater already present on
`main`; it never checks out pull-request-head code with write credentials. Its
only write target is `automation/loop-memory`. The branch blocks deletion and
non-fast-forward updates. Because organization policy disables deploy keys, the
workflow also signs all canonical generated files with an Actions-only Ed25519
private key. The reviewed public key on `main` lets operators reject any branch
write that did not come from trusted automation, while an expected protected-
`main` SHA rejects replay of an older valid signed snapshot. Invalid branch
state is discarded and deterministically rebuilt from the immutable bootstrap.

The generated branch contains:

- `.agent-loop/STATE.json` - canonical live state
- `.agent-loop/LOOP_STATE.md` - generated human view
- `.agent-loop/MERGE_LOG.jsonl` - append-only merge history
- `.agent-loop/STATE.sig` - signature over all three canonical generated files

## Merge Intent

Every PR adds exactly one immutable file at
`.agent-loop/merge-intents/<chunk-id>.json`:

```json
{
  "schema_version": 1,
  "initiative_id": "WS-AUTH-001",
  "chunk_id": "WS-AUTH-001-06",
  "chunk_title": "Canonical Actor Profile And Identity Link",
  "next_chunk_id": "WS-AUTH-001-07",
  "next_chunk_title": "Authorization Kernel And Permission Registry",
  "next_requires_explicit_start": true
}
```

Agent Gates rejects missing, modified, duplicate, malformed, unknown-key,
mismatched path/chunk, or incomplete next-chunk metadata before merge. The
post-merge updater fetches this exact added file from the reviewed final head;
PR-body edits cannot substitute lifecycle authority.

The protected `main` branch requires `agent-gates` and Backend `test`, and it
dismisses stale approvals after a new push. A changed intent therefore needs
fresh checks and human review before merge.

## Normal Operation

1. The manager reviews and merges the normal PR.
2. `Loop Memory` resolves every unrecorded first-parent commit through the
   protected-main SHA. On first use, the immutable `WS-ENG-001-02` merge intent
   anchors the activation commit; later runs start from the canonical ledger
   tail. Canceled or out-of-order events therefore cannot lose a merge.
3. The updater validates the committed merge intent and records observed
   Backend, Agent Gates, and CodeRabbit conclusions from each final PR head.
4. The workflow commits generated files directly to `automation/loop-memory`.
5. Work stops. A next chunk starts only under the generated explicit gate.

## Read Current State

```bash
git fetch origin automation/loop-memory
git show origin/automation/loop-memory:.agent-loop/STATE.json
git show origin/automation/loop-memory:.agent-loop/LOOP_STATE.md
python3 scripts/update_post_merge_memory.py verify-state \
  --state-root <checked-out-state-branch> \
  --public-key .agent-loop/keys/loop-memory-signing-public.pem \
  --expected-main-sha "$(git rev-parse origin/main)"
```

## Recovery

If the workflow fails because of repository permissions or a transient GitHub
error, replay trusted default-branch automation with:

```bash
gh api --method POST repos/Flow-Research/workstream/dispatches \
  -f event_type=loop-memory-replay \
  -F client_payload[merge_sha]=<40-character-merged-main-sha>
```

`repository_dispatch` always selects the workflow from the default branch;
callers cannot choose feature-branch workflow code for the write token. Replays
are idempotent and reconcile skipped intermediate commits. Invalid immutable
intent requires an explicit corrective engineering PR; generated files must
not be edited by hand.

## Review Policy

Implementation, specification, generator, workflow, policy, and hand-edited
memory changes retain all normal review requirements. Only deterministic output
committed by `Loop Memory` to `automation/loop-memory` skips the second review
and PR cycle.
