# antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | e14568c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review --commit-message "Sprint V1 Diary Bernie voice and intent UX review" --message "antigravity-sprint-v1-diary-bernie-voice-and-intent-ux-review ready for Codex review"` |

## Mission

Plan the visible Diary/Bernie UX for a friendlier professional Bernie voice and typed tool-intent responses, including how a receptionist might ask to extend an appointment while the UI shows proposal/review/confirmation states without implying autonomous writes.

## Scope

### In Scope

docs/diary/diary.js; docs/diary/diary.css; review/test_diary_smoke.py; wording and layout for Bernie chat/review cards that distinguish response voice, proposed diary action, required staff confirmation, and immutable audit/write boundaries.

### Out of Scope

Backend implementation; GraphRAG retrieval changes; taskpane/Command Centre; broad Diary redesign; creating direct write controls without backend proposal evidence.

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

Diary smoke tests for voice/reference/proposal separation; no confirm/write controls without backend evidence; node --check; frontend version check if assets change.

## Merge Criteria

Plan accepted by Ariadne; UX keeps Bernie helpful and professional while making deterministic state and staff-confirmation boundaries visible.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none (plan stage only)
- Verification run: local pytest smoke harness executed and passed to verify baseline stability
- Remaining risks: none (plan stage only)
