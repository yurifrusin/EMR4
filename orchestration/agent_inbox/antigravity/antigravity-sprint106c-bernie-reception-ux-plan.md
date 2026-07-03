# antigravity-sprint106c-bernie-reception-ux-plan

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 1fec462 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint106c-bernie-reception-ux-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint106c-bernie-reception-ux-plan --commit-message "Sprint 106C Bernie reception UX plan" --message "antigravity-sprint106c-bernie-reception-ux-plan ready for Codex review"` |

## Mission

Plan the Diary/reception interaction implications for typed Bernie context frames: how Bernie should present natural, professional responses while deterministic state/guardrail facts prevent false no-slot, stale warning, or future-appointment blocks.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, sprint_closeout, docs/diary Bernie UI code, existing review harness, no-slot suggestion UI, chat transcript state, recent user screenshot issues recorded in closeout context, and backend Bernie response shapes. Produce a plan only: identify UI copy/state surfaces likely affected by typed context frames and what should remain unchanged.

### Out of Scope

No production code during plan phase. No broad Diary redesign, no persisted session work, no autonomous booking, no provider migration, no live PHI, no implementation unless Ariadne explicitly releases complete sprint task.

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

Plan must list affected Diary files/selectors/tests if implementation is later approved, specific UI behaviours to preserve, and how to verify that Bernie can show last-message/chat history without stale prompt text or logically false warnings.

## Merge Criteria

Ariadne can accept the plan if it keeps UI changes minimal, respects the chat-turn direction, avoids scripting Bernie voice into brittle copy tables, and identifies deterministic checks for false/no-slot stale-message regressions.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
