# codex-sprint-g4-create-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 1e49398 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-g4-create-confirm-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-g4-create-confirm-invariants --commit-message "Sprint G4 create-confirm invariants" --message "codex-sprint-g4-create-confirm-invariants ready for Codex review"` |

## Mission

Plan adversarial invariants for migrating the human create-booking modal to signed create-confirm while keeping status-after-create separate and direct POST compatibility bounded.

## Scope

### In Scope

Tests/invariants around create proposal evidence, confirm payload freshness, warnings acceptance, no direct POST from signed-capable create UI, no status PATCH if create confirm fails, and no broad grammar.

### Out of Scope

Production code during plan gate; edit/update G3 path; drag/drop/resize; cancel/delete/status grammar; raw endpoint removal; persisted sessions; GraphRAG; UI redesign.

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

Focused pytest/review smoke plan; diff check.

## Merge Criteria

Plan is scoped, adversarial, and explicit about create/status boundary, warning acceptance, signed evidence, and compatibility boundary.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-sprint-g4-create-confirm-invariants.md`; `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g4-create-confirm-invariants.md`.
- Verification run: Read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and this task packet; inspected the existing create proposal/confirm route, schema, diary create Save branch, and adjacent tests with `rg`/targeted file reads; plan packet captured with the explicit venv Python path. `git diff --check` to be run before submit.
- Remaining risks: Implementation must choose whether to reuse the Bernie-named create-confirm route or add a neutral staff-create-confirm alias/input without duplicating validation; direct POST compatibility must be tightly bounded so the signed-capable create UI cannot silently bypass confirm evidence; status-after-create must remain a separate PATCH that only runs after confirmed create success.
