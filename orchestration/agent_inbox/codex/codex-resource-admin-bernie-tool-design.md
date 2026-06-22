# codex-resource-admin-bernie-tool-design

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/resource-admin-bernie-tool-design` |
| Status | queued |
| Created | 7fd03d0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-resource-admin-bernie-tool-design --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-resource-admin-bernie-tool-design --commit-message "Resource admin and Bernie tool design" --message "codex-resource-admin-bernie-tool-design ready for Codex review"` |

## Mission

Design the next backend/resource-admin foundation needed before Bernie can safely suggest receptionist actions. This sprint is plan-gated: first produce the implementation plan and stop.

## Scope

### In Scope

Orchestration/design docs, implementation_plan.md notes if appropriate, and possibly a thin backend/API design proposal for room/resource/waiting-area admin and Bernie tool boundaries. Identify canonical concepts and exact future endpoints/tools, but do not implement production code before plan approval.

### Out of Scope

No UI implementation, no autonomous Bernie actions, no LLM agent runtime, no booking drag/drop/resize, no production schema migration unless explicitly approved after the plan, and no edits to Claude/Antigravity task packets. Do not start coding until Codex/user approves the plan and says complete sprint task.

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

Plan stage: implementation plan packet plus GUI echo. Implementation stage after approval: docs diff check, and any code verification only if implementation scope is explicitly approved.

## Merge Criteria

Codex/user accept the plan; design separates rooms, resources, waiting areas, patient identity, attendance status, and future Bernie supervised tool calls; next implementation slices are concrete and testable.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
