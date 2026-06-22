# claude-location-scoped-diary-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 32f1577 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-location-scoped-diary-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-location-scoped-diary-contract --commit-message "Add location-scoped diary contract" --message "Location-scoped diary backend contract ready for Codex review"` |

## Mission

Plan first, then after explicit approval implement the smallest backend changes needed so diary templates, rooms, waiting areas, rosters, and appointments do not assume one physical location per practice.

## Scope

### In Scope

PracticeLocation, Room, WaitingArea, DiaryTemplate, DiaryRoster, Appointment.location_id, seed/test data, focused schemas/routers/tests, migrations only if needed.

### Out of Scope

Diary frontend, taskpane, Command Centre, full practice/location admin UI, drag/drop/resize, online booking portal, Bernie runtime.

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

Plan packet first. After approval: focused location/diary/appointment pytest, backend py_compile, migration check if changed, git diff --check.

## Merge Criteria

A one-location practice continues to behave exactly as today; multi-location data cannot leak or ambiguously mix diary templates/rooms/waiting areas/rosters/appointments; tests describe the intended location boundary.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
