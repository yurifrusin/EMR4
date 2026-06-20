# review-claude-claude-provisional-link-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-provisional-link-contract` |
| Status | integrated |

## Review Request

Provisional booking link contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py` — `AppointmentOut` gains `breaks_overlap: list[str] = Field(default_factory=list)` (soft-block warning, defaults to empty; GET routes return `[]`, create/update routes populate it)
  - `app/routers/appointments.py` — import `DiaryBreak/DiaryColumn/DiaryTemplate` from `app.models.diary`; add `_get_break_overlaps()` helper (queries DiaryBreak via DiaryColumn+DiaryTemplate join for the practitioner); wire into `create_appointment` and `update_appointment` (both now return an explicit `AppointmentOut` instance with `breaks_overlap` populated — does NOT block the booking, soft warning only)
  - `tests/test_break_overlap_contract.py` — 4 new tests: overlap during break → 201 + `breaks_overlap` populated; outside break → 201 + empty list; reschedule into break via PUT → 200 + populated; no diary template → 201 + empty list (graceful)
  - `orchestration/agent_inbox/claude/claude-provisional-link-contract.md` — this file (status + completion notes)
  - Note: provisional-link contract (patient_id PUT, 422 on clearing both identity fields) was already complete via prior integration commits `a58e98a`/`14b8fda`. Tests `test_appointment_patient_link.py` (9 tests) already pass.
- Verification run (all on clean test DB, sequential):
  - `pytest tests/test_break_overlap_contract.py tests/test_appointment_patient_link.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py -v` → **44/44 passed** in 94s
  - `pytest tests/test_diary_template.py tests/test_diary_roster.py tests/test_slots.py tests/test_booking_patient_flow.py tests/test_nurse_practitioner.py -v` → **50/50 passed** in 138s
  - Combined total: **94/94 passed**
  - `py_compile app/routers/appointments.py app/schemas/appointments.py` → OK
  - `git diff --check` → OK (CRLF warning on .md only, not a code issue)
- Remaining risks:
  - `breaks_overlap` on GET routes returns `[]` always (break check is only run on create/update). A future task could wire it into GET for completeness, but it's not needed for the contract.
  - `_get_break_overlaps` queries DiaryBreak via DiaryColumn.practitioner_id. If a column has no practitioner_id (label-only column), its breaks are never returned — correct for appointment booking, since label-only columns are not bookable.
  - Test DB requires pgvector extension; `CREATE EXTENSION IF NOT EXISTS vector` must run before `create_all` on a fresh DB (conftest's `engine` fixture does not do this — add to conftest or pre-create extension in the test DB setup).

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-provisional-link-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated into `master` as part of Sprint 12. Accepted the soft warning-only break overlap contract and the existing provisional-to-linked patient API compatibility. Re-ran focused appointment and diary-regression tests after integration.
- Follow-up required: Consider populating `breaks_overlap` on appointment GET/list responses later if API clients need passive review of existing break overlaps. Keep label-only/non-practitioner room booking semantics separate from practitioner-backed appointment creation.
