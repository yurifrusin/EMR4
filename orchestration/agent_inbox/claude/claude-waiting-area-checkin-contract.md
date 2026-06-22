# claude-waiting-area-checkin-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 7fd03d0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-waiting-area-checkin-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-checkin-contract --commit-message "Waiting area check-in contract" --message "claude-waiting-area-checkin-contract ready for Codex review"` |

## Mission

Design and, after plan approval only, implement the backend contract for assigning waiting areas during patient check-in and status transitions. This sprint is plan-gated: first produce the implementation plan and stop.

## Scope

### In Scope

Potentially app/routers/appointments.py, app/schemas/appointments.py, app/models/appointments.py only if required, focused tests around waiting-area assignment/check-in/status mutation, and task/review packet notes. Consider whether status PATCH should accept waiting_area_id or whether update/check-in should remain separate. Preserve practice scoping, patient identity rules, same-day waiting-room semantics, and correction/backtracking rules.

### Out of Scope

No diary frontend changes, no taskpane changes, no room/admin UI, no drag/drop/resize, no Bernie implementation, no SMS/reminder confirmation, no billing/finalisation locking. Do not start coding until Codex/user approves the plan and says complete sprint task.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan stage: implementation plan packet plus GUI echo. Implementation stage after approval: focused pytest for appointment status/waiting-area/patient-link contracts, plus py_compile for touched backend modules.

## Merge Criteria

Codex accepts the plan before coding; implementation stays scoped; tests pass; API semantics make waiting-area assignment explicit without confusing patient identity confirmation, SMS confirmation, or attendance status.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py` — added `waiting_area_id: Optional[uuid.UUID] = None`
    to `AppointmentStatusUpdate`. No other schema changes (field already present in
    `AppointmentUpdate` and `AppointmentOut`; no migration needed).
  - `app/routers/appointments.py` — `update_appointment_status` now inspects
    `body.model_fields_set` after setting `appt.status`:
      - `waiting_area_id` absent → area unchanged (backward compat)
      - `waiting_area_id=null` (explicit) → `appt.waiting_area_id = None`
      - `waiting_area_id=<UUID>` → calls existing `_ensure_waiting_area` cross-practice /
        inactive guard, then assigns. `db.commit()` and re-fetch are unchanged.
  - `tests/test_waiting_area_checkin_contract.py` — new file, 8 tests:
      (a) `test_checkin_requires_auth` — 401 without token
      (b) `test_status_patch_without_area_field_preserves_existing_area` — field absent,
          existing area unchanged
      (c) `test_status_patch_with_area_assigns_atomically` — UUID → status + area set
      (d) `test_status_patch_with_null_area_clears_assignment` — explicit null → area
          cleared
      (e) `test_status_patch_with_cross_practice_area_returns_404` — wrong-practice UUID
      (f) `test_status_patch_with_inactive_area_returns_404` — inactive area UUID
      (g) `test_status_patch_can_reassign_to_different_area` — second PATCH changes area
      (h) `test_status_change_without_area_field_does_not_clear_existing_area` — two
          status transitions (InConsult → Completed) without area field; area persists

- Verification run:
  - New tests in isolation: `pytest tests/test_waiting_area_checkin_contract.py -v
    --tb=short -p no:randomly` → **8 passed** in 13 s
  - Previously-verified suite + new tests: `pytest tests/test_waiting_area_checkin_contract.py
    tests/test_waiting_area_contract.py tests/test_appointment_status_mutations.py
    tests/test_break_overlap_contract.py tests/test_appointment_patient_link.py
    tests/test_appointment_conflicts.py tests/test_diary_template.py
    tests/test_diary_roster.py tests/test_slots.py tests/test_booking_patient_flow.py
    tests/test_nurse_practitioner.py -q --tb=short -p no:randomly`
    → **111 passed, 1 warning** in 142 s (no regressions)
  - Full suite (`pytest tests/ -q --tb=short -p no:randomly`) → **191 passed, 1 warning,
    5 errors**; the 5 errors are all in `tests/test_waiting_room.py` with
    `UniqueViolation: users_email_key` — a pre-existing test-ordering issue in that file
    (it was also excluded from the previous sprint's 103-test verification). None of the
    5 errors involve code touched by this task.
  - `py_compile app/schemas/appointments.py app/routers/appointments.py
    tests/test_waiting_area_checkin_contract.py` → OK
  - `git diff --check` → OK (only a CRLF/LF notice on the task packet, not production code)

- Remaining risks:
  - `test_waiting_room.py` has a session-ordering fragility (5 tests error when run after
    other test files due to `UniqueViolation` on `users_email_key`). This is pre-existing
    and unrelated to this task, but Codex may want to schedule a fix (conftest `gp_user`
    fixture email collision when TRUNCATE does not fully reset the sequence within a
    shared DB session).
  - Terminal-status auto-clear of `waiting_area_id` is deliberately out of scope. If a
    patient is marked Completed or Cancelled, the area assignment persists in the DB (the
    waiting-room endpoint already filters by status so the assignment is invisible in the
    queue, but it remains in the row). Diary/reception UI should clear the area on
    terminal transitions if that is the desired UX — backend does not enforce it.
  - No uniqueness constraint on `queue_position` within a practice+date (pre-existing,
    carried from the resource contract task).
