# plan-claude-claude-appointment-audit-actor-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-audit-actor-contract` |
| Status | pending_plan_review |
| Created | 2026-06-26 18:03 +1000 |
| Source HEAD | `38067fb` |

## Plan Summary

Add a bounded, read-time backend contract exposing a safe staff-actor display (name/role) on the appointment audit endpoint, without widening audit scope, adding columns, or exposing PHI.

## My Understanding

GET /api/v1/appointments/{id}/audit returns AppointmentAuditLogOut rows whose only actor field is confirmed_by_user_id (bare UUID), so staff cannot read who confirmed/changed/cancelled. User has email, role (GP/Receptionist/Nurse/Admin/PracticeOwner), and an OPTIONAL linked Practitioner (first/last name); User itself has no name. Clinician users have a real name; receptionists usually have no practitioner link so display must fall back to email local-part. Endpoint is already authenticated and practice-scoped. Goal: surface human-readable actor metadata at read time only.

## Intended Surface / Boundary

Backend API contract only. app/schemas/appointments.py: add confirmed_by_display (str) and confirmed_by_role (str|None) to AppointmentAuditLogOut. app/routers/appointments.py: in get_appointment_audit, batch-load actor User + joinedload practitioner and populate display; add _actor_display helper. Keep confirmed_by_user_id for stable machine identity. Display rule: practitioner 'First Last' if linked, else email local-part, else 'Unknown'; role = user.role.value or None. Staff name/role/email-local are operational staff metadata, not patient PHI.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/AI code, full user-directory API, patient/clinical PHI in audit rows, warning-code persistence, supervisor dashboard, Bernie, billing, SMS. No DB migration (derived at read time); add one only if a verified backend gap is found (not expected). Proposal endpoints untouched and non-mutating.

## Files I Expect To Edit

app/schemas/appointments.py; app/routers/appointments.py; tests/test_appointment_audit.py

## Implementation Steps

1) Add confirmed_by_display + confirmed_by_role to AppointmentAuditLogOut; construct schema explicitly in the endpoint since fields are derived. 2) Add _actor_display(user)->(display,role) helper with name->email-local->Unknown fallback. 3) In get_appointment_audit, batch-load relevant User rows with joinedload(User.practitioner) (single practice-scoped query), map id->(display,role), build ordered response preserving all existing fields. 4) Verify _write_audit and all four mutation paths unchanged. 5) Add focused tests: practitioner name for clinician actor, email local-part for receptionist, role matches, ordering/practice-scope/404/401 still hold.

## Visual / Behavioural Acceptance Checks

Backend JSON contract change only; no visual surface changes (diary grid, cards, slots, waiting room, status chips, taskpane, Command Centre unchanged). GET /{id}/audit still 401 unauthenticated, 404 cross-practice, [] for fresh appt, ordered by created_at. Each entry additionally carries confirmed_by_display + confirmed_by_role; confirmed_by_user_id unchanged.

## Risks / Ambiguities

Display-format choice (email local-part fallback) may need Codex preference adjustment - one-line change. N+1 mitigated by single batched user load. PHI boundary: only staff name/role/email-local exposed, no patient identifiers. Confirmed non-mutating: proposal endpoints and _write_audit callers untouched; change is read-path only. Possible follow-up (out of scope, would suggest-task): same actor display on proposal audit-context preview.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
