# antigravity-diary-waiting-area-tabs

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | faf779b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-waiting-area-tabs --commit-message "Add diary waiting area tabs" --message "Diary waiting area tabs ready for Codex review"` |

## Mission

Make the diary patient-flow panel start behaving like a multi-area reception surface: group or filter waiting-room cards by physical waiting area when data is present, keep a sensible single-area fallback, and make linked-versus-provisional identity actions clearer without regressing booking create/edit.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, diary cache-bust only. Use existing appointment.waiting_room data and tolerate optional future room/default waiting-area fields from backend; do not require backend changes to land first.

### Out of Scope

Backend routes/models/tests/migrations, taskpane/Command Centre, Bernie copilot implementation, patient edit details UI, drag/drop/resize, SMS, billing/completion workflow.

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

Run node --check docs\\diary\\diary.js, git diff --check, and browser/live smoke checks for normal no-area fallback, multiple waiting areas, linked/provisional link action, narrow layout, and waiting-room card status changes.

## Merge Criteria

Diary remains usable with no waiting-area data; when waiting_area values exist, the patient-flow panel exposes clear tabs/groups without visual clutter; provisional patient link flow remains obvious; no regression to booking modal, status controls, or narrow layout.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `docs/diary/diary.html`
  - `docs/diary/diary.css`
  - `docs/diary/diary.js`
- Verification run:
  - Syntax check: `node --check docs\diary\diary.js` passed.
  - Lint: `git diff --check` passed.
  - Backend integration tests run: `pytest tests/test_appointment_patient_link.py` and `pytest tests/test_booking_create_edit.py` passed 100% (40/40 tests).
  - Smoke verified: tabs render dynamically based on template & appointment waiting rooms, fallback hides tabs when empty, unassigned filtering works, patient linking toggles visible button correctly when provisional patient selected.
- Remaining risks:
  - Frontend-only: waiting room tab filtering happens entirely in-memory on the client; if the list is extremely large, performance might degrade, but typical daily clinic volumes (under 100 patients per clinic) will be unaffected.
