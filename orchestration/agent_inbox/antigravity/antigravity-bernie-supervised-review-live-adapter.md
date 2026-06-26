# antigravity-bernie-supervised-review-live-adapter

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 317173c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-supervised-review-live-adapter --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-supervised-review-live-adapter --commit-message "Dispatch Sprint 50 Bernie review live adapter" --message "Sprint 50 dispatched to Antigravity"` |

## Mission

Connect the diary Bernie review panel to the backend supervised-booking staff_review response behind an explicit feature/smoke gate, without posting confirmation or writing appointments.

## Scope

### In Scope

Plan first. After approval, docs/diary/diary.{html,css,js} and review harness files only as needed. Add a feature/smoke-gated client adapter that can call the existing /api/v1/appointments/proposals/bernie/supervised-booking endpoint with deterministic fixture/dev input, render the returned staff_review payload in the Sprint 49 review panel, and expose stable selectors/structured checks. Preserve smoke fixture modes. Confirm button must remain disabled until explicit approval and must not post to confirm-Bernie in this sprint.

### Out of Scope

Backend routes/schemas/models/tests, real confirm-Bernie submission, autonomous booking writes, Gemini/LLM calls, taskpane, Command Centre, booking modal redesign, waiting-room/status UI, resource admin, billing, SMS, and enabling the live adapter by default in normal diary mode.

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

Plan packet first. After approval: node --check docs/diary/diary.js; deterministic Playwright/review checks for fixture modes and adapter mode using route interception or a local stubbed response; prove no confirm-Bernie POST/write path exists; run frontend version integrity; git diff --check.

## Merge Criteria

Plan is accepted and names exact feature gate. Implementation preserves normal diary behaviour, keeps all write paths disabled, renders real Sprint 48 staff_review shape from an intercepted/stubbed backend response, passes deterministic review checks, and requires no Computer Use screenshots.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
