# claude-sprint-n8-bernie-route-outcome-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | eb0de40 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n8-bernie-route-outcome-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n8-bernie-route-outcome-contract --commit-message "Sprint N8 Bernie route outcome contract" --message "claude-sprint-n8-bernie-route-outcome-contract ready for Codex review"` |

## Mission

Plan the route-level contract for wiring real Bernie interpret, supervised booking, proposal, and confirmation outcomes into server-owned Bernie session events.

## Scope

### In Scope

Plan only first. app/routers/appointments.py, app/services/bernie/session_store.py usage, appointment/Bernie schemas and focused tests. Define how route outcomes should append compact server events without PHI-heavy payloads, how failures map to no_slot/handed_off/proposal states, and how confirmation binding should stay fail-closed.

### Out of Scope

No production code before plan approval. No database migration or persisted session table. No GraphRAG/practice knowledge wiring. No Diary UI redesign. No autonomous booking or auto-confirm. No broad API-spine rewrite.

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

Focused Bernie route/session/confirmation tests, py_compile touched Python, git diff --check; Diary smoke only if deployable Diary assets change.

## Merge Criteria

Plan identifies exact routes and state outcomes, preserves staff-confirmed writes only, and gives bounded implementation steps with PHI/advisory/confirmation guardrails.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none.
- Verification run: Claude headless plan attempt returned 429 session limit reset notice before producing a plan.
- Remaining risks: Superseded by Ariadne/Codex implementation from the accepted Codex worker invariant plan.
