# claude-time-model-regression-tests

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 882381e |
| Start Command | `python scripts\agent_worktrees.py handin` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-time-model-regression-tests --commit-message "Add canonical time model regression tests" --message "Canonical time model regression tests ready for Codex review"` |

## Mission

Expand regression coverage for the canonical appointment time model and diary-facing API behavior after the appointment_date/start_time_local migration.

## Scope

### In Scope

tests/ only, plus minimal test fixtures/helpers if required. Cover legacy start_time compatibility, new appointment_date + start_time_local booking, update behavior, slots by clinic-local date, and AppointmentOut fields needed by diary. If a genuine production bug blocks a test, document it clearly and keep any production change minimal.

### Out of Scope

No frontend work. No schema redesign. No Room/DiaryRoster implementation. No Gemini SDK work. Do not move handoff/current or merge to master.

## Required Steps

1. Run the start command above.
2. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
3. Work only inside the stated scope unless the user or Codex expands it.
4. Do not merge to `master`.
5. Do not move `handoff/current`.
6. Run the verification listed below.
7. Finish with the submit command above.

## Verification

Run .venv\\Scripts\\python.exe -m pytest tests. Also run .venv\\Scripts\\python.exe -m compileall app scripts tests if production code is touched.

## Merge Criteria

Tests prove old start_time clients still work, new local date/time clients work, updates preserve canonical fields, slots respect clinic-local day/time, and diary response fields include appointment_date/start_time_local without breaking existing appointment conflict tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
