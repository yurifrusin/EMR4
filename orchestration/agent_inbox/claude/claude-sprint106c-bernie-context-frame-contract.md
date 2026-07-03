# claude-sprint106c-bernie-context-frame-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 1fec462 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint106c-bernie-context-frame-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint106c-bernie-context-frame-contract --commit-message "Sprint 106C Bernie context-frame contract" --message "claude-sprint106c-bernie-context-frame-contract ready for Codex review"` |

## Mission

Plan the backend/domain slice for Bernie typed receptionist context frames and reception-skill policy, following the accepted Fable architecture direction and the new temporal-policy foundation.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, sprint_closeout, Fable consult packets, app/services/bernie/*, app/routers/appointments.py Bernie paths, patient booking context, temporal policy, slot normalizer/proposal tests, and Bernie release gates. Produce a plan for typed context-frame contracts that separate requested appointment facts, roster/schedule facts, patient booking context, slot-search facts, advisory warnings, and hard guardrail outcomes before Bernie speaks. Preserve staff-confirmed booking only.

### Out of Scope

No production code during plan phase. No persisted Bernie session DB table/migration yet, no autonomous booking, no broad API-spine rewrite, no LLM provider migration, no Diary UI implementation beyond noting required contract implications, no PHI/log-retention changes.

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

Plan must list exact files expected to change, public JSON compatibility expectations, focused backend tests to add/run, live-provider/release-gate implications, and risks around prompt freedom versus deterministic guardrails.

## Merge Criteria

Ariadne can accept the plan if it gives a bounded backend contract for typed context frames, keeps guardrails deterministic, avoids spaghetti transition tables, preserves existing booking confirmation safety, and can be implemented in one small sprint.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
