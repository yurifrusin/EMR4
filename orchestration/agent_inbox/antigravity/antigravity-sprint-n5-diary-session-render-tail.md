# antigravity-sprint-n5-diary-session-render-tail

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 9a38e67 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-n5-diary-session-render-tail --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-n5-diary-session-render-tail --commit-message "Sprint N5 diary session render tail" --message "antigravity-sprint-n5-diary-session-render-tail ready for Codex review"` |

## Mission

Plan Sprint N5 Diary UI work to consume the minimal Bernie session endpoint: active-session load, new-session event, event append/refetch, stale revision banner, latest-message/history rendering, and confirm evidence echo without browser-owned authority.

## Scope

### In Scope

Plan first only. docs/diary/diary.js, diary.html/css if needed, review/test_diary_smoke.py. Use N4/N5 server state as source of truth; browser holds presentation state only. Preserve latest-message visible default and older history disclosure. No browser storage of PHI.

### Out of Scope

No implementation before plan gate, no backend schemas/routes, no visual redesign, no GraphRAG/practice-knowledge wiring, no auto-confirm, no taskpane/Command Centre work, no live PHI.

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

Plan must specify node --check, route-intercepted/session endpoint Playwright smoke checks, stale revision/refetch checks, no localStorage/sessionStorage PHI checks, and frontend asset version policy if runtime assets change.

## Merge Criteria

Codex can accept the plan when the UI is renderer/event source only, no client authority is introduced, exact files/tests are named, and stale/conflict UX is clear.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
