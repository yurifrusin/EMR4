# claude-appointment-cancel-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 1f26087 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-cancel-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-cancel-proposal-contract --commit-message "appointment-cancel-proposal-contract" --message "claude-appointment-cancel-proposal-contract ready for Codex review"` |

## Mission

Plan first, then harden the backend contract for destructive appointment cancellation/deletion so diary cancellation can be preflighted before any write. Confirm whether existing status/waiting-area proposals cover cancellation adequately or whether a dedicated cancel/delete proposal endpoint/test coverage is needed.

## Scope

### In Scope

app/routers/appointments.py; app/schemas/appointments.py; focused appointment proposal/cancel/delete tests; minimal production fixes only if tests expose a real safety gap

### Out of Scope

Diary frontend implementation; taskpane; Command Centre; patient workflows; resource admin; migrations unless a proven schema issue; broad appointment redesign; direct writes that bypass proposal semantics

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

Plan packet first. After complete sprint task: py_compile touched appointment router/schema, focused pytest for cancellation/delete proposal semantics and adjacent appointment update/status proposal tests, git diff --check

## Merge Criteria

Codex can verify cancellation/delete is proposal-gated or explicitly proven safely covered by existing proposal contracts, destructive writes are blocked/warning-gated as appropriate, tests are scoped and passing, and no unrelated surfaces changed

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
