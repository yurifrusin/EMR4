# antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 25d9ab5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics --commit-message "Sprint R25 no-write live-provider sampling UX semantics" --message "antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics ready for Codex review"` |

## Mission

Plan, then after approval define receptionist/product semantics for a default-disabled no-write live-provider sampling harness. Focus on evidence labels, staff copy, cost/latency expectations, and when to declare live-provider readiness unproven.

## Scope

### In Scope

orchestration docs/review artifact only; no-write live-provider sampling semantics; provider metadata expectations; receptionist-facing acceptance criteria; no-authority language

### Out of Scope

Making live Gemini/Vertex calls, enabling runtime prompt wiring, frontend UI, database migrations, real appointment writes, mutation routes, secrets or service-account setup

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

Submit a concrete review artifact or plan packet; no code tests unless relevant

## Merge Criteria

Ariadne can integrate clear acceptance criteria for a default-disabled no-write provider sampling harness

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: [receptionist_review_r25.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/receptionist_review_r25.md)
- Verification run: Verified `git status` output to ensure strict documentation-only scope compliance, and verified correct schema paths/links.
- Remaining risks: Telemetry metadata schema compliance must be enforced when the backend sampling scaffold is wired in. Latency must be monitored to ensure the timeout threshold and asynchronous isolation invariants hold under load.
