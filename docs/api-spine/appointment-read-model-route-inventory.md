# Appointment Read-Model Route Inventory

Date: 2026-07-08

Sprint: 202

## Purpose

This inventory links the appointment-first GraphQL read roots to existing
FastAPI appointment GET/read routes without creating a runtime resolver,
renaming routes, or opening any command surface.

It answers one narrow question: which current appointment-router read routes can
support the GraphQL appointment/diary/audit/Bernie read graph, and which read
roots or routes remain deliberately partial, external, or unmapped?

## Read Route Bridge

| GraphQL read surface | FastAPI GET route | Handler | Coverage | Route posture | Notes |
|---|---|---|---|---|---|
| `Query.viewer` | `none` | `none` | `external` | `read_model_only` | Viewer is resolved from authenticated principal/context, not an appointment-router route. |
| `Query.practice` | `none` | `none` | `external` | `read_model_only` | Practice/location/roster reads are outside this appointment-router slice. |
| `Query.patient` | `none` | `none` | `external` | `read_model_only` | Patient summaries belong to patient/clinical read surfaces, not the appointment router. |
| `Query.diary` | `GET /api/v1/appointments` | `list_appointments` | `partial` | `read_only_route` | Current route returns filtered appointment rows, not a full `DiaryDay` envelope. |
| `Query.diary.appointments` | `GET /api/v1/appointments` | `list_appointments` | `partial` | `read_only_route` | Appointment list can feed diary cards, but roster/resources/breaks remain separate read concerns. |
| `Query.diary.waitingAreas` | `GET /api/v1/appointments/waiting-room` | `get_waiting_room` | `partial` | `read_only_route` | Current waiting-room route is a bounded appointment list, not the full GraphQL waiting-area object graph. |
| `Query.diary.availabilityContext` | `GET /api/v1/appointments/slots/{practitioner_id}` | `get_available_slots` | `partial` | `read_only_route` | Per-practitioner slot read can inform availability context but does not reserve or propose slots. |
| `Query.appointment` | `GET /api/v1/appointments/{appointment_id}` | `get_appointment` | `full` | `read_only_route` | Direct single appointment read. |
| `Query.appointment.auditTrail` | `GET /api/v1/appointments/{appointment_id}/audit` | `get_appointment_audit` | `partial` | `read_only_route` | Appointment-scoped audit trail; general `AuditFilter` remains broader than this route. |
| `Query.bernieSession` | `GET /api/v1/appointments/bernie/sessions/active` | `get_active_bernie_session` | `partial` | `read_only_route` | Current route returns the active session for current practice/user/surface, not arbitrary session by id. |
| `Query.audit` | `GET /api/v1/appointments/{appointment_id}/audit` | `get_appointment_audit` | `partial` | `read_only_route` | GraphQL root is general audit filtering; current route is appointment-scoped. |
| `Query.directorySearch` | `none` | `none` | `external` | `read_model_only` | MBS/SNOMED/library lookup is outside this appointment-router slice. |
| `none` | `GET /api/v1/appointments/types` | `list_appointment_types` | `unmapped` | `read_only_route` | Reference vocabulary route; currently no dedicated GraphQL query root. |
| `none` | `GET /api/v1/appointments/{appointment_id}/checkin-defaults` | `get_checkin_defaults` | `unmapped` | `read_only_route` | Check-in context/defaults only; no native `check_in` command authority. |
| `none` | `GET /api/v1/appointments/bernie/pilot-eligibility` | `get_bernie_pilot_eligibility` | `unmapped` | `read_only_route` | Feature/pilot gate read, not appointment mutation authority. |

Coverage meanings:

- `full`: current GET route directly supports the named read surface.
- `partial`: current GET route supports part of the read surface, with a known
  shape or scope gap.
- `external`: read surface belongs to authentication, patient, practice,
  directory, or another future read model outside this appointment-router slice.
- `unmapped`: current appointment GET route is read-only but has no dedicated
  GraphQL root in this prototype.

## Outside The Read Graph

The following compatibility writes are deliberately outside the GraphQL read
graph and must not be bridged to a query root:

| Method and route | Handler | Classification | Read-graph status |
|---|---|---|---|
| `POST /api/v1/appointments` | `create_appointment` | `compatibility write` | `outside_read_graph` |
| `PUT /api/v1/appointments/{appointment_id}` | `update_appointment` | `compatibility write` | `outside_read_graph` |
| `PATCH /api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | `compatibility write` | `outside_read_graph` |
| `DELETE /api/v1/appointments/{appointment_id}` | `cancel_appointment` | `compatibility write` | `outside_read_graph` |

Proposal commands, confirm commands, command-style POST reads, and Bernie
session POST commands are also outside this read-route bridge. They remain
covered by the appointment command alignment inventory and the OpenAPI drift
guard, not by this GraphQL read-model route inventory.

## Closed Gates

This inventory does not authorize:

- proposal-only route idempotency enforcement;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- slot-search reservation or replay semantics;
- provider calls or live provider gates;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Boundary

This is a declaration-continuity artifact. It does not prove runtime resolver
implementation, schema conversion correctness, authorization policy,
performance, database access behavior, provider readiness, or production
deployment readiness.

`tests/test_api_spine_appointment_read_model_route_inventory.py` validates this
inventory by parsing only this markdown file,
`docs/api-spine/graphql/appointment-diary-read.graphql`,
`app/routers/appointments.py`, and
`tests/test_api_spine_appointment_openapi_drift_guard.py`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_read_model_route_inventory.py -q
```
