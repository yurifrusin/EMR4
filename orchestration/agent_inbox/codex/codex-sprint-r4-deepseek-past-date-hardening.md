# codex-sprint-r4-deepseek-past-date-hardening

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r4-past-date-hardening` |
| Status | submitted |
| Created | 20a420f |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r4-deepseek-past-date-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r4-deepseek-past-date-hardening --commit-message "Sprint R4 DeepSeek past-date hardening" --message "codex-sprint-r4-deepseek-past-date-hardening ready for Codex review"` |

## Mission

Use DeepSeek Flash to harden Bernie slot normalization and supervised/interpret proposal paths so backdated or past requested appointment dates cannot proceed as safe executable searches/proposals.

## Scope

### In Scope

app/services/bernie_slot_normalizer.py; narrowly related app/routers/appointments.py handling if needed; focused tests for normalizer, interpret route, and supervised booking past-date behavior; R4 docs/closeout notes.

### Out of Scope

Diary UI redesign; Word/taskpane assets; live provider calls; patient collision cap/self-source work already fixed in D8; broad session store redesign; GraphRAG/indexer automation.

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

py_compile touched Python files; pytest focused normalizer/interpret/supervised R4 tests plus adjacent D8 collision tests; git diff --check.

## Merge Criteria

Past absolute dates before the request/reference date block deterministically with typed issue code and no executable proposal; today same-day clamp behavior remains unchanged; D8 collision tests remain green.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
