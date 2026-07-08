# External Router Read-Root Inventory

Date: 2026-07-08

Sprint: 205

## Purpose

This inventory follows Sprint 202's appointment-router read-model inventory by
mapping the GraphQL read roots that were marked `external` to current
non-appointment router read surfaces.

It covers only these GraphQL roots:

- `Query.viewer`
- `Query.practice`
- `Query.patient`
- `Query.directorySearch`

The inventory is static declaration continuity. It does not create GraphQL resolvers,
does not create GraphQL runtime resolvers, change route behavior, import routers
at runtime, execute handlers, or grant write authority.

## External Read Route Bridge

| GraphQL read surface | Current read source | Handler/source symbol | Coverage | Route posture | Notes |
|---|---|---|---|---|---|
| `Query.viewer` | `GET /api/v1/auth/me` | `get_me` | `partial` | `read_only_route` | Current auth read returns user id, email, role, and practice id; GraphQL `Viewer` also reserves practice object, practitioner link, environment posture, feature flags, and capability hints. |
| `Query.viewer.environment` | `none` | `none` | `gap` | `read_model_gap` | No dedicated safe environment-posture read route exists yet. |
| `Query.viewer.featureFlags` | `none` | `none` | `gap` | `read_model_gap` | No dedicated feature-flag read route exists yet. |
| `Query.viewer.capabilities` | `none` | `none` | `gap` | `read_model_gap` | Capability hints remain a future read-model surface, not runtime FGA authority. |
| `Query.practice` | `GET /api/v1/diary/locations` | `get_locations` | `partial` | `read_only_route` | Practice root can begin with location reads but no single full `Practice` envelope exists. |
| `Query.practice.locations` | `GET /api/v1/diary/locations` | `get_locations` | `full` | `read_only_route` | Current route lists active practice-scoped locations. |
| `Query.practice.rooms` | `GET /api/v1/diary/rooms` | `get_rooms` | `partial` | `read_only_route` | Current route lists rooms and default waiting-area links; GraphQL room edges also expect location object expansion. |
| `Query.practice.waitingAreas` | `GET /api/v1/diary/waiting-areas` | `get_waiting_areas` | `partial` | `read_only_route` | Current route lists waiting areas; GraphQL also reserves `currentSummary`. |
| `Query.practice.diaryTemplates` | `GET /api/v1/diary/template` | `get_diary_template` | `partial` | `read_only_route` | Current route returns the current template shape, including fallback JSON; GraphQL reserves object-linked template fields. |
| `Query.practice.roster` | `GET /api/v1/diary/roster` | `get_diary_roster` | `partial` | `read_only_route` | Current route returns date/location roster entries; GraphQL reserves linked location, room, and practitioner objects. |
| `Query.practice.appointmentTypes` | `GET /api/v1/appointments/types` | `list_appointment_types` | `partial` | `read_only_route` | Appointment type vocabulary currently lives in the appointment router and remains read-only. |
| `Query.practice.practitioners` | `none` | `none` | `gap` | `read_model_gap` | No dedicated practitioner directory read route exists yet; existing template/roster reads may carry practitioner identifiers but not the full `Practitioner` graph. |
| `Query.patient` | `GET /api/v1/patients/{patient_id}` | `get_patient` | `partial` | `read_only_route` | Current route returns patient demographics for the authenticated practice; GraphQL `Patient` also reserves document, clinical, booking, reminder, and message subgraphs. |
| `Query.patient.clinicalSummary` | `GET /api/v1/patients/{patient_id}/summary` | `get_patient_summary` | `partial` | `read_only_route` | Current summary covers active diagnoses, medications, allergies, and recent encounters. |
| `Query.patient.clinicalSummary.allergies` | `GET /api/v1/patients/{patient_id}/allergies` | `list_allergies` | `partial` | `read_only_route` | Current route lists allergy rows; GraphQL uses a compact `ClinicalSummaryItem` shape. |
| `Query.patient.clinicalSummary.activeProblems` | `GET /api/v1/patients/{patient_id}/history` | `list_history` | `partial` | `read_only_route` | Current history read can inform the clinical summary but is not a GraphQL resolver implementation. |
| `Query.patient.clinicalSummary.activeMedications` | `GET /api/v1/patients/{patient_id}/medications` | `list_medications` | `partial` | `read_only_route` | Current route lists active medications. |
| `Query.patient.clinicalSummary.lastEncounterAt` | `GET /api/v1/patients/{patient_id}/encounters` | `list_encounters` | `partial` | `read_only_route` | Current route lists recent encounters; GraphQL reserves a summary timestamp. |
| `Query.patient.document` | `GET /api/v1/patients/{patient_id}` | `get_patient` | `partial` | `read_only_route` | Current patient read includes document-link fields but not a dedicated document metadata graph. |
| `Query.patient.recentAppointments` | `GET /api/v1/appointments` | `list_appointments` | `partial` | `read_only_route` | Patient-specific appointment lists remain covered by the appointment read-model inventory. |
| `Query.patient.futureAppointments` | `GET /api/v1/appointments` | `list_appointments` | `partial` | `read_only_route` | Future appointment filtering is route-supported by query parameters, not a GraphQL resolver. |
| `Query.patient.bookingContext` | `app/services/bernie_patient_context.py` | `build_patient_booking_context` | `partial` | `service_read_model` | Current patient booking context is a backend service used by Bernie; it is not exposed as a standalone read route. |
| `Query.patient.reminders` | `none` | `none` | `gap` | `read_model_gap` | No patient reminder read route is currently mapped in this slice. |
| `Query.patient.messages` | `none` | `none` | `gap` | `read_model_gap` | No patient message read route is currently mapped in this slice. |
| `Query.directorySearch` | `GET /api/v1/search-mbs` | `search_mbs` | `partial` | `read_only_route` | Current MBS lookup is a read route over the local directory table. |
| `Query.directorySearch` | `GET /api/v1/search-snomed` | `search_snomed` | `partial` | `read_only_route` | Current SNOMED lookup is a read route over the local directory table. |
| `Query.directorySearch.RACGP_GUIDELINES` | `none` | `none` | `gap` | `read_model_gap` | No RACGP guideline lookup route is implemented. |
| `Query.directorySearch.COCHRANE_LIBRARY` | `none` | `none` | `gap` | `read_model_gap` | No Cochrane lookup route is implemented. |

