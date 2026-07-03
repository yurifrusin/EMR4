# antigravity-sprint-k1b-advisory-retrieval-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 736a9ce |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-k1b-advisory-retrieval-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-k1b-advisory-retrieval-ux-review --commit-message "Dispatch Sprint K1b Antigravity advisory retrieval UX plan" --message "antigravity-sprint-k1b-advisory-retrieval-ux-review ready for Codex review"` |

## Mission

Plan the visible Diary/Bernie UX for advisory retrieval facts: how retrieved practice facts should appear in latest/chat/review panels, how to keep wording helpful and professional, and how to prevent retrieved facts from looking like booking authority or confirmed slot truth.

## Scope

### In Scope

docs/diary/diary.js; docs/diary/diary.css only if needed; review/test_diary_smoke.py fixtures/assertions for advisory retrieval display and non-authority controls.

### Out of Scope

Backend retrieval implementation; Graph/vector store deployment; persisted sessions; auto-mode; taskpane/Command Centre changes; broad redesign; PHI-bearing storage; any confirm/action control driven by retrieval.

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

Plan first only. Later implementation should run node --check docs\\diary\\diary.js, focused/full review/test_diary_smoke.py as relevant, frontend version check, and git diff --check.

## Merge Criteria

Plan defines where advisory facts render, how provenance/confidence is shown or hidden, when not to show them, and tests proving confirm/candidate/no-slot UI is not created by retrieval.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
