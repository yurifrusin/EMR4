# codex-command-proposal-review-harness

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/command-proposal-review-harness` |
| Status | queued |
| Created | 7a8d07d |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-command-proposal-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-command-proposal-review-harness --commit-message "Add command proposal review harness" --message "Command proposal review harness ready for Codex review"` |

## Mission

Plan first, then after approval create the review harness and developer-facing API snippets for the formal command/proposal layer so future sprints can test agent-safe workflows consistently.

## Scope

### In Scope

orchestration docs, sprint closeout/review harness updates, developer guide snippets if an existing guide is the right place, PowerShell/API examples for the create proposal endpoint and expected response classes.

### Out of Scope

Production backend/frontend changes, migrations, diary UI, taskpane, Command Centre, Bernie runtime, modifying Claude/Antigravity packets after dispatch.

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

Plan packet first. After approval: git diff --check and, if snippets are executable, one local API or schema-level verification note.

## Merge Criteria

Review harness clearly explains how to test proposal/safe/blocked/warning paths; future worker agents can reuse the pattern; no runtime behaviour changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
