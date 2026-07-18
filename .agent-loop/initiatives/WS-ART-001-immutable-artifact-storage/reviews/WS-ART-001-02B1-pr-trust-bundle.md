# PR Trust Bundle: WS-ART-001-02B1

## Chunk

`WS-ART-001-02B1` - S3-Compatible MinIO And AWS

Merge intent: `.agent-loop/merge-intents/WS-ART-001-02B1.json`

## Goal

Add one provider-neutral S3 protocol implementation, prove it against real
MinIO for local/CI use, and validate an isolated native AWS configuration
without making AWS runtime-eligible before its separately owned live-proof
chunk.

## What Changed

- Added `S3CompatibleArtifactStore` behind the existing ArtifactStore v2 and
  typed external-service factory boundaries.
- Added real digest-pinned MinIO to local/CI composition and shared conformance.
- Added closed AWS workload-identity configuration and isolation proof while
  preserving the stable pre-I/O `artifact_provider_live_proof_required` guard.
- Added canonical S3 namespace, region, bucket, prefix, and endpoint validation.
- Added sanitized credential/metadata/endpoint failure paths and deep
  traceback/object-graph tests.
- Added exact async SDK pins and cumulative CI coverage guards.
- Integrated AUTH PR #148 while leaving all AUTH runtime activation with AUTH.

## Scope Control

The chunk adds no product route, upload admission, put-attempt state,
verification publication, recovery operation, presigned URL, multipart upload,
list/delete/copy capability, Flow Node path, R2 profile, or authorization
activation. `WS-ART-001-02C1` remains inactive until this chunk merges and the
user explicitly starts it.

## Acceptance Proof

- [x] Server-derived sealed commitment controls every provider object key.
- [x] Exact replay and conditional no-overwrite semantics are deterministic.
- [x] Object size fails before provider I/O above 512 MiB.
- [x] Real LocalStorage and MinIO pass the same ArtifactStore v2 vectors.
- [x] AWS credential resolution is limited to one explicitly selected workload
  source with ambient providers, proxies, and behavior controls rejected.
- [x] Native AWS fails before factory, credentials, namespace, scratch, or I/O.
- [x] ART/AUTH ownership remains separated after AUTH PR #148 integration.
- [x] Exactly one schema-v2 merge intent names only the same-initiative 02C1
  successor and requires a separate explicit start.

## Tests And Checks

```text
428 real-service focused tests PASS
S3CompatibleArtifactStore coverage 92%
S3 validation coverage 100%
Combined changed-subsystem coverage 92.95%
Ruff PASS
pip check PASS
87 agent-gate tests PASS
Stale artifact/authorization/review/Workstream wording PASS
Markdown links PASS
git diff --check PASS
```

GitHub Backend CI remains authoritative for the isolated full suite, the 78
percent repository floor, and all cumulative focused 90 percent gates.

## Internal Review

Reviewed code SHA: `9cd41ab907aba323f1fbd79dac8bbe1602bcc30f`

All nine required reviewer tracks passed the exact integrated SHA with no
remaining finding. Every reviewer session is closed. Reviewer IDs and the
addressed repair history are recorded in the internal review evidence.

## External Review

| Source | Status | Notes |
|---|---:|---|
| GitHub Actions | Pending | Runs the isolated full suite, repository floor, cumulative focused gates, and real MinIO proof. |
| CodeRabbit | Pending | External review starts after publication. |
| Human review | Pending | Only the user may approve merge. |

## Remaining Risks

- AWS is configuration-ready but intentionally unavailable until Chunk 07.
- MinIO proves protocol behavior only for local and CI environments.
- Durable admission, verification, publication, and recovery are later chunks.

## Human Review Focus

- Is there truly one S3 protocol adapter rather than provider-specific forks?
- Can untrusted input influence object identity, credential sources, endpoints,
  proxies, or namespace selection?
- Does native AWS fail before every credential and provider side effect?
- Are ART and AUTH responsibilities still separate after PR #148 integration?
- Are all later ART capabilities still inactive?

## Human Merge Ownership

- [ ] I can explain what changed and why.
- [ ] I know what could break.
- [ ] I accept the remaining risks.
- [ ] GitHub CI and external review pass.
- [ ] The user explicitly approved this PR for merge.
