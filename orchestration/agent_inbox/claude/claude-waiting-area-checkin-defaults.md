# claude-waiting-area-checkin-defaults

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 4d8d1c7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-waiting-area-checkin-defaults --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-checkin-defaults --commit-message "Waiting area check-in defaults" --message "claude-waiting-area-checkin-defaults ready for Codex review"` |

## Mission

Plan, then after approval implement, the backend contract for selecting/defaulting waiting areas during check-in and optionally clearing waiting_area_id on terminal attendance states. Keep identity verification, booking confirmation, attendance, and waiting-area placement separate.

## Scope

### In Scope

app/routers/appointments.py, app/schemas/appointments.py, app/models/diary.py only if required, focused tests around waiting_area_id assignment/defaulting/clearing, practice scoping, inactive/cross-practice guards, and terminal status behaviour.

### Out of Scope

No diary frontend, no taskpane, no room/admin UI, no Bernie runtime, no SMS/email/voice reminder confirmation, no billing/finalisation locking, no drag/drop/resize, no patient demographic edits.

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

Plan packet first. After approval: focused pytest for waiting-area/status/check-in contracts, py_compile for touched backend modules, git diff --check.

## Merge Criteria

Codex accepts the plan before coding; API semantics make default waiting-area assignment explicit and test-covered; terminal-status clearing policy is deliberate and documented; tests pass; no frontend files touched.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py` — added `AppointmentCheckinDefaults` schema
    (`suggested_waiting_area_id: Optional[uuid.UUID]`, `room_name: Optional[str]`).
  - `app/routers/appointments.py` — (a) added `Room, DiaryRoster` to diary model
    imports and `AppointmentCheckinDefaults` to schema imports; (b) defined
    `TERMINAL_STATUSES = (Completed, Cancelled, NoShow, DNA)` alongside the existing
    `NON_BLOCKING_STATUSES`; (c) added read-only `GET /{id}/checkin-defaults` route
    (auth: `get_current_user`; lookup chain: DiaryRoster → Room →
    `default_waiting_area_id` → WaitingArea.is_active; returns nulls at every missing
    or inactive step); (d) added `elif body.status in TERMINAL_STATUSES:
    appt.waiting_area_id = None` branch in `update_appointment_status` — fires only
    when `waiting_area_id` is absent from `body.model_fields_set` (explicit values
    always win via the existing `if` branch).
  - `tests/test_waiting_area_checkin_defaults.py` — new file, 9 tests:
      (a) GET requires auth → 401
      (b) GET cross-practice appointment → 404
      (c) GET no DiaryRoster → both fields null
      (d) GET roster + active default → UUID + room name returned
      (e) GET roster + inactive area → suggested null, room_name returned
      (f) PATCH Completed, field absent → area auto-cleared
      (g) PATCH Cancelled, field absent → area auto-cleared
      (h) PATCH InConsult (active), field absent → area preserved
      (i) PATCH Completed with explicit UUID → explicit wins, area assigned
  - `tests/test_waiting_area_checkin_contract.py` — updated one test
    (`test_status_change_without_area_field_does_not_clear_existing_area`): the
    Completed step previously asserted area was preserved; now correctly asserts
    area is None (auto-clear policy). InConsult step assertion unchanged.

- Verification run:
  - New tests in isolation: `pytest tests/test_waiting_area_checkin_defaults.py -v
    --tb=short -p no:randomly` → **9 passed** in 38 s
  - Full focused suite (9 new + 111 previously-verified):
    `pytest tests/test_waiting_area_checkin_defaults.py
    tests/test_waiting_area_checkin_contract.py tests/test_waiting_area_contract.py
    tests/test_appointment_status_mutations.py tests/test_break_overlap_contract.py
    tests/test_appointment_patient_link.py tests/test_appointment_conflicts.py
    tests/test_diary_template.py tests/test_diary_roster.py tests/test_slots.py
    tests/test_booking_patient_flow.py tests/test_nurse_practitioner.py
    -q --tb=short -p no:randomly` → **120 passed, 1 warning** in 165 s
  - `py_compile` on all 4 touched files → OK
  - `git diff --check` → OK (CRLF notice on task packet only, not production code)

- Remaining risks:
  - Auto-clear on terminal is a policy decision captured in tests. If a receptionist
    accidentally marks a patient Completed, the area assignment is lost. Mitigation: a
    corrective PATCH /status to an active status with an explicit `waiting_area_id`
    re-assigns. The UI should handle this path.
  - GET /checkin-defaults degrades gracefully when DiaryRoster is not populated (returns
    nulls). Practices that do not use DiaryRoster will always see nulls, which is correct.
    The endpoint is purely advisory; the UI/Bernie should present the suggestion for
    confirmation rather than applying it silently.
  - `test_waiting_room.py` session-ordering fragility is pre-existing and unrelated to
    this task (5 tests error with UniqueViolation when run after other files; the file
    was excluded from all sprint verifications).
