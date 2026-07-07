# API Spine Appointment Idempotency Confirmation-Family Integration Tests

| Item | Value |
|---|---|
| Sprint | 146 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | Cross-family route-level integration proof only |
| Runtime posture | No route behavior changed |

## Purpose

Sprint 145 recorded that all five proposal-confirm appointment mutation
families are wired to the appointment command idempotency ledger. Sprint 146
adds one DB-backed integration matrix to prove their shared behavior through
the actual FastAPI routes rather than only through per-family contract suites.

## Covered Confirmation Families

| Family | Route | Operation ID | Route family |
|---|---|---|---|
| Staff create confirm | `POST /api/v1/appointments/proposals/create/confirm` | `confirmAppointmentCreateProposal` | `create-confirm` |
| Bernie create confirm | `POST /api/v1/appointments/proposals/create/confirm-bernie` | `confirmAppointmentCreateProposal` | `create-confirm-bernie` |
| Status confirm | `POST /api/v1/appointments/proposals/status-confirm` | `confirmAppointmentStatusProposal` | `status-confirm` |
| Update confirm | `POST /api/v1/appointments/proposals/update/confirm` | `confirmAppointmentUpdateProposal` | `update-confirm` |
| Delete confirm | `POST /api/v1/appointments/proposals/delete-confirm` | `confirmAppointmentDeleteProposal` | `delete-confirm` |

## Executable Matrix

`tests/test_api_spine_confirmation_family_idempotency_integration.py` drives
each family through these shared route-level cases:

1. missing `Idempotency-Key` fails closed before appointment, audit, ledger, or
   Bernie session-event side effects;
2. same-key/same-body replay returns the stored response without a second
   appointment, audit, ledger, or Bernie session-event side effect;
3. same-key/different-body conflict returns `409 idempotency_key_conflict`
   without a second side effect;
4. active `in_progress` rows return `409 idempotency_key_in_progress`;
5. stale `in_progress` rows return `409 idempotency_key_stale_in_progress`;
6. `failed_transient` rows return
   `503 idempotency_key_failed_transient`.

The test also checks that completed ledger rows retain the expected operation
ID, route family, state, and stored response body.

## Boundary Preserved

This sprint deliberately does not add or approve:

- proposal-only route idempotency enforcement;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- slot-search reservation/replay semantics;
- provider calls, live-provider gates, or Access AI invocation changes;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Next Decision

The confirmation-family command surface now has both per-family contract tests
and cross-family route-level integration tests. The next sprint should be a
policy/preflight decision before expanding scope:

- proposal-only appointment route idempotency;
- raw compatibility write idempotency and deprecation posture;
- or a broader command-surface idempotency audit outside appointments.

Do not open more than one of those surfaces in the same sprint.
