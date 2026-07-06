# API Spine Appointment Command Envelope Alignment Inventory

| Item | Value |
|---|---|
| Sprint | 121 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Inventory artifact only; no route behavior, schema, database, provider, or GraphQL wiring changed |
| Steward posture | Appointment-first, command-plane alignment, compatibility writes identified but not changed |

## Source Pass

Reviewed sources:

- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `orchestration/api_spine_post_sprint118_checkpoint.md`
- `orchestration/api_spine_programme.md`
- `orchestration/bernie_release_gates.md`
- `tests/test_api_spine_artifacts.py`

## Classification Legend

- `proposal command`: prepares a backend proposal, warning/block envelope, freshness or confirmation evidence, and no appointment write.
- `confirm command`: performs a write only after explicit confirmation and evidence checks.
- `command-style read`: accepts command-shaped input and returns normalized/search/selection evidence without writing appointments.
- `Bernie session command`: creates or appends bounded Bernie session state without appointment mutation authority.
- `compatibility write`: current legacy-compatible mutating route outside the proposal-confirm envelope.
- `read-only route`: returns current appointment, diary, audit, slot, or reference state without writing.

## Route Inventory

| Current FastAPI route | Handler | API Spine family | Classification | Alignment notes |
|---|---|---|---|---|
| `POST /api/v1/appointments/proposals/create` | `propose_create_appointment` | `proposeAppointmentCreate` | `proposal command` | Practice-scoped mutating-role surface; prepares warnings, blocks, `create_proposal_freshness_id`, `signed_confirmation_evidence`, confirm endpoint, and confirm payload; no appointment write. |
| `POST /api/v1/appointments/proposals/create/confirm` | `confirm_create_proposal_route` | `confirmAppointmentCreateProposal` | `confirm command` | Requires `confirmed=true`, safe proposal, freshness recomputation, signed confirmation evidence, warning acknowledgement, revalidation, and audit evidence before creating one appointment. |
| `POST /api/v1/appointments/proposals/update/{appointment_id}` | `propose_update_appointment` | `proposeAppointmentUpdate` | `proposal command` | Practice-scoped update/reschedule proposal; checks identity, conflicts, breaks, terminal status, temporal guard, warnings/blocks, freshness, signed evidence, and confirm payload; no appointment write. |
| `POST /api/v1/appointments/proposals/update/confirm` | `confirm_update_proposal_route` | `confirmAppointmentUpdateProposal` | `confirm command` | Confirms backend-prepared update evidence through the update confirmation path; write authority remains behind explicit confirmation and evidence checks. |
| `POST /api/v1/appointments/proposals/status/{appointment_id}` | `propose_status_update` | `proposeAppointmentStatus` | `proposal command` | Prepares status-change evidence with waiting-area side-effect visibility, warning/block envelope, freshness, signed evidence, and confirm payload; no appointment write. |
| `POST /api/v1/appointments/proposals/waiting-area/{appointment_id}` | `propose_waiting_area_update` | `proposeAppointmentStatus` | `proposal command` | Waiting-area proposal shares the status command family; prepares staff-review evidence and blocks/warnings without mutating appointment state. |
| `POST /api/v1/appointments/proposals/status-confirm` | `confirm_status_proposal_route` | `confirmAppointmentStatusProposal` | `confirm command` | Requires explicit confirmation, signed evidence, freshness/current-state revalidation, and audit evidence before status or waiting-area mutation. |
| `POST /api/v1/appointments/proposals/delete/{appointment_id}` | `propose_delete_appointment` | `proposeAppointmentDelete` | `proposal command` | Prepares delete/cancel proposal, always requires staff confirmation, includes freshness/signed evidence, and does not delete. |
| `POST /api/v1/appointments/proposals/delete-confirm` | `confirm_delete_proposal_route` | `confirmAppointmentDeleteProposal` | `confirm command` | Requires explicit confirmation, signed evidence, freshness/current-state revalidation, and audit evidence before delete/cancel mutation. |
| `POST /api/v1/appointments/proposals/slot-search/normalize` | `normalize_slot_search_proposal_command` | `normalizeSlotSearchCommand` | `command-style read` | Deterministic normalizer with explicit `reference_date`; no database lookup, slot search, provider call, audit write, or appointment mutation. |
| `POST /api/v1/appointments/proposals/slot-search` | `propose_slot_search` | `proposeSlotSearch` | `command-style read` | Practice-scoped schedule/conflict search; returns candidate slots, warnings, and no-slot context without reserving or writing an appointment. |
| `POST /api/v1/appointments/proposals/slot-search/normalized` | `propose_normalized_slot_search` | `proposeSlotSearch` plus normalization | `command-style read` | Normalizes first, then searches only if safe; blocked normalization avoids schedule evaluation and still performs no mutation. |
| `POST /api/v1/appointments/proposals/slot-search/selection` | `propose_slot_selection_for_create` | `selectSlotForCreateProposal` | `command-style read` | Validates selected slot evidence, then prepares create-proposal evidence; returned proposal still requires staff confirmation before any write. |
| `POST /api/v1/appointments/proposals/bernie/tool-intent` | `propose_bernie_tool_intent` | Bernie deterministic tool-intent wrapper around update proposal family | `command-style read` | Resolves supported Bernie diary wording into deterministic proposal evidence. V1 supports appointment extension only, never writes appointment state, and cannot bypass proposal/confirm contracts. |
| `POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction` | `interpret_bernie_booking_instruction` | Bernie booking-instruction interpretation | `command-style read` | Interprets staff booking text into structured intent without creating proposals, searching slots, confirming bookings, or writing appointments. Interpreter provider remains default-disabled/gate-controlled; live mode may persist bounded Access AI audit metadata only. |
| `POST /api/v1/appointments/proposals/bernie/supervised-booking` | `propose_bernie_supervised_booking` | Bernie supervised wrapper around slot-search and create proposal families | `command-style read` | Normalizes, searches, and optionally builds existing create-proposal evidence for staff review; does not confirm, create, audit, call LLMs, or invoke providers. |
| `POST /api/v1/appointments/proposals/create/confirm-bernie` | `confirm_bernie_create_proposal` | Bernie-specific create confirmation variant | `confirm command` | Confirmation-grade Bernie booking write surface; should be treated as a create-confirm family variant, not a separate provider authority path. |
| `POST /api/v1/appointments/proposals/bernie/no-slot-suggestion-selection` | `select_no_slot_suggestion` | Bernie no-slot next-request preparation | `command-style read` | Validates staff selection of a prior no-slot suggestion and returns a pre-populated supervised-booking request; caller must submit that request to supervised booking to search slots. |
| `GET /api/v1/appointments/bernie/pilot-eligibility` | `get_bernie_pilot_eligibility` | Bernie pilot eligibility read | `read-only route` | Evaluates feature/user/practice allowlist posture only; no appointment, provider, or session mutation. |
| `GET /api/v1/appointments/bernie/sessions/active` | `get_active_bernie_session` | Bernie session state read | `read-only route` | Returns or reuses active bounded Bernie session state for the current practice/user/surface; no appointment mutation authority. |
| `POST /api/v1/appointments/bernie/sessions/new` | `create_new_bernie_session` | Bernie session lifecycle | `Bernie session command` | Creates bounded Bernie session state for the current practice/user/surface; this is not appointment write authority and does not create proposals or bookings. |
| `POST /api/v1/appointments/bernie/sessions/{session_id}/events` | `append_bernie_session_event` | Bernie session lifecycle | `Bernie session command` | Appends bounded client session events with owner/surface/revision/idempotency checks; this is session-state bookkeeping, not appointment mutation authority. |
| `POST /api/v1/appointments` | `create_appointment` | legacy compatibility create | `compatibility write` | Uses `raw_compat_create` evidence/header posture and mutates directly through the compatibility path; outside proposal-confirm envelope. |
| `PUT /api/v1/appointments/{appointment_id}` | `update_appointment` | legacy compatibility update | `compatibility write` | Current direct update compatibility path; outside proposal-confirm envelope and should stay visible in alignment/deprecation planning. |
| `PATCH /api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | legacy compatibility status | `compatibility write` | Current direct status compatibility path; outside proposal-confirm envelope and should stay visible in alignment/deprecation planning. |
| `DELETE /api/v1/appointments/{appointment_id}` | `cancel_appointment` | legacy compatibility delete | `compatibility write` | Uses `raw_compat_delete` evidence/header posture and mutates directly through the compatibility path; outside proposal-confirm envelope. |
| `GET /api/v1/appointments/types` | `list_appointment_types` | reference read | `read-only route` | Appointment type vocabulary only. |
| `GET /api/v1/appointments` | `list_appointments` | diary read model | `read-only route` | Appointment list read filtered by tenant/date/practitioner/patient/status/location. |
| `GET /api/v1/appointments/{appointment_id}` | `get_appointment` | appointment read model | `read-only route` | Single appointment read. |
| `GET /api/v1/appointments/{appointment_id}/checkin-defaults` | `get_appointment_checkin_defaults` | check-in context read | `read-only route` | Context/defaults only; no native `check_in` command authority yet. |
| `GET /api/v1/appointments/{appointment_id}/audit` | `get_appointment_audit` | audit read model | `read-only route` | Audit trail read only. |
| `GET /api/v1/appointments/waiting-room` | `list_waiting_room` | waiting-room read model | `read-only route` | Waiting-room state read only. |
| `GET /api/v1/appointments/slots/{practitioner_id}` | `list_available_slots` | availability read model | `read-only route` | Slot availability read; proposal or confirmation routes remain separate. |

## Alignment Findings

- The current FastAPI surface already has proposal-confirm families for create, update, status/waiting-area, and delete/cancel writes.
- Slot-search normalize/search/normalized/selection routes match the API Spine command-style read posture: command-shaped input, deterministic evidence, and no booking write.
- Bernie intent, interpretation, supervised booking, no-slot selection, and session routes are appointment-adjacent surfaces in the appointments router. They do not create appointment write authority by themselves; the session routes maintain bounded session state, and interpreter provider mode remains default-disabled/gate-controlled.
- Current backend confirm route names differ from the OpenAPI draft for several canonical paths:
  - backend `POST /api/v1/appointments/proposals/status-confirm` vs OpenAPI `/appointments/proposals/status/confirm`;
  - backend `POST /api/v1/appointments/proposals/delete-confirm` vs OpenAPI `/appointments/proposals/delete/confirm`;
  - backend `POST /api/v1/appointments/proposals/slot-search/selection` vs OpenAPI `/appointments/proposals/slot-search/select`.
- Bernie-specific intent/session/supervised routes and `POST /api/v1/appointments/proposals/create/confirm-bernie` are not represented explicitly in the Sprint 101 OpenAPI draft.
- The OpenAPI draft requires `Idempotency-Key` for mutating or confirmation-grade command attempts. Current FastAPI proposal/confirmation handlers expose freshness and signed-evidence checks, but this inventory does not prove route-level idempotency-key enforcement.
- Compatibility writes remain present for create, update, status, and delete. They are useful for existing clients, but they are not the API Spine target envelope.

## Smallest Next Alignment Slice

Recommended Sprint 122:

**Appointment command OpenAPI drift guard.**

Add a non-invasive static guard that keeps this inventory, the current
`app/routers/appointments.py` route strings, and
`docs/api-spine/openapi/appointment-commands.yaml` aligned. The guard should
record the current canonical-path mismatches as deliberate drift entries rather
than changing runtime routes. Once that guard is stable, the next implementation
choice can be either:

- update the OpenAPI draft to include backend compatibility aliases and
  Bernie-specific supervised/confirm variants; or
- introduce backend route aliases for the cleaner canonical OpenAPI names while
  preserving existing compatibility paths.

## Gates Still Closed

This inventory does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.
