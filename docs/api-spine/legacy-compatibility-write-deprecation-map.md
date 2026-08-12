# Legacy Compatibility Write Deprecation Map

Date: 2026-07-08

Sprint: 204

## Purpose

This map records the legacy appointment compatibility writes that still mutate
appointment state outside the proposal-confirm command envelope, and names the
existing proposal/confirm families that should become their replacement path.

It is a declaration and deprecation-planning artifact only. It does not change
route behavior, remove compatibility routes, enforce new idempotency on raw
routes, or open any GraphQL mutation or provider surface.

## Compatibility Write Map

| Compatibility write | Handler | Raw compatibility tag | Replacement proposal route | Replacement confirm route | Read-model witness routes | Deprecation posture |
|---|---|---|---|---|---|
| `POST /api/v1/appointments` | `create_appointment` | `raw_compat_create` | `POST /api/v1/appointments/proposals/create` | `POST /api/v1/appointments/proposals/create/confirm`; `POST /api/v1/appointments/proposals/create/confirm-bernie` | `GET /api/v1/appointments`; `GET /api/v1/appointments/{appointment_id}`; `GET /api/v1/appointments/{appointment_id}/audit` | `compatibility_supported_until_client_parity` |
| `PUT /api/v1/appointments/{appointment_id}` | `update_appointment` | `raw_compat_update` | `POST /api/v1/appointments/proposals/update/{appointment_id}`; `POST /api/v1/appointments/proposals/bernie/tool-intent` | `POST /api/v1/appointments/proposals/update/confirm` | `GET /api/v1/appointments/{appointment_id}`; `GET /api/v1/appointments/{appointment_id}/audit` | `compatibility_supported_until_client_parity` |
| `PATCH /api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | `raw_compat_status` | `POST /api/v1/appointments/proposals/status/{appointment_id}`; `POST /api/v1/appointments/proposals/waiting-area/{appointment_id}` | `POST /api/v1/appointments/proposals/status-confirm` | `GET /api/v1/appointments/{appointment_id}`; `GET /api/v1/appointments/waiting-room`; `GET /api/v1/appointments/{appointment_id}/audit` | `compatibility_supported_until_client_parity` |
| `DELETE /api/v1/appointments/{appointment_id}` | `cancel_appointment` | `raw_compat_delete` | `POST /api/v1/appointments/proposals/delete/{appointment_id}` | `POST /api/v1/appointments/proposals/delete-confirm` | `GET /api/v1/appointments/{appointment_id}`; `GET /api/v1/appointments/{appointment_id}/audit` | `compatibility_supported_until_client_parity` |

## Current Raw Compatibility Signal

The existing `_raw_compat_evidence_and_headers()` helper is the current
compatibility signal. Its setting is
`settings.appointment_raw_compat_mode`, with default mode `audit`:

| Mode | Current meaning | Deprecation status |
|---|---|---|
| `audit` | attach the `raw_compat_*` evidence tag only | current default |
| `header` | attach the `raw_compat_*` evidence tag and `Deprecation` response header | available, not enabled by this map |
| `off` | suppress both raw compatibility evidence and deprecation headers | allowed only as an explicit compatibility/debug posture, not a migration target |

Changing this setting is outside this sprint. A future move from `audit` to
`header`, or any attempt to remove a raw compatibility route, needs separate
release-gate evidence and explicit review.

## Deprecation Preconditions

Every compatibility write must remain supported until all of these conditions
are proven for its replacement family:

- the human Diary UI path emits the proposal route, not the raw compatibility
  write, for the ordinary staff workflow;
- the confirm route requires explicit staff confirmation where the action is
  mutating or destructive;
- the confirm route echoes backend-provided freshness or signed evidence and
  revalidates before writing;
- route-level idempotency posture is documented for the replacement family;
- raw compatibility signal mode remains documented, with default `audit`;
- audit evidence remains attributable to the authenticated actor, practice,
  action family, and appointment target;
- read-model witnesses can show the resulting appointment and appointment audit
  state without using GraphQL mutations;
- import, migration, recovery, or other system-level compatibility needs have a
  separate explicit path before the raw route is retired;
- receptionist-facing and backend tests cover the replacement path before any
  client is redirected away from the compatibility route.

## Current Non-Deprecation Decision

The current decision is `map_only`.

No route is deprecated in code by this artifact. The compatibility writes stay
visible as legacy-supported surfaces while the proposal-confirm families remain
the preferred API Spine path for ordinary product clients and Bernie-authored
actions.

## Conditional-command reorientation (2026-08-12)

The target migration now has an additional invariant: all four compatibility
writes must converge internally on the same backend-owned conditional-command
kernel as their proposal/confirm replacements before removal. This architecture
does not change current route behavior.

- update, status and delete must lock and recheck the current appointment;
- create must serialize and recheck the relevant schedule-conflict domain,
  because there is no pre-existing appointment row to lock;
- current authority must be checked inside the mutation transaction;
- backend freshness/precondition evidence, human or policy confirmation,
  idempotency and audit must remain distinct; and
- stale, schedule-conflict, revoked-authority, confirmation-required,
  validation and idempotency-conflict results must fail closed with no mutation.

An implicit backend freshness check is therefore part of the desired common
kernel. It is not implicit human confirmation: a route whose action requires
confirmation must present separate valid confirmation evidence or return a
typed `confirmation_required` result.

## Boundary

This map does not authorize:

- removing, renaming, blocking, or changing compatibility write routes;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- proposal-only route idempotency expansion;
- GraphQL mutations;
- provider prompt wiring or live provider calls;
- provider dry-run wiring;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports;
- historical diary material access;
- broad historical diary trove mining;
- external patient clients;
- runtime FGA clients;
- direct database writes by model output;
- model-to-database writes outside REST command handlers.

## Source Artifacts

This map is validated against:

- `tests/test_api_spine_appointment_openapi_drift_guard.py`;
- `orchestration/api_spine_appointment_command_alignment_inventory.md`;
- `docs/api-spine/appointment-read-model-route-inventory.md`;
- `orchestration/api_spine_adr.md`;
- `docs/api-spine/blueprint-first-model-second-boundary.md`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
```
