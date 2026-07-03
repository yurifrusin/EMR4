# antigravity-sprint-n1a-diary-reception-rehome-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | d76f100 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-n1a-diary-reception-rehome-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-n1a-diary-reception-rehome-review --commit-message "Sprint N1a diary reception rehome review" --message "antigravity-sprint-n1a-diary-reception-rehome-review ready for Codex review"` |

## Mission

Review and/or implement the N1a diary/reception domain rehome from a frontend-contract and smoke-harness perspective. Ensure the Diary UI and review harness keep seeing byte-identical reception_policy and bernie.reception_context.v1 contracts.

## Scope

### In Scope

Inspect app/services/bernie frames/policy consumers, docs/diary/diary.js reception_policy consumption, review/test_diary_smoke.py reception_policy cases, and backend schema tests. If implementing, keep to pure rehome/facade changes only and avoid overlap unless assigned after plan review.

### Out of Scope

No UI redesign, no copy/catalog work, no envelopes, no suggestion/action grammar additions, no migrations, no GraphRAG, no auto-mode.

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

Plan packet first. Later implementation verification should include diary smoke focused reception_policy checks if UI contract risk exists, plus backend focused tests and git diff --check.

## Merge Criteria

A plan or bounded implementation lane that protects frontend contract compatibility and flags any byte-identity risk for Ariadne.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: [test_bernie_diary_rehome_compatibility.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_bernie_diary_rehome_compatibility.py)
- Verification run:
  - Focused pytest: `pytest tests/test_bernie_diary_rehome_compatibility.py` (4 passed, 1 skipped as expected since `app.services.diary` is not yet present on the isolated branch).
  - Domain tests: `pytest tests/test_bernie_domain_package.py tests/test_bernie_temporal_policy.py tests/test_bernie_context_frames.py` (35 passed).
  - Smoke tests: `pytest review/test_diary_smoke.py -k reception_policy` (5 passed).
  - Git diff: `git diff --check` passed.
- Remaining risks: None. The compatibility suite tests both current flat-module invariants and cross-package facade object identity dynamically, so it will automatically check Claude's implementation when integrated.
