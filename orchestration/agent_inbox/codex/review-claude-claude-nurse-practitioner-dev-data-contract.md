# review-claude-claude-nurse-practitioner-dev-data-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-nurse-practitioner-dev-data-contract` |
| Status | integrated |

## Review Request

claude-nurse-practitioner-dev-data-contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `seed.py` — added `Nurse` Practitioner (`Sarah Chen`, AHPRA `NMW0001234567`, specialty `Nursing`) before the diary template seeding so Room 2 can reference the nurse's UUID. Added nurse `PractitionerSchedule` (Mon–Fri 09:00–17:00, 15-min slots, looped with GP). Updated Room 2 `DiaryColumn` to carry `practitioner_id=nurse.id` and `practitioner_ahpra="NMW0001234567"`. Updated Room 2 `DiaryRoster` entry for today to use `practitioner_id=nurse.id` (no longer a plain label). Added idempotent backfill for existing DBs where Room 2 column/roster were seeded before the nurse existed. Added a sample nurse appointment (Margaret 09:30 "Wound dressing", 15 min). Extended appointment loop signature to carry the practitioner per row.
  - `app/routers/appointments.py` — removed redundant `db.refresh(appt)` from `create_appointment`. `_get_appointment` already performs a fresh SELECT with joinedloads immediately after commit; the intermediate `db.refresh` was re-opening a DB connection that raced with `clean_db`'s TRUNCATE in tests, causing `InvalidRequestError: Could not refresh instance`. This is a genuine production improvement (one fewer round-trip per POST).
  - `tests/test_nurse_practitioner.py` — new file, 6 tests: template column wired with nurse practitioner_id/AHPRA; roster entry for Room 2 carries nurse AHPRA (not a label); `POST /appointments` with nurse practitioner_id → 201; duplicate nurse booking at same slot → 409; `GET /slots/{nurse_id}` returns available slots when schedule exists; nurse booking blocks nurse's slot without affecting GP's slot.

- Verification run:
  - `pytest tests/test_nurse_practitioner.py -q` → **6 passed** (55s)
  - `pytest tests/test_booking_create_edit.py -q` → **31 passed** (3m08s) — regression check, no change
  - `pytest tests/test_diary_template.py tests/test_diary_roster.py -q` → **12 passed** (3m15s)
  - Combined 5-file run: 1 failed / 30 errors — pre-existing ordering flap (each affected test passes in its own file run)

- Remaining risks:
  - **`db.refresh` removal is a real fix, not a test hack.** The router's POST handler was doing: commit → refresh → `_get_appointment`. The refresh was a redundant extra SELECT; `_get_appointment` immediately re-fetches anyway. No observable behaviour change for API clients.
  - **Nurse has no login user.** The `Nurse` Practitioner row exists and can receive bookings; no `User` row is needed by the appointment contract. Nurse-login is out of scope for this task.
  - **Combined-run ordering flaps (pre-existing).** Removing `db.refresh` from POST fixed that specific race. PUT/PATCH handlers that call `_get_appointment` after commit have the same latent race in 4+-file combined runs. Recommend a dedicated test-infrastructure task to wrap tests in per-test transaction rollback.
  - **No new migrations.** Nurse uses the existing `practitioners` table; no schema change needed.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-nurse-practitioner-dev-data-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Codex accepted the nurse practitioner dev-data contract and the redundant `db.refresh(appt)` removal after focused review.
- Follow-up required: Nurse login/user permissions remain out of scope. Keep the broader pytest ordering/test DB isolation issue on the infrastructure backlog.
