# codex-bernie-reception-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-reception-acceptance-review` |
| Status | integrated |
| Created | 67f1c02 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-reception-acceptance-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-reception-acceptance-review --commit-message "Bernie Product API Acceptance Review" --message "codex-bernie-reception-acceptance-review ready for Codex review"` |

## Mission

Independently analyse the current Bernie screenshots, backend contracts, diary UI, audit seams, and implementation-plan fit; submit acceptance criteria and risks for Ariadne to use when judging Claude and Antigravity plans.

## Scope

### In Scope

Plan/review packet first only. Read-only inspection of Bernie backend contracts, diary UI, review harness, Access AI/audit seams, orchestration/resource_admin_bernie_tool_design.md, orchestration/phase_programmes.md, and screenshots. Identify what is working, what is not, what belongs in Sprint 96, what must be deferred, and what should cause plan resubmission.

### Out of Scope

Production code edits before plan approval; implementing or integrating other worker work; live service setup; live Caller ID/OPV/phone integration; broad implementation-plan rewrite; broad security/dependency work.

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

Review must include concrete acceptance gates, hidden risks, API/UX resubmission criteria, recommended focused tests, and an explicit check that Caller ID and OPV/PVM remain placeholders only for this sprint.

## Merge Criteria

Ariadne accepts the review if it gives actionable criteria for accepting/rejecting the other plans and keeps Sprint 96 focused on product usability plus API rigor.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Read-only acceptance criteria used as Ariadne input; no production files integrated from this packet.
- Verification run: Acceptance criteria were reconciled into `orchestration/sprint_96_plan_review.md` and the replacement UX implementation.
- Remaining risks: None for this packet; live phone and external identity-provider work remains deferred.