Coverage meanings:

- `full`: current read route directly supports the named read surface.
- `partial`: current read route or source supports part of the read surface,
  with a known shape or scope gap.
- `gap`: the GraphQL SDL reserves the surface, but no current read route/source
  is mapped in this inventory.

Route posture meanings:

- `read_only_route`: a current GET route can supply read-model data.
- `service_read_model`: a current backend service can supply read-model data but
  is not a standalone HTTP read route.
- `read_model_gap`: no current read route/source is mapped.

## Deliberate Exclusions

This inventory does not map:

- patient create/update or patient-file generation commands;
- clinical allergy/history/care-plan/consent writes;
- diary room/waiting-area mutation routes;
- appointment proposal commands, confirm commands, command-style POST reads, or
  raw compatibility writes;
- Access AI invocation, provider prompt, provider response, or provider dry-run
  surfaces;
- practice-knowledge advisory retrieval as directory authority.

practice-knowledge facts may remain advisory frames through their existing
service boundary. They do not become `Query.directorySearch`, availability
facts, booking policy, confirmation authority, or GraphQL write authority in
this sprint.

## Closed Gates

This inventory does not authorize:

- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- model-to-database writes outside REST command handlers;
- any raw compatibility deprecation mode change.

## Boundary

This is a declaration-continuity artifact. It does not prove runtime GraphQL
resolver implementation, schema conversion correctness, authorization policy,
performance, database access behavior, provider readiness, patient-facing
client readiness, or production deployment readiness.

`tests/test_api_spine_external_router_read_root_inventory.py` validates this
inventory by parsing only this markdown file,
`docs/api-spine/graphql/appointment-diary-read.graphql`, selected `app/routers`
source files, `app/services/bernie_patient_context.py`, and the existing
appointment read-model route inventory test at
`tests/test_api_spine_appointment_read_model_route_inventory.py`.

The selected router sources are:

- `app/routers/auth.py`
- `app/routers/appointments.py`
- `app/routers/clinical.py`
- `app/routers/diary.py`
- `app/routers/patients.py`
- `app/routers/search.py`

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_router_read_root_inventory.py -q
```
