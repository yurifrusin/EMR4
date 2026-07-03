# antigravity-sprint-n7-diary-session-outcome-ui-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | f46cb2f |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-n7-diary-session-outcome-ui-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-n7-diary-session-outcome-ui-review --commit-message "Sprint N7 Diary session outcome UI review" --message "antigravity-sprint-n7-diary-session-outcome-ui-review ready for Codex review"` |

## Mission

Plan the Diary Bernie UI implications of server-owned outcome events: how the panel should refetch/render outcome state, handle stale revisions, preserve current booking UX, and avoid showing contradictory messages.

## Scope

### In Scope

Plan first only. docs/diary/diary.js, diary.css/html only if needed, review/test_diary_smoke.py. Focus on UI contract, stale/refetch states, no contradictory no-slot/proposal messages, and preserving current visible Bernie flow while server outcome events are added.

### Out of Scope

No implementation before plan approval, no backend route/schema changes, no database migration, no GraphRAG, no auto-mode, no taskpane/Command Centre, no visual redesign outside compact session/outcome state affordances.

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

Plan must specify node --check, focused route-intercepted Diary smoke checks for outcome snapshots, stale conflicts, confirm disabled on stale evidence, no browser PHI/session authority, and asset version checks if deployable assets change.

## Merge Criteria

Codex can accept the plan when the Diary remains a renderer/event source, contradictory UI messages are prevented by state/reason codes rather than ad hoc copy catches, and current Bernie booking/confirm flows are preserved.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
