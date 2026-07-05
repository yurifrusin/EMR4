# codex-sprint-r13-deepseek-diary-smoke-focused-fix

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r13-diary-smoke-focused-fix` |
| Status | queued |
| Created | 137482c |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r13-deepseek-diary-smoke-focused-fix --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r13-deepseek-diary-smoke-focused-fix --commit-message "Sprint R13 DeepSeek focused Diary smoke recovery" --message "codex-sprint-r13-deepseek-diary-smoke-focused-fix ready for Codex review"` |

## Mission

Plan then implement the smallest deterministic harness/source fix that restores the unrelated Bernie session/pilot Diary smoke checks without weakening R12 reason-code coverage.

## Scope

### In Scope

Plan gate first. After approval, likely review/test_diary_smoke.py fixtures/helpers and docs/diary/diary.js only if diagnosis proves a real frontend regression. Preserve R12 reason-code tests and signed-confirm invariants.

### Out of Scope

Backend schema/routes, broad refactors, removing assertions instead of fixing setup/semantics, screenshots/manual browser exploration, live provider calls, and overlapping diagnosis artifact edits.

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

node --check docs\\diary\\diary.js if JS changes; focused failing Bernie session/pilot smoke tests; full review/test_diary_smoke.py if feasible; git diff --check.

## Merge Criteria

Focused failures pass or are reduced to documented genuine product defects; no R12 reason-code regression; Ariadne can review a narrow diff.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
