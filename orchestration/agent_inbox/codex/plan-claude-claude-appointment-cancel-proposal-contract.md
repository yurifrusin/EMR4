# plan-claude-claude-appointment-cancel-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-cancel-proposal-contract` |
| Status | integrated |
| Created | 2026-06-25 11:41 +1000 |
| Source HEAD | `e1e0f9e` |

## Plan Summary

Fix DELETE waiting_area gap; add proposals/delete endpoint + schemas; 7 tests for DELETE and new proposal path

## My Understanding

Assessment: propose_status_update with status=Cancelled fully covers proposal-gated cancellation (warns waiting_area_cleared, autonomy_tier=proposal always, blocks already_in_status). The gap is DELETE /{id}: (1) it is a SOFT CANCEL not a hard delete — sets appt.status=Cancelled and commits, leaves the row in DB — but it does NOT clear waiting_area_id the way PATCH /{id}/status does for terminal statuses (line 1098-1099 of appointments.py), so a patient can appear stranded in the waiting area after a diary delete; (2) it has zero test coverage; (3) it bypasses the proposal layer entirely. Fix: (a) one-line repair to DELETE /{id} to clear waiting_area_id on cancel, matching PATCH behavior; (b) new POST /proposals/delete/{appointment_id} endpoint with intent=delete_appointment — returns autonomy_tier=proposal always (destructive irreversible action), warns waiting_area_cleared if patient is in an area, blocks already_in_status=Cancelled, command payload includes clears_waiting_area:bool; (c) two new schemas AppointmentDeleteCommand and AppointmentDeleteProposalOut; (d) 7 targeted tests.

## Intended Surface / Boundary

app/routers/appointments.py (fix DELETE waiting_area + new proposals/delete endpoint); app/schemas/appointments.py (two new schemas); tests/test_appointment_status_mutations.py or a new test_appointment_cancel.py (7 new tests). No diary frontend, no taskpane, no migrations.

## Out Of Scope

No diary frontend. No migrations. No taskpane or Command Centre. No hard deletes or schema removals. No changes to propose_status_update or other proposal endpoints.

## Files I Expect To Edit

app/routers/appointments.py — add appt.waiting_area_id = None to cancel_appointment; add new proposals/delete/{appointment_id} endpoint; add import for new schemas. app/schemas/appointments.py — add AppointmentDeleteCommand (appointment_id, clears_waiting_area: bool) and AppointmentDeleteProposalOut (intent=delete_appointment, safe, requires_confirmation, autonomy_tier, summary, command, warnings, blocks). tests/test_appointment_status_mutations.py — append 7 new tests in a DELETE section.

## Implementation Steps

1. In app/schemas/appointments.py: add AppointmentDeleteCommand and AppointmentDeleteProposalOut after AppointmentWaitingAreaProposalOut. 2. In app/routers/appointments.py: import new schemas. 3. In cancel_appointment (DELETE /{id}, line 1104): after appt.status = AppointmentStatus.Cancelled, add appt.waiting_area_id = None before db.commit(). 4. After cancel_appointment, add POST /proposals/delete/{appointment_id}: auth via require_role, _get_appointment, check body.status (none needed — delete always means Cancelled); BLOCK if appt.status == Cancelled (already_in_status); WARN if appt.waiting_area_id is not None (waiting_area_cleared); autonomy_tier always proposal; command has clears_waiting_area = appt.waiting_area_id is not None. 5. Add 7 tests: (A) test_delete_requires_auth → 401; (B) test_delete_soft_cancels_appointment → 204, db.refresh shows status=Cancelled, row still exists; (C) test_delete_clears_waiting_area_on_cancel → appt in area, DELETE → 204, waiting_area_id=None; (D) test_delete_cross_practice_returns_404 → 404; (E) test_delete_proposal_requires_auth → 401; (F) test_delete_proposal_warns_waiting_area_cleared → appt in area, proposal → 200, waiting_area_cleared warning, clears_waiting_area=True, autonomy_tier=proposal, row unchanged; (G) test_delete_proposal_blocked_already_cancelled → 200, blocks already_in_status, safe=False. 6. Run pytest tests/test_appointment_status_mutations.py -q + py_compile.

## Visual / Behavioural Acceptance Checks

cancel_appointment sets waiting_area_id=None on commit. DELETE 401 without auth. DELETE 204 with auth, appointment row remains with status=Cancelled and waiting_area_id=None. DELETE cross-practice 404. proposals/delete 401 without auth. proposals/delete warns waiting_area_cleared when patient in area, autonomy_tier=proposal, row unchanged. proposals/delete blocks already_in_status=Cancelled. All pre-Sprint-28 tests still pass.

## Risks / Ambiguities

The one-line waiting_area fix to DELETE changes behavior: previously DELETE left waiting_area_id set; after fix it clears it. This is the correct behavior (consistent with PATCH terminal status). No test currently asserts the old broken behavior, so no existing test breaks. New proposals/delete endpoint is additive. The endpoint intent delete_appointment is distinct from update_appointment_status so Bernie tooling can distinguish a diary delete from a status-only cancel.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
