# antigravity-bernie-reception-ux-plan

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | superseded |
| Created | 67f1c02 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-reception-ux-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-reception-ux-plan --commit-message "Bernie Reception UX Plan" --message "antigravity-bernie-reception-ux-plan ready for Codex review"` |

## Mission

Plan a calm, practice-usable diary UX for Bernie-assisted booking that feels like a helpful reception assistant, not a safety alarm, while preserving explicit staff confirmation.

## Scope

### In Scope

Plan packet first only. Review docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and the provided screenshots. Propose copy and visual hierarchy replacing Supervised Booking Review, robot/masked iconography, red blocked theatre, and BERNIE PROVISIONAL BOOKING. Include candidate-slot click-through, visible provisional slot focus, patient details and identity evidence where available, clear Confirm button and keyboard shortcut, calm warnings, no wasted labels, and deterministic smoke checks.

### Out of Scope

Production code edits before plan approval; backend/schema changes except documented contract requests; live phone/Medicare/provider integrations; broad diary redesign; taskpane, Command Centre, billing, SMS, resource admin, GCP/auth, and any bypass of staff confirmation.

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

Plan must name exact diary files/tests to touch, copy/UX acceptance criteria, keyboard confirmation path checks, confirmation-gate checks, no-write-before-confirm checks, asset cache-bust/version checks, and local/deployed smoke strategy.

## Merge Criteria

Ariadne accepts the plan only if it substantially improves receptionist usability, keeps API guardrails invisible but effective, uses screen space for decision information, and avoids scope drift into phone/OPV work.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None integrated. Initial plan was rejected; resubmission stalled in the Antigravity/Gemini channel.
- Verification run: Superseded by accepted Codex/Ariadne replacement UX implementation and deterministic diary harness.
- Remaining risks: None from Antigravity code, because no Antigravity Sprint 96 code was integrated.
