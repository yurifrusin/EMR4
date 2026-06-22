# plan-claude-claude-appointment-update-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-update-proposal-contract` |
| Status | integrated |
| Created | 2026-06-23 01:15 +1000 |
| Source HEAD | `9fb853d` |

## Plan Summary

Two non-mutating proposal endpoints: POST /proposals/update/{id} (reschedule/edit, blocks on terminal/conflict, warns on break/provisional) and POST /proposals/status/{id} (status change, execute_with_report for routine, proposal for terminal, blocks on same-status). 6 new schemas, 12 new tests.

## My Understanding

Mirrors the existing create-proposal pattern for the edit/status-change surface. Direct mutation endpoints (PUT/PATCH/DELETE) stay unchanged. No schema changes required.

## Intended Surface / Boundary

app/schemas/appointments.py, app/routers/appointments.py, tests/test_appointment_update_proposal.py (new). No frontend, no migrations, no models.

## Out Of Scope

Diary grid, taskpane, Command Centre, Bernie LLM, patient demographics, room/location admin UI, SMS, billing, existing direct-mutation endpoints.

## Files I Expect To Edit

app/schemas/appointments.py (6 new schemas), app/routers/appointments.py (2 new endpoints + imports), tests/test_appointment_update_proposal.py (new, 12 tests)

## Implementation Steps

1. Schemas: AppointmentUpdateProposalIn, AppointmentUpdateCommand, AppointmentUpdateProposalOut, AppointmentStatusProposalIn, AppointmentStatusCommand, AppointmentStatusProposalOut. 2. POST /proposals/update/{id}: merge body over existing, check terminal block, conflict block, break/provisional warnings, return proposal. 3. POST /proposals/status/{id}: check same-status block, terminal warning, waiting-area-cleared warning, set autonomy_tier (execute_with_report for routine non-terminal, proposal for terminal, blocked). 4. Tests: 7 update + 5 status.

## Visual / Behavioural Acceptance Checks

pytest test_appointment_update_proposal.py test_appointment_proposals.py test_appointment_status_mutations.py test_booking_create_edit.py all pass; py_compile on both modified source files clean; git diff --check clean; no Appointment rows written during any proposal test.

## Risks / Ambiguities

Terminal re-transition modelled as warning not block (judgment call). Cancel handled via proposals/status with status=Cancelled, not a separate endpoint. autonomy_tier execute_with_report applies only to non-terminal, no-warning status changes — Codex can tighten to proposal-always if preferred.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
