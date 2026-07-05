# antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | bed06b3 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review --commit-message "Sprint R22 fake-provider scenario UX acceptance review" --message "antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review ready for Codex review"` |

## Mission

Gemini/Antigravity: define receptionist-facing acceptance criteria and risky copy boundaries for R22 fake-provider scenario gates. Focus on whether the proposed structured outputs would be safe and understandable to reception staff.

## Scope

### In Scope

orchestration scenario/UX safety artifact, references to fake_provider_prompt_ux_safety_review.md, bernie_release_gates.md, manifest_eval tests

### Out of Scope

Production code wiring, live AI calls, frontend implementation, database migrations

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

Submit a concise orchestration artifact with accepted/rejected scenario expectations, staff-facing copy boundaries, and live-provider readiness blockers.

## Merge Criteria

Ariadne can use the artifact to review R22 tests and decide whether live Gemini wiring remains blocked.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: [orchestration/fake_provider_scenario_ux_acceptance_review.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/fake_provider_scenario_ux_acceptance_review.md)
- Verification run: Created the UX safety review and acceptance criteria document for Sprint R22. Ran focused verification tests with `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_manifest_prompt_evaluation.py tests/test_bernie_fake_provider_adversarial_prompt.py` which all passed (76 passed).
- Remaining risks: The review document is purely static documentation outlining boundaries and gates; there are no code changes, meaning zero runtime regression risk. However, actual live Vertex/Gemini wiring still requires addressing the listed readiness blockers.
