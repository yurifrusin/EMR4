# API Spine Appointment Idempotency Route Integration Preflight

| Item | Value |
|---|---|
| Sprint | 130 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Route integration preflight only; no appointment route wiring changed |
| Steward posture | Define the first safe route-wiring contract before HTTP `Idempotency-Key` enforcement |

## First Route Family

The first route family should be:

- route: `POST /api/v1/appointments/proposals/create/confirm`;
- handler: `confirm_create_proposal_route`;
- canonical operation id: `confirmAppointmentCreateProposal`;
- route family: `create-confirm`;
- helper: `claim_appointment_command()` before any appointment mutation and
  `complete_appointment_command()` after appointment/audit success.

Do not wire `confirm-bernie`, update, status, delete, raw compatibility writes,
or proposal-only routes in the same sprint as the first staff create-confirm
integration.

## Required Route Order

The route implementation must follow this order:

1. authenticate and authorize actor/practice;
2. require and normalize HTTP `Idempotency-Key`;
3. build the typed confirmation request body used for canonical hashing;
4. call `claim_appointment_command()` before `_create_appointment_record()` or
   `_write_audit()`;
5. map `replay` to the stored response without running confirmation checks or
   writing a second appointment;
6. map `conflict` to `409 idempotency_key_conflict`;
7. map `in_progress` to `409 idempotency_key_in_progress` or `425 too_early`;
8. map `stale_in_progress` to a fail-closed response; no overwrite behavior is
   approved in this preflight;
9. map `failed_transient` to a fail-closed retry/escalation response; no silent
   retry is approved in this preflight;
10. run existing signed-evidence, freshness, conflict, role/tenant, warning,
    and current-state checks only for `started`;
11. perform appointment write, audit write, and
    `complete_appointment_command()` inside the same database transaction;
12. commit only after appointment, audit, and ledger completion are durable.

If a `started` claim is followed by a business-rule failure, the route must
roll back the transaction or otherwise remove the in-progress claim before
returning. A blocked freshness, signed-evidence, warning, role/tenant, or
current-state check must not leave an orphaned `in_progress` row.

## Fail-Closed Response Map

Sprint 131 route tests should use these provisional mappings unless a later
review changes them:

| Helper decision | HTTP status | Response code |
|---|---:|---|
| `replay` | Stored status | Stored response body |
| `conflict` | 409 | `idempotency_key_conflict` |
| `in_progress` | 409 or 425 | `idempotency_key_in_progress` |
| `stale_in_progress` | 409 | `idempotency_key_stale_in_progress` |
| `failed_transient` | 503 | `idempotency_key_failed_transient` |

`expires_at` remains unused for confirmation-write rows because completed
confirmation replay evidence is authoritative audit-adjacent evidence and must
not silently expire by default. Any TTL or cleanup behavior requires a later
reviewed policy change.

Proposal-only route idempotency remains a separate concern. This preflight
targets only the confirm step; `POST /api/v1/appointments/proposals/create`
must not be silently pulled into the first route wiring sprint.

## Required Route Tests Before Wiring

A future wiring sprint must add tests proving:

- missing `Idempotency-Key` blocks before writing;
- first confirmed create writes one appointment, one audit row, and one
  completed ledger row;
- same-key/same-body replay returns the same stored response and writes no
  second appointment or audit row;
- same-key/different-body returns `409 idempotency_key_conflict`;
- same-key active in-progress returns `409 idempotency_key_in_progress` or
  `425 too_early`;
- stale `in_progress` returns the selected fail-closed response and writes no
  second appointment;
- `failed_transient` returns the selected fail-closed response and writes no
  second appointment;
- freshness, signed evidence, warning acknowledgement, and role/tenant checks
  still run for the first execution and are not bypassed by idempotency.
- business-rule failures after a started claim roll back or remove the claim;
- proposal-only create route behavior remains unchanged and separately tracked.

## Still Not Implemented

Sprint 130 does not:

- bind HTTP `Idempotency-Key` in appointment routes;
- import `AppointmentCommandIdempotency` or `appointment_idempotency` from
  `app/routers/appointments.py`;
- change proposal or confirmation responses;
- change database transaction behavior;
- add provider calls, GraphQL mutations, runtime FGA clients, external patient
  clients, H15/H-series runtime imports, memory/RAG/GraphRAG, broad trove
  mining, or additional model-to-database writes.

## Smallest Next Alignment Slice

Recommended Sprint 131:

**Staff create-confirm idempotency route tests.**

Add failing or guarded route-level tests for the staff create-confirm family
before implementing the route wiring. Keep Bernie/update/status/delete/raw
families out of scope until the first family is green.
