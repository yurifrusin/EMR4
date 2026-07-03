# codex-sprint-n8-route-outcome-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | eb0de40 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-n8-route-outcome-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-n8-route-outcome-invariants --commit-message "Sprint N8 route outcome invariants" --message "codex-sprint-n8-route-outcome-invariants ready for Codex review"` |

## Mission

Produce an invariant plan for wiring server-owned Bernie outcome events into the actual booking routes, with tests proving compact state transitions, idempotency/staleness, and no-write-before-confirm boundaries.

## Scope

### In Scope

Plan first. app/routers/appointments.py, app/services/bernie/session_store.py if tiny helper needed, app/services/bernie/session.py if transition constants need additive adjustment, tests/test_bernie_session_store.py, tests/test_bernie_signed_confirmation_evidence.py, and one focused route test file if needed.

### Out of Scope

No production code before plan approval. No persisted sessions, migrations, GraphRAG, Diary UI, taskpane, Command Centre, auto-mode, or broad API review.

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

Focused route/session tests, py_compile touched Python, git diff --check.

## Merge Criteria

Plan gives exact invariants for successful interpretation, no-slot, candidate/proposal, confirm success/failure, and session binding, with fail-closed behaviour and PHI-minimised payloads.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
