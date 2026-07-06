# deepseek-sprint109-provider-gate-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 39dac51b |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task deepseek-sprint109-provider-gate-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task deepseek-sprint109-provider-gate-adversarial-review --commit-message "DeepSeek Sprint 109 provider-gate adversarial review" --message "deepseek-sprint109-provider-gate-adversarial-review ready for Codex review"` |

## Mission

DeepSeek Flash review only: identify adversarial failure modes and minimum blocking checks before any runtime-provider/live-smoke gate opening is proposed.

## Scope

### In Scope

Read AGENTS.md; orchestration/protocol_alerts.md; orchestration/parallel_workstreams.md; orchestration/sprint_closeout.md; orchestration/bernie_release_gates.md; Access AI/Bernie interpreter tests. Produce a compact adversarial review artifact; no production code.

### Out of Scope

No provider enablement, no live calls, no route/model/schema/UI edits, no database writes, no raw trove/H15/H-series runtime use, no memory/RAG/GraphRAG, no GraphQL mutations.

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

Artifact only; git diff --check if files are edited. Ariadne will verify and integrate any useful findings.

## Merge Criteria

Review names concrete risks, differentiates blockers from nice-to-haves, and keeps all blocked gates blocked pending Yuri approval.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/review-deepseek-sprint109-provider-gate-adversarial-review.md`
- Verification run:
  - DeepSeek worker ran `git diff --check`; Ariadne reran proposal guard and
    diff hygiene before integration.
- Remaining risks:
  - Review only; no gate value changed.
