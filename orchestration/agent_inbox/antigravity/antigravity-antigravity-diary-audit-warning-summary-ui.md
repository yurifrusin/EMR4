# antigravity-antigravity-diary-audit-warning-summary-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | pending_plan_review |
| Created | a448194 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-antigravity-diary-audit-warning-summary-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-antigravity-diary-audit-warning-summary-ui --commit-message "Antigravity Diary Audit Warning Summary UI" --message "antigravity-antigravity-diary-audit-warning-summary-ui ready for Codex review"` |

## Mission

Plan, then after approval display persisted appointment audit warning metadata in the read-only diary Audit History section without adding mutation controls.

## Scope

### In Scope

Plan packet first. After approval: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, smoke fixtures, and review/test_diary_smoke.py or review/checks_diary.json as needed for deterministic warning-summary assertions. Cache-bust diary assets if changed.

### Out of Scope

Backend implementation, appointment mutation/proposal logic, broad booking modal redesign, supervisor dashboard, Bernie runtime/tool execution, taskpane, Command Centre, SMS, billing, resource administration, cancelled appointment restore/reactivation.

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

Plan packet first. After approval: node --check docs/diary/diary.js, deterministic diary review smoke with compact assertions for warning summary rendering, frontend version check if assets change, git diff --check, targeted browser checks only if structural assertions cannot prove behaviour.

## Merge Criteria

Codex can verify audit history remains read-only, warning summaries render clearly when the backend/smoke data provides them, empty/no-warning rows remain clean, and no appointment mutation or unrelated diary UI behaviour changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
