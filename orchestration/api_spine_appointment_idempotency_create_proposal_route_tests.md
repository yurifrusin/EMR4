# API Spine Appointment Create-Proposal Idempotency Route-Test Contract

| Item | Value |
|---|---|
| Sprint | 148 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | Guarded route-test contract only |
| Runtime posture | No route behavior changed |

## Scope

This contract covers only:

| Route | Handler | OpenAPI operation | Classification |
|---|---|---|---|
| `POST /api/v1/appointments/proposals/create` | `propose_create_appointment` | `proposeAppointmentCreate` | proposal command |

The route currently builds a proposal envelope and optional staff-confirmation
payload. It does not create an appointment, write audit rows, reserve a slot, or
complete the confirmation idempotency ledger.

## Contract Decision

Create-proposal idempotency is future client-discipline behavior, not
confirmation-write replay authority.

Future implementation must not use create-proposal idempotency to:

- authorize or imply appointment creation;
- reserve diary slots;
- skip staff confirmation;
- replace signed confirmation evidence;
- weaken `create_proposal_freshness_id` or later confirmation revalidation;
- replay a confirmed appointment response.

## Future Behavior Tests

When a later sprint intentionally wires proposal-route enforcement, the skipped
tests in `tests/test_api_spine_create_proposal_idempotency_route_contract.py`
should be enabled and made executable. They define the first accepted behavior
surface:

1. missing `Idempotency-Key` fails closed before proposal evidence is minted;
2. blank or whitespace-only `Idempotency-Key` is treated as missing;
3. a valid keyed create-proposal request returns a proposal envelope with no
   appointment, audit, confirmation-ledger, or slot-reservation side effect;
4. same-key/same-body retry does not create write authority or reserve a slot;
5. same-key/different-body behavior is explicitly scoped to proposal client
   discipline, not durable confirmation-write replay;
6. generated confirmation payloads still require staff confirmation, signed
   evidence, freshness, and the already-wired confirmation ledger.

These future tests must become DB-backed `POST
/api/v1/appointments/proposals/create` integration tests when unskipped, not
only static source/document checks.

## Pending Replay-Model Decision

Sprint 148 deliberately does not choose create-proposal replay behavior. Sprint
149 must choose one of:

| Option | Meaning | Current preference |
|---|---|---|
| Deterministic re-evaluation | Require `Idempotency-Key`, but do not create a proposal ledger; same-key retries are fresh proposal evaluations and same-key/different-body does not return `409`. | Preferred default unless client/product needs conflict discipline |
| Short-retention proposal marker | Store a bounded proposal marker; same-key/different-body returns a proposal-scoped `409`, never appointment write replay. | Acceptable if client retries need stricter discipline |
| Stored proposal-envelope replay | Store and replay the proposal envelope for a short period. | Highest risk; only acceptable if freshness/evidence semantics are preserved and retention is short |

Whichever option is chosen, create-proposal idempotency must remain separate
from confirmation-write replay authority.

## Current No-Wiring Guard

Sprint 148 must keep the current FastAPI route unwired:

- no `Idempotency-Key` header binding on `propose_create_appointment`;
- no `claim_appointment_command()` call from `propose_create_appointment` or
  `_build_create_appointment_proposal`;
- no `complete_appointment_command()` call from `propose_create_appointment` or
  `_build_create_appointment_proposal`;
- no appointment/audit mutation behavior changes;
- no appointment command idempotency ledger rows from create-proposal calls;
- no raw compatibility route behavior changes.

## Gates Still Closed

This contract does not open:

- update/status/waiting-area/delete proposal idempotency enforcement;
- raw compatibility `POST`, `PUT`, `PATCH`, or `DELETE` idempotency
  enforcement;
- slot-search reservation or replay semantics;
- Bernie interpreter/session command idempotency expansion;
- provider calls, live-provider gates, or Access AI invocation changes;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Recommended Sprint 149

Before wiring, run a focused review on the create-proposal replay model and
choose one implementation shape:

- deterministic re-evaluation with required key but no proposal ledger;
- short-retention proposal marker that rejects same-key/different-body retries;
- or stored proposal-envelope replay with explicit short retention.

Do not implement until that choice is explicit.
