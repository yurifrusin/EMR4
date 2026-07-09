# antigravity-sprint257-practitioner-consumer-boundary

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 5c415db6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint257-practitioner-consumer-boundary --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint257-practitioner-consumer-boundary --commit-message "Sprint 257 practitioner consumer boundary" --message "antigravity-sprint257-practitioner-consumer-boundary ready for Codex review"` |

## Mission

Review the consumer/API ergonomics and external-client boundary for GET /api/v1/practice/practitioners before any rest_route_ready=true approval request.

## Scope

### In Scope

Inspect docs/api-spine/practitioner-directory-consumer-contract-check.md, tests/fixtures/api_spine_practitioner_directory/consumer_contract_report.json, scripts/practitioner_directory_consumer_contract_report.py, app/routers/practice.py, app/schemas/practice.py, and route tests. Produce a review packet under orchestration/agent_inbox/codex/ covering OpenAPI shape, query defaults/bounds, response fields, sensitive-field absence, internal-consumer fit, and external patient-client non-exposure.

### Out of Scope

Do not implement UI, client code, route/schema/service changes, GraphQL/SDL changes, provider/memory/H15/trove wiring, deployment changes, or readiness flag changes.

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

Static review preferred; optionally run the existing consumer contract report/test and report exact commands/results. Always report git status --short --branch.

## Merge Criteria

Ariadne can integrate the packet if it gives an explicit consumer-boundary pass/fail/dissent, identifies any contract ambiguity or external exposure concern, and keeps readiness approval separate from contract evidence.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
