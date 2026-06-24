# plan-claude-claude-appointment-status-waiting-area-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-status-waiting-area-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-25 08:24 +1000 |
| Source HEAD | `f16251d` |

## Plan Summary

Harden propose_status_update with missing warning; add waiting-area-only proposal endpoint and 7 new tests

## My Understanding

The existing propose_status_update endpoint (app/routers/appointments.py:718-810) handles already_in_status, already_terminal, and waiting_area_cleared. Two gaps: (1) body.status is terminal AND body.waiting_area_id is non-null is a contradictory command (completing while assigning to an area) — currently no warning raised; (2) cross-practice and non-existent appointment tests are absent for the status proposal path. No endpoint exists for proposing a waiting-area change without a status change — moving a patient between areas is a real reception workflow Bernie will need.

## Intended Surface / Boundary

app/routers/appointments.py and app/schemas/appointments.py (new schemas + new endpoint); tests/test_appointment_update_proposal.py (new tests only). No taskpane, diary, migrations, or other routers.

## Out Of Scope

No mutations (PUT/PATCH/DELETE). No migrations. No taskpane or diary frontend. No changes to existing test logic or other router files.

## Files I Expect To Edit

app/routers/appointments.py — add warning to propose_status_update; add POST /proposals/waiting-area/{id} endpoint. app/schemas/appointments.py — add AppointmentWaitingAreaProposalIn, AppointmentWaitingAreaCommand, AppointmentWaitingAreaProposalOut schemas. tests/test_appointment_update_proposal.py — add 7 new tests.

## Implementation Steps

1. In propose_status_update (app/routers/appointments.py:737-765): after clears_waiting_area block, add: if body.status in TERMINAL_STATUSES and body.waiting_area_id is not None, append warning waiting_area_assigned_on_terminal (severity=warning, message: assigning to a waiting area while marking terminal is contradictory). 2. In app/schemas/appointments.py: add AppointmentWaitingAreaProposalIn (waiting_area_id: Optional[UUID]), AppointmentWaitingAreaCommand (appointment_id, waiting_area_id, clears_waiting_area: bool), AppointmentWaitingAreaProposalOut (intent=update_appointment_waiting_area, safe, requires_confirmation, autonomy_tier, summary, command, warnings, blocks). 3. In app/routers/appointments.py after propose_status_update: add POST /proposals/waiting-area/{appointment_id} endpoint: auth via require_role(*MUTATING_APPOINTMENT_ROLES), _get_appointment, _ensure_waiting_area if non-null, BLOCK already_in_area if new area == current area, WARNING clears_waiting_area if null and currently has area, autonomy_tier execute_with_report (no terminal semantics here). 4. In tests/test_appointment_update_proposal.py: add STATUS_URL cross-practice test, STATUS_URL non-existent-UUID test, WAITING_AREA_URL assign test (execute_with_report), WAITING_AREA_URL clear test (warning), WAITING_AREA_URL already-in-area block test, WAITING_AREA_URL cross-practice 404 test, WAITING_AREA_URL non-existent 404 test. 5. Run pytest tests/test_appointment_update_proposal.py -q.

## Visual / Behavioural Acceptance Checks

propose_status_update with {status: Completed, waiting_area_id: <valid_id>} returns 200, warnings contains waiting_area_assigned_on_terminal, autonomy_tier=proposal. proposals/waiting-area/{id} with valid new area returns 200, intent=update_appointment_waiting_area, safe=True, autonomy_tier=execute_with_report. proposals/waiting-area/{id} with null area (current area set) returns 200, clears_waiting_area=True, warning waiting_area_cleared. proposals/waiting-area/{id} same area as current returns 200, safe=False, blocked already_in_area. proposals/waiting-area/{id} cross-practice returns 404. proposals/waiting-area/{id} random UUID returns 404. All 24 existing tests still pass (31 total with 7 new).

## Risks / Ambiguities

waiting_area_assigned_on_terminal warning could affect existing test that sends terminal+waiting_area_id — reviewed all 5 existing status tests, none do this. New endpoint shares _ensure_waiting_area helper with existing code — no new blast radius.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
