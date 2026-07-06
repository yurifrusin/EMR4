# claude-r30-action-grammar-replay-consumer

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/action-grammar-replay-consumer` |
| Status | queued |
| Created | da852ba5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-r30-action-grammar-replay-consumer --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-r30-action-grammar-replay-consumer --commit-message "Dispatch R30 action grammar replay consumer" --message "claude-r30-action-grammar-replay-consumer ready for Codex review"` |

## Mission

Plan the deterministic synthetic replay consumer over the R29 native Diary action grammar. The consumer should replay authored fake day/action slices against grammar invariants, proving useful consumption before any H15 semantic gate opening or full-trove mining. Plan first only; no implementation until approved.

## Scope

### In Scope

Read AGENTS.md, R28 Fable full-trove readiness packet, R29 action grammar files/tests/reviews, existing Bernie scenario/replay tests, and action envelope/confirm gate tests. Produce an implementation-ready plan naming exact fixture/test/helper files, synthetic fixture shape, grammar consumption invariants, no-write/no-provider/no-trove boundaries, and verification.

### Out of Scope

Production route/UI/provider changes before approval, raw local_data, ignored JSON, H15 semantic fixtures, broad full-trove processing, live provider calls, migrations, autonomous writes, and master/handoff movement.

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

Plan packet only. Must include file boundary, synthetic-only fixture rules, no raw/H-series semantic promotion, no route/UI changes, focused pytest plan, and how replay proves grammar consumption without tautology.

## Merge Criteria

Ariadne receives an implementation-ready plan for the smallest deterministic synthetic replay consumer over the action grammar.

## Dissent / Risks

Claude session-limited; Codex produced the plan. See orchestration/agent_inbox/codex/plan-r30-action-grammar-replay-consumer.md for full plan.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- orchestration/agent_inbox/codex/plan-r30-action-grammar-replay-consumer.md (new plan artifact produced by Codex)
- Verification run:
- Plan packet inspection only. Claude unavailable; Codex produced the plan. See plan artifact for full verification steps.
- Remaining risks:
- Tautology risk is the central design challenge; plan addresses with authored expected values, consumer-side dispatch branching, and standalone synthetic-descriptor test.
- Claude lane replaced per protocol; DeepSeek Flash or Ariadne should implement per plan.
