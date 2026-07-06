# API Spine Appointment Idempotency-Key Gap Inspection

| Item | Value |
|---|---|
| Sprint | 124 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Inspection artifact only; no route behavior, schema, database, provider, or GraphQL wiring changed |
| Steward posture | OpenAPI command-plane requirement identified; FastAPI enforcement not implemented yet |

## Source Pass

Reviewed sources:

- `docs/api-spine/openapi/appointment-commands.yaml`
- `orchestration/api_spine_appointment_command_alignment_inventory.md`
- `tests/test_api_spine_appointment_openapi_drift_guard.py`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/bernie/session_store.py`
- `tests/test_bernie_session_store.py`
- `tests/test_bernie_session_routes.py`

## OpenAPI Requirement

The Sprint 101 OpenAPI draft defines `components.parameters.IdempotencyKey` as
a required `Idempotency-Key` header for mutating or confirmation-grade command
attempts. The current OpenAPI `paths:` use that header on these canonical
appointment command routes:

| OpenAPI path | Operation | Current backend route family | Current enforcement status |
|---|---|---|---|
| `POST /appointments/proposals/create` | `proposeAppointmentCreate` | `POST /api/v1/appointments/proposals/create` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/create/confirm` | `confirmAppointmentCreateProposal` | `POST /api/v1/appointments/proposals/create/confirm` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/update` | `proposeAppointmentUpdate` | `POST /api/v1/appointments/proposals/update/{appointment_id}` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/update/confirm` | `confirmAppointmentUpdateProposal` | `POST /api/v1/appointments/proposals/update/confirm` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/status` | `proposeAppointmentStatus` | `POST /api/v1/appointments/proposals/status/{appointment_id}` and `POST /api/v1/appointments/proposals/waiting-area/{appointment_id}` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/status/confirm` | `confirmAppointmentStatusProposal` | `POST /api/v1/appointments/proposals/status-confirm` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/delete` | `proposeAppointmentDelete` | `POST /api/v1/appointments/proposals/delete/{appointment_id}` | `missing_http_header_enforcement` |
| `POST /appointments/proposals/delete/confirm` | `confirmAppointmentDeleteProposal` | `POST /api/v1/appointments/proposals/delete-confirm` | `missing_http_header_enforcement` |

The command-style read slot-search paths intentionally use only
`X-Correlation-Id` in the OpenAPI draft and are outside this idempotency-key
gap unless a future policy changes that posture.

## Current FastAPI State

`app/routers/appointments.py` currently has no `Header(...)` binding and no
`Idempotency-Key` HTTP-header enforcement for appointment proposal,
confirmation, compatibility write, or slot-search routes.

Existing safety controls are valuable but not equivalent to HTTP idempotency:

- proposal freshness ids detect stale proposal evidence;
- signed confirmation evidence binds staff review evidence to proposal content;
- explicit `confirmed=true` gates irreversible confirmation writes;
- raw compatibility routes carry `raw_compat_*` audit/header posture;
- Bernie session event routes and server outcome events have session-scoped
  body idempotency fields.

Those controls do not provide a durable appointment-command replay ledger that
binds `Idempotency-Key` to actor, practice, operation, and request body hash as
described by the OpenAPI parameter.

## Compatibility Write Gap

The raw compatibility write routes are not part of the canonical OpenAPI
command `paths:`, but they still mutate appointment state:

- `POST /api/v1/appointments`
- `PUT /api/v1/appointments/{appointment_id}`
- `PATCH /api/v1/appointments/{appointment_id}/status`
- `DELETE /api/v1/appointments/{appointment_id}`

Sprint 124 does not decide whether these legacy routes should require
`Idempotency-Key`, expose a weaker compatibility warning, or be retired behind
the proposal-confirm envelope. That decision should be made before any
behavioral implementation.

## Non-Equivalence Boundary

Bernie session idempotency is intentionally scoped to session events and
server-owned outcome events. It is useful for turn/session replay safety, but it
does not satisfy appointment command-plane `Idempotency-Key` enforcement.

Likewise, OpenAPI metadata from Sprint 123 documents backend aliases and Bernie
variants only. It does not create route aliases, idempotency stores, or runtime
headers.

## Smallest Next Alignment Slice

Recommended Sprint 125:

**Appointment command idempotency policy packet.**

Define the behavior before implementation:

- which proposal routes require `Idempotency-Key`;
- which confirmation routes require `Idempotency-Key`;
- whether raw compatibility writes require, warn, or remain exempt during
  deprecation;
- where the replay ledger lives;
- how the key binds to actor, practice, operation, and request body hash;
- how conflicts, replays, stale proposal evidence, signed confirmation evidence,
  and audit records interact;
- how tests will prove no duplicate appointment write on replay.

## Gates Still Closed

This inspection does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.
