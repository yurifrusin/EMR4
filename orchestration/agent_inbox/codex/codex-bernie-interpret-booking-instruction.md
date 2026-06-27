# codex-bernie-interpret-booking-instruction

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-interpret-booking-instruction` |
| Status | queued |
| Created | 558734e |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-interpret-booking-instruction --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-interpret-booking-instruction --commit-message "Dispatch Sprint 63 Bernie interpret booking instruction" --message "Sprint 63 dispatched: Bernie interpret booking instruction endpoint"` |

## Mission

Add the first read-only Bernie AI runway slice: a mocked-first booking-instruction interpretation provider boundary and endpoint that converts staff text into validated structured booking intent without writes, audits, PHI logging, or direct model coupling.

## Scope

### In Scope

Backend-only provider abstraction and route contract for interpreting a booking instruction; config/default-off posture; fake provider for tests; strict request/response schemas for intent, slots, confidence, missing fields, safety flags, and clarifying question; deterministic tests proving no DB writes, no audit writes, no live LLM/provider call by default, and safe validation/fallback behavior.

### Out of Scope

No frontend UI, no real booking/proposal creation, no appointment mutation, no audit writes, no Gemini/Vertex live call in tests, no provider credentials, no prompt tuning beyond a minimal interface, no PHI logging, no taskpane/diary visual changes, no migrations unless absolutely required and justified in the plan.

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

py_compile touched backend files; focused pytest for Bernie interpret endpoint/provider fake; adjacent Bernie supervised booking/review payload tests if relevant; no-write/no-audit/no-LLM proof; git diff hygiene.

## Merge Criteria

Plan packet first with Role codex-worker, Worker Name Cicero, Worker Branch codex/bernie-interpret-booking-instruction; implementation only after explicit complete sprint task; narrow backend-only diff; deterministic tests pass; endpoint is read-only and default-safe.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
