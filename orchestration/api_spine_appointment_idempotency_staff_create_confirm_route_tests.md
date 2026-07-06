# API Spine Staff Create-Confirm Idempotency Route Tests

| Item | Value |
|---|---|
| Sprint | 131 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Guarded route-test contract only; route implementation still unwired |
| Steward posture | Define deterministic staff create-confirm route tests before enabling HTTP `Idempotency-Key` |

## Route Family Under Test

Only this family is in scope:

- route: `POST /api/v1/appointments/proposals/create/confirm`;
- handler: `confirm_create_proposal_route`;
- canonical operation id: `confirmAppointmentCreateProposal`;
- route family: `create-confirm`;
- helper calls: `claim_appointment_command()` and
  `complete_appointment_command()`.

Out of scope for this route-test slice:

- `POST /api/v1/appointments/proposals/create/confirm-bernie`;
- update/status/delete confirmation routes;
- raw compatibility writes;
- proposal-only `POST /api/v1/appointments/proposals/create`;
- slot-search and Bernie command-style reads.

## Future Executable Test Cases

The route wiring sprint must turn on deterministic tests for:

1. missing `Idempotency-Key` returns a fail-closed error before appointment or
   audit writes;
2. first confirmed create with a key writes exactly one appointment, one audit
   row, and one completed ledger row;
3. same-key/same-body replay returns the stored response and writes no second
   appointment or audit row;
4. same-key/different-body returns `409 idempotency_key_conflict`;
5. same-key active in-progress returns `409 idempotency_key_in_progress` or
   `425 too_early`;
6. stale `in_progress` returns `409 idempotency_key_stale_in_progress` and
   writes no second appointment;
7. `failed_transient` returns `503 idempotency_key_failed_transient` and writes
   no second appointment;
8. freshness, signed evidence, warning acknowledgement, and role/tenant checks
   still run for first execution;
9. business-rule failures after a started claim roll back or remove the claim;
10. proposal-only create route behavior remains unchanged.

## Activation Rule

The guarded tests in
`tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py` must
remain skipped until Sprint 132 or later wires the route. When wiring begins,
remove the skip markers and make the tests execute against the real route.

## Still Not Implemented

Sprint 131 does not:

- bind HTTP `Idempotency-Key` in appointment routes;
- import `appointment_idempotency` from `app/routers/appointments.py`;
- change proposal or confirmation responses;
- change database transaction behavior;
- add provider calls, GraphQL mutations, runtime FGA clients, external patient
  clients, H15/H-series runtime imports, memory/RAG/GraphRAG, broad trove
  mining, or additional model-to-database writes.

## Smallest Next Alignment Slice

Recommended Sprint 132:

**Staff create-confirm route idempotency wiring.**

Wire only the staff create-confirm route and make the guarded tests executable.
Keep Bernie/update/status/delete/raw/proposal-only families out of scope.
