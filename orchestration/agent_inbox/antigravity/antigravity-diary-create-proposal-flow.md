# antigravity-diary-create-proposal-flow

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 7a8d07d |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-create-proposal-flow --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-create-proposal-flow --commit-message "Use appointment create proposal in diary modal" --message "Diary create proposal flow ready for Codex review"` |

## Mission

Plan first, then after approval make the diary booking modal call the appointment create proposal endpoint before writing a new booking, so reception sees clear conflict blocks, break warnings, provisional-patient warnings, and an explicit confirmation step.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, diary cache-bust only if assets change. Booking-create modal flow only; use POST /api/v1/appointments/proposals/create before POST /appointments.

### Out of Scope

Backend route/schema changes, taskpane, Command Centre, waiting-room panel layout, main diary appointment geometry, location selector redesign, patient demographics, Bernie runtime, drag/drop/resize.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

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

Plan packet first. After approval: node --check docs\\diary\\diary.js; git diff --check; visual/manual notes for safe create, break warning confirmation, conflict block, provisional patient warning if UI supports provisional booking.

## Merge Criteria

New booking creation still works; conflict/break/provisional messages are receptionist-friendly; blocked proposals do not write; confirmed proposals write through existing create endpoint; no unrelated diary layout changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - docs/diary/diary.html
  - docs/diary/diary.css
  - docs/diary/diary.js
- Verification run:
  - JavaScript Syntax Verification (node --check docs/diary/diary.js) - Passed successfully.
  - Whitespace check (git diff --check) - Clean.
  - Backend pytest suite (python -m pytest tests/test_appointment_patient_link.py tests/test_booking_create_edit.py) - 40 passed.
- Remaining risks:
  - Mock proposal checking runs locally in smoke mode; live mode depends on the correctness and availability of the backend proposals/create route.
