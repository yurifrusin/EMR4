# API Spine Appointment Create-Proposal Idempotency Route-Test Contract

| Item | Value |
|---|---|
| Sprint | 148 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | Guarded route-test contract only |
| Runtime posture | Sprint 150 wires syntactic header enforcement only |

## Scope

This contract covers only:

| Route | Handler | OpenAPI operation | Classification |
|---|---|---|---|
| `POST /api/v1/appointments/proposals/create` | `propose_create_appointment` | `proposeAppointmentCreate` | proposal command |

The route builds a proposal envelope and optional staff-confirmation payload.
As of Sprint 150 it requires a non-blank `Idempotency-Key` header, then
deterministically re-evaluates the current diary state. It does not create an
appointment, write audit rows, reserve a slot, create proposal idempotency
ledger rows, or complete the confirmation idempotency ledger.

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

Sprint 150 enabled the future behavior tests in
`tests/test_api_spine_create_proposal_idempotency_route_contract.py` as
DB-backed route tests. They define the accepted behavior surface:

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

## Replay-Model Decision

Sprint 149 chose deterministic re-evaluation before Sprint 150 wiring:

| Option | Meaning | Current preference |
|---|---|---|
| Deterministic re-evaluation | Require `Idempotency-Key`, but do not create a proposal ledger; same-key retries are fresh proposal evaluations and same-key/different-body does not return `409`. | Chosen |
| Short-retention proposal marker | Store a bounded proposal marker; same-key/different-body returns a proposal-scoped `409`, never appointment write replay. | Rejected for first pass |
| Stored proposal-envelope replay | Store and replay the proposal envelope for a short period. | Rejected for first pass |

Whichever option is chosen, create-proposal idempotency must remain separate
from confirmation-write replay authority.

## Current Wiring Guard

Sprint 150 keeps the FastAPI route wired narrowly:

- `propose_create_appointment` binds `Idempotency-Key` from the HTTP header;
- missing or whitespace-only keys return `400 idempotency_key_required`;
- non-blank short keys are accepted for Sprint 150; OpenAPI `minLength: 8`
  enforcement remains a future compatibility decision;
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

## Recommended Sprint 151

Before expanding to other proposal routes, add an OpenAPI/FastAPI header
alignment guard for create-proposal, including the currently deferred
`minLength: 8` question and client-readiness note.
