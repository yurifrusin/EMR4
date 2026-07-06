# antigravity-sprint109-live-smoke-ux-readiness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 39dac51b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint109-live-smoke-ux-readiness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint109-live-smoke-ux-readiness --commit-message "Sprint 109 live-smoke UX readiness review" --message "antigravity-sprint109-live-smoke-ux-readiness ready for Codex review"` |

## Mission

Plan/review only: assess staff-visible UX and acceptance implications for a future no-write live-provider smoke, without enabling live providers or changing runtime behavior.

## Scope

### In Scope

docs/diary/diary.js; review/test_diary_smoke.py; Sprint 108 provider metadata behavior; closeout and release-gate docs. Produce a plan/review artifact identifying copy, debug labels, staff warnings, and acceptance tests needed before a future approved smoke.

### Out of Scope

No UI implementation unless explicitly approved after plan review; no provider enablement, no live calls, no backend changes, no autonomous booking writes, no H15/trove, no memory/RAG/GraphRAG.

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

Plan/review artifact only; if touching docs, run git diff --check. Do not run live provider smoke.

## Merge Criteria

Artifact is proposal-only, preserves no-write/no-live-default posture, and separates future UX acceptance from gate approval.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint109-live-smoke-ux-readiness.md`
- Verification run:
  - Plan accepted for UX criteria and integrated into
    `docs/bernie-band2-provider-gate-criteria.md`.
- Remaining risks:
  - Antigravity CLI repeatedly prefaced the run with stale `--print-timeout`
    investigation chatter; useful Sprint 109 plan content was still captured.
