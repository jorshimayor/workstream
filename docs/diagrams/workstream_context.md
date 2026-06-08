# Workstream System Context

This is the C4-style context view. It shows Workstream as one system inside the broader Flow ecosystem.

The diagram intentionally separates current v0.1 scope from future adapter boundaries. Workstream owns evaluation, contribution records, payment status, and reputation signals. It does not own Flow login, agent identity standards, escrow contracts, settlement rails, or external task origins.

```mermaid
flowchart LR
  pm["Project Manager<br/>Creates projects, guides, policies, and tasks"]
  worker["Human-Agent Contributor<br/>Claims work, submits packets, attests to output"]
  reviewer["Reviewer<br/>Reviews evidence, findings, and checker results"]
  ops["Operator / Admin<br/>Handles overrides, audits, and reconciliation"]

  flowAuth["Flow Identity<br/>External human identity and auth tokens"]
  workstream["Workstream<br/>Task evaluation and contribution infrastructure"]

  postgres[("Postgres<br/>Record database")]
  storage["Object Storage Abstraction<br/>Local now, R2/S3-compatible later"]

  origins["External Task Origins<br/>Enterprise, Bittensor, protocols, internal teams"]
  erc8004["ERC-8004<br/>Agent identity and agent reputation"]
  erc8183["ERC-8183<br/>Task contract and escrow layer"]
  settlement["x402 / OmniClaw / USDC<br/>Payment request and settlement rails"]
  consumers["Reputation / Reporting Consumers<br/>Routing, dashboards, future filters"]

  pm --> workstream
  worker --> workstream
  reviewer --> workstream
  ops --> workstream

  workstream --> flowAuth
  workstream --> postgres
  workstream --> storage

  origins -.->|"Later: source adapters normalize into Workstream task contracts"| workstream
  workstream -.->|"Later: read agent identity and reputation before claim; write outcome after accepted work"| erc8004
  workstream -.->|"Later: reference task contract or escrow when origin requires it"| erc8183
  workstream -.->|"Later: create payment request from accepted contribution and locked payment policy"| settlement
  workstream -.->|"Later: publish contribution, payment, and reputation signals"| consumers

  classDef current fill:#e7f5ff,stroke:#1c7ed6,color:#0b2942
  classDef record fill:#e6fcf5,stroke:#0ca678,color:#063b2c
  classDef external fill:#f1f3f5,stroke:#868e96,color:#212529
  classDef later fill:#fff3bf,stroke:#f08c00,color:#4a2f00

  class workstream current
  class postgres,storage record
  class pm,worker,reviewer,ops,flowAuth external
  class origins,erc8004,erc8183,settlement,consumers later
```

## Context Rules

- Flow identity is the human identity and auth boundary.
- Workstream verifies Flow-issued tokens; it does not own login, signup, password reset, password storage, or primary auth sessions.
- Workstream treats a working contributor as a human-agent unit for workflow purposes, while preserving separate human and agent references when agent identity is introduced.
- ERC-8004 is the future agent identity and agent reputation rail.
- ERC-8183 is the future task contract and escrow rail.
- x402, OmniClaw, and USDC settlement are future payment execution rails.
- v0.1 stays focused on the internal project guide -> task -> submission -> checks -> review -> revision -> contribution/payment/reputation loop.
