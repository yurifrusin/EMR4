# codex-bernie-dev-review-selector-help

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-dev-review-selector-help` |
| Status | submitted |
| Created | ae57b2a |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-dev-review-selector-help --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-dev-review-selector-help --commit-message "Dispatch Sprint 58 Bernie selector help" --message "codex-bernie-dev-review-selector-help ready for Codex review"` |

## Mission

Plan first, then after approval add a tiny dev-only explanatory/help affordance around the Bernie fixture-state selector so staff/dev reviewers understand the blocked, candidate_selection_required, and confirmation_ready states without exposing anything in default diary mode.

## Scope

### In Scope

Plan packet only first. After approval, docs/diary UI assets and review deterministic Playwright checks as needed; explicit bernie_dev_review=true gating only; concise helper text or tooltip near the fixture selector; no default exposure; no endpoint calls caused by help text alone; preserve selector state behavior and explicit approval before confirm-Bernie; route-intercept all tests; bump asset versions if runtime assets change.

### Out of Scope

Backend routes/schemas, production/default exposure, autonomous booking, natural-language LLM parsing, live API writes in tests, taskpane, Command Centre, migrations, patient/resource admin, billing, SMS, broad diary redesign, unrelated refactors.

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

Plan packet first. After approval: node --check for changed JS, frontend version integrity, deterministic Playwright checks for help visibility/gating/no-call behavior, existing diary review harness, no confirm-Bernie POST before explicit staff approval, and git diff --check.

## Merge Criteria

Plan names exact UI boundary and no-production-exposure guarantees. Implementation is minimal, dev-gated, deterministic, route-intercepted, has no live writes, preserves existing Bernie selector semantics, passes listed verification, and submits via protocol review packet.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Coordination only: created `orchestration/agent_inbox/codex/plan-codex-codex-bernie-dev-review-selector-help.md` and updated this task packet status/notes. No runtime, docs, or test files changed.
- Verification run: `python scripts\agent_worktrees.py handin`; `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-dev-review-selector-help ...`; `git status --short --branch`.
- Remaining risks: Implementation not started by design; runtime verification remains pending until Ariadne sends exactly `complete sprint task`.
