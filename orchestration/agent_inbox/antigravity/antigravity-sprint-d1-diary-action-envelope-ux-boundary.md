# antigravity-sprint-d1-diary-action-envelope-ux-boundary

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | superseded |
| Created | 7bab79b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-d1-diary-action-envelope-ux-boundary --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-d1-diary-action-envelope-ux-boundary --commit-message "Sprint D1 diary action envelope UX boundary" --message "antigravity-sprint-d1-diary-action-envelope-ux-boundary ready for Codex review"` |

## Mission

Review the Diary UI after G1-G6 and plan how visible human/Bernie action surfaces should consume typed diary action envelopes without adding confusing controls or broad redesign. Focus on confirmation copy, no raw fallback after signed failure, and future actions like extend/cancel/check-in.

## Scope

### In Scope

docs/diary/diary.js, docs/diary/diary.html, review/test_diary_smoke.py, orchestration/sprint_closeout.md

### Out of Scope

No production implementation during plan phase, no visual redesign, no taskpane, no Command Centre, no GraphRAG, no new Bernie natural-language grammar.

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

Plan should identify UI affordance invariants and smoke tests for a small D1 implementation. It must distinguish current compatibility fallback from signed-capable no-fallback behaviour.

## Merge Criteria

Ariadne can approve a small UI/test plan that supports a native diary action envelope boundary and preserves existing G1-G6 interaction behaviour.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
- Superseded by Ariadne: Antigravity CLI returned no submitted artifact and its durable worktree remained clean. D1 became a backend-only descriptor extraction with no Diary UI asset changes.
