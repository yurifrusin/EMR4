# codex-sprint106c-context-frame-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 1fec462 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint106c-context-frame-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint106c-context-frame-invariants --commit-message "Sprint 106C Bernie context-frame invariants" --message "codex-sprint106c-context-frame-invariants ready for Codex review"` |

## Mission

Plan the invariant and verification harness for Bernie typed context frames so Ariadne can catch false no-slot, stale warning, future-appointment blocking, and roster/schedule explanation regressions deterministically.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, sprint_closeout, app/services/bernie/*, tests/test_bernie_* relevant to turn/context/slots, review/test_diary_smoke.py where relevant, and Bernie release gates. Produce a plan only for backend and/or harness assertions that prove context facts, model-facing advisories, and guardrail decisions are separated.

### Out of Scope

No production code during plan phase. No UI implementation, no persisted session table, no provider migration, no autonomous booking, no broad API rewrite.

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

Plan must list exact tests/harness files expected to change later, scenarios to cover, and how to distinguish true no-slot from roster unavailable, stale state, future-appointment advisory, and model uncertainty.

## Merge Criteria

Ariadne can accept the plan if it gives a small deterministic test surface that complements Claude backend design and Antigravity UX planning without duplicating either.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:

## Integration Notes

- Integration result: Superseded by Curie/Codex in-thread plan and Ariadne implementation of the backend frame/policy foundation.
- Files changed in implementation: `app/services/bernie/frames.py`, `app/services/bernie/policy.py`, `app/services/bernie/__init__.py`, `tests/test_bernie_context_frames.py`, and Sprint 106C coordination docs.
- Verification: py_compile passed for new Bernie frame/policy exports; focused backend Bernie/slot suite passed; local test schema reset afterwards.
