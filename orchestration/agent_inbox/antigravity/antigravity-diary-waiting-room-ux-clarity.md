# antigravity-diary-waiting-room-ux-clarity

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 7fd03d0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-waiting-room-ux-clarity --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-waiting-room-ux-clarity --commit-message "Diary waiting room UX clarity" --message "antigravity-diary-waiting-room-ux-clarity ready for Codex review"` |

## Mission

Design and, after plan approval only, implement diary Waiting Room panel clarity improvements for receptionist workflow. This sprint is plan-gated: first produce the implementation plan and stop.

## Scope

### In Scope

Potentially docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js. Focus on the Waiting Room side panel only: clearer section counts, less noisy area tabs, card density/stacking ideas inside the panel, and clearer action wording around Check In/Start Consult/Complete if needed.

### Out of Scope

Do not alter diary grid appointment positioning, overlap handling, start/end time geometry, booking duration rendering, booking create/edit modal behaviour, taskpane, backend, Command Centre, drag/drop/resize, or Bernie. Do not start coding until Codex/user approves the plan and says complete sprint task.

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

Plan stage: implementation plan packet plus GUI echo. Implementation stage after approval: node --check docs\\diary\\diary.js, git diff --check, and manual visual acceptance notes for Waiting Room panel only.

## Merge Criteria

Codex accepts the plan before coding; changes are limited to the Waiting Room panel; diary booking slots remain positioned by actual time/duration with no unintended cascade/stacking; panel improvements help receptionist scanning without changing appointment semantics.

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
  - Diff check: `git diff --check` passed.
  - Test suite: `pytest tests/test_appointment_patient_link.py tests/test_booking_create_edit.py` passed 100% (40/40 tests).
  - Manual checklist: Collapsible sections expand/collapse correctly, chevrons adjust dynamically, tab layout behaves as a segmented control, count badges render on the right, and hover action buttons reduce visual noise.
- Remaining risks:
  - None. Changes are purely cosmetic and structural within the Waiting Room panel layout, fully isolated from core appointment positioning or billing flows.
