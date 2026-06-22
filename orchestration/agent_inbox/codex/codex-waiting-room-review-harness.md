# codex-waiting-room-review-harness

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | completed |
| Created | 4d8d1c7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-waiting-room-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-waiting-room-review-harness --commit-message "Waiting room review harness" --message "codex-waiting-room-review-harness ready for Codex review"` |

## Mission

Plan, then after approval prepare the Sprint 15 review harness and design guardrails for room-to-waiting-area defaults, Expected Today compacting, and direct API/user-review checks.

## Scope

### In Scope

orchestration docs, sprint_closeout draft/checklist, PowerShell API snippets for waiting-area check-in verification, design notes only if needed. May reference orchestration/resource_admin_bernie_tool_design.md.

### Out of Scope

No production backend/frontend code, no migrations, no taskpane/Command Centre, no Bernie runtime, no drag/drop/resize, no duplicating Claude/Antigravity implementation scopes.

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

Plan packet first. After approval: git diff --check; no runtime tests unless helper scripts are added.

## Merge Criteria

Codex accepts the plan before work; output gives the user exact manual/API review steps and preserves room/resource/waiting-area terminology; no production code changed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/sprint_closeout.md`; `orchestration/agent_inbox/codex/codex-waiting-room-review-harness.md`
- Verification run: `git diff --check`
- Remaining risks: This is a review harness only. It assumes the integrated Sprint 15 backend/UI work will expose clear behaviour for room default waiting-area assignment, explicit area override, and terminal-status clearing/filtering. Codex/orchestrator still needs to compare the checklist against Claude/Antigravity's final implementation details before declaring Sprint 15 ready for user review.
