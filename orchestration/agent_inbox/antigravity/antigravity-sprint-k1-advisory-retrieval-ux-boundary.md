# antigravity-sprint-k1-advisory-retrieval-ux-boundary

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | pending_plan_review |
| Created | 944883f |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-k1-advisory-retrieval-ux-boundary --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-k1-advisory-retrieval-ux-boundary --commit-message "Sprint K1 advisory retrieval UX boundary" --message "antigravity-sprint-k1-advisory-retrieval-ux-boundary ready for Codex review"` |

## Mission

Plan Sprint K1 Diary/Bernie UI review for consuming advisory practice knowledge without making it look like deterministic diary truth. Focus on how retrieved practice facts should be labelled, disclosed, and kept out of confirm/no-slot authority.

## Scope

### In Scope

Plan only first. docs/diary/diary.js and review/test_diary_smoke.py planning only if UI display of advisory facts is included; copy/disclosure/state names; smoke-test strategy for ensuring advisory retrieval does not show confirm/no-slot authority or overwrite schedule explanations.

### Out of Scope

No implementation before plan gate, no backend ownership, no visual redesign, no slot search changes, no booking write path, no persisted sessions, no production GraphRAG.

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

Plan packet first. Later implementation, if UI changes, should run node --check, frontend version check, focused review smoke tests, and git diff --check.

## Merge Criteria

A concrete UI/UX plan for clearly advisory retrieved practice facts, with deterministic diary/reception state remaining visibly authoritative.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
