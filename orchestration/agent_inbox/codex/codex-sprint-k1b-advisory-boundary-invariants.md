# codex-sprint-k1b-advisory-boundary-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 736a9ce |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-k1b-advisory-boundary-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-k1b-advisory-boundary-invariants --commit-message "Dispatch Sprint K1b Codex advisory invariant plan" --message "codex-sprint-k1b-advisory-boundary-invariants ready for Codex review"` |

## Mission

Plan adversarial invariants for K1b advisory retrieval: retrieved facts may explain or suggest only, and must not alter deterministic diary state, slot/search truth, roster truth, policy hard blocks, confirm affordance, session freshness, audit evidence, or write payloads.

## Scope

### In Scope

tests around app/services/practice_knowledge, Bernie route/outcome/confirm/evidence tests, review/test_diary_smoke.py if UI consumes advisory frames; plan only until approved.

### Out of Scope

Production code before approval; graph/vector store deployment; persisted PHI/session tables; auto-mode; broad API rewrite; real PHI; worker edits on master.

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

Plan first only. Later implementation should add negative/adversarial tests, run relevant backend and Diary smoke subsets, py_compile/node checks as applicable, and git diff --check.

## Merge Criteria

Plan defines no-authority negative tests, fail-closed retrieval outage tests, provenance/source handling tests, and stale/session non-interference tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
