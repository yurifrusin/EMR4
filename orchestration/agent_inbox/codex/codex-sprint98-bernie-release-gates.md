# codex-sprint98-bernie-release-gates

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint98-bernie-release-gates` |
| Status | queued |
| Created | 7c05164 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint98-bernie-release-gates --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint98-bernie-release-gates --commit-message "Sprint 98 Bernie release gates" --message "codex-sprint98-bernie-release-gates ready for Codex review"` |

## Mission

Plan independent Sprint 98 release gates so the exact issues from Yuri's screenshots block closeout: raw missing practitioner_id despite resolved practitioner, no path back to choose another slot, and Confirm booking returning generic Not Found.

## Scope

### In Scope

Plan only as a Codex worker. Inspect orchestration/bernie_release_gates.md, review/test_diary_smoke.py, scripts/smoke_bernie_interpreter.py, existing Bernie backend tests, and Sprint 97 closeout. Propose test/release-gate additions and documentation updates.

### Out of Scope

No production backend or Diary UI implementation, no GraphQL/API-spine implementation, no broad architecture docs beyond release-gate notes, and no code before approval.

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

Plan must include exact blocking tests/checks, distinguish route-intercepted from live checks, specify any live Diary residual user check, and name how CI/local review should catch generic Not Found and raw ID leaks.

## Merge Criteria

Ariadne accepts the plan only if it is independent of the backend/UI worker implementations and creates a practical closeout gate for the reported screenshots.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
