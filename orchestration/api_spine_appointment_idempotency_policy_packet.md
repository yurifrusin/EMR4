# API Spine Appointment Idempotency Policy Packet

| Item | Value |
|---|---|
| Sprint | 125 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Policy packet only; no route behavior, schema, database, provider, or GraphQL wiring changed |
| Steward posture | Define command replay behavior before implementation |

## Source Pass

Reviewed sources:

- `docs/api-spine/openapi/appointment-commands.yaml`
- `orchestration/api_spine_appointment_idempotency_gap.md`
- `orchestration/api_spine_appointment_command_alignment_inventory.md`
- `tests/test_api_spine_appointment_idempotency_gap.py`
- `app/routers/appointments.py`
- `app/services/bernie/session_store.py`

## Policy Scope

`Idempotency-Key` is an appointment command-plane concern. It is not a provider
gate, GraphQL mutation channel, Bernie session-event replay feature, or raw
model-output mechanism.

Implementation should be staged:

| Route family | Policy decision | Rationale |
|---|---|---|
| Proposal routes in OpenAPI (`create`, `update`, `status`, `delete`) | Require syntactic `Idempotency-Key` after client readiness, but do not treat proposals as write replay authority | OpenAPI already requires the header; proposals are non-mutating, so replay is useful for client discipline but must not create write authority. |
| Confirmation routes in OpenAPI (`create/confirm`, `update/confirm`, `status/confirm`, `delete/confirm`) | Require `Idempotency-Key` and durable replay ledger before enforcement | These routes can create, update, status-change, or delete appointments. |
| Backend alias confirmation routes (`status-confirm`, `delete-confirm`) | Same as their canonical OpenAPI confirmation family | Alias naming must not weaken command-plane policy. |
| Bernie create confirmation (`create/confirm-bernie`) | Same as create confirmation, plus existing Bernie session/evidence checks | Bernie-specific confirmation is a create-confirm family variant, not a separate authority path. |
| Slot-search command-style reads | No `Idempotency-Key` requirement by default | OpenAPI currently uses `X-Correlation-Id` only; searches do not reserve or mutate appointments. |
| Bernie intent/interpreter/supervised/no-slot command-style reads | No appointment-command `Idempotency-Key` requirement by default | Session-level idempotency remains separate and does not authorize appointment writes. |
| Raw compatibility writes | Explicit migration decision required before enforcement | They mutate state but are outside canonical command `paths:`; policy should either require, warn, or retire them in a deliberate compatibility sprint. |

## Replay Ledger Requirements

Future implementation should introduce a durable appointment command replay
ledger before requiring the header on confirmation routes.

Minimum binding fields:

- `practice_id`
- `actor_user_id`
- `actor_role`
- `operation_id`
- `route_family`
- `idempotency_key_hash`
- `request_body_hash`
- `request_body_canonicalization_version`
- `response_status_code`
- `response_body_hash`
- `result_kind`
- `target_appointment_id`
- `created_at`
- `expires_at` (nullable for confirmation-write entries)

Minimum uniqueness:

- unique `(practice_id, actor_user_id, operation_id, idempotency_key_hash)`
- same tuple + same `request_body_hash` returns the stored result
- same tuple + different `request_body_hash` returns `409 idempotency_key_conflict`

Retention:

- confirmation-write entries should not expire while the referenced
  appointment mutation remains clinically/audit relevant;
- proposal-only entries, if implemented, may use a shorter retention window;
- raw request bodies should not be stored unless a later security review
  explicitly approves encrypted storage.

Canonicalization:

- `request_body_hash` must be computed from a deterministic JSON form with
  sorted object keys, stable scalar encoding, and no insignificant whitespace;
- the canonicalization version must be stored so future changes can be
  introduced without reinterpreting old hashes.

Operation identity:

- backend aliases must share the same semantic `operation_id` as their
  canonical OpenAPI command family;
- `status-confirm` shares `confirmAppointmentStatusProposal`;
- `delete-confirm` shares `confirmAppointmentDeleteProposal`;
- `create/confirm-bernie` shares the create-confirm replay family while
  retaining Bernie-specific evidence checks.

Actor role:

- `actor_role` is stored for audit and first-execution authorization evidence;
- uniqueness is scoped to `actor_user_id`, not role, so a later role change by the same user cannot create a second write with the same idempotency key;
- first execution must still pass the current role/tenant policy.

## Execution Order

Future confirmation implementation should follow this order:

1. Authenticate and resolve practice/actor.
2. Require and normalize `Idempotency-Key`.
3. Canonicalize the request body and compute `request_body_hash`.
4. Create or lock the replay ledger row for the same actor/practice/operation/
   key before any appointment write.
5. If same body was already completed, return the stored response without
   performing a second appointment write.
6. If same key was used with a different body, return
   `409 idempotency_key_conflict`.
7. If no replay exists, run existing confirmation checks: explicit
   `confirmed=true`, proposal freshness, signed confirmation evidence, warning
   acknowledgement, current-state revalidation, role/tenant policy, and audit
   preparation.
8. Perform the appointment write once.
9. Persist the appointment write, replay ledger result, and audit evidence in
   the same transaction. Confirmation writes must not commit unless the replay ledger result is committed too.
10. Return the confirmed response.

Important interaction:

- A same-key/same-body replay after a successful write should return the stored
  result even if the original proposal would now be stale.
- A new key for stale proposal evidence should still fail closed through the
  existing freshness checks.
- Idempotency must not bypass signed confirmation evidence or staff
  confirmation on the first execution.

## Required Tests Before Implementation Closes

Future implementation should prove:

- same key + same body on `create/confirm` returns the same appointment id and
  creates only one appointment;
- same key + different body on `create/confirm` returns
  `idempotency_key_conflict`;
- same key + same body on update/status/delete confirmation does not repeat the
  mutation and proves the backend does not repeat the mutation on replay;
- keys are scoped by practice, actor, and operation;
- missing key on enforced confirmation routes fails with a typed `400` or `422`;
- stale proposal evidence still blocks when submitted with a new key;
- raw compatibility route behavior matches the compatibility policy chosen for
  that route family;
- audit evidence records idempotency replay vs first execution without exposing raw request bodies.

## Out of Scope

This packet does not:

- add a database table or migration;
- add FastAPI `Header(...)` bindings;
- require clients to send `Idempotency-Key` today;
- change raw compatibility route behavior;
- add GraphQL mutations;
- wire providers, runtime FGA clients, external patient clients, H15/H-series
  runtime imports, memory/RAG/GraphRAG, broad trove mining, or model-to-database
  writes.

## Smallest Next Alignment Slice

Recommended Sprint 126:

**Appointment command idempotency storage design.**

Draft the concrete storage contract and transaction boundary for the replay
ledger, including Alembic/model shape, uniqueness, TTL, audit linkage,
body-hash canonicalization, and rollback behavior. Do this before route
enforcement.

## Gates Still Closed

This policy packet does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.
