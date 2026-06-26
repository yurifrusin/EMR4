# plan-claude-claude-claude-appointment-audit-warning-summary-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-claude-appointment-audit-warning-summary-contract` |
| Status | pending_plan_review |
| Created | 2026-06-26 20:07 +1000 |
| Source HEAD | `d61b791` |

## Plan Summary

Persist bounded, code-only warning metadata on confirmed appointment mutations so audit history proves staff confirmed over warnings; blocked/aborted proposals still write nothing. Backend-only; resolves a pre-existing two-head alembic divergence in the same migration.

## My Understanding

Proposal endpoints surface warnings (break_overlap, provisional_patient, waiting_area_cleared, etc.) but the confirmed mutation endpoints (POST /, PUT /{id}, PATCH /{id}/status, DELETE /{id}) write AppointmentAuditLog rows with no record of acknowledged warnings, so audit history cannot prove staff confirmed over a warning. This sprint persists bounded, safe (code-only, no free text/PHI) acknowledged-warning metadata on those confirmed mutations and exposes it on GET /{id}/audit. Blocked/aborted proposals must still write nothing.

## Intended Surface / Boundary

Backend appointment audit/proposal surface only: app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, one Alembic migration, focused tests. NO frontend. No diary grid, appointment cards, booking slots, waiting-room panels, or status-colour rendering change — purely the persisted audit contract behind those surfaces.

## Out Of Scope

Diary UI, supervisor dashboard, Bernie runtime/tools, taskpane, Command Centre, SMS, billing, patient demographics, unrelated appointment flows, and any broad audit framework beyond appointment-mutation warning metadata.

## Files I Expect To Edit

app/models/appointments.py (add confirmed_warnings column to AppointmentAuditLog); app/schemas/appointments.py (optional confirmed_warning_codes on AppointmentCreate/AppointmentUpdate/AppointmentStatusUpdate/AppointmentDeleteIn; confirmed_warnings on AppointmentAuditLogOut); app/routers/appointments.py (allowlist+sanitiser, _write_audit param, four mutation endpoints, audit read); alembic/versions/<new>_add_audit_confirmed_warnings.py (add column + merge two heads); tests/test_appointment_audit_warnings.py (new) and/or extend tests/test_appointment_audit.py.

## Implementation Steps

1) Model: confirmed_warnings = Column(JSON, nullable=True) on AppointmentAuditLog (list of short codes, null when none). 2) Router allowlist KNOWN_WARNING_CODES={break_overlap,provisional_patient,already_terminal,waiting_area_cleared,waiting_area_assigned_on_terminal} + _sanitize_warning_codes() keeps only allowlisted codes, dedupes order-preserving, caps length, returns None when empty (no free text/PHI ever stored). 3) Schemas: add optional confirmed_warning_codes to the four mutation bodies (proposal endpoints ignore it) and confirmed_warnings to AppointmentAuditLogOut. 4) Router: _write_audit gains confirmed_warnings param; create/update/status/delete pass _sanitize_warning_codes(body.confirmed_warning_codes); get_appointment_audit returns it. 5) Migration: new revision down_revision=(274919209522,h8i9j0k1l2m3) merges the two existing heads AND adds nullable confirmed_warnings column; downgrade drops it. 6) Tests per acceptance below.

## Visual / Behavioural Acceptance Checks

Confirmed POST/PUT/PATCH-status/DELETE with confirmed_warning_codes=[provisional_patient] -> audit row confirmed_warnings==[provisional_patient] and GET /{id}/audit returns it. No-code mutation -> confirmed_warnings null/absent. Garbage input [provisional_patient,__evil__,<script>] -> persists [provisional_patient] only. Blocked create (conflict) -> still zero audit rows. All existing test_appointment_audit.py assertions still pass. py_compile touched modules; alembic upgrade head resolves to a single head and applies cleanly; git diff --check clean.

## Risks / Ambiguities

Pre-existing TWO alembic heads (274919209522 + h8i9j0k1l2m3 both off g7h8i9j0k1l2) means alembic upgrade head currently errors; I resolve it via a merge down_revision in this migration — flagging because it alters migration topology and Codex may prefer a standalone merge migration (can split if preferred). Code-only design deliberately stores warning codes not messages to avoid PHI/free-text leakage; persisting human-readable summary is possible but increases PHI surface (recommend code-only). AppointmentCreate is shared by POST / and POST /proposals/create; new optional field is ignored by the proposal path. Codes are client-asserted and validated against an allowlist but not cryptographically tied to the originating proposal — acceptable at this audit tier.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
