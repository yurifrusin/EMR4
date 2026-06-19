# codex-patient-search-new-patient-hardening

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/patient-search-new-patient-hardening` |
| Status | in_progress |
| Created | 14bc9e4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-patient-search-new-patient-hardening --commit-message "Patient search new patient hardening" --message "codex-patient-search-new-patient-hardening ready for Codex review"` |

## Mission

Substantial Codex-worker implementation slice: harden the DB-backed patient search and New Patient creation path so the project has reliable tests around how patients enter the system and how staff find them.

## Scope

### In Scope

Focused backend patient tests and minimal fixes they expose. Prefer tests/test_patients.py or a new focused patient create/search test file. Candidate coverage: POST /patients, POST /patients/with-file, GET /patients/search by name/Medicare/phone, practice scoping, duplicate/validation edge cases if current API defines them, and generated filename/file-path response behaviour. Production changes may touch app/routers/patients.py, app/schemas/patients.py, create_patient_file.py, and seed/test helpers only as needed.

### Out of Scope

OneDrive or filesystem import tools; broad patient-file migration; appointment or diary frontend code; booking/status endpoints; taskpane UI; Command Centre; Gemini/AI behaviour; unrelated refactors.

## Required Steps

1. Work from a disposable Codex worker checkout on `codex/patient-search-new-patient-hardening`, starting from `handoff/current`.
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

Run the focused patient test suite you create or extend, plus any existing patient tests. Run git diff --check. If create_patient_file.py is touched, run a minimal generator smoke test or explain why not.

## Merge Criteria

Patient search/New Patient behaviour is covered by meaningful tests; any production changes are minimal and match existing API style; no real patient data or generated patient files are committed; completion notes include files changed, verification, remaining risks, and whether user manual testing is needed.

## Dissent / Risks

No dissent on the patient changes. Out-of-scope note: while checking the broader
suite, the pre-existing appointment tests failed independently with appointment
creation 500s and then test DB fixture errors (`practices` missing after teardown).
Those failures were not caused by the patient-lane changes and should be handled
by the appointment-contract lane or integration review.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/routers/patients.py`, `tests/test_patients.py`, this task packet.
- Verification run: `.venv\Scripts\python.exe -m pytest tests\test_patients.py -q` -> 8 passed; reran after broader-suite failure -> 8 passed. `git diff --check` -> clean. `create_patient_file.py` was not touched; the `/patients/with-file` test generates a real `.docx` into pytest `tmp_path` as the generator smoke path.
- Remaining risks: No user manual testing required for this backend-only hardening. Full `pytest tests -q` was attempted twice but timed out before completion; the existing appointment tests then failed separately with appointment-router/test-fixture errors outside this workstream.
