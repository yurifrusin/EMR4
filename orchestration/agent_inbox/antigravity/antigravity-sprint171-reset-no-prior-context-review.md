# antigravity-sprint171-reset-no-prior-context-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | ff2d57d4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint171-reset-no-prior-context-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint171-reset-no-prior-context-review --commit-message "Sprint 171 reset no-prior context review" --message "Sprint 171 reset/no-prior context review ready for Codex review"` |

## Mission

Plan first, then after approval provide independent product/domain review for the Sprint 171 reset/no-prior context matrix. Challenge whether the proposed fixtures match receptionist expectations and avoid unsafe inherited context.

## Scope

### In Scope

Plan packet first. After approval, review artifacts under orchestration/agent_inbox/codex or docs/adversarial if useful; optionally propose fixture names and acceptance points. Focus on explicit context reset, omitted context threading, no-prior partial follow-ups, current-turn relative date anchoring, and staff-facing safety implications.

### Out of Scope

Production app code, Diary UI changes, live provider/provider dry-run, memory/RAG/GraphRAG, H15/H-series runtime, historical diary material, GraphQL mutations, model-to-database writes, broad UX redesign, raw fixture rewrites outside approved Sprint 171 scope.

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

Read-only review artifact or focused tests if useful; .\.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q; .\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q; git diff --check

## Merge Criteria

Plan accepted first; review artifact gives concrete accept/reject criteria or low-risk fixture suggestions; no provider/runtime gates are opened; any implementation suggestions remain bounded to authored synthetic replay fixtures.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
