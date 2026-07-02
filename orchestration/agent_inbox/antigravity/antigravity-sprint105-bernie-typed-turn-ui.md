# antigravity-sprint105-bernie-typed-turn-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 50b28c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint105-bernie-typed-turn-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint105-bernie-typed-turn-ui --commit-message "Dispatch Sprint 105 typed turn UI plan" --message "antigravity-sprint105-bernie-typed-turn-ui ready for Codex review"` |

## Mission

Plan Sprint 105 Diary UI work for typed Bernie turns and eventful clarification/suggestion interactions. Move the chat surface from plain transcript plus prompt reuse toward typed staff/Bernie events that can be submitted to the backend contract without stale prompt leakage.

## Scope

### In Scope

Plan packet first only. In scope for eventual implementation planning: docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, and review/test_diary_smoke.py. Plan typed client events for staff instruction, clarification reply, no-slot suggestion click, candidate selection, choose another time, proposal preview, refresh/date navigation stale clearing, and confirmation. Preserve compact reception UI, no-slot clickable alternatives, New Session, auto-preview toggle, and separation between composer draft text and submitted turn history.

### Out of Scope

No production code before plan approval. Do not redesign the entire diary panel, implement voice/listener/wake-word lanes, add limited auto-mode, bypass backend confirmation, move patient details verification into booking recognition, or touch broad taskpane/clinical surfaces.

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

Plan must specify deterministic UI/review tests for composer clearing after submit, typed suggestion click not reusing stale prose as a prompt, Refresh/Today/Prev/Next clearing stale proposal evidence, candidate selection preserving candidate snapshot ids, confirmation sending backend evidence, and ordinary-mode visual copy remaining compact.

## Merge Criteria

Plan is mergeable when it names exact frontend state fields/events, avoids overlap with backend schema implementation, includes asset version strategy, records risks/dissent, and keeps the Sprint 104 user-tested live flow working during migration.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
