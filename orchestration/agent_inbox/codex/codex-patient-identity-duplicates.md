# codex-patient-identity-duplicates

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/patient-identity-duplicates` |
| Status | integrated |
| Created | a095401 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-patient-identity-duplicates --commit-message "Patient identity duplicate foundation" --message "codex-patient-identity-duplicates ready for Codex review"` |

## Mission

Substantial Codex worker slice: start the backend foundation for safer patient creation by adding focused tests and minimal API/model support for patient identity fields and duplicate-candidate handling.

## Scope

### In Scope

app/models/patients.py; app/schemas/patients.py; app/routers/patients.py; alembic/versions if a migration is needed; tests/test_patients.py or a new focused patient identity test file; create_patient_file.py only if generated-file mapping needs a minimal adjustment.

### Out of Scope

Diary frontend; appointment/roster/nurse booking work; taskpane UI implementation; OneDrive import tooling; ADHA/IHI service integration; Medicare claiming integration; broad demographic redesign beyond the smallest useful fields/tests.

## Required Steps

1. Run the start command above.
   - Codex-app worker note: work from a disposable worker checkout/branch for
     `codex/patient-identity-duplicates`. Do not commit or push to the durable
     `codex/current` mirror, and do not use `C:\Users\YuriFrusin\Documents\EMR4-worktrees\codex`
     as the implementation checkout for this task.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not commit or push this task on `codex/current`; it is the durable mirror,
  not a Codex-app worker branch.
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

.venv\\Scripts\\python.exe -m pytest tests/test_patients.py -q plus any new focused patient identity tests; alembic upgrade/head check if migration added; git diff --check; generator smoke if create_patient_file.py touched.

## Merge Criteria

Patient creation/update/search contract has tests for duplicate candidates and important identifiers; Medicare IRN/IHI support is either implemented minimally or explicitly deferred with tests/docs showing the current boundary; no real patient data or generated documents are committed; branch is unique and does not touch codex/current/master/handoff/current.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/models/patients.py`, `app/schemas/patients.py`, `app/routers/patients.py`
    added Medicare IRN/IHI support and a warning-only duplicate-candidate API.
  - `alembic/versions/d4e5f6a7b8c9_add_patient_medicare_irn.py` adds
    `patients.medicare_irn` and an IHI index.
  - `tests/test_patients.py` adds focused patient identity, search, and duplicate
    candidate coverage.
- Verification run:
  - Codex worker: focused patient tests passed in an isolated throwaway test DB;
    Alembic upgrade/current check passed; `git diff --check` passed.
  - Orchestrator added a formatted-identifier regression test and re-ran the
    integration verification before committing.
- Remaining risks:
  - Duplicate detection is warning-only and heuristic; it does not replace formal
    IHI/Medicare validation.
  - Patient identifier fields are backend/schema foundations only until the
    taskpane New Patient/Edit Patient UI exposes them.
