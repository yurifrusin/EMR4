# claude-sprint-r6-temporal-harness-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | d367b7f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r6-temporal-harness-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r6-temporal-harness-foundation --commit-message "Sprint R6 Claude temporal harness foundation" --message "claude-sprint-r6-temporal-harness-foundation ready for Codex review"` |

## Mission

Implement a compact deterministic temporal-boundary harness or focused pytest coverage for Bernie same-day/past-date slot-search policies, prioritising clock-injected same-day past-window coverage without production behavior changes unless a real bug is exposed.

## Scope

### In Scope

tests/bernie_scenarios loader/replay fixtures if minimal clock support is needed; selected executable fixture(s); focused route/harness tests around same-day window_fully_past, clamp_earliest, and past-date boundaries; completion notes.

### Out of Scope

Diary UI, taskpane/Word assets, GitHub Pages assets, live provider calls, broad session-store redesign, raw appointment mutation date-policy changes, migrations, broad harness rewrite.

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

py_compile touched harness/tests; pytest tests/test_bernie_scenario_integrity.py tests/bernie_scenarios -q; focused same-day/no-slot/slot-search tests as applicable; git diff --check.

## Merge Criteria

At least one high-value same-day or temporal-boundary behavior becomes deterministic executable coverage, existing R5 past-date replay still passes, and no production behavior changes are made unless justified by failing tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
