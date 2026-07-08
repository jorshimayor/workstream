# Chunk Map: WS-FE-001 — Frontend Operations Console

| Chunk | Title | Upstream issue | Risk | Status |
|---|---|---|---:|---|
| `WS-FE-001-01` | Canonical React + Vite app foundation | #50 | L2 | Implemented; internal review + human checkpoint pending |
| `WS-FE-001-02` | Task queue + task detail/claim/submit | #51 / #52 | L2 | Planned; needs start signal |
| `WS-FE-001-03` | Review queue + review decision + findings | #56 | L2 | Planned; blocked on review/revision backend (#34–#38) |
| `WS-FE-001-04` | Dashboard (role-aware) | — | L1 | Planned; thin once screens exist |
| `WS-FE-001-05` | Guide & policy activation flow | #49 | L2 | Planned; needs start signal |
| `WS-FE-001-06` | Contribution / payment / reputation record | #53 / #55 | L1 | Planned; blocked on payment/reputation backend (#39–#40) |
| `WS-FE-001-07` | Audit console | #51 (audit slice) | L2 | Planned; last per build order |

Build order follows `docs/website_flow.md` §5. Each chunk gets its own contract in
`chunks/` and its own explicit start signal; the loop does not auto-advance.
