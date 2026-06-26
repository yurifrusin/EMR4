# antigravity-diary-audit-history-readability

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 8e36c52 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-diary-audit-history-readability --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-audit-history-readability --commit-message "Diary audit history readability" --message "antigravity-diary-audit-history-readability ready for Codex review"` |

## Mission

Sprint 34 / Programme 2D readiness: plan and, after approval, polish the diary's read-only audit history rendering so staff can understand confirmed appointment history without seeing raw IDs or confusing action labels.

## Scope

### In Scope

Plan packet first. After approval, docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, smoke-mode audit fixtures, review/checks_diary.json and review/test_diary_smoke.py if useful. Render backend actor display fields when present, keep UUID fallback restrained, preserve collapsed/read-only behaviour, and improve action/status copy only inside audit history.

### Out of Scope

Backend implementation, taskpane, Command Centre, Gemini/AI provider code, write actions from audit history, warning-code persistence, broad supervisor dashboard, visual redesign of unrelated diary panels, restore/reactivation, billing, SMS, and direct Bernie execution.

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

Plan packet first. After approval, node --check docs/diary/diary.js, deterministic diary review smoke with any new audit readability assertion, frontend version check if diary assets change, git diff --check, and targeted browser checks only if structural checks cannot verify the behaviour.

## Merge Criteria

Audit history remains hidden on create, collapsed and read-only on edit, renders friendly actor/action/status text from backend-shaped fixtures, degrades gracefully for missing fields, deterministic review checks pass, and unrelated booking flows are untouched.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.js, review/test_diary_smoke.py
- Verification run: node --check docs/diary/diary.js (syntax check), git diff --check (no trailing whitespace), and .venv\Scripts\pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q (all 17 checks passing, including new readability assertions for friendly names, status changes, UUID fallbacks, and transition sentences)
- Remaining risks: None. The implementation uses local mock configurations and robust fallback logic for formatting display names and UUIDs. The audit layout collapsed-by-default behavior and unrelated booking modal structures remain untouched.
