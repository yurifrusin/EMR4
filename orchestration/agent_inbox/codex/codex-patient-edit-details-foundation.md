# codex-patient-edit-details-foundation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/patient-edit-details-foundation` |
| Status | integrated |
| Created | faf779b |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-patient-edit-details-foundation --commit-message "Add patient edit details foundation" --message "Patient edit details foundation ready for Codex review"` |

## Mission

Add the first safe patient-detail editing foundation for the taskpane and backend. The aim is to let staff correct demographics/identifiers after patient creation while preserving the hard duplicate protections for IHI and Medicare card plus IRN.

## Scope

### In Scope

app/routers/patients.py, app/schemas/patients.py, tests/test_patients.py, EMR4 Sidebar/src/taskpane/taskpane.html, EMR4 Sidebar/src/taskpane/taskpane.css, EMR4 Sidebar/src/taskpane/taskpane.js, docs/taskpane/* via sync_taskpane.py, cache-bust if taskpane assets change. Keep the UI restrained: an Edit Patient Details action for the currently loaded patient, not a full patient administration module.

### Out of Scope

Diary frontend, waiting-area backend contract, appointment routes/models, Command Centre clinical coding, generated Word document rewrite, OneDrive import tooling, ADHA/IHI live verification, OCR, Bernie copilot implementation.

## Required Steps

1. Run the start command above.
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

Run focused patient pytest, node --check on taskpane source and docs copy, sync_taskpane.py if source taskpane changes, git diff --check, and any small smoke/manual notes needed for edit/cancel/save/duplicate-block behaviours.

## Merge Criteria

PUT /patients/{id} blocks hard duplicates against other patients while allowing the same patient to keep their own identifiers; taskpane exposes a usable edit-details path for the loaded patient; duplicate/error/success/cancel states are clear; docs/taskpane is synced and cache-busted; no diary or appointment regressions.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/routers/patients.py`; `tests/test_patients.py`; `EMR4 Sidebar/src/taskpane/taskpane.html`; `EMR4 Sidebar/src/taskpane/taskpane.css`; `EMR4 Sidebar/src/taskpane/taskpane.js`; synced `docs/taskpane/taskpane.html`; synced `docs/taskpane/taskpane.css`; synced `docs/taskpane/taskpane.js`.
- Verification run: `python sync_taskpane.py` (succeeded; existing docstring `\S` SyntaxWarning); `node --check "EMR4 Sidebar\src\taskpane\taskpane.js"`; `node --check docs\taskpane\taskpane.js`; `git diff --check` (exit 0; Git line-ending warning for synced docs JS); focused patient pytest passed with isolated DB: `$env:TEST_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_test_patient_edit'; C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_patients.py -q` -> 20 passed. Earlier attempts against the default shared `gp_pms_test` collided with a concurrent pytest process from another workstream and produced fixture duplicate-user/teardown errors; no patient-edit assertion failed there before the shared-DB collision.
- Remaining risks: Taskpane edit/cancel/save/duplicate-block paths were code-reviewed and syntax-checked but not manually exercised inside Word/Office; saving patient demographics updates the DB and in-memory taskpane banner only, and intentionally does not rewrite the generated Word document header/file name.
