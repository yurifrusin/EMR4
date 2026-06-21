# review-claude-claude-waiting-area-resource-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-waiting-area-resource-contract` |
| Status | queued |

## Review Request

Waiting area resource contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/models/diary.py` — added `WaitingArea` model (named physical area, practice-scoped, ordered, active flag); added `Room.default_waiting_area_id FK → waiting_areas.id`
  - `app/models/appointments.py` — added `Appointment.waiting_area_id FK → waiting_areas.id` and `Appointment.queue_position`
  - `app/schemas/appointments.py` — added `waiting_area_id` and `queue_position` to `AppointmentUpdate` and `AppointmentOut`
  - `app/schemas/diary.py` — added `WaitingAreaOut` schema
  - `app/routers/diary.py` — added `GET /api/v1/diary/waiting-areas` endpoint (practice-scoped, active only, ordered by display_order)
  - `app/routers/appointments.py` — added `waiting_area_id` query filter to `GET /waiting-room`; added `_ensure_waiting_area` cross-practice guard; added `appointment_date == today` filter to waiting-room; added `queue_position.nullslast()` ordering; added `queue_position` to PUT update path
  - `alembic/versions/f6a7b8c9d0e1_add_waiting_area.py` — migration: creates `waiting_areas` table; adds `waiting_area_id` and `queue_position` to `appointments`; adds `default_waiting_area_id` to `rooms`
  - `seed.py` — seeds sample `WaitingArea` rows for the dev clinic
  - `tests/test_waiting_area_contract.py` — 9 new tests covering auth gate, practice-scoped list, cross-practice isolation, inactive exclusion, backward compat, filter by area, filter excludes unassigned, PUT assignment, cross-practice rejection

- Verification run:
  - Full 103-test suite: `pytest tests/test_waiting_area_contract.py tests/test_break_overlap_contract.py tests/test_appointment_patient_link.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_diary_template.py tests/test_diary_roster.py tests/test_slots.py tests/test_booking_patient_flow.py tests/test_nurse_practitioner.py -v --tb=short -p no:randomly` → **103 passed, 1 warning** in 310s
  - Verified migration chain: `f6a7b8c9d0e1` upgrades cleanly on fresh test DB (`Base.metadata.create_all` in engine fixture)
  - `py_compile`/`git diff --check` clean

- Remaining risks:
  - The `appointment_date == today` filter added to `GET /waiting-room` uses `_practice_zoneinfo` (requires `tzdata` on Windows for non-UTC timezones). On machines without `tzdata`, this could raise `ZoneInfoNotFoundError` and return 500. Mitigated: fallback in `_practice_zoneinfo` uses `DEFAULT_PRACTICE_TIMEZONE` but that also requires tzdata. Consider adding a bare `try/except ZoneInfoNotFoundError` final fallback to UTC in `_practice_zoneinfo` for robustness.
  - The `rooms.default_waiting_area_id → waiting_areas.id` FK creates a cascade cycle with `waiting_areas.practice_id → practices.id` and `rooms.practice_id → practices.id`. PostgreSQL handles TRUNCATE CASCADE cycles correctly, but the cycle should be noted for future schema engineers.
  - `queue_position` is not validated for uniqueness within a practice+date; duplicates are possible if clients don't manage ordering. Acceptable for now as a backend-only primitive.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-waiting-area-resource-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
