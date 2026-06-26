# claude-claude-bernie-slot-search-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | 3645361 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-claude-bernie-slot-search-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-claude-bernie-slot-search-proposal-contract --commit-message "Claude Bernie Slot Search Proposal Contract" --message "claude-claude-bernie-slot-search-proposal-contract ready for Codex review"` |

## Mission

Plan first, then after approval add a non-mutating backend slot-search proposal contract for future Bernie/reception use so staff can ask for candidate appointment slots without creating or changing appointments.

## Scope

### In Scope

Plan packet first. After approval, backend appointment/slots/proposal surfaces only as needed, likely app/schemas/appointments.py, app/routers/appointments.py, and focused tests. The endpoint should be practice-scoped, auth/role-gated, location-aware where current slot logic supports it, return typed candidate slots plus warnings/blocks/summary, and must not write appointments or audit rows.

### Out of Scope

Diary UI implementation, autonomous Bernie runtime, LLM calls, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, mutation of appointments, and broad scheduling redesign.

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

Plan packet first. After approval: py_compile touched backend modules/tests; focused pytest proving role/practice scoping, no appointment/audit writes, expected candidate slot output, conflict/break/location handling where applicable, and git diff --check.

## Merge Criteria

Codex can verify a typed, non-mutating slot-search proposal endpoint suitable for future Bernie command previews, with tests passing and no production UI or appointment mutation changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
