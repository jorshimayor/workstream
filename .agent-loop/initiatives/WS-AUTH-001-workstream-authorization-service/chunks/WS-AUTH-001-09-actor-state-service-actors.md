# Parent Chunk: WS-AUTH-001-09 - Actor State, Identity Revocation, And Service Actors

## Status

Split before runtime implementation on 2026-07-16 after required L1 plan
review. No application or migration code was written under the combined
contract.

## Why the split was required

The combined contract crossed four independently reviewable authorization
boundaries:

- closed action registration and the fixed service-identity field;
- controlled service-actor provisioning;
- privacy-bounded actor and identity-link administration reads; and
- actor/link lifecycle mutations with final Access Administrator concurrency.

It also omitted required migration, model-registry, authorization, route
manifest, and rate-control test files; conflicted with the canonical `/api/v1`
route families; and made application startup depend on database rows that the
running application was supposed to provision. Those defects made the original
contract unimplementable without inventing authority or bypassing its own
startup rule.

## Child chunks

| Chunk | Title | Boundary |
|---|---|---|
| `WS-AUTH-001-09A` | Fixed Service Identity Foundation | Register eight planned AUTH-09 route actions, make a service ActorProfile carry one fixed service identity, and define the exact static service-action matrix. No route or action becomes active. |
| `WS-AUTH-001-09B` | Controlled Service Actor Provisioning | Activate only `actor.service.provision` and bind one opaque Identity Issuer subject to one fixed service ActorProfile. |
| `WS-AUTH-001-09C` | Actor And Identity-Link Administration Reads | Activate only bounded actor-detail and actor identity-link reads. |
| `WS-AUTH-001-09D` | Actor And Identity-Link Lifecycle Mutations | Activate suspend/reactivate/deactivate and link revoke/reactivate with idempotency, audit/invalidation, and final-admin concurrency proof. |

## Canonical route boundary

The children implement only the adopted repository route families:

```text
GET  /api/v1/actors/{actor_profile_id}
POST /api/v1/actors/{actor_profile_id}/suspend
POST /api/v1/actors/{actor_profile_id}/reactivate
POST /api/v1/actors/{actor_profile_id}/deactivate
GET  /api/v1/actors/{actor_profile_id}/identity-links
POST /api/v1/actor-identity-links/{identity_link_id}/revoke
POST /api/v1/actor-identity-links/{identity_link_id}/reactivate
POST /api/v1/service-actors
```

Actor/service collection routes, service detail routes, `/admin/actors`
aliases, a second human identity-link endpoint, and client-selected service
ActionIds remain outside AUTH-09.

## Ordering

`WS-AUTH-001-09A -> WS-AUTH-001-09B -> WS-AUTH-001-09C -> WS-AUTH-001-09D -> WS-AUTH-001-10`

Neither child starts the next automatically. Each child requires its own
evidence, internal review, PR, explicit human merge approval, signed merge
memory, and stop. WS-ART service-action consumption remains inactive until
AUTH-09B has merged; the actions themselves remain planned until each owning
WS-ART chunk supplies its resource facts, guards, surface, and behavior proof.
