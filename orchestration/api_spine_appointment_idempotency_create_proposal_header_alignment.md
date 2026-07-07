# API Spine Create-Proposal Header Alignment Guard

| Item | Value |
|---|---|
| Sprint | 151-152 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | OpenAPI/FastAPI alignment guard only |
| Runtime posture | No behavior change after Sprint 150; Sprint 152 keeps minLength deferred |

## Guarded Alignment

`POST /api/v1/appointments/proposals/create` now has a deliberately split
contract:

- OpenAPI records the shared `Idempotency-Key` header as required with
  `minLength: 8` and `maxLength: 128`.
- OpenAPI also records
  `x-emr4-proposal-header-posture.runtime_validation: non_blank_only` on
  `proposeAppointmentCreate`.
- FastAPI binds `idempotency_key` with
  `Header(None, alias="Idempotency-Key")` on `propose_create_appointment`.
- FastAPI normalizes the key before proposal evidence is minted.
- OpenAPI `minLength: 8` is deliberately not enforced at runtime yet.

That last point is intentional. Sprint 150 established client discipline for
the first proposal-only route by rejecting missing or blank headers. It did not
make a client-compatibility decision to reject short non-blank keys.

Sprint 152 made that client-readiness decision and kept runtime `minLength: 8`
enforcement deferred. The decision is recorded in
`orchestration/api_spine_appointment_idempotency_create_proposal_minlength_readiness.md`.
The important evidence is that the real diary create-proposal caller still has
to prove the non-blank header path, and the sibling proposal handlers
`propose_update_appointment`, `propose_status_update`, and
`propose_delete_appointment` do not yet bind `Idempotency-Key` in FastAPI.

## Preserved Replay Model

The create-proposal route continues to use deterministic re-evaluation:

- no proposal ledger;
- no stored proposal replay;
- no same-key/different-body conflicts;
- no appointment writes;
- no audit writes;
- no slot reservations.

The `Idempotency-Key` is syntactic client discipline for proposal requests, not
confirmation-grade replay authority. Durable replay remains owned by the
proposal-confirm routes and their appointment command ledger.

## Guard Tests

`tests/test_api_spine_create_proposal_header_alignment.py` asserts:

- `/appointments/proposals/create` references the shared OpenAPI
  `IdempotencyKey` parameter;
- the shared parameter remains required and keeps the `8..128` documented
  header shape;
- the operation-level `x-emr4-proposal-header-posture` annotation records that
  runtime `minLength` enforcement is deferred;
- `propose_create_appointment` binds the header before calling
  `_build_create_appointment_proposal`;
- the runtime normalizer remains non-blank only until a separate
  client-compatibility decision changes it;
- the create-proposal route/helper do not call appointment command ledger
  helpers or reference `AppointmentCommandIdempotency`;
- all four canonical OpenAPI proposal operations keep referencing the shared
  `IdempotencyKey` parameter;
- the current FastAPI proposal-header binding gap is explicit for
  `propose_update_appointment`, `propose_status_update`, and
  `propose_delete_appointment`;
- the Sprint 152 minLength decision has named client-readiness preconditions;
- adjacent command gates remain closed.

`tests/test_api_spine_create_proposal_idempotency_route_contract.py` also proves
that a one-character non-blank key currently succeeds. That is intentional until
the client-readiness decision is made.

## Gates Still Closed

This sprint does not open:

- update/status/waiting-area/delete proposal idempotency enforcement;
- raw compatibility write idempotency enforcement;
- slot-search reservation or replay semantics;
- Bernie interpreter/session command idempotency expansion;
- provider calls;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Recommended Sprint 152

Choose the next proposal-only surface deliberately. The lowest-risk continuation
is either a client-readiness decision for enforcing OpenAPI `minLength: 8` on
create-proposal, or a preflight for update/status proposal-only header
discipline. Do not roll the shared header across raw compatibility writes by
default.

## Recommended Sprint 153

Close the concrete proposal-header readiness gap before tightening
`minLength`: either preflight/wire the real diary create-proposal caller to send
an 8+ character key, or preflight the next proposal-only route's non-blank
header discipline. Keep raw compatibility writes out of scope.
