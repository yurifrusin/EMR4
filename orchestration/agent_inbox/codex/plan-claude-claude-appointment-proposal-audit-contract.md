# plan-claude-claude-appointment-proposal-audit-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-proposal-audit-contract` |
| Status | integrated |
| Created | 2026-06-26 17:18 +1000 |
| Source HEAD | `662e61e` |

## Plan Summary

Add a practice-scoped appointment proposal-decision audit trail: a new AppointmentAuditEvent model + migration, audit rows written only on confirmed mutating writes (create/update/waiting-area/status/cancel), a per-appointment scoped history read endpoint, and focused pytest. Proposals stay non-mutating and create no audit rows.

## My Understanding

Sprint 33 / Programme 2D wants high-risk appointment proposal *decisions* to leave a deterministic history so future supervisors and Bernie tooling can review what was actually confirmed, without giving any model direct DB autonomy. The proposal endpoints (POST /proposals/create|update|status|waiting-area|delete) are already non-mutating preflight; the real writes happen on POST '' (create), PUT /{id} (update + waiting-area moves), PATCH /{id}/status, and DELETE /{id} (soft-cancel). The audit must hook the confirmed *write* paths only, capturing who confirmed, appointment id + practice id, action type, status target where relevant, cancellation reason where relevant, a non-PHI warnings-summary, and a timestamp. Because proposals never write, blocked/aborted proposals naturally produce no audit rows.

## Intended Surface / Boundary

Backend appointment audit/proposal-history data model + API only: app/models/appointments.py (new model), app/models/__init__.py (register), app/schemas/appointments.py (audit Out schema), app/routers/appointments.py (write-path audit hook + one read endpoint), one new Alembic migration, and one new pytest module. No behaviour change to existing proposal/mutation semantics.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/AI provider code, receptionist free-text messaging, restore/reactivation, billing, SMS, a broad/generic audit-log framework beyond appointment proposal decisions, and any direct model-to-database Bernie execution. No change to who may mutate appointments, to conflict/break/terminal validation, or to existing endpoint response shapes.

## Files I Expect To Edit

app/models/appointments.py (add AppointmentAuditAction enum + AppointmentAuditEvent model); app/models/__init__.py (import/register + __all__); app/schemas/appointments.py (add AppointmentAuditEventOut); app/routers/appointments.py (add _record_appointment_audit helper, call it in create_appointment/update_appointment/update_appointment_status/cancel_appointment on success, add GET /{appointment_id}/audit); alembic/versions/<new>_add_appointment_audit_events.py (down_revision 274919209522); tests/test_appointment_proposal_audit.py (new).

## Implementation Steps

1) Add AppointmentAuditAction enum (Create, Update, WaitingAreaChange, StatusChange, Cancel) + AppointmentAuditEvent model (id, practice_id FK+index, appointment_id FK+index, confirmed_by FK users nullable, action enum, status_target AppointmentStatus nullable, cancellation_reason String(500) nullable, warning_codes JSONB default list, confirmed_with_warnings Boolean default False, created_at timestamptz server_default now). 2) Register model in app/models/__init__.py. 3) Add _record_appointment_audit(db, appt, action, current_user, status_target=None, cancellation_reason=None, warning_codes=None) that db.add()s a row in the same transaction as the mutation, before db.commit(). 4) Hook it into the four write endpoints on the success path only: create=Create (warning codes from existing breaks_overlap + provisional); PUT=WaitingAreaChange when the only meaningful changed fields are waiting-area related (waiting_area_id/waiting_room/queue_position) else Update; PATCH status=StatusChange with status_target; DELETE=Cancel with cancellation_reason. Recompute warning codes server-side (non-PHI codes only, e.g. break_overlap, provisional_patient, waiting_area_cleared). 5) Add GET /api/v1/appointments/{appointment_id}/audit returning practice-scoped events newest-first (404 on cross-practice via _get_appointment). 6) Add migration creating appointment_audit_events with practice_id + appointment_id indexes. 7) Write tests. 8) Verify: py_compile touched modules, focused pytest, adjacent appointment mutation suites, git diff --check.

## Visual / Behavioural Acceptance Checks

Each confirmed create/update/waiting-area/status/cancel write inserts exactly one practice-scoped audit row capturing actor, action, status target (status/cancel), cancellation reason (cancel), and non-PHI warning codes. The five proposal endpoints insert zero audit rows. A write rejected by validation (e.g. 409 conflict, terminal block) inserts zero audit rows. GET /{id}/audit returns that appointment's rows newest-first for the owning practice and 404 for another practice. Existing appointment proposal/mutation tests still pass unchanged. This is backend-only; no diary grid, booking slot, card, panel, or waiting-room UI is touched.

## Risks / Ambiguities

1) Waiting-area-vs-update action classification on PUT is inferred from changed fields (heuristic); alternative is an explicit action hint on the request body, but that changes the write schema — recommend inference to stay minimal and non-breaking, flagged for Codex. 2) warning_codes recomputed at write time rather than trusting client/proposal payload, to stay deterministic and avoid trusting caller-supplied data. 3) JSONB column is Postgres-specific (matches existing diary models and the Postgres test DB). 4) Read endpoint uses get_current_user (any authenticated practice user) for review; could be tightened to mutating roles if Codex prefers. 5) Audit is non-PHI by design (codes + ids only, no patient names in warning_codes).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
