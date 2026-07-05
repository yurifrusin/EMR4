# claude-sprint-r7-raw-temporal-guard-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | ad2ea75 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r7-raw-temporal-guard-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r7-raw-temporal-guard-contract --commit-message "Sprint R7 Raw Temporal Guard Contract" --message "claude-sprint-r7-raw-temporal-guard-contract ready for Codex review"` |

## Mission

Implement explicit temporal/date guardrails for raw appointment create/update and compatibility proposal paths, using existing diary temporal policy helpers where safe.

## Scope

### In Scope

app/routers/appointments.py; app/services/diary/temporal.py only if a tiny reusable helper is needed; focused backend tests for direct create/update/proposal temporal rejection or clarification semantics.

### Out of Scope

Diary UI, taskpane/Word assets, migrations, live provider calls, broad route rewrites, signed-confirm authority redesign, receptionist scenario corpus changes unless needed for a focused regression.

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

Run py_compile for touched backend/tests and focused pytest for raw appointment temporal guards plus adjacent existing appointment proposal/status tests selected by the implementation plan.

## Merge Criteria

Past absolute dates and fully elapsed same-day raw mutation windows cannot silently create or move appointments; compatible paths keep existing signed-confirm/evidence boundaries; tests prove no regression for valid future/same-day-open requests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
