# antigravity-bernie-supervised-review-ui-harness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 090ff0b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-supervised-review-ui-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-supervised-review-ui-harness --commit-message "Dispatch Sprint 49 Bernie review UI harness" --message "Sprint 49 dispatched to Antigravity"` |

## Mission

Add a deterministic diary smoke/review UI harness that renders the Sprint 48 staff_review payload for staff review, without live Bernie runtime, autonomous writes, or screenshot-heavy verification.

## Scope

### In Scope

Plan first. After approval, docs/diary/diary.{html,css,js} and review harness files only as needed. Add a smoke-gated staff-review panel/rendering path driven by fixture staff_review payloads for blocked, candidate_selection_required, and confirmation_ready outcomes. Include stable data-testid/selectors and deterministic Playwright/pytest review checks for headline/status/action, candidate/selected slot summary, confirm button disabled until explicit simulated staff approval, and no mutation/API write behaviour in smoke mode.

### Out of Scope

Backend routes/schemas/models/tests, live Bernie natural-language runtime, Gemini/LLM calls, direct appointment writes, real confirm-Bernie submission against live backend, taskpane, Command Centre, booking modal redesign, drag/drop, waiting-room/status UI, billing, SMS, resource admin, and any non-smoke production workflow activation.

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

Plan packet first. After approval: node --check docs/diary/diary.js; run deterministic review/Playwright checks added or updated for the smoke-gated Bernie review panel; run existing diary review harness if relevant; prove no live API mutation/write path is triggered in smoke mode; git diff --check.

## Merge Criteria

Plan packet is acceptable and names exact UI boundary. Implementation is smoke/review-harness gated, uses stable selectors, consumes the Sprint 48 staff_review shape, preserves existing diary/booking/waiting-room behaviour, and passes deterministic UI checks without requiring Computer Use screenshots.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/checks_diary.json, review/test_diary_smoke.py
- Verification run: node --check docs/diary/diary.js, python scripts/check_frontend_versions.py, .venv/Scripts/pytest review/test_diary_smoke.py, and git diff --check.
- Remaining risks: None. The Bernie Booking Review panel operates strictly under smoke-gated parameters, renders the deterministic payloads from Sprint 48 contract cleanly, and has no backend or mutation write side-effects.
