# Workstream Reference Specifications

The eight WS-ARCH/WS-AUTH/WS-CON/WS-IMP/WS-REV files in this directory are
byte-immutable archival inputs supplied on 2026-07-11.

| File | Status | SHA-256 |
|---|---|---|
| `WS-ARCH-001-workstream-v0.1-architecture-baseline.pdf` | archival input | `547176dcedf41895ed896d5262a6ab8c6c029d71dac50bd17ed9da65f692b9b3` |
| `WS-AUTH-001-actor-profile-role-and-authorization-service-specification.md` | archival input | `464a7afb032e950b83e8fdb8c04fafe0b9ebddf549c4475dca684946740869a9` |
| `WS-AUTH-001-actor-profile-role-and-authorization-service-specification.pdf` | archival input | `69670ed59006b29cb7f60d12101cedf250c82a3488497f07d6c27e140aef1d2e` |
| `WS-CON-001-contribution-record-and-compensation-boundary-specification.pdf` | archival input | `34c4337f27e42a5b0ed5e153fe8ccd492ecede202c2764506a930d109aef66c1` |
| `WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.md` | archival input | `e2116bce55fda1cce46a93e64bedcb47133d3898c1d4a51863385803e9dac210` |
| `WS-IMP-001-workstream-v0.1-coding-agent-implementation-specification.pdf` | archival input | `12f094e49c5c80f117e42d0f7f962b843f34508ab58d7f1d8def5f50fef532ed` |
| `WS-REV-001-review-lifecycle-specification.md` | archival input | `87d2c4c5b2158bd11ed76985f8abdc3303be7dcdf7de470bae6b3bcf92b56fe4` |
| `WS-REV-001-review-lifecycle-specification.pdf` | archival input | `d4ab94f2db6ec47dacc6a9063934e481d7089db5bfe142d724aa0b025bc00b52` |

The same values remain machine-checkable in `SHA256SUMS` and are bound by the
WS-AUTH-001 `SOURCE_MANIFEST.md` planning record. Neither checksum source is
updated as part of reconciliation.

These inputs are not the repository's reconciled runtime contract. In
particular, Workstream retains the canonical `/api/v1` namespace even where an
archival input uses `/v1`. WS-AUTH-001 takes precedence over the current
token-role authorization bootstrap under accepted ADR 0012. The reconciled
canonical text lives in `docs/spec_authorization_service.md`; active repository
documentation points there without editing the eight archived files.
