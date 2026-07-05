# antigravity-sprint-r2-clarification-acceptance-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | a45c323 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r2-clarification-acceptance-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r2-clarification-acceptance-review --commit-message "Sprint R2 Gemini clarification acceptance review" --message "antigravity-sprint-r2-clarification-acceptance-review ready for Codex review"` |

## Mission

Use Gemini as an independent receptionist-domain and test-design reviewer for Sprint R2 clarification merge semantics, with real acceptance criteria and dissent, not UX-only review.

## Scope

### In Scope

Review R1 corpus clarification scenarios, docs/orchestration reception workstream notes, likely backend/session behaviours, expected staff-facing clarification outcomes, and propose concrete acceptance scenarios or fixture refinements under tests/fixtures/bernie_scenarios/ if needed.

### Out of Scope

Production backend implementation, Diary visual redesign, broad copy rewrites, GraphRAG, live provider prompt engineering, direct master/handoff updates, and changes outside scenario/docs/test-design artifacts unless explicitly approved after plan.

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

Plan packet first; after implementation approval, YAML fixture integrity tests if fixture edits are made, plus a concise review artifact with pass/fail acceptance checklist and risks.

## Merge Criteria

Gemini review clearly states whether R2 semantics preserve known fields, distinguish extension-vs-booking clarification, and avoid stale-session resurrection; any suggested fixture changes parse under existing integrity tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [tests/fixtures/bernie_scenarios/booking_to_extension_switch_during_clarification.yaml](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/fixtures/bernie_scenarios/booking_to_extension_switch_during_clarification.yaml)
  - [docs/receptionist_review_r2.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/receptionist_review_r2.md)
- Verification run:
  - Ran scenario integrity tests: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py` which completed successfully (all 8 passed, 1 skipped).
  - Validated that the newly added scenario fixture conforms fully to scenario schema and category constraints.
- Remaining risks:
  - Implicit correction vs explicit clarification logic overlap on the backend.
  - Concurrency checks must strictly enforce server-side revision controls to block stale session resurrection.

