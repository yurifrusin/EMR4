# claude-sprint109-band2-provider-gate-criteria

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/sprint109-band2-provider-gate-criteria` |
| Status | queued |
| Created | 39dac51b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint109-band2-provider-gate-criteria --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint109-band2-provider-gate-criteria --commit-message "Sprint 109 Band-2 provider gate criteria" --message "claude-sprint109-band2-provider-gate-criteria ready for Codex review"` |

## Mission

Plan only: define the backend/API criteria and evidence packet required before any Bernie/Access AI runtime-provider or live-smoke gate could be considered for approval.

## Scope

### In Scope

AGENTS.md; orchestration/parallel_workstreams.md; orchestration/sprint_closeout.md; orchestration/bernie_release_gates.md; Access AI and Bernie interpreter tests/docs. Produce a concise review plan/artifact only; identify required commands, blocked values, approval payload shape, and exact no-enable boundaries.

### Out of Scope

No code wiring, no provider enablement, no live calls, no GCP/ADC changes, no route/schema/model mutations, no GraphQL mutations, no H15/trove, no memory/RAG/GraphRAG, no database writes from model output.

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

Plan artifact only; cite files inspected and proposed verification commands. git diff --check if files are edited.

## Merge Criteria

Artifact is proposal-only, names blocked gates that remain blocked, and states explicit Yuri approval requirement before any gate changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
