# codex-sprint99-confidence-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint99-confidence-acceptance-review` |
| Status | integrated |
| Created | 76e00f9 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint99-confidence-acceptance-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint99-confidence-acceptance-review --commit-message "Sprint 99 confidence acceptance review" --message "codex-sprint99-confidence-acceptance-review ready for Codex review"` |

## Mission

As a Codex worker, independently review the current Bernie booking-confidence problem and submit acceptance criteria, edge cases, and API/UI risk notes for Ariadne before implementation release.

## Scope

### In Scope

Plan/review packet first only. Read-only inspection of app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py, tests/test_bernie_interpret_booking_instruction.py, tests/test_bernie_sprint98_release_gates.py, orchestration/bernie_release_gates.md, and latest sprint_closeout. Focus on confidence axes, decision bands, fuzzy matching, omitted-date inference, first-person response copy, details disclosure, and release-gate coverage.

### Out of Scope

Production code edits; dispatching/integrating other workers; live provider or browser testing; broad API-spine design beyond capturing follow-up boundaries.

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

Submit a plan/review packet with concrete acceptance gates, likely hidden risks, recommended tests, and resubmission criteria for Claude/Antigravity plans. No production files changed.

## Merge Criteria

Ariadne can use the review if it clearly identifies what must be implemented in Sprint 99 versus deferred to API-spine/voice/identity-provider sprints, and it challenges any overreach or unsafe confidence aggregation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-sprint99-confidence-acceptance-review.md` and this source task packet only. No production code, tests, or runtime diary files changed.
- Verification run: `python scripts\agent_worktrees.py handin --agent codex` succeeded; `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint99-confidence-acceptance-review --summary "Sprint 99 confidence acceptance review"` succeeded; read-only review of the scoped Bernie backend, diary UI, smoke tests, release gates, parallel workstreams, and latest closeout completed; `git diff --check` passed with only the existing CRLF/LF working-copy warning on this coordination packet. No production test suite was run because this is a coordination-only acceptance review.
- Remaining risks: Claude/Antigravity implementation plans should be rejected or resubmitted if they collapse confidence into one scalar, expose raw IDs/codes in ordinary mode, rely on UI warning-code parsing, weaken no-write/confirm gates, omit omitted-date/fuzzy-match/duplicate-patient tests, or broaden into live phone/voice/Medicare/OPV/PVM/API-spine work.
