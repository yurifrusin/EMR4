# claude-sprint257-practitioner-readiness-veto

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 5c415db6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint257-practitioner-readiness-veto --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint257-practitioner-readiness-veto --commit-message "Sprint 257 practitioner readiness veto" --message "claude-sprint257-practitioner-readiness-veto ready for Codex review"` |

## Mission

Review whether GET /api/v1/practice/practitioners has enough evidence to ask Yuri for rest_route_ready=true, and submit a readiness/safety veto packet naming any blockers or unsafe implications.

## Scope

### In Scope

Read docs/api-spine/practitioner-directory-readiness-criteria.json, practitioner-directory-runtime-evidence-refresh.json, practitioner-directory-post-implementation-readiness-review.json, practitioner-directory-approved-gate.json, practitioner-directory-consumer-contract-check.md, app/routers/practice.py, app/schemas/practice.py, app/services/practice/practitioner_directory_read.py, and tests/test_practitioner_directory_route.py. Produce a concise review packet under orchestration/agent_inbox/codex/ with go/no-go recommendation, missing evidence, unsafe readiness wording, and exact blockers.

### Out of Scope

Do not edit route/schema/service code, readiness fixtures, tests, provider code, GraphQL/SDL, memory/RAG/GraphRAG, H15/H-series material, deployment config, or production readiness docs. Do not approve or flip rest_route_ready.

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

Static review only unless you choose to run focused existing tests. If tests are run, report exact commands/results. Always report git status --short --branch.

## Merge Criteria

Ariadne can integrate the packet if it gives an explicit go/no-go recommendation, maps findings to Sprint 255 readiness criteria, and names any blockers or confirms no blockers without implying readiness approval.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: orchestration/agent_inbox/codex/review-claude-sprint257-practitioner-readiness-veto.md (new — read-only review artifact, no route/schema/service/test/fixture changes)
- Verification run: static review only; git status --short --branch confirmed clean on claude/current; no tests run (read-only task per specification)
- Remaining risks: If Antigravity or DeepSeek lanes surface blockers not visible in the source files I reviewed (route variants, SDL stubs, missed imports), those should be treated as additive. The separate-Yuri-approval-payload requirement (criterion 13) is the hardest gate to skip — even when all four documentation gaps (rate-limit decision, deployment surface naming, RLS gap record, field encryption gap record) are closed, the readiness flip must still wait for a new approval payload targeting rest_route_ready=true specifically.
