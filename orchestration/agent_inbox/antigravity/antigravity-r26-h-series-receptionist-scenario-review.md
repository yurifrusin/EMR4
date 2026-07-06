# antigravity-r26-h-series-receptionist-scenario-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | superseded |
| Created | 6a4099f5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-r26-h-series-receptionist-scenario-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-r26-h-series-receptionist-scenario-review --commit-message "R26 H-series receptionist scenario review" --message "antigravity-r26-h-series-receptionist-scenario-review ready for Codex review"` |

## Mission

Review H21/H-series neutral movement findings as receptionist-domain/product input and write a tangible review artifact recommending which synthetic deterministic Diary/Bernie scenarios should be added next, without inspecting raw trove content.

## Scope

### In Scope

docs/receptionist_review_r26.md only after plan approval; committed H-series docs and existing scenario corpus docs

### Out of Scope

production code, tests, raw local_data/ignored JSON, semantic labelling, live provider calls, frontend changes

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

Tangible docs/receptionist_review_r26.md artifact with scenario recommendations, risks, and acceptance criteria

## Merge Criteria

Ariadne receives a safe Gemini/product review mapping neutral movement profiles to deterministic scenario priorities

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run: Antigravity submitted a review artifact, but Ariadne rejected it for semantically mapping neutral H-series deltas into receptionist workflows despite the corrective prompt. Ariadne replaced it with a source-safe local review.
- Remaining risks: Future Gemini review prompts need an even stronger H15-gate warning when neutral historical aggregates are involved.
