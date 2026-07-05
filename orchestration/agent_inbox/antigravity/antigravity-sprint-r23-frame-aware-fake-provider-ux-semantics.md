# antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | c8fed3c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics --commit-message "Sprint R23 frame-aware fake-provider UX semantics" --message "antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics ready for Codex review"` |

## Mission

Gemini/Antigravity: define receptionist-safe frame-shape acceptance criteria for fake-provider outputs after R22. Review proposal, clarify, refusal, and read_request frames and identify which fields must/must-not appear before live provider dry-run.

## Scope

### In Scope

orchestration UX/semantics artifact referencing manifest_eval.py, R22 closeout, fake_provider_scenario_ux_acceptance_review.md, bernie_release_gates.md

### Out of Scope

Production code, frontend UI, live AI calls, DB/migrations, runtime prompt wiring

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

Submit a concise orchestration artifact with accepted/rejected frame-shape rules and live-provider readiness blockers.

## Merge Criteria

Ariadne can use the artifact to review R23 frame-aware validator tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [fake_provider_frame_shape_acceptance_criteria.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/fake_provider_frame_shape_acceptance_criteria.md)
- Verification run:
  - Created [fake_provider_frame_shape_acceptance_criteria.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/fake_provider_frame_shape_acceptance_criteria.md) defining MUST/MUST-NOT constraints for the four receptionist-safe frame kinds (`proposal`, `clarify`, `refusal`, `read_request`).
  - Cross-referenced logic with [frames.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/services/diary/frames.py), [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/schemas/appointments.py), [manifest_eval.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/services/ai/evals/manifest_eval.py), [fake_provider_scenario_ux_acceptance_review.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/fake_provider_scenario_ux_acceptance_review.md), and [bernie_release_gates.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/bernie_release_gates.md).
  - Executed focused pytest suite: `.venv/Scripts/python.exe -m pytest tests/test_bernie_manifest_receptionist_scenarios.py tests/test_bernie_manifest_prompt_evaluation.py tests/test_bernie_fake_provider_adversarial_prompt.py -q` (all passed successfully).
- Remaining risks:
  - None; this is a documentation-only sprint defining frame-shape criteria, introducing zero runtime codebase or database risks.

