# Workstream Reference Specifications

The eight WS-ARCH/WS-AUTH/WS-CON/WS-IMP/WS-REV files in this directory are
byte-immutable archival inputs supplied on 2026-07-11. Their hashes are recorded
in `SHA256SUMS` and `SOURCE_MANIFEST.md` under the WS-AUTH-001 initiative.

These inputs are not the repository's reconciled runtime contract. In
particular, Workstream retains the canonical `/api/v1` namespace even where an
archival input uses `/v1`. WS-AUTH-001 takes precedence over the current
token-role authorization bootstrap, subject to the human approval gates in the
initiative plan. Chunk `WS-AUTH-001-01` will publish the reconciled canonical
authorization text at `docs/spec_authorization_service.md` and update active
repository documentation without editing the eight archived files.
