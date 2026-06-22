# review-claude-claude-waiting-area-checkin-defaults

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-waiting-area-checkin-defaults` |
| Status | queued |

## Review Request

claude-waiting-area-checkin-defaults ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-waiting-area-checkin-defaults.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
