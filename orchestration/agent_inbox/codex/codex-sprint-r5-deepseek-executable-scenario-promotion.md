# codex-sprint-r5-deepseek-executable-scenario-promotion

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r5-scenario-promotion` |
| Status | submitted |
| Created | 2687ef6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r5-deepseek-executable-scenario-promotion --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r5-deepseek-executable-scenario-promotion --commit-message "Sprint R5 DeepSeek executable scenario promotion" --message "codex-sprint-r5-deepseek-executable-scenario-promotion ready for Codex review"` |

## Mission

Use DeepSeek Flash to promote selected R3/R4 natural-language Bernie receptionist fixtures into executable scenario replay coverage where the current harness can express the behavior cleanly, starting with past-date guardrails and same-day past-window clarification.

## Scope

### In Scope

tests/fixtures/bernie_scenarios/*.yaml selected R3/R4 fixtures; tests/bernie_scenarios/loader.py and replay.py only if minimal schema/action support is needed; focused scenario integrity/replay tests; closeout notes.

### Out of Scope

Diary UI, taskpane/Word assets, live provider calls, direct raw appointment mutation date-policy hardening, broad session-store redesign, GraphRAG/MCP/indexer automation.

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

py_compile touched harness files; pytest tests/test_bernie_scenario_integrity.py tests/bernie_scenarios -q; focused adjacent Bernie normalizer/confidence/supervised tests if R4 fixtures are promoted; git diff --check.

## Merge Criteria

At least one high-value R3/R4 corpus scenario becomes executable and passes; non-executable scenarios remain valid corpus memory with xfail/reason metadata; no appointment/audit mutation occurs unless a scenario explicitly expects it.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
