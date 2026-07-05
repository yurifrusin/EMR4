# antigravity-sprint-r20-manifest-prompt-safety-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | e0406aa |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r20-manifest-prompt-safety-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r20-manifest-prompt-safety-review --commit-message "Sprint R20 Manifest prompt safety review" --message "antigravity-sprint-r20-manifest-prompt-safety-review ready for Codex review"` |

## Mission

Gemini/Antigravity: review how Bernie should safely consume the read-only Diary Capability Manifest. Focus on prompt wording, receptionist trust, refusal/clarification rules, and dangers of schema literacy being mistaken for authority.

## Scope

### In Scope

orchestration/bernie_diary_manifest_review.md, orchestration/manifest_drift_review.md, app/services/diary/capability_manifest.py, relevant Bernie interaction/release-gate docs, orchestration review artifact.

### Out of Scope

Runtime prompt changes, live AI calls, backend mutations, UI redesign, database migrations, codebase dumping.

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

Write a concise artifact under orchestration/ with accepted prompt-safety principles, refusal rules, and acceptance criteria for manifest consumption.

## Merge Criteria

Ariadne can use the artifact to review Claude/DeepSeek work and decide whether live prompt injection is safe yet.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [orchestration/manifest_prompt_safety_review.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/manifest_prompt_safety_review.md) (Created safety review artifact)
- Verification run:
  - Local inspection of backend manifest capability fields and enums.
  - Review of current prompt safety principles, refusal/clarification rules, and acceptance criteria.
- Remaining risks:
  - Divergence between manifest schema updates and LLM system prompt instructions (mitigated by version checks and automated safety validation checks).
