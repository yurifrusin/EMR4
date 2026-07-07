# API Spine Appointment Idempotency - Create-Confirm Client Header

| Item | Value |
|---|---|
| Sprint | 155 |
| Programme | Programme 2G / EMR4 API Spine |
| Classification | Client header emission for already-enforced create confirmation routes |
| Runtime backend behavior changed | No |
| Decision | Wire staff create-confirm and create-confirm-Bernie client headers first; defer update/status/delete confirm and proposal-only binding |

## Context

Sprint 154 proved that the Diary frontend could prepare create proposals with an
HTTP `Idempotency-Key`, but the immediate confirmation hops still missed the
header even though their FastAPI routes already enforce it through the
appointment command idempotency ledger.

## Implemented Client Posture

Sprint 155 adds stable client-side header emission for create confirmation
only:

| Caller | Endpoint family | Header source |
|---|---|---|
| `saveBooking` create-confirm branch | `/appointments/proposals/create/confirm` | Existing `btn-booking-save.dataset.idempotencyKey`, shared with the modal create-proposal attempt |
| Bernie review confirm adapter | `/appointments/proposals/create/confirm-bernie` | `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", payload.confirm_endpoint)` |

The key is stable for retries of the same staged confirmation. This preserves
the backend confirmation ledger's replay semantics instead of creating a fresh
key on every double-submit or retry.

## Deferred Gaps

Sprint 155 deliberately leaves these gaps documented for later bounded slices:

- update-confirm client header emission;
- status-confirm client header emission;
- delete-confirm client header emission;
- Bernie tool-intent confirm header emission;
- proposal-only backend header binding for update/status/waiting-area/delete;
- raw compatibility write idempotency;
- strict runtime `minLength: 8` enforcement.

## Closed Gates

This sprint does not change backend route behavior, OpenAPI schema, idempotency
ledger semantics, provider calls, GraphQL mutations, H15/H-series runtime
imports, memory/RAG/GraphRAG runtime wiring, or broad historical diary trove
access.

## Next Step

Sprint 156 should choose either status-confirm/delete-confirm client header
emission or update-confirm client header emission as the next bounded confirm
family. Proposal-only backend binding should wait until the confirmed-write
client surface is no longer broken.
