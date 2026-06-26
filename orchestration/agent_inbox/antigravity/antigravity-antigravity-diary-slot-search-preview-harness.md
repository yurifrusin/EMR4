# antigravity-antigravity-diary-slot-search-preview-harness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 3645361 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-antigravity-diary-slot-search-preview-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-antigravity-diary-slot-search-preview-harness --commit-message "Antigravity Diary Slot Search Preview Harness" --message "antigravity-antigravity-diary-slot-search-preview-harness ready for Codex review"` |

## Mission

Plan first, then after approval add a tiny deterministic diary/review harness surface for future read-only slot-search proposal previews, without exposing autonomous Bernie or adding mutation controls.

## Scope

### In Scope

Plan packet first. After approval, docs/diary smoke fixtures and review harness files only unless a minimal diary helper is unavoidable. Add deterministic checks that can render or validate a read-only slot-search proposal preview shape from mock data, using stable selectors/compact assertions.

### Out of Scope

Backend implementation, live API integration unless Claude's contract is already integrated and trivially callable, autonomous Bernie runtime, appointment create/edit/status/cancel mutations, taskpane, Command Centre, resource admin, SMS, billing, and broad diary layout changes.

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

Plan packet first. After approval: node --check if diary JS changes; pytest review/test_diary_smoke.py or a small review pytest for the slot-search preview; frontend version check if assets change; git diff --check.

## Merge Criteria

Codex can verify the diary/review harness has a read-only slot-search preview path or test fixture that helps future Bernie UI work stay deterministic and cheap, with no mutation affordance added.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/checks_diary.json, review/test_diary_smoke.py
- Verification run: syntax check (`node --check`), deterministic smoke assertions (`pytest` on module-scoped `diary_page` fixture), frontend asset version check (`check_frontend_versions.py`), and `git diff --check`.
- Remaining risks: None. The preview features are fully gated by `smoke=true` and `slot_preview=true` parameters and do not affect live production workflows. Clicking slot-preview candidates behaves as a no-op via event propagation blockages, protecting booking creations.

