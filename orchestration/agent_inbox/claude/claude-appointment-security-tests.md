# claude-appointment-security-tests

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | a647920 |
| Start Command | `python scripts\agent_worktrees.py handin` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-security-tests --commit-message "Add appointment security regression tests" --message "Appointment/security regression tests ready for Codex review"` |

## Mission

Add regression tests for authenticated consultation endpoints, practice-scoped finalise, appointment conflict validation, and duration-aware slots.

## Scope

### In Scope

Test files and minimal test fixture/helpers only. Prefer pytest/FastAPI TestClient or direct route/service tests. You may add dev test dependencies only if already present tooling cannot cover this.

### Out of Scope

Do not change production appointment, consultation, patient, or diary implementation. Do not alter migrations. Do not move handoff/current or merge to master.

## Required Steps

1. Run the start command above.
2. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
3. Work only inside the stated scope unless the user or Codex expands it.
4. Do not merge to `master`.
5. Do not move `handoff/current`.
6. Run the verification listed below.
7. Finish with the submit command above.

## Verification

Run the new tests in .venv. Also run python -m compileall app scripts create_patient_file.py create_patient_template.py sync_taskpane.py seed.py if production imports are touched.

## Merge Criteria

Tests demonstrate unauthorized consultation calls fail, finalise cannot cross practice boundaries, overlapping appointments are rejected, adjacent appointments are allowed, and /slots marks all overlapped slots unavailable.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
