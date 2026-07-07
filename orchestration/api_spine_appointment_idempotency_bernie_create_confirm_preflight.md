# API Spine Bernie Create-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 133 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Preflight/review only; no route behavior changed |
| Steward posture | Define the next confirmation-family idempotency boundary before widening HTTP `Idempotency-Key` enforcement |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_storage_design.md`
- `orchestration/api_spine_appointment_idempotency_route_integration_preflight.md`
- `orchestration/api_spine_appointment_idempotency_staff_create_confirm_route_tests.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_bernie_confirm_create_proposal.py`
- `tests/test_bernie_route_outcome_events.py`
- `tests/test_bernie_session_store.py`
- `tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py`

## Candidate Route

The next narrow confirmation family is:

- route: `POST /api/v1/appointments/proposals/create/confirm-bernie`;
- handler: `confirm_bernie_create_proposal`;
- typed body: `BernieCreateProposalConfirmationIn`, after manual validation from `Body(...)`;
- canonical operation id: `confirmAppointmentCreateProposal`;
- proposed route family label: `create-confirm-bernie`;
- writes today: one appointment plus bounded appointment audit evidence, and, when a server-session binding is present, Bernie `confirm_submitted` and `confirmation_outcome` session events.

The canonical operation id intentionally matches staff create-confirm because
both routes confirm the same semantic appointment-create proposal operation.
`route_family` stays distinct so audit/reporting can still identify the Bernie
surface.

## Do Not Wire Yet

Do not enforce HTTP `Idempotency-Key` on `confirm-bernie` until the next wiring
sprint resolves the session-event boundary below. Do not wire update, status,
delete, raw compatibility writes, proposal-only routes, slot-search routes,
Bernie session event routes, providers, GraphQL mutations, memory/RAG/GraphRAG,
H15/H-series runtime imports, or broad historical diary trove material as part
of this preflight.

## Extra Boundary Compared With Staff Create-Confirm

Staff create-confirm is a single database-backed appointment/audit transaction.
`confirm-bernie` has the same appointment confirmation concern plus a separate
server-owned Bernie session transition concern:

1. validation may return structured blocked confirmation output instead of HTTP errors;
2. optional `session_binding` validation may reject stale or mismatched Bernie session coordinates;
3. `confirm_submitted` is appended before the appointment write when bound session evidence is accepted;
4. `confirmation_outcome` is appended after blocked or confirmed outcomes;
5. the current session store has its own event idempotency keys and stale-revision rules.

Because the appointment ledger and Bernie session store are not one obvious
database transaction, the wiring sprint must state exactly how replay and
rollback interact with session events before implementation.

## Proposed Claim Order

The wiring sprint should start from this order, then adjust only if tests prove
another order is safer:

1. authenticate and authorize actor/practice;
2. require and normalize HTTP `Idempotency-Key`;
3. manually validate `BernieCreateProposalConfirmationIn`;
4. canonicalize the validated body using `model_dump(mode="json")`;
5. claim the appointment command ledger with operation id `confirmAppointmentCreateProposal` and route family `create-confirm-bernie`;
6. map replay/conflict/in-progress/stale/failed-transient decisions before session events, confirmation checks, appointment writes, or audit writes;
7. run existing Bernie validation, signed-evidence, freshness, entity, and session-binding checks;
8. append session events only for the transaction owner and only after the replay decision is known;
9. if a blocked response occurs after a started claim, roll back the appointment ledger claim unless the route deliberately stores blocked responses for replay in a separately reviewed policy;
10. on confirmed write, complete the ledger with the final response and target appointment id in the same database transaction as the appointment and audit write;
11. commit only after appointment/audit/ledger completion are durable;
12. return stored response on replay without re-appending Bernie session events or creating another appointment/audit row.

## Required Wiring Tests

Future route wiring must add executable tests for:

- missing `Idempotency-Key` blocks before appointment, audit, ledger, or Bernie session event mutation;
- invalid confirmation payload does not create a ledger row unless the wiring sprint explicitly chooses and tests replayable invalid responses;
- first confirmed Bernie create writes one appointment, one audit trail, one completed ledger row, and the expected session events when a binding is present;
- same-key/same-body replay returns the stored response without a second appointment, audit row, `confirm_submitted`, or `confirmation_outcome`;
- same-key/different-body returns `409 idempotency_key_conflict` without a second appointment, audit row, or session event;
- in-progress, stale-in-progress, and failed-transient rows fail closed without appointment, audit, or session event mutation;
- stale or mismatched `session_binding` remains fail-closed and is not bypassed by idempotency;
- confirmed write rollback cannot leave a completed ledger row without the appointment/audit result;
- stored-response replay is distinguishable from a new confirmed mutation in compliance telemetry.

## Open Implementation Decisions

- Should structured blocked Bernie confirmation responses after a started claim
  be replayable, or should they roll back the claim like staff create-confirm
  business-rule blocks? Default recommendation: roll back blocked claims until a
  separate policy approves replayable blocked outcomes.
- Should invalid manual body validation return `400` under idempotency wiring or
  preserve the current structured blocked `200` response? Default
  recommendation: preserve current response shape unless a dedicated API
  compatibility sprint changes it.
- Should Bernie session event replay telemetry be added now, or should replay
  avoid session-store mutation entirely and rely on the appointment ledger
  response? Default recommendation: replay must not append session events.

## Gates Still Closed

This preflight does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.

## Smallest Next Alignment Slice

Recommended Sprint 134:

**Bernie create-confirm idempotency route-test contract.**

Add guarded or executable tests for the `confirm-bernie` family based on this
preflight, especially the no-double-session-event replay cases, before adding
HTTP `Idempotency-Key` enforcement to the route.
