# claude-sprint-r1-bernie-scenario-replay-harness

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | 788242c |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r1-bernie-scenario-replay-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r1-bernie-scenario-replay-harness --commit-message "Sprint R1 Bernie Scenario Replay Harness" --message "claude-sprint-r1-bernie-scenario-replay-harness ready for Codex review"` |

## Mission

Build the backend pytest replay harness for the first Bernie receptionist scenario corpus. The harness should load version-controlled scenario fixtures, run ordered backend/session turns where feasible, assert structured outcomes/preserved fields/forbidden outcomes, and support expected-failing scenarios for known behaviour that R2 will fix.

## Scope

### In Scope

1) Inspect existing Bernie/session/interpreter tests and reuse their fixtures/patterns. 2) Add a compact scenario loader and pytest harness under tests/bernie_scenarios/ or an equivalent test-only package. 3) Define the scenario schema fields needed for R1: id, category, reference_date, initial_state, turns, expected outcomes, preserved fields, forbidden outcomes, and optional xfail reason. 4) Add minimal seed/demo fixtures only if required to prove the harness mechanics; Antigravity owns the main corpus content. 5) Keep the harness backend/session/domain focused and emit compact pass/fail evidence.

### Out of Scope

No Diary frontend/UI changes. No broad prompt rewrite. No GraphRAG, production PHI/log ingestion, auto-mode, or unconfirmed writes. Do not fix the clarification merge bug in this lane unless Ariadne explicitly expands scope after plan review. Do not own the full scenario corpus content beyond minimal harness fixtures.

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

py_compile on new/changed test harness files; focused pytest for tests/bernie_scenarios or equivalent; relevant existing Bernie session/interpreter tests if touched; git diff --check

## Merge Criteria

Harness loads fixtures deterministically, supports expected failures, proves at least one passing scenario path or documented harness-only fixture, stays test-only unless a tiny justified seam is approved, and leaves scenario authorship boundary clear for Antigravity

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
